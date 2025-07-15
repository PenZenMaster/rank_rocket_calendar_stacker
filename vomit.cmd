@echo off
setlocal enabledelayedexpansion

echo Searching for .query.get(...) usage in src\...

set "SRC_DIR=src"

for /r %SRC_DIR% %%f in (*.py) do (
    findstr /C:".query.get(" "%%f" >nul
    if !errorlevel! == 0 (
        echo Match found in: %%f
    )
)

echo Search complete.
pause
