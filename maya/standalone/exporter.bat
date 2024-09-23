@echo off
set SCRIPTS_DIR=%~dp0
call %SCRIPTS_DIR%\standalone_env.bat
mayapy %SCRIPTS_DIR%\exporter.py %*
