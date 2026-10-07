import re

with open('app/bridge_api.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = "from app.config import DB_PATH, CACHE_DIR"
replacement = "from app.app_core import DB_PATH, CACHE_DIR"

if target in py:
    py = py.replace(target, replacement)
    with open('app/bridge_api.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Fixed import in bridge_api.py")
else:
    print("Target not found in bridge_api.py")
