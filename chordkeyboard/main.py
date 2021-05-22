#!/usr/bin/env python
# Copyright (c) 2021, see AUTHORS. Licensed under GPLv3+, see LICENSE.

import asyncio
import re
import signal

import evdev
import evdev.ecodes as ec

IDL = '05D9FF3433364D4743175718'
IDR = '05DBFF353237464843168412'
L = f'/dev/input/by-id/usb-www.BeyondQ.com_DuMang_KeyBoard_DK6_{IDL}-event-kbd'
R = f'/dev/input/by-id/usb-www.BeyondQ.com_DuMang_KeyBoard_DK6_{IDR}-event-kbd'

REAL_MAP = {
    ec.KEY_Z: 'a',
    ec.KEY_S: 'r',
    ec.KEY_D: 's',
    ec.KEY_V: 't',
    ec.KEY_N: 'n',
    ec.KEY_K: 'e',
    ec.KEY_L: 'i',
    ec.KEY_SLASH: 'o',
    ec.KEY_X: 'down',
    ec.KEY_C: 'up',
    ec.KEY_COMMA: 'left',
    ec.KEY_DOT: 'right',
    ec.KEY_LEFTSHIFT: 'lthumb',
    ec.KEY_SPACE: 'rthumb',
}

VALNAME_MAP = {
    0: 'release',
    1: 'press',
    2: 'repeat',
}


def type_(*codes):
    def press_release(ui):
        for code in codes:
            ui.write(ec.EV_KEY, code, 1)
            ui.write(ec.EV_KEY, code, 0)
        ui.syn()
    return press_release


RULES = (
    # a-rocks
    ('a press  r press  r release', 'a defused', type_(ec.KEY_A,
                                                       ec.KEY_L)),
    ('a defused (.*?) a release', r'\1', None),

    # r-rocks
    ('r (press|defused)  s press  s release', 'r defused',
     type_(ec.KEY_C)),
    ('r (press|defused)  t press  t release', 'r defused',
     type_(ec.KEY_W)),
    ('r (press|defused)  o press  o release', 'r defused',
     type_(ec.KEY_C, ec.KEY_O)),
    ('r defused (.*?) r release', r'\1', None),

    # s-rocks
    ('s (press|defused)  t press  t release', 's defused',
     type_(ec.KEY_D)),
    ('s (press|defused)  r press  r release', 's defused',
     type_(ec.KEY_L)),
    ('s (press|defused)  up press', 's defused  up inactive',
     type_(ec.KEY_Z)),
    ('s defused (.*?) s release', r'\1', None),

    # t-rocks
    ('t (press|defused)  s press  s release', 't defused',
     type_(ec.KEY_P)),
    ('t (press|defused)  n press  n release', 't defused',
     type_(ec.KEY_T, ec.KEY_H)),
    ('t (press|defused)  e press  e release', 't defused',
     type_(ec.KEY_T, ec.KEY_H, ec.KEY_E)),
    ('t defused (.*?) t release', r'\1', None),

    # n-rocks
    ('n (press|defused)  a press  a release', 'n defused',
     type_(ec.KEY_H, ec.KEY_A)),
    ('n (press|defused)  t press  t release', 'n defused',
     type_(ec.KEY_N, ec.KEY_D, ec.KEY_SPACE)),
    ('n (press|defused)  e press  e release', 'n defused',
     type_(ec.KEY_H, ec.KEY_E)),
    ('n defused (.*?) n release', r'\1', None),

    # e-rocks
    ('e (press|defused)  t press  t release', 'e defused',
     type_(ec.KEY_E, ec.KEY_D, ec.KEY_SPACE)),
    ('e (press|defused)  n press  n release', 'e defused',
     type_(ec.KEY_H)),
    ('e defused (.*?) e release', r'\1', None),

    # i-rocks
    ('i (press|defused)  n press  n release', 'i defused',
     type_(ec.KEY_I, ec.KEY_N, ec.KEY_G)),
    ('i (press|defused)  e press  e release', 'i defused',
     type_(ec.KEY_U)),
    ('i (press|defused)  right press', 'i defused  right inactive',
     type_(ec.KEY_J)),
    ('i defused (.*?) i release', r'\1', None),

    # o-rocks
    ('o (press|defused)  e press  e release', 'o defused',
     type_(ec.KEY_O, ec.KEY_U)),
    ('o defused (.*?) o release', r'\1', None),

    # arst neio
    ('a press (.*?) a release', r'\1', type_(ec.KEY_A)),
    ('r press (.*?) r release', r'\1', type_(ec.KEY_R)),
    ('s press (.*?) s release', r'\1', type_(ec.KEY_S)),
    ('t press (.*?) t release', r'\1', type_(ec.KEY_T)),
    ('n press (.*?) n release', r'\1', type_(ec.KEY_N)),
    ('e press (.*?) e release', r'\1', type_(ec.KEY_E)),
    ('i press (.*?) i release', r'\1', type_(ec.KEY_I)),
    ('o press (.*?) o release', r'\1', type_(ec.KEY_O)),

    # rthumb-starting combos
    ('rthumb (press|defused)  lthumb press',
     'rthumb defused  lthumb defused',
     type_(ec.KEY_BACKSPACE)),
    ('rthumb defused  lthumb defused (.*?) rthumb repeat',
     r'rthumb defused  lthumb defused \1', None),
    ('rthumb defused  lthumb defused (.*?) lthumb repeat',
     r'rthumb defused  lthumb defused \1', type_(ec.KEY_BACKSPACE)),
    ('rthumb defused  lthumb defused (.*?) lthumb release',
     r'rthumb defused \1', None),
    ('rthumb defused (.*?) rthumb release', r'\1', None),

    # lthumb-starting combos
    ('lthumb (press|defused)  rthumb press',
     'lthumb defused  rthumb defused', type_(ec.KEY_ENTER)),
    ('lthumb defused  rthumb defused (.*?) rthumb repeat',
     r'lthumb defused  rthumb defused \1', type_(ec.KEY_ENTER)),
    ('lthumb defused  rthumb defused (.*?) lthumb repeat',
     r'lthumb defused  rthumb defused \1', None),

    ('lthumb defused  rthumb defused (.*?) rthumb release',
     r'lthumb defused \1', None),
    ('lthumb defused (.*?) lthumb repeat', r'lthumb defused \1', None),
    ('lthumb defused (.*?) lthumb release', r'\1', None),

    ('rthumb press (.*?) rthumb release', r'\1', type_(ec.KEY_SPACE)),
    ('rthumb (press|defused) (.*?) rthumb repeat',
     r'rthumb defused  \2', None),

    ('lthumb press (.*?) lthumb release', r'\1', None),  # yet

    # nav
    ('up press', 'up inactive', type_(ec.KEY_UP)),
    ('up repeat', '', type_(ec.KEY_UP)),
    ('up inactive (.*) up release', r'\1', None),

    ('down press', 'down inactive', type_(ec.KEY_DOWN)),
    ('down repeat', '', type_(ec.KEY_DOWN)),
    ('down inactive (.*) down release', r'\1', None),

    ('left press', 'left inactive', type_(ec.KEY_LEFT)),
    ('left repeat', '', type_(ec.KEY_LEFT)),
    ('left inactive (.*) left release', r'\1', None),

    ('right press', 'right inactive', type_(ec.KEY_RIGHT)),
    ('right repeat', '', type_(ec.KEY_RIGHT)),
    ('right inactive (.*) right release', r'\1', None),
)


