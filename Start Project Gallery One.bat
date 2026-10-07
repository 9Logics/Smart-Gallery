@echo off
cd /d "%~dp0"
echo Checking for updates...
git pull
start pythonw app.py --bridge
