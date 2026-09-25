import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Using regex to grab everything from `function generateYearlyTheme(year) {` down to the closing brace before `function showRecapSlide`
pattern = r"function generateYearlyTheme\(year\).*?(?=function showRecapSlide)"
new_code = '''function generateYearlyTheme(year) {
    const container = document.getElementById('theme-canvas');
    if (container) container.innerHTML = '';
}

'''
js = re.sub(pattern, new_code, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Blobs definitively removed.")
