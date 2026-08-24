with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'id="view-settings"' in line:
        print(''.join(lines[i:i+40]))
        break
