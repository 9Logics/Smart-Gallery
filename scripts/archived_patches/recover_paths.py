import sqlite3
import hashlib
import os

conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()

c.execute("SELECT path FROM photos")
photo_paths = set(row[0] for row in c.fetchall())

c.execute("SELECT DISTINCT photo_path FROM faces")
face_paths = set(row[0] for row in c.fetchall())

c.execute("SELECT DISTINCT photo_path FROM album_photos")
album_paths = set(row[0] for row in c.fetchall())

missing_paths = (face_paths | album_paths) - photo_paths
print(f"Paths in faces/albums but not in photos: {len(missing_paths)}")

hash_map = {}
for p in missing_paths:
    h = hashlib.md5(p.encode('utf-8')).hexdigest()
    hash_map[h] = p

print("Example mappings:")
for h, p in list(hash_map.items())[:5]:
    print(f"{h} -> {p}")

import json
with open('hash_to_path.json', 'w', encoding='utf-8') as f:
    json.dump(hash_map, f)
print("Saved hash_to_path.json")
