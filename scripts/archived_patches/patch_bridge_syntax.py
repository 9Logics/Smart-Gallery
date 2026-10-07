import re

with open('app/bridge_api.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = r".replace('\', '/')"
replacement = r".replace('\\', '/')"

py = py.replace(target, replacement)
with open('app/bridge_api.py', 'w', encoding='utf-8') as f:
    f.write(py)
print("Fixed bridge_api.py syntax error")
