from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

system_bp = Blueprint('system', __name__)

@system_bp.route('/api/settings/scan-folder', methods=['POST'])
def save_scan_folder():
    data = request.json
    folder = data.get('folder', '').strip()
    if not folder or not os.path.exists(folder):
        return jsonify({'error':
            'Invalid folder path or folder does not exist'}), 400
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('scan_folder', ?)"
        , (folder,))
    conn.commit()
    conn.close()
    started = start_scan_thread(folder)
    return jsonify({'success': True, 'started': started})

@system_bp.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.json or {}
        for k, v in data.items():
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                (k, str(v)))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    else:
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        settings_dict = {r[0]: r[1] for r in rows}
        if 'scan_folder' not in settings_dict:
            settings_dict['scan_folder'] = ''
        if 'google_maps_key' not in settings_dict:
            settings_dict['google_maps_key'] = ''
        return jsonify(settings_dict)

@system_bp.route('/api/settings/hero_overrides', methods=['GET'])
def get_hero_overrides():
    return jsonify(load_hero_overrides())

@system_bp.route('/api/settings/hero_override', methods=['POST'])
def add_hero_override():
    data = request.json
    path = data.get('path')
    status = data.get('status')
    if not path or not status:
        return jsonify({'error': 'Missing path or status'}), 400
    overrides = load_hero_overrides()
    if path in overrides['whitelist']:
        overrides['whitelist'].remove(path)
    if path in overrides['blacklist']:
        overrides['blacklist'].remove(path)
    if status == 'whitelist':
        overrides['whitelist'].append(path)
    elif status == 'blacklist':
        overrides['blacklist'].append(path)
        from scene_classifier import scene_cache, save_scene_cache
        scene_cache[path] = False
        save_scene_cache()
    save_hero_overrides(overrides)
    return jsonify({'success': True})

@system_bp.route('/api/settings/hero_scenic_photos')
def get_hero_scenic_photos():
    """Return all photos the AI scene classifier has indexed as scenic/nature."""
    from scene_classifier import scene_cache
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    search = request.args.get('search', '').strip().lower()
    scenic_paths = [p for p, v in scene_cache.items() if v is True]
    if search:
        scenic_paths = [p for p in scenic_paths if search in os.path.
            basename(p).lower() or search in p.lower()]
    total = len(scenic_paths)
    start = (page - 1) * per_page
    end = start + per_page
    paged = scenic_paths[start:end]
    return jsonify({'photos': [{'path': p} for p in paged], 'total': total,
        'page': page})

@system_bp.route('/api/settings/hero_all_photos')
def get_hero_all_photos():
    """Return paginated photos for hero whitelist picker."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    search = request.args.get('search', '').strip()
    offset = (page - 1) * per_page
    conn = get_db_connection()
    c = conn.cursor()
    if search:
        c.execute(
            """
            SELECT path, filename FROM photos 
            WHERE trashed_at IS NULL AND archived_at IS NULL
              AND (filename LIKE ? OR path LIKE ? OR place_name LIKE ?)
            ORDER BY date_taken DESC LIMIT ? OFFSET ?
        """
            , (f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
    else:
        c.execute(
            """
            SELECT path, filename FROM photos 
            WHERE trashed_at IS NULL AND archived_at IS NULL
            ORDER BY date_taken DESC LIMIT ? OFFSET ?
        """
            , (per_page, offset))
    rows = c.fetchall()
    c.execute(
        'SELECT COUNT(*) FROM photos WHERE trashed_at IS NULL AND archived_at IS NULL'
        )
    total = c.fetchone()[0]
    conn.close()
    return jsonify({'photos': [{'path': r[0], 'filename': r[1]} for r in
        rows], 'total': total, 'page': page})

@system_bp.route('/api/stats/heatmap')
def api_stats_heatmap():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return jsonify({})
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT substr(date_taken, 9, 2) as day, count(*)
        FROM photos 
        WHERE substr(date_taken, 1, 4) = ? AND substr(date_taken, 6, 2) = ? AND trashed_at IS NULL 
        GROUP BY day
    """
        , (year, month.zfill(2)))
    data = c.fetchall()
    conn.close()
    return jsonify({row[0]: row[1] for row in data})

