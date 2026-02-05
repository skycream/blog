@echo off
title Blog Bot - @carbonblogbot
echo ========================================
echo   Blog Bot Starting...
echo   Telegram: @carbonblogbot
echo ========================================
echo.
echo Press Ctrl+C to stop the bot.
echo.
cd /d "%~dp0"
python telegram_bot.py
pause
