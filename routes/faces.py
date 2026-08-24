from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

faces_bp = Blueprint('faces', __name__)

@faces_bp.route('/api/faces/edit-tag', methods=['POST'])
def edit_face_tag():
    data = request.json
    conn = None
    try:
        try:
            face_id = int(data.get('face_id'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid or missing face_id format'}), 400
        new_name = data.get('new_name', '').strip()
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT photo_path, person_id FROM faces WHERE id = ?',
            (face_id,))
        face_row = cursor.fetchone()
        if not face_row:
            conn.close()
            return jsonify({'error': 'Face not found'}), 404
        photo_path, old_person_id = face_row
        if not new_name:
            cursor.execute('INSERT INTO people (name) VALUES (NULL)')
            new_person_id = cursor.lastrowid
            cursor.execute('UPDATE people SET name = ? WHERE id = ?', (
                f'Person {new_person_id}', new_person_id))
            cursor.execute('UPDATE faces SET person_id = ? WHERE id = ?', (
                new_person_id, face_id))
            print(
                f'Isolated face {face_id} to new separate unnamed Person {new_person_id}'
                )
        else:
            cursor.execute('SELECT id FROM people WHERE LOWER(name) = LOWER(?)'
                , (new_name,))
            existing_person = cursor.fetchone()
            if existing_person:
                new_person_id = existing_person[0]
                cursor.execute('UPDATE faces SET person_id = ? WHERE id = ?',
                    (new_person_id, face_id))
                print(
                    f'Merged face {face_id} into existing person ID {new_person_id} ({new_name})'
                    )
            else:
                cursor.execute('INSERT INTO people (name) VALUES (?)', (
                    new_name,))
                new_person_id = cursor.lastrowid
                cursor.execute('UPDATE faces SET person_id = ? WHERE id = ?',
                    (new_person_id, face_id))
                print(
                    f'Created new person ID {new_person_id} ({new_name}) and tagged face {face_id} to it'
                    )
        cursor.execute('SELECT cover_face_id FROM people WHERE id = ?', (
            new_person_id,))
        existing_cover = cursor.fetchone()
        if existing_cover and existing_cover[0] is None:
            cursor.execute('SELECT id FROM faces WHERE person_id = ? LIMIT 1',
                (new_person_id,))
            cov_face = cursor.fetchone()
            if cov_face:
                cursor.execute(
                    'UPDATE people SET cover_face_id = ? WHERE id = ?', (
                    cov_face[0], new_person_id))
        if old_person_id is not None:
            try:
                old_person_id_int = int(old_person_id)
                cursor.execute('SELECT COUNT(*) FROM faces WHERE person_id = ?'
                    , (old_person_id_int,))
                rem_count = cursor.fetchone()[0]
                if rem_count == 0:
                    cursor.execute('SELECT name FROM people WHERE id = ?',
                        (old_person_id_int,))
                    old_name_row = cursor.fetchone()
                    if old_name_row and (old_name_row[0] is None or
                        old_name_row[0].startswith('Person ')):
                        cursor.execute('DELETE FROM people WHERE id = ?', (
                            old_person_id_int,))
                        print(
                            f'Deleted empty unnamed person ID {old_person_id_int}'
                            )
            except Exception as clean_err:
                print(
                    f'Cleanup of old person {old_person_id} failed: {clean_err}'
                    )
        conn.commit()
        conn.close()
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({'success': True, 'person_id': new_person_id})
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        print(f'Error in edit_face_tag: {e}')
        return jsonify({'error': str(e)}), 500

@faces_bp.route('/api/faces/add_to_video', methods=['POST'])
def add_person_to_video():
    """Tag an existing named person in a video without a bounding box crop."""
    data = request.json
    path = data.get('video_path')
    person_id = data.get('person_id')
    if not path or not person_id:
        return jsonify({'error':
            'Missing required fields (video_path, person_id)'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        p_id = int(person_id)
        cursor.execute('SELECT id FROM people WHERE id = ?', (p_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Person not found'}), 404
        cursor.execute(
            'SELECT id FROM faces WHERE photo_path = ? AND person_id = ?',
            (path, p_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': True, 'already_exists': True})
        cursor.execute(
            """
            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
            VALUES (?, 0, 0, 0, 0, NULL, ?, 1)
        """
            , (path, p_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@faces_bp.route('/api/faces/add_manual', methods=['POST'])
def add_manual_face():
    data = request.json
    path = data.get('photo_path')
    x = data.get('x')
    y = data.get('y')
    w = data.get('w')
    h = data.get('h')
    person_id = data.get('person_id')
    raw_name = data.get('person_name')
    person_name = raw_name.strip() if raw_name else ''
    if not path or x is None or y is None or w is None or h is None:
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    p_id = None
    if person_id:
        p_id = int(person_id)
    elif person_name:
        cursor.execute('SELECT id FROM people WHERE name = ?', (person_name,))
        p_row = cursor.fetchone()
        if p_row:
            p_id = p_row[0]
        else:
            cursor.execute('INSERT INTO people (name) VALUES (?)', (
                person_name,))
            p_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
        VALUES (?, ?, ?, ?, ?, NULL, ?, 1)
    """
        , (path, int(x), int(y), int(w), int(h), p_id))
    face_id = cursor.lastrowid
    if p_id:
        cursor.execute('SELECT cover_face_id FROM people WHERE id = ?', (p_id,)
            )
        cov_row = cursor.fetchone()
        if cov_row and not cov_row[0]:
            cursor.execute('UPDATE people SET cover_face_id = ? WHERE id = ?',
                (face_id, p_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'face_id': face_id, 'person_id': p_id})

@faces_bp.route('/api/faces/delete', methods=['POST'])
def delete_face():
    data = request.json
    face_id = data.get('face_id')
    if not face_id:
        return jsonify({'error': 'Missing face ID'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT person_id FROM faces WHERE id = ?', (face_id,))
    f_row = cursor.fetchone()
    if f_row and f_row[0]:
        p_id = f_row[0]
        cursor.execute('SELECT cover_face_id FROM people WHERE id = ?', (p_id,)
            )
        cov_row = cursor.fetchone()
        if cov_row and cov_row[0] == face_id:
            cursor.execute(
                'SELECT id FROM faces WHERE person_id = ? AND id != ? LIMIT 1',
                (p_id, face_id))
            other_face = cursor.fetchone()
            new_cover = other_face[0] if other_face else None
            cursor.execute('UPDATE people SET cover_face_id = ? WHERE id = ?',
                (new_cover, p_id))
    cursor.execute(
        'UPDATE faces SET person_id = NULL, is_manual = -1 WHERE id = ?', (
        face_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@faces_bp.route('/api/faces/rescan', methods=['POST'])
def rescan_faces():
    global scan_status
    with scan_lock:
        if scan_status['status'] == 'scanning':
            return jsonify({'error': 'A scan is already in progress'}), 400
        scan_status['status'] = 'scanning'
        scan_status['cancel_requested'] = False
        scan_status['total'] = 0
        scan_status['processed'] = 0
        scan_status['current_file'] = 'Initializing face rescan...'
        scan_status['phase'] = 'Rescanning Faces (Recall Optimized)'

    def run_rescan():
        try:
            processor = face_processor.FaceProcessor()
        except Exception as e:
            print(f'Error initializing face detector: {e}')
            scan_status['status'] = 'idle'
            scan_status['phase'] = ''
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT path FROM photos WHERE trashed_at IS NULL')
        photos = [r[0] for r in cursor.fetchall()]
        scan_status['total'] = len(photos)
        cursor.execute(
            'DELETE FROM faces WHERE is_manual = 0 OR is_manual IS NULL')
        cursor.execute(
            """
            DELETE FROM people 
            WHERE id NOT IN (SELECT DISTINCT person_id FROM faces WHERE person_id IS NOT NULL)
            AND (name IS NULL OR name LIKE 'Person %')
        """
            )
        conn.commit()
        for idx, path in enumerate(photos):
            with scan_lock:
                if scan_status.get('cancel_requested'):
                    break
            with scan_lock:
                scan_status['processed'] = idx + 1
                scan_status['current_file'] = os.path.basename(path)
            thumb_path = get_thumbnail_path(path)
            is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            detect_path = path
            if os.path.exists(detect_path):
                try:
                    faces = processor.detect_and_extract_faces(detect_path,
                        min_confidence=0.5)
                    for face in faces:
                        bbox = face['bbox']
                        emb_bytes = face['embedding'].tobytes()
                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
                        """
                            , (path, bbox[0], bbox[1], bbox[2], bbox[3],
                            emb_bytes))
                except Exception as e:
                    print(f'Error in face rescan extraction for {path}: {e}')
            if idx % 10 == 0:
                conn.commit()
        conn.commit()
        print('Running incremental face clustering after rescan...')
        try:
            run_incremental_clustering()
        except Exception as e:
            print(f'Error in face clustering: {e}')
        conn.close()
        scan_status['status'] = 'idle'
        scan_status['phase'] = ''
        print('Face rescan completed.')
    threading.Thread(target=run_rescan, daemon=True).start()
    return jsonify({'success': True})

@faces_bp.route('/api/faces/force_cluster', methods=['POST'])
def manual_force_cluster():

    def cluster_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Clustering Faces'
            scan_status['processed'] = 0
            scan_status['total'] = 1
            scan_status['current_file'] = ''
        try:
            run_incremental_clustering()
        finally:
            with scan_lock:
                scan_status['processed'] = 1
                scan_status['status'] = 'idle'
    threading.Thread(target=cluster_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Clustering started'})

@faces_bp.route('/api/faces/safe_rescan', methods=['POST'])
def manual_safe_rescan():

    def safe_rescan_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Safe Face Rescan (Preserving Names)'
            scan_status['processed'] = 0
            scan_status['total'] = 1
            scan_status['current_file'] = ''
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT path FROM photos WHERE path NOT IN (SELECT DISTINCT photo_path FROM faces)'
                )
            paths_no_faces = [r[0] for r in cursor.fetchall()]
            video_exts = '.mp4', '.mov', '.m4v', '.hevc'
            paths_no_faces.sort(key=lambda x: 1 if x.lower().endswith(
                video_exts) else 0)
            with scan_lock:
                scan_status['total'] = len(paths_no_faces)
            processor = face_processor.FaceProcessor()
            for i, p in enumerate(paths_no_faces):
                if os.path.exists(p):
                    detected = processor.detect_and_extract_faces(p)
                    for face in detected:
                        bx, by, bw, bh = face['bbox']
                        emb_bytes = face['embedding'].tobytes()
                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, 0)
                        """
                            , (p, bx, by, bw, bh, emb_bytes))
                with scan_lock:
                    scan_status['processed'] = i + 1
                    scan_status['current_file'] = os.path.basename(p)
            conn.commit()
            conn.close()
            run_incremental_clustering()
        except Exception as e:
            print(f'Error in safe rescan: {e}')
        finally:
            with scan_lock:
                scan_status['status'] = 'idle'
    threading.Thread(target=safe_rescan_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Safe face rescan started'})

@faces_bp.route('/api/faces/training_pairs', methods=['GET'])
def get_training_pairs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT f.id, f.embedding, f.photo_path, p.name, p.id
        FROM faces f
        JOIN people p ON f.person_id = p.id
        WHERE p.name != 'Unknown'
        LIMIT 50
    """
        )
    named_faces = cursor.fetchall()
    cursor.execute(
        """
        SELECT f.id, f.embedding, f.photo_path
        FROM faces f
        WHERE f.person_id IS NULL OR f.person_id IN (SELECT id FROM people WHERE name = 'Unknown')
        LIMIT 200
    """
        )
    unassigned_faces = cursor.fetchall()
    conn.close()
    pairs = []
    if named_faces and unassigned_faces:
        import numpy as np
        for nf in named_faces[:10]:
            n_emb = np.frombuffer(nf[1], dtype=np.float32)
            for uf in unassigned_faces:
                u_emb = np.frombuffer(uf[1], dtype=np.float32)
                dist = np.linalg.norm(n_emb - u_emb)
                if 0.4 < dist < 0.75:
                    pairs.append({'distance': float(dist), 'person_id': nf[
                        4], 'person_name': nf[3], 'named_face_id': nf[0],
                        'unknown_face_id': uf[0], 'named_photo': nf[2],
                        'unknown_photo': uf[2]})
                    if len(pairs) >= 5:
                        break
            if len(pairs) >= 5:
                break
    pairs.sort(key=lambda x: x['distance'])
    return jsonify({'pairs': pairs})

