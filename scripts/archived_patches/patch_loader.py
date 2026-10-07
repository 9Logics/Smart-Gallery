import os
path = 'app/static/js/core.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('<i data-lucide="loader" class="spin"></i>', '<i data-lucide="loader" style="animation: spin 1s linear infinite;"></i>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Fixed loader animation in core.js")