@system_bp.route('/api/stats/calendar')
def api_stats_calendar():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT substr(date_taken, 1, 10) as day, count(*)
        FROM photos 
        WHERE date_taken IS NOT NULL AND date_taken != 'Undated' AND trashed_at IS NULL AND archived_at IS NULL AND date_taken >= '1999-01-01'
        GROUP BY day
        ORDER BY day ASC
    """
        )
    data = c.fetchall()
    conn.close()
    return jsonify({row[0]: row[1] for row in data})

@system_bp.route('/api/stats')
@cache_api(timeout=30)
def api_stats():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT substr(date_taken, 1, 4) as year, substr(date_taken, 6, 2) as month, file_type, count(*), sum(size)
        FROM photos 
        WHERE date_taken IS NOT NULL AND date_taken != 'Undated' 
        GROUP BY year, month, file_type
    """
        )
    monthly_data = c.fetchall()
    c.execute(
        """
        SELECT 
            SUM(CASE WHEN file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN 1 ELSE 0 END) as total_videos,
            SUM(CASE WHEN file_type NOT IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN 1 ELSE 0 END) as total_photos,
            SUM(CASE WHEN file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN size ELSE 0 END) as total_video_size,
            SUM(CASE WHEN file_type NOT IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN size ELSE 0 END) as total_photo_size
        FROM photos
    """
        )
    totals = c.fetchone()
    conn.close()
    stats = {'total_photos': totals[1] if totals and totals[1] else 0,
        'total_videos': totals[0] if totals and totals[0] else 0,
        'total_photo_size': totals[3] if totals and totals[3] else 0,
        'total_video_size': totals[2] if totals and totals[2] else 0,
        'yearly': {}}
    for row in monthly_data:
        year = row[0]
        month = row[1]
        ftype = row[2]
        count = row[3]
        size = row[4] or 0
        if not year or len(year) != 4 or not year.isdigit():
            continue
        if not month or len(month) != 2 or not month.isdigit():
            continue
        if year not in stats['yearly']:
            stats['yearly'][year] = {'photos': 0, 'videos': 0,
                'storage_photos': 0, 'storage_videos': 0, 'months': {}}
            for m in range(1, 13):
                stats['yearly'][year]['months'][f'{m:02d}'] = {'photos': 0,
                    'videos': 0, 'storage_photos': 0, 'storage_videos': 0}
        if ftype in ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC'):
            stats['yearly'][year]['videos'] += count
            stats['yearly'][year]['storage_videos'] += size
            stats['yearly'][year]['months'][month]['videos'] += count
            stats['yearly'][year]['months'][month]['storage_videos'] += size
        else:
            stats['yearly'][year]['photos'] += count
            stats['yearly'][year]['storage_photos'] += size
            stats['yearly'][year]['months'][month]['photos'] += count
            stats['yearly'][year]['months'][month]['storage_photos'] += size
    return jsonify(stats)

@system_bp.route('/api/data/export', methods=['GET'])
def export_cache():
    import zipfile
    import io
    import shutil
    import tempfile
    exp_photos = request.args.get('photos') == 'true'
    exp_albums = request.args.get('albums') == 'true'
    exp_faces = request.args.get('faces') == 'true'
    exp_face_imgs = request.args.get('face_imgs') == 'true'
    exp_thumbs = request.args.get('thumbs') == 'true'
    exp_ai = request.args.get('ai') == 'true'
    memory_file = io.BytesIO()
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
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
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
                zf.write(file_path, rel_path)
    try:
        os.remove(temp_db_path)
    except:
        pass
    memory_file.seek(0)
    return send_file(memory_file, download_name='gallery_backup.zip',
        as_attachment=True)