async def process_events(event_gen, ui):
    pipeline = ''
    async for event in event_gen:
        if event.type != ec.EV_KEY:
            continue
        if event.code not in REAL_MAP:
            print('unknown, ignored:', evdev.categorize(event), sep=': ')
            continue

        name, val = REAL_MAP[event.code], VALNAME_MAP[event.value]

        if (val == 'repeat' and name not in ('up', 'down', 'left', 'right',
                                             'lthumb', 'rthumb')):
            continue  # ignore repeats

        pipeline += f' {name} {val} '

        prev_pipeline = None
        while prev_pipeline != pipeline:
            prev_pipeline = pipeline
            print('>', pipeline)
            for condition, replacement, action in RULES:
                if re.search(condition, pipeline.strip()):
                    print('>', pipeline)
                    print('<', condition)
                    pipeline = re.sub(condition, replacement, pipeline,
                                      count=1)
                    pipeline = ' ' + pipeline.strip() + ' '
                    print('.', pipeline)
                    if action:
                        action(ui)
                    break
        print('=', pipeline)


def main():
    ui = evdev.uinput.UInput()
    event_queue = asyncio.Queue()

    # cleanup

    async def shutdown(sig, loop):
        print(f'Caught {sig.name}')
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
        print('Stopping...')
        await event_queue.join()
        loop.call_soon_threadsafe(loop.stop)
        ui.close()
        print('Stopped.')

    loop = asyncio.get_event_loop()
    for sig in signal.SIGINT, signal.SIGTERM, signal.SIGHUP:
        loop.add_signal_handler(sig, lambda sig=sig:
                                asyncio.create_task(shutdown(sig, loop)))

    # event reading

    async def collect_events(device_path):
        print(f'Opening device {device_path}...')
        device = evdev.InputDevice(device_path)
        device.grab()
        print(f'Opened device {device_path}.')
        async for event in device.async_read_loop():
            await event_queue.put(event)

    for device in (L, R):
        asyncio.ensure_future(collect_events(device))

    # queue -> generator, calling the most interesting function

    async def unwind_queue(event_and_extras_queue):
        while True:
            event = await event_and_extras_queue.get()
            yield event
            event_queue.task_done()

    try:
        loop.run_until_complete(process_events(unwind_queue(event_queue), ui))
    except asyncio.exceptions.CancelledError:
        print('Terminating.')


if __name__ == '__main__':
    main()
