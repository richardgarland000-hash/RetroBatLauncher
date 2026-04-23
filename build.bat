@echo off
:: ============================================================
::  build.bat  –  Compile RetroBatLauncher.exe
::  Run this from the project root on Windows with Python installed
:: ============================================================

setlocal enabledelayedexpansion

echo.
echo  ================================================
echo   RetroBat Launcher  ^|  Build Script
echo  ================================================
echo.

:: ── Check Python ────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ and add it to PATH.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo  Python: %%v

:: ── Check / install PyInstaller ─────────────────────────────
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo  PyInstaller not found. Installing…
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] pip install pyinstaller failed.
        pause & exit /b 1
    )
)
for /f "tokens=*" %%v in ('python -m PyInstaller --version') do echo  PyInstaller: %%v

:: ── Clean previous build ────────────────────────────────────
echo.
echo  Cleaning old build artefacts…
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

:: ── Build ───────────────────────────────────────────────────
echo.
echo  Running PyInstaller…
echo.
python -m PyInstaller launcher.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check output above.
    pause & exit /b 1
)

:: ── Report ──────────────────────────────────────────────────
echo.
echo  ================================================
echo   Build complete!
echo   Executable: dist\RetroBatLauncher.exe
echo  ================================================
echo.
echo  Place RetroBatLauncher.exe in or next to your RetroBat
echo  installation folder, then double-click to launch.
echo.
pause
