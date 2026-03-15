@echo off
setlocal
cd /d "%~dp0..\Projects\46_OpenClaw_QuickSetup"
python install_v2.py
if %errorlevel% neq 0 (
  echo.
  echo [ERROR] Cai dat that bai. Vui long xem log tren man hinh.
  pause
) else (
  echo.
  echo [OK] Hoan tat. Mo report tai output\install_report.md
  pause
)
endlocal
