@echo off
echo Compiling Project Gallery One...
taskkill /F /IM "Project Gallery One.exe" >nul 2>&1
taskkill /F /IM "python.exe" >nul 2>&1
pyinstaller --name "Project Gallery One" --onefile --windowed --add-data "app/templates;app/templates" --add-data "app/static;app/static" --icon="app/static/favicon.ico" --collect-all numpy --collect-all onnxruntime --distpath . app.py
echo Done!
