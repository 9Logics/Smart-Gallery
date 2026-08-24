from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

metadata_bp = Blueprint('metadata', __name__)

@metadata_bp.route('/api/archive/move', methods=['POST'])
def archive_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({'error': 'No photos provided'}), 400
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for path in photo_paths:
        try:
            cursor.execute('UPDATE photos SET archived_at = ? WHERE path = ?',
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), path))
            success_count += 1
        except Exception as e:
            print(f'Error archiving {path}: {e}')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'count': success_count})

@metadata_bp.route('/api/archive/restore', methods=['POST'])
def unarchive_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({'error': 'No photos provided'}), 400
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for path in photo_paths:
        try:
            cursor.execute(
                'UPDATE photos SET archived_at = NULL WHERE path = ?', (path,))
            success_count += 1
        except Exception as e:
            print(f'Error unarchiving {path}: {e}')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'count': success_count})

@metadata_bp.route('/api/trash/move', methods=['POST'])
def trash_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({'error': 'No photos provided'}), 400
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for path in photo_paths:
        if os.path.exists(path):
            success, trash_path, err = send_file_to_trash(path)
            cursor.execute('UPDATE photos SET trashed_at = ? WHERE path = ?',
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), path))
            success_count += 1
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'count': success_count})

@metadata_bp.route('/api/trash/restore', methods=['POST'])
def restore_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({'error': 'No photos provided'}), 400
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for path in photo_paths:
        file_hash = hashlib.md5(path.encode('utf-8')).hexdigest()
        ext = os.path.splitext(path)[1]
        trash_path = os.path.join(TRASH_DIR, file_hash + ext)
        if os.path.exists(trash_path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                os.rename(trash_path, path)
                cursor.execute(
                    'UPDATE photos SET trashed_at = NULL WHERE path = ?', (
                    path,))
                success_count += 1
            except Exception as e:
                print(f'Error restoring {path} from trash: {e}')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'count': success_count})

@metadata_bp.route('/api/trash/empty', methods=['POST'])
def empty_trash():
    return jsonify({'error':
        'Empty trash is disabled. Delete items individually.'}), 400

@metadata_bp.route('/api/trash/purge', methods=['POST'])
def purge_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({'error': 'No photos provided'}), 400
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    import send2trash
    for path in photo_paths:
        try:
            if os.path.exists(path):
                send2trash.send2trash(path)
            completely_delete_photo_data(cursor, path)
            success_count += 1
        except Exception as e:
            print(f'Error purging file {path}: {e}')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'count': success_count})

@metadata_bp.route('/api/metadata/rescan', methods=['POST'])
def manual_metadata_rescan():

    def rescan_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Refreshing EXIF & Dates'
            scan_status['processed'] = 0
            scan_status['total'] = 0
            scan_status['current_file'] = ''
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT path FROM photos')
            all_paths = [r[0] for r in cursor.fetchall()]
            with scan_lock:
                scan_status['total'] = len(all_paths)
            for i, p in enumerate(all_paths):
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
                import os
                if os.path.exists(p):
                    meta = extract_metadata(p)
                    cursor.execute(
                        """
                        UPDATE photos SET 
                        date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, 
                        latitude = ?, longitude = ?, camera_make = ?, camera_model = ?, 
                        f_stop = ?, exposure_time = ?, focal_length = ?, iso = ?, 
                        duration = ?, fps = ?, video_codec = ? 
                        WHERE path = ?
                    """
                        , (meta['date_taken'], meta['width'], meta['height'
                        ], meta['size'], meta['file_type'], meta['latitude'
                        ], meta['longitude'], meta['camera_make'], meta[
                        'camera_model'], meta['f_stop'], meta[
                        'exposure_time'], meta['focal_length'], meta['iso'],
                        meta['duration'], meta['fps'], meta['video_codec'], p))
                with scan_lock:
                    scan_status['processed'] = i + 1
                    scan_status['current_file'] = os.path.basename(p)
            conn.commit()
            from face_processor import build_face_index
            build_face_index()
        except Exception as e:
            print('Error in EXIF rescan:', e)
        finally:
            with scan_lock:
                scan_status['status'] = 'idle'
                scan_status['phase'] = ''
    import threading
    thread = threading.Thread(target=rescan_task)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@metadata_bp.route('/api/metadata/refresh_places', methods=['POST'])
def manual_refresh_places():

    def refresh_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Refreshing Places Geocoding'
            scan_status['processed'] = 0
            scan_status['current_file'] = ''
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM geocoding_cache')
            conn.commit()
            cursor.execute(
                'SELECT path, latitude, longitude FROM photos WHERE latitude IS NOT NULL'
                )
            photos = cursor.fetchall()
            with scan_lock:
                scan_status['total'] = len(photos)
            for i, (p, lat, lon) in enumerate(photos):
                place = reverse_geocode(lat, lon)
                if place:
                    cursor.execute(
                        'UPDATE photos SET place_name = ? WHERE path = ?',
                        (place, p))
                    conn.commit()
                with scan_lock:
                    scan_status['processed'] = i + 1
                    scan_status['current_file'] = os.path.basename(p)
        except Exception as e:
            print(f'Error in refreshing places: {e}')
        finally:
            conn.close()
            with scan_lock:
                scan_status['status'] = 'idle'
    threading.Thread(target=refresh_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Places refresh started'})

