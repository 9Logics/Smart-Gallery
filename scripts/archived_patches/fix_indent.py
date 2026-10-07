import os
path = 'app/routes/system.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if '            bat_content = f"""@echo off' in lines[i]:
        lines[i] = lines[i].replace('            bat_content', '            bat_content')
        break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
