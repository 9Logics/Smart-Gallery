import os

file_path = 'app/app_core.py'
with open(file_path, 'r', encoding='utf-8') as f:
    src = f.read()

src = src.replace("_process_thumb_global_global", "_process_thumb_global")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Fixed double rename")
