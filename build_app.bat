@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building App...
pyinstaller --noconsole --onefile --add-data "templates;templates" --add-data "static;static" app.py

echo Build complete! Check the dist/ folder for your new executable.
pause
