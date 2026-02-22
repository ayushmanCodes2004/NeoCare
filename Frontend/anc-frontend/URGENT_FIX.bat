@echo off
REM Quick fix for Tailwind CSS version mismatch

cd /d "%~dp0"

echo Fixing Tailwind CSS version mismatch...
echo Current: v4.2.0 (beta) - Expected: v3.4.4 (stable)

REM Remove problematic v4 packages
call npm uninstall tailwindcss @tailwindcss/node @tailwindcss/postcss

REM Install correct v3 version
call npm install tailwindcss@^3.4.4 --save-dev

REM Reinstall clsx to be sure
call npm install clsx

echo.
echo ✅ Fixed! Restart dev server with: npm run dev
pause
