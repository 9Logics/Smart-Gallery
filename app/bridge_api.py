# app/bridge_api.py — pywebview JS-Python Bridge API
# Phase 1: This file mirrors existing Flask routes as direct Python methods.
# Each method is callable from JavaScript via: await window.pywebview.api.method_name(...)

import os
import json
import sqlite3
from app.app_core import (
    get_db_connection, DB_PATH, THUMBNAILS_DIR, FACES_DIR,
    CACHE_DIR, TRASH_DIR, scan_status, parse_smart_dates, build_date_sql
)


class GalleryApi:
    """
    pywebview JS-Python Bridge API.
    
    All public methods are exposed to JavaScript as:
        await window.pywebview.api.method_name(arg1, arg2, ...)
    
    Return values must be JSON-serializable (dict, list, str, int, bool, None).
    """

    # ─── READ: Photos ───────────────────────────────────────────

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
                for member in zf.infolist():
                    member_path = os.path.abspath(os.path.join(temp_extract, member.filename))
                    if not member_path.startswith(os.path.abspath(temp_extract)):
                        continue
                    zf.extract(member, temp_extract)
                
            with scan_lock:
                scan_status['cancel_requested'] = True
                
            imported_db = os.path.join(temp_extract, 'gallery.db')
            if os.path.exists(imported_db):
                conn = get_db_connection()
                conn.execute('PRAGMA foreign_keys = OFF;')
                conn.execute("ATTACH DATABASE '{}' AS import_db".format(imported_db.replace("'", "''")))
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

    def fetch_internal(self, method, path, body=None):
        """
        Routes generic fetch() calls directly into Flask's in-memory 
        test_client without any actual network/port overhead!
        """
        from app.app_core import app
        import json
        client = app.test_client()
        
        # Format query params if path has them
        kwargs = {}
        if body is not None:
            kwargs['json'] = body
            
        if method.upper() == 'GET':
            resp = client.get(path, **kwargs)
        elif method.upper() == 'POST':
            resp = client.post(path, **kwargs)
        elif method.upper() == 'DELETE':
            resp = client.delete(path, **kwargs)
        elif method.upper() == 'PUT':
            resp = client.put(path, **kwargs)
        else:
            return {'error': f'Unsupported method {method}'}
            
        if resp.is_json:
            return resp.get_json()
            
        # Fallback for non-JSON returns (like raw text/html)
        try:
            decoded = resp.data.decode('utf-8')
            try:
                return json.loads(decoded)
            except json.JSONDecodeError:
                return {'error': 'Response was not JSON', 'text': decoded}
        except UnicodeDecodeError:
            return {'error': 'Response was binary data and cannot be routed through fetch_internal() bridge'}
