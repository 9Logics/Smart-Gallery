import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = "if (e.key.toLowerCase() === 'm' && !document.querySelector('input:focus')) {"
replacement = "if (e.key && e.key.toLowerCase() === 'm' && !document.querySelector('input:focus')) {"

if target in js:
    js = js.replace(target, replacement)
    print("Fixed e.key error in core.js")
else:
    print("Target not found in core.js!")

with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
    f.write(js)
