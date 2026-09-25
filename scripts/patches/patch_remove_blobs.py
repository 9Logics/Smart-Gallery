import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the generateYearlyTheme function body with just a canvas clear
old_func_pattern = r"(function generateYearlyTheme\(year\) \{)(.*?\n\})(\n\nfunction showRecapSlide)"

new_func = r"\1\n    const container = document.getElementById('theme-canvas');\n    if (container) container.innerHTML = '';\n\3"

# actually, using a simple replace might be easier
js = re.sub(r"function generateYearlyTheme\(year\) \{.*?\n\nfunction showRecapSlide", "function generateYearlyTheme(year) {\n    const container = document.getElementById('theme-canvas');\n    if (container) container.innerHTML = '';\n}\n\nfunction showRecapSlide", js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Removed weird blobs from generateYearlyTheme!")
