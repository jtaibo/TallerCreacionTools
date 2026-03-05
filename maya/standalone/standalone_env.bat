@echo off
set SCRIPTS_DIR=%~dp0
set MAYA_VERSION=2026
set MAYA_PATH="C:\Program Files\Autodesk\Maya%MAYA_VERSION%\bin\"
set ASSIMP_PATH="C:\Program Files\Assimp\bin\x64"
set PATH=%MAYA_PATH%;%ASSIMP_PATH%;%PATH%
set PYTHONPATH=%SCRIPTS_DIR%\..\python;%PYTHONPATH%
