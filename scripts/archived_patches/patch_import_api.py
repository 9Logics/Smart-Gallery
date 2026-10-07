import re

with open('app/bridge_api.py', 'r', encoding='utf-8') as f:
    py = f.read()

replacement = """
    def select_import_file(self):
        import webview
        window = webview.active_window()
        if not window and webview.windows:
            window = webview.windows[0]
        if window:
            result = window.create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=('ZIP Archives (*.zip)', 'All Files (*.*)')
            )
            if result:
                return {'path': result[0] if isinstance(result, (list, tuple)) else result}
        return None

    def import_backup(self, params):
        import os
        import zipfile
        import shutil
        import sqlite3
        from app.app_core import BASE_DIR, CACHE_DIR, DB_PATH, get_db_connection, scan_status, scan_lock
        
        zip_path = params.get('path')
        if not zip_path or not os.path.exists(zip_path):
            return {'error': 'Invalid backup file'}
            
        imp_photos = params.get('photos', True)
        imp_albums = params.get('albums', True)
        imp_faces = params.get('faces', True)
        imp_face_imgs = params.get('face_imgs', True)
        imp_thumbs = params.get('thumbs', True)
        imp_ai = params.get('ai', True)
        
        temp_extract = os.path.join(BASE_DIR, '.cache_temp_import')
        if os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
        os.makedirs(temp_extract)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_extract)
                
            with scan_lock:
                scan_status['cancel_requested'] = True
                
            imported_db = os.path.join(temp_extract, 'gallery.db')
            if os.path.exists(imported_db):
                conn = get_db_connection()
                conn.execute('PRAGMA foreign_keys = OFF;')
                conn.execute(f"ATTACH DATABASE '{imported_db}' AS import_db")
                try:
                    if imp_photos:
                        conn.execute('INSERT OR REPLACE INTO settings SELECT * FROM import_db.settings')
                        conn.execute('INSERT OR IGNORE INTO photos SELECT * FROM import_db.photos')
                        conn.execute('INSERT OR IGNORE INTO geocoding_cache SELECT * FROM import_db.geocoding_cache')
                    if imp_albums:
                        conn.execute('INSERT OR IGNORE INTO albums SELECT * FROM import_db.albums')
                        conn.execute('INSERT OR IGNORE INTO album_photos SELECT * FROM import_db.album_photos')
                    if imp_faces:
                        conn.execute('INSERT OR IGNORE INTO people SELECT * FROM import_db.people')
                        conn.execute('INSERT OR IGNORE INTO faces SELECT * FROM import_db.faces')
                    conn.commit()
                except Exception as e:
                    print(f"Error merging DB: {e}")
                finally:
                    conn.execute('DETACH DATABASE import_db')
                    conn.close()
            
            for item in os.listdir(temp_extract):
                if item == 'gallery.db':
                    continue
                s = os.path.join(temp_extract, item)
                d = os.path.join(CACHE_DIR, item)
                
                if item == 'thumbnails' and not imp_thumbs:
                    continue
                if item == 'faces' and not imp_face_imgs:
                    continue
                if item in ('scene_cache.json', 'hero_overrides.json') and not imp_ai:
                    continue
                    
                if os.path.isdir(s):
                    if not os.path.exists(d):
                        os.makedirs(d)
                    for root, dirs, files in os.walk(s):
                        rel = os.path.relpath(root, s)
                        dest_root = os.path.join(d, rel)
                        if not os.path.exists(dest_root):
                            os.makedirs(dest_root)
                        for file in files:
                            shutil.copy2(os.path.join(root, file), os.path.join(dest_root, file))
                else:
                    shutil.copy2(s, d)
                    
            shutil.rmtree(temp_extract)
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    def get_scan_status(self):"""

py = re.sub(r'def get_scan_status\(self\):', replacement, py, count=1)
with open('app/bridge_api.py', 'w', encoding='utf-8') as f:
    f.write(py)
print("Patched bridge_api.py with native import")
