@echo off
title AUTO TAP BOT LAUNCHER
color 0A
cls

echo ========================================
echo     AUTO TAP LAUNCHER BY CR FAUZI 08
echo ========================================
echo.

:: ===============================
:: CEK PYTHON
:: ===============================
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python Not Found!
    echo Install Python 3.13 First!.
    pause
    exit
)

:: ===============================
:: CEK FLAG FILE
:: ===============================
IF EXIST dependency_check.flag (
    echo Dependency Already check.
    echo.
    goto RUN
)

echo Checking dependency ...
echo.

:: Upgrade pip silent
python -m pip install --upgrade pip >nul 2>&1

:: ===============================
:: INSTALL + STATUS
:: ===============================

echo Checking Keyboard...
python -m pip install keyboard >nul 2>&1 && echo Keyboard  : Ready!

echo Checking PyAutoGUI...
python -m pip install pyautogui >nul 2>&1 && echo PyAutoGUI : Ready!

echo Checking OpenCV...
python -m pip install opencv-python >nul 2>&1 && echo OpenCV   : Ready!

echo Checking NumPy...
python -m pip install numpy >nul 2>&1 && echo NumPy    : Ready!

echo Checking Watchdog...
python -m pip install watchdog >nul 2>&1 && echo Watchdog : Ready!

echo.
echo Dependency Finish Check.
echo.

:: Buat flag agar tidak cek lagi
echo checked > dependency_check.flag

:RUN
echo RUNING AUTO TAP...
echo.
python auto_tap.py

pause
