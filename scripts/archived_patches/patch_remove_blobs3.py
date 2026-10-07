import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_func = False
for line in lines:
    if line.startswith('function generateYearlyTheme(year)'):
        in_func = True
        new_lines.append('function generateYearlyTheme(year) {\n')
        new_lines.append("    const container = document.getElementById('theme-canvas');\n")
        new_lines.append("    if (container) container.innerHTML = '';\n")
        new_lines.append('}\n')
        continue
    
    if in_func:
        if line.startswith('function showRecapSlide'):
            in_func = False
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(js_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Blobs manually destroyed.")
