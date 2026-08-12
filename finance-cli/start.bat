@echo off
title Finance Tracker - Closing this window stops the server
cd /d "%~dp0"
streamlit run finance/web.py
pause
