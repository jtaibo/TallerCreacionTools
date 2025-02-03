#TallerCreacionTools

This code is experimental. Use it at your own risk.

Master branch has been ported to Maya 2025 (Qt6, PySide6). If you are
using Maya 2024 or earlier, select tag "Maya2024_PySide2".

## Installation in Maya (Windows)

Just execute maya/install.bat and open Maya. Two new shelves (TLC and
TLC_devel) should appear.

In case of problems with the installation script, follow the manual
procedure.

## Manual installation

Copy `maya/shelves` contents to `Documents/Maya/<version>/shelves`, where
`<version>` should be replaced with the Maya version you are using (e.g.
2025).

Edit `Documents/Maya/<version>/Maya.env` and make sure `PYTHONPATH` points to
the absolute path where `maya\python` directory is located in your system
(e.g. `PYTHONPATH=C:\devel\TallerCreacionTools\maya\python`).

Start Maya. Two new shelves (TLC and TLC_devel) should appear.
