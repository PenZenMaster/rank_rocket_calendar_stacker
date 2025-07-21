@echo off
REM Clean Python cache files and __pycache__ directories

REM Delete all .pyc files
for /r %%i in (*.pyc) do del /f /q "%%i"

REM Delete all __pycache__ folders
for /d /r %%d in (__pycache__) do rd /s /q "%%d"

echo Python cache cleanup complete.
