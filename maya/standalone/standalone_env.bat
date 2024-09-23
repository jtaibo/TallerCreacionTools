@echo off
set SCRIPTS_DIR=%~dp0
set MAYA_VERSION=2025
set MAYA_PATH="C:\Program Files\Autodesk\Maya%MAYA_VERSION%\bin\"
set PATH=%MAYA_PATH%;%PATH%
set PYTHONPATH=%SCRIPTS_DIR%\..\python;%PYTHONPATH%
