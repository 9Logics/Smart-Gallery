import sqlite3
import os

conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()
c.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
scan_folder = c.fetchone()[0]

print(f"Scan folder: {scan_folder}")

c.execute("SELECT path FROM photos")
db_paths = set(row[0] for row in c.fetchall())

disk_paths = []
for root, dirs, files in os.walk(scan_folder):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic')):
            disk_paths.append(os.path.join(root, file))

missing_from_db = [p for p in disk_paths if p not in db_paths]

print(f"Total files on disk: {len(disk_paths)}")
print(f"Files missing from database (likely deleted from UI but still on disk): {len(missing_from_db)}")
