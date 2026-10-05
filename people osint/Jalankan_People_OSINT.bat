@echo off
chcp 65001 >nul
cd /d "%~dp0people osint"
python "%~dp0people osint\people_scout.py" %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Terjadi kesalahan pada program [Kode: %ERRORLEVEL%].
    pause
)
