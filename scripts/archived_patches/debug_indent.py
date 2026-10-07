import os
path = 'app/routes/system.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "bat_content =" in line:
        print(f"Line {i}: {line}")
    if "def update_app():" in line:
        print(f"Update app at line {i}")
