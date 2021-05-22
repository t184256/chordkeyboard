from setuptools import setup

setup(
    name='chordkeyboard',
    version='0.0.1',
    url='https://github.com/t184256/chordkeyboard',
    author='Alexander Sosedkin',
    author_email='monk@unboiled.info',
    description="chordkeyboard: my Dumang DK6 remapper",
    packages=['chordkeyboard',],
    install_requires=['evdev'],
    entry_points={
        'console_scripts': [
            'chordkeyboard = chordkeyboard.main:main',
        ],
    },
)
