with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'id="settings-view"' in line:
        print(''.join(lines[i:i+60]))
        break
