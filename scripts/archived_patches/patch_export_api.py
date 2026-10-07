import re

with open('app/bridge_api.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """    # "?"?"? READ: Scan Status "?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
    
    def get_scan_status(self):"""

replacement = """    # "?"?"? EXPORT / NATIVE BACKUP "?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
    
    def export_backup(self, params):
        import webview
        import time
        import os
        import io
        import zipfile
        import tempfile
        import shutil
        from app.config import DB_PATH, CACHE_DIR
        
        window = webview.active_window()
        if not window and webview.windows:
            window = webview.windows[0]
            
        date_str = time.strftime('%Y-%m-%d %H-%M')
        default_filename = f"gallery_backup {date_str}.zip"
        
        if window:
            result = window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_filename,
                file_types=('ZIP Archives (*.zip)', 'All Files (*.*)')
            )
            if not result:
                return {'success': False, 'cancelled': True}
            save_path = result[0] if isinstance(result, (list, tuple)) else result
        else:
            save_path = os.path.join(os.path.expanduser('~'), 'Downloads', default_filename)

        exp_photos = params.get('photos', True)
        exp_albums = params.get('albums', True)
        exp_faces = params.get('faces', True)
        exp_face_imgs = params.get('face_imgs', True)
        exp_thumbs = params.get('thumbs', True)
        exp_ai = params.get('ai', True)

        temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
        os.close(temp_db_fd)
        shutil.copy2(DB_PATH, temp_db_path)
        
        temp_conn = sqlite3.connect(temp_db_path)
        temp_cursor = temp_conn.cursor()
        temp_conn.execute('PRAGMA foreign_keys = OFF;')
        if not exp_photos:
            temp_cursor.execute('DELETE FROM photos')
            temp_cursor.execute('DELETE FROM settings')
            temp_cursor.execute('DELETE FROM geocoding_cache')
        if not exp_albums:
            temp_cursor.execute('DELETE FROM albums')
            temp_cursor.execute('DELETE FROM album_photos')
        if not exp_faces:
            temp_cursor.execute('DELETE FROM people')
            temp_cursor.execute('DELETE FROM faces')
        temp_conn.commit()
        temp_conn.execute('VACUUM')
        temp_conn.close()

        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(temp_db_path, 'gallery.db')
            for root, dirs, files in os.walk(CACHE_DIR):
                for file in files:
                    if file.endswith(('.db', '.db-wal', '.db-shm', '.tmp')):
                        continue
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, CACHE_DIR).replace('\\\\', '/')
                    
                    if rel_path.startswith('thumbnails/') and not exp_thumbs:
                        continue
                    if rel_path.startswith('faces/') and not exp_face_imgs:
                        continue
                    if file in ('scene_cache.json', 'hero_overrides.json') and not exp_ai:
                        continue
                    
                    try:
                        zf.write(file_path, rel_path)
                    except Exception as e:
                        print(f"Skipping {file_path} in export: {e}")
                        
        try:
            os.remove(temp_db_path)
        except:
            pass
            
        return {'success': True, 'path': save_path}

    # "?"?"? READ: Scan Status "?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
    
    def get_scan_status(self):"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/bridge_api.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched bridge_api.py")
else:
    print("Target not found in bridge_api.py")
