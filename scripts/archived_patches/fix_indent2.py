import os
path = 'app/routes/system.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('                        bat_content = f"""@echo off', '            bat_content = f"""@echo off')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
