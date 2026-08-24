from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/api/scan/status')
def get_scan_status():
    return jsonify(scan_status)

@scan_bp.route('/api/scan/cancel', methods=['POST'])
def cancel_scan():
    global scan_status
    with scan_lock:
        if scan_status['status'] == 'scanning':
            scan_status['cancel_requested'] = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'message':
            'No active scan to cancel'})

@scan_bp.route('/api/scan/reevaluate_faces', methods=['POST'])
def reevaluate_faces():
    """
    Recalculate centroids for named people and reassign automatic faces if they match
    another named person significantly better, or unassign if they no longer match.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL AND f.is_manual != -1
        """
            )
        rows = cursor.fetchall()
        person_embeddings = {}
        for person_id, emb_blob in rows:
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            if person_id not in person_embeddings:
                person_embeddings[person_id] = []
            person_embeddings[person_id].append(emb)
        centroids = {}
        for person_id, embs in person_embeddings.items():
            centroids[person_id] = np.mean(embs, axis=0)
        if not centroids:
            return jsonify({'success': True, 'reassigned': 0, 'unassigned': 0})
        cursor.execute(
            """
            SELECT f.id, f.person_id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL 
              AND (f.is_manual = 0 OR f.is_manual IS NULL)
        """
            )
        face_rows = cursor.fetchall()
        reassigned_count = 0
        unassigned_count = 0
        for f_id, current_person_id, emb_blob in face_rows:
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            best_other_person_id = None
            best_other_dist = 1.0
            current_dist = 1.0
            for p_id, centroid in centroids.items():
                dist = face_processor.compute_cosine_distance(emb, centroid)
                if p_id == current_person_id:
                    current_dist = dist
                elif dist < best_other_dist:
                    best_other_dist = dist
                    best_other_person_id = p_id
            if (best_other_person_id is not None and best_other_dist < 0.4 and
                best_other_dist < current_dist - 0.05):
                cursor.execute('UPDATE faces SET person_id = ? WHERE id = ?',
                    (best_other_person_id, f_id))
                reassigned_count += 1
            elif current_dist > 0.48:
                cursor.execute('UPDATE faces SET person_id = NULL WHERE id = ?'
                    , (f_id,))
                unassigned_count += 1
        conn.commit()
    return jsonify({'success': True, 'reassigned': reassigned_count,
        'unassigned': unassigned_count})

@scan_bp.route('/api/scan_directory', methods=['POST'])
def manual_scan_directory():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'No directory set'}), 400
        root_dir = row[0]

    def scan_task():
        scan_directory(root_dir)
    threading.Thread(target=scan_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Directory scan started'})

@scan_bp.route('/api/scan/track_moved', methods=['POST'])
def track_moved_files():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        root_dir = row[0] if row else None

    def track_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Tracking moved/missing files'
            scan_status['processed'] = 0
            scan_status['total'] = 0
            scan_status['current_file'] = ''
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT path, filename, size FROM photos')
            photos = cursor.fetchall()
            missing_photos = []
            for p, f, s in photos:
                import os
                if not os.path.exists(p):
                    missing_photos.append((p, f, s))
            if root_dir and missing_photos:
                print('Scanning for moved files...')
                with scan_lock:
                    scan_status['total'] = len(missing_photos)
                available_files = {}
                roots_to_scan = [root_dir]
                scanned_roots = set()
                shell = None
                try:
                    import win32com.client
                    import pythoncom
                    pythoncom.CoInitialize()
                    shell = win32com.client.Dispatch('WScript.Shell')
                except ImportError:
                    pass
                while roots_to_scan:
                    current_root = roots_to_scan.pop(0)
                    import os
                    real_root = os.path.realpath(current_root)
                    if real_root in scanned_roots:
                        continue
                    scanned_roots.add(real_root)
                    for root, dirs, files in os.walk(current_root):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
                            import os
                            ext = os.path.splitext(file)[1].lower()
                            if ext in ['.jpg', '.jpeg', '.png', '.webp',
                                '.heic', '.heif', '.mp4', '.mov', '.m4v',
                                '.hevc']:
                                p = os.path.join(root, file)
                                try:
                                    s = os.path.getsize(p)
                                    available_files[file, s] = p
                                except:
                                    pass
                            elif ext == '.lnk' and shell:
                                try:
                                    shortcut = shell.CreateShortCut(os.path
                                        .join(root, file))
                                    if os.path.isdir(shortcut.Targetpath):
                                        roots_to_scan.append(shortcut.Targetpath)
                                except Exception:
                                    pass
                for i, (old_path, fname, fsize) in enumerate(missing_photos):
                    with scan_lock:
                        if scan_status.get('cancel_requested'):
                            break
                    with scan_lock:
                        scan_status['processed'] = i + 1
                        scan_status['current_file'] = fname
                    new_path = available_files.get((fname, fsize))
                    if new_path:
                        print(f'Moved file found: {old_path} -> {new_path}')
                        cursor.execute('SELECT 1 FROM photos WHERE path = ?',
                            (new_path,))
                        if cursor.fetchone():
                            cursor.execute(
                                'UPDATE OR IGNORE faces SET photo_path = ? WHERE photo_path = ?'
                                , (new_path, old_path))
                            cursor.execute(
                                'UPDATE OR IGNORE album_photos SET photo_path = ? WHERE photo_path = ?'
                                , (new_path, old_path))
                            completely_delete_photo_data(cursor, old_path)
                        else:
                            cursor.execute(
                                'UPDATE photos SET path = ? WHERE path = ?',
                                (new_path, old_path))
                            cursor.execute(
                                'UPDATE faces SET photo_path = ? WHERE photo_path = ?'
                                , (new_path, old_path))
                            cursor.execute(
                                'UPDATE album_photos SET photo_path = ? WHERE photo_path = ?'
                                , (new_path, old_path))
                    else:
                        print(f'File permanently deleted: {old_path}')
                        completely_delete_photo_data(cursor, old_path)
                conn.commit()
        except Exception as e:
            print('Error in track_moved:', e)
            import traceback
            traceback.print_exc()
        finally:
            with scan_lock:
                scan_status['status'] = 'idle'
                scan_status['phase'] = ''
    import threading
    thread = threading.Thread(target=track_task)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@scan_bp.route('/api/scan/hero-ai', methods=['POST'])
def scan_hero_ai():

    def hero_scan_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Hero AI Aesthetic Scan'
            scan_status['processed'] = 0
            scan_status['total'] = 1
            scan_status['current_file'] = ''
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT path FROM photos')
            all_paths = [r[0] for r in cursor.fetchall()]
            conn.close()
            from scene_classifier import scene_cache, check_scene, save_scene_cache
            video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v',
                '.hevc', '.wmv', '.flv')
            unscanned = [p for p in all_paths if not p.lower().endswith(
                video_exts)]
            with scan_lock:
                scan_status['total'] = len(unscanned)
            for p in unscanned:
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
                with scan_lock:
                    if scan_status['status'] != 'scanning':
                        break
                    scan_status['processed'] += 1
                    scan_status['current_file'] = os.path.basename(p)
                is_scenic = check_scene(p)
                scene_cache[p] = is_scenic
            save_scene_cache()
            with scan_lock:
                scan_status['status'] = 'idle'
                scan_status['phase'] = 'Idle'
        except Exception as e:
            import traceback
            traceback.print_exc()
            with scan_lock:
                scan_status['status'] = 'error'
                scan_status['phase'] = str(e)
    threading.Thread(target=hero_scan_task, daemon=True).start()
    return jsonify({'success': True})

