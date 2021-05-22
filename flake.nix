{
  description = "chordkeyboard: my Dumang DK6 remapper";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let pkgs = nixpkgs.legacyPackages.${system}; in
        rec {
          chordkeyboard = pkgs.python3Packages.buildPythonPackage {
            pname = "chordkeyboard";
            version = "0.0.1";
            src = ./.;
            propagatedBuildInputs = with pkgs.python3Packages; [
              evdev
            ];
            doCheck = false;
          };
          defaultPackage = chordkeyboard;
          devShell = import ./shell.nix { inherit pkgs; };
        }
      );
}
