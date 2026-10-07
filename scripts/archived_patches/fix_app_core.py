import os
file_path = "app/app_core.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_scan = """      cursor.execute('SELECT path FROM photos')
      existing_files = {r[0] for r in cursor.fetchall()}
      new_files = [p for p in file_list if p not in existing_files]"""

new_scan = """      cursor.execute('SELECT path FROM photos')
      existing_files = {os.path.normpath(r[0]) for r in cursor.fetchall()}
      new_files = [p for p in file_list if os.path.normpath(p) not in existing_files]
      # Also normalize p before processing so we consistently use normalized paths down the line
      new_files = [os.path.normpath(p) for p in new_files]"""

if old_scan in content:
    content = content.replace(old_scan, new_scan)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed scan_directory logic.")
else:
    print("Could not find the target string in app_core.py")
