@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Creating virtual environment...
if not exist ".venv-build\Scripts\python.exe" py -3.12 -m venv .venv-build
if errorlevel 1 goto :error

echo [2/3] Installing build dependencies...
.venv-build\Scripts\python.exe -m pip install --upgrade pip
.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
if errorlevel 1 goto :error

echo [3/3] Building WordReviewTool.exe...
.venv-build\Scripts\pyinstaller.exe --noconfirm --clean WordReviewTool.spec
if errorlevel 1 goto :error

echo.
echo Build complete: dist\WordReviewTool.exe
pause
exit /b 0

:error
echo.
echo Build failed. Review the messages above.
pause
exit /b 1
