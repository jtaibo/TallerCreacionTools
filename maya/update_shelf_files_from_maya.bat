@echo off

set MAYA_VERSION=2023
set MAYA_DOCS=%HOMEDRIVE%\%HOMEPATH%\Documents\maya\%MAYA_VERSION%\

set SHELVES_DIR=%MAYA_DOCS%\prefs\shelves
set ICONS_DIR=%MAYA_DOCS%\prefs\icons

if exist %SHELVES_DIR% (
    echo Copying shelf files
    copy %SHELVES_DIR%\shelf_TLC*.mel shelves
    REM copy icons\*.png %ICONS_DIR%
) else (
    echo Shelves directory not found!
    echo Verify that you have Maya %MAYA_VERSION% installed in your system
)

echo(
echo Shelf files updated from current Maya configuration!
echo(	

pause
