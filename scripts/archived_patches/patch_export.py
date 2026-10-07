import re

with open('app/routes/system.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(temp_db_path, 'gallery.db')
        for root, dirs, files in os.walk(CACHE_DIR):
            for file in files:
                if file.endswith('.db') or file.endswith('.db-wal'
                    ) or file.endswith('.db-shm'):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, CACHE_DIR).replace('\\',
                    '/')
                if rel_path.startswith('thumbnails/') and not exp_thumbs:
                    continue
                if rel_path.startswith('faces/') and not exp_face_imgs:
                    continue
                if (file == 'scene_cache.json' or file == 'hero_overrides.json'
                    ) and not exp_ai:
                    continue
                if file.endswith('.tmp'):
                    continue
                zf.write(file_path, rel_path)"""

replacement = """    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(temp_db_path, 'gallery.db')
        for root, dirs, files in os.walk(CACHE_DIR):
            for file in files:
                if file.endswith('.db') or file.endswith('.db-wal'
                    ) or file.endswith('.db-shm'):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, CACHE_DIR).replace('\\\\',
                    '/')
                if rel_path.startswith('thumbnails/') and not exp_thumbs:
                    continue
                if rel_path.startswith('faces/') and not exp_face_imgs:
                    continue
                if (file == 'scene_cache.json' or file == 'hero_overrides.json'
                    ) and not exp_ai:
                    continue
                if file.endswith('.tmp'):
                    continue
                try:
                    zf.write(file_path, rel_path)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"Failed to zip {file_path!r}: {e}")"""

code = code.replace(target, replacement)
with open('app/routes/system.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Added try-except to system.py export")
