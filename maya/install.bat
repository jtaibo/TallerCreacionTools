@echo off

setlocal enabledelayedexpansion
goto:main

:install_tlc
set MAYA_VERSION=%~1
set MAYA_DOCS=%HOMEDRIVE%\%HOMEPATH%\Documents\maya\%MAYA_VERSION%\

set SHELVES_DIR=%MAYA_DOCS%\prefs\shelves
set ICONS_DIR=%MAYA_DOCS%\prefs\icons

if exist %SHELVES_DIR% (
    echo Copying shelf files
    copy shelves\* %SHELVES_DIR%
    copy icons\*.png %ICONS_DIR%
) else (
    echo Shelves directory not found!
    echo Verify that you have Maya %MAYA_VERSION% installed in your system
)

REM Modify the environment variable MAYA_ENV if you are using it in a non-default path
set MAYA_ENV=%MAYA_DOCS%\Maya.env
if exist %MAYA_ENV% (
    findstr /m "PYTHONPATH" %MAYA_ENV%
    if !errorlevel! == 0 (
        echo(
        echo PYTHONPATH variable is already defined in %MAYA_ENV%
        echo Please, verify that everything is in place
        findstr "PYTHONPATH" %MAYA_ENV%
    ) else (
        echo Updating Maya.env file
        echo PYTHONPATH=%cd%\python >> %MAYA_ENV%
    )
) else (
    echo Creating Maya.env file
    echo PYTHONPATH=%cd%\python > %MAYA_ENV%
)

exit /B 0


:main

echo Maya TLC installer (developer version)
echo ======================================
echo(

REM This installer is meant to be used by developers
REM Scripts are reached in the local git repository
REM
REM A different installer will be created for end users
REM This installer will place scripts in Maya scripts directory

set MAYA_VERSIONS=2023 2024 2025

FOR /F "tokens=3* delims= " %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Personal"') do (set MYDOCUMENTS=%%a)

(for %%v in (%MAYA_VERSIONS%) do (
	set MAYA_DOCS=%MYDOCUMENTS%\maya\%%v\
	if exist !MAYA_DOCS!\ (
		echo Installing tools for Maya %%v
		call:install_tlc %%v
	)
))

echo(
echo Installation finished!
echo(	

pause
