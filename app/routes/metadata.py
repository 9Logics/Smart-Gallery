from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, shutil, hashlib
from datetime import datetime
from app.app_core import *

metadata_bp = Blueprint('metadata', __name__)


@metadata_bp.route('/api/archive/move', methods=['POST'])
def archive_photos():
    data = request.json
    paths = data.get('paths', data.get('photos', []))
    if not paths:
        return jsonify({'status': 'error', 'message': 'No paths provided'}), 400
    conn = get_db_connection()
    try:
        now = datetime.now().isoformat()
        cursor = conn.cursor()
        success_count = 0
        for path in paths:
            cursor.execute('UPDATE photos SET archived_at = ? WHERE path = ?', (now, path))
            if cursor.rowcount > 0:
                success_count += 1
        conn.commit()
        if success_count == 0 and len(paths) > 0:
            return jsonify({'status': 'error', 'message': 'Failed to archive: paths not found in database'}), 400
        return jsonify({'status': 'success', 'count': success_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@metadata_bp.route('/api/archive/restore', methods=['POST'])
def restore_archived_photos():
    data = request.json
    paths = data.get('paths', data.get('photos', []))
    if not paths:
        return jsonify({'status': 'error', 'message': 'No paths provided'}), 400
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        success_count = 0
        for path in paths:
            cursor.execute('UPDATE photos SET archived_at = NULL WHERE path = ?', (path,))
            if cursor.rowcount > 0:
                success_count += 1
        conn.commit()
        if success_count == 0 and len(paths) > 0:
            return jsonify({'status': 'error', 'message': 'Failed to unarchive: paths not found in database'}), 400
        return jsonify({'status': 'success', 'count': success_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@metadata_bp.route('/api/trash/move', methods=['POST'])
def trash_photos():
    data = request.json
    paths = data.get('paths', data.get('photos', []))
    if not paths:
        return jsonify({'status': 'error', 'message': 'No paths provided'}), 400
    conn = get_db_connection()
    try:
        now = datetime.now().isoformat()
        cursor = conn.cursor()
        success_count = 0
        errors = []
        for path in paths:
            success, trash_path, err = send_file_to_trash(path)
            if success:
                cursor.execute('UPDATE photos SET trashed_at = ? WHERE path = ?', (now, path))
                if cursor.rowcount > 0:
                    success_count += 1
                else:
                    errors.append(f"{path}: Database row not found")
            else:
                errors.append(f"{path}: {err}")
        conn.commit()
        if len(errors) > 0:
            return jsonify({'status': 'error', 'message': 'Failed to trash some items: ' + ', '.join(errors)}), 400
        return jsonify({'status': 'success', 'count': success_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@metadata_bp.route('/api/trash/restore', methods=['POST'])
def restore_trashed_photos():
    data = request.json
    paths = data.get('paths', data.get('photos', []))
    if not paths:
        return jsonify({'status': 'error', 'message': 'No paths provided'}), 400
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        success_count = 0
        errors = []
        for path in paths:
            file_hash = hashlib.md5(path.encode('utf-8')).hexdigest()
            ext = os.path.splitext(path)[1]
            trash_path = os.path.join(TRASH_DIR, file_hash + ext)
            if os.path.exists(trash_path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                try:
                    os.rename(trash_path, path)
                    cursor.execute('UPDATE photos SET trashed_at = NULL WHERE path = ?', (path,))
                    if cursor.rowcount > 0:
                        success_count += 1
                    else:
                        errors.append(f"{path}: Database row not found")
                except Exception as e:
                    errors.append(f"{path}: {str(e)}")
            else:
                errors.append(f"{path}: File not found in trash directory")
        conn.commit()
        if len(errors) > 0:
            return jsonify({'status': 'error', 'message': 'Failed to restore some items: ' + ', '.join(errors)}), 400
        return jsonify({'status': 'success', 'count': success_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@metadata_bp.route('/api/trash/empty', methods=['POST'])
def empty_trash():
    return jsonify({'status': 'error', 'message': 'Empty trash is disabled. Delete items individually.'}), 400


@metadata_bp.route('/api/trash/purge', methods=['POST'])
def purge_photos():
    data = request.json
    paths = data.get('paths', data.get('photos', []))
    if not paths:
        return jsonify({'status': 'error', 'message': 'No paths provided'}), 400
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        success_count = 0
        import send2trash
        for path in paths:
            file_hash = hashlib.md5(path.encode('utf-8')).hexdigest()
            ext = os.path.splitext(path)[1]
            trash_path = os.path.join(TRASH_DIR, file_hash + ext)
            
            if os.path.exists(trash_path):
                send2trash.send2trash(trash_path)
            elif os.path.exists(path):
                send2trash.send2trash(path)
                
            completely_delete_photo_data(cursor, path)
            success_count += 1
        conn.commit()
        return jsonify({'status': 'success', 'count': success_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

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
        conn = None
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
        except Exception as e:
            print('Error in EXIF rescan:', e)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            set_scan_idle()
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
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM geocoding_cache')
            conn.commit()
            cursor.execute(
                'SELECT path, latitude, longitude FROM photos WHERE latitude IS NOT NULL AND longitude IS NOT NULL'
                )
            photos = cursor.fetchall()
            with scan_lock:
                scan_status['total'] = len(photos)
            for i, (p, lat, lon) in enumerate(photos):
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
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
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            set_scan_idle()
    threading.Thread(target=refresh_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Places refresh started'})



