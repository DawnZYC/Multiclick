@echo off
cd /d "%~dp0"
conda run -n multiclick python app\main.py
if errorlevel 1 pause
