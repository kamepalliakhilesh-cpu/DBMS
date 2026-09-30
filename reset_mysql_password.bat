@echo off
:: Batch Script to Reset MySQL Root Password to root123 on Windows
setlocal EnableDelayedExpansion

echo =======================================================
echo   MySQL Root Password Reset Utility
echo =======================================================
echo.

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Administrator privileges required.
    echo Requesting elevation...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~dpnx0\"\"' -Verb RunAs"
    exit /b
)

echo [*] Stopping MySQL80 service...
net stop MySQL80 >nul 2>&1

set INIT_FILE=%~dp0mysql_init_password.sql
set MYSQLD_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe
set MY_INI=C:\ProgramData\MySQL\MySQL Server 8.0\my.ini

if not exist "%MYSQLD_EXE%" (
    echo [ERROR] mysqld.exe not found at "%MYSQLD_EXE%"
    pause
    exit /b
)

echo [*] Applying new root password (root123)...
start /b "" "%MYSQLD_EXE%" --defaults-file="%MY_INI%" --init-file="%INIT_FILE%" --console >nul 2>&1

:: Wait 4 seconds for mysqld to process init-file
timeout /t 4 /nobreak >nul

echo [*] Terminating temporary mysqld process...
taskkill /f /im mysqld.exe >nul 2>&1

echo [*] Restarting MySQL80 service...
net start MySQL80

echo.
echo =======================================================
echo [SUCCESS] MySQL root password has been reset to: root123
echo =======================================================
echo.
pause