@system_bp.route('/api/data/import', methods=['POST'])
def import_cache():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.zip'):
        try:
            import zipfile
            import shutil
            imp_photos = request.form.get('photos') == 'true'
            imp_albums = request.form.get('albums') == 'true'
            imp_faces = request.form.get('faces') == 'true'
            imp_face_imgs = request.form.get('face_imgs') == 'true'
            imp_thumbs = request.form.get('thumbs') == 'true'
            imp_ai = request.form.get('ai') == 'true'
            temp_extract = os.path.join(BASE_DIR, '.cache_temp_import')
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)
            os.makedirs(temp_extract)
            with zipfile.ZipFile(file, 'r') as zf:
                zf.extractall(temp_extract)
            global scan_status
            with scan_lock:
                scan_status['cancel_requested'] = True
            imported_db = os.path.join(temp_extract, 'gallery.db')
            if os.path.exists(imported_db):
                conn = get_db_connection()
                conn.execute('PRAGMA foreign_keys = OFF;')
                conn.execute(f"ATTACH DATABASE '{imported_db}' AS import_db")
                try:
                    if imp_photos:
                        conn.execute(
                            'INSERT OR REPLACE INTO settings SELECT * FROM import_db.settings'
                            )
                        conn.execute(
                            'INSERT OR IGNORE INTO photos SELECT * FROM import_db.photos'
                            )
                        conn.execute(
                            'INSERT OR IGNORE INTO geocoding_cache SELECT * FROM import_db.geocoding_cache'
                            )
                    if imp_albums:
                        conn.execute(
                            'INSERT OR IGNORE INTO albums SELECT * FROM import_db.albums'
                            )
                        conn.execute(
                            'INSERT OR IGNORE INTO album_photos SELECT * FROM import_db.album_photos'
                            )
                    if imp_faces:
                        conn.execute(
                            'INSERT OR IGNORE INTO people SELECT * FROM import_db.people'
                            )
                        conn.execute(
                            'INSERT OR IGNORE INTO faces SELECT * FROM import_db.faces'
                            )
                    conn.commit()
                except Exception as e:
                    print('DB Merge Error:', e)
                finally:
                    conn.execute('DETACH DATABASE import_db')
                    conn.execute('PRAGMA foreign_keys = ON;')
                    conn.close()
            if imp_thumbs and os.path.exists(os.path.join(temp_extract,
                'thumbnails')):
                os.makedirs(THUMBNAILS_DIR, exist_ok=True)
                for item in os.listdir(os.path.join(temp_extract, 'thumbnails')
                    ):
                    s = os.path.join(temp_extract, 'thumbnails', item)
                    d = os.path.join(THUMBNAILS_DIR, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
            if imp_face_imgs and os.path.exists(os.path.join(temp_extract,
                'faces')):
                os.makedirs(FACES_DIR, exist_ok=True)
                for item in os.listdir(os.path.join(temp_extract, 'faces')):
                    s = os.path.join(temp_extract, 'faces', item)
                    d = os.path.join(FACES_DIR, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
            if imp_ai:
                scene_src = os.path.join(temp_extract, 'scene_cache.json')
                hero_src = os.path.join(temp_extract, 'hero_overrides.json')
                if os.path.exists(scene_src):
                    shutil.copy2(scene_src, os.path.join(CACHE_DIR,
                        'scene_cache.json'))
                if os.path.exists(hero_src):
                    shutil.copy2(hero_src, os.path.join(CACHE_DIR,
                        'hero_overrides.json'))
            try:
                import scene_classifier
                if os.path.exists(scene_classifier.SCENE_CACHE_FILE):
                    with open(scene_classifier.SCENE_CACHE_FILE, 'r') as f:
                        scene_classifier.scene_cache = json.load(f)
                else:
                    scene_classifier.scene_cache = {}
            except Exception:
                pass
            try:
                import face_processor
                face_processor._face_index = None
                face_processor._id_map = None
            except Exception:
                pass
            try:
                shutil.rmtree(temp_extract)
            except:
                pass
            return jsonify({'success': True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@system_bp.route('/api/data/delete_all', methods=['POST'])
def delete_all_data():
    try:
        import shutil, time
        global scan_status
        with scan_lock:
            scan_status['cancel_requested'] = True

        # Clear database tables safely
        conn = get_db_connection()
        cursor = conn.cursor()
        tables = ['settings', 'photos', 'faces', 'sqlite_sequence', 'people', 'albums', 'album_photos', 'geocoding_cache']
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
            except Exception:
                pass
        conn.commit()
        conn.close()

        # Safely clear subdirectories in CACHE_DIR
        for item in os.listdir(CACHE_DIR):
            if item.endswith('.db') or item.endswith('-wal') or item.endswith('-shm'):
                continue
            item_path = os.path.join(CACHE_DIR, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    os.unlink(item_path)
            except Exception:
                pass

        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        os.makedirs(FACES_DIR, exist_ok=True)
        os.makedirs(TRASH_DIR, exist_ok=True)
        
        # Re-init default settings
        init_db()

        try:
            import scene_classifier
            scene_classifier.scene_cache = {}
        except Exception:
            pass
            
        try:
            import face_processor
            face_processor._face_index = None
            face_processor._id_map = None
        except Exception:
            pass
            
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



def browse_directory():
    import tkinter as tk
    from tkinter import filedialog
    # Hide root window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Select Media Folder")
    root.destroy()
    
    if folder_path:
        return jsonify({'path': folder_path.replace('/', '\\')})
    return jsonify({'path': None})

@system_bp.route('/api/settings/browse_directory', methods=['GET'])
def browse_directory():
    import subprocess, os, sys
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'picker.ps1')
        CREATE_NO_WINDOW = 0x08000000
        result = subprocess.check_output(['powershell', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-File', script_path], text=True, creationflags=CREATE_NO_WINDOW).strip()
        if result:
            return jsonify({'path': result})
    except Exception as e:
        print(f"Browse error: {e}")
    return jsonify({'path': None})

@system_bp.route('/api/settings/validate-folder', methods=['POST'])
def validate_folder():
    data = request.json
    folder = data.get('folder', '').strip()
    
    if not folder:
        return jsonify({'valid': False, 'error': 'Folder path is empty.'})
        
    if not os.path.exists(folder) or not os.path.isdir(folder):
        return jsonify({'valid': False, 'error': 'Folder does not exist or is not a directory.'})
        
    # Check if media exists
    has_media = False
    valid_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.mp4', '.mov', '.avi', '.mkv'}
    
    try:
        for root, dirs, files in os.walk(folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_exts:
                    has_media = True
                    break
            if has_media:
                break
    except Exception:
        pass
        
    if not has_media:
        return jsonify({'valid': False, 'error': 'No media (photos/videos) found in this folder.'})
        
    return jsonify({'valid': True})
