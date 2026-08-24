from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
    row = cursor.fetchone()
    scan_folder = row[0] if row else None
    conn.close()
    
    onboarding_required = scan_folder is None or scan_folder.strip() == '' 
    
    # Optionally, if there are no photos in the DB, we can also force it? 
    # But usually setting scan_folder is enough for setup.
    return render_template('index.html', onboarding_required=onboarding_required)

@misc_bp.route('/api/search/suggestions')
def get_search_suggestions():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    parsed_list = parse_smart_dates(q)
    suggestions = []
    if parsed_list:
        conn = get_db_connection()
        cursor = conn.cursor()
        for parsed in parsed_list:
            cond_sql, cond_params = build_date_sql(parsed, 'photos')
            if cond_sql:
                cursor.execute(
                    f'SELECT COUNT(*) FROM photos WHERE {cond_sql} AND trashed_at IS NULL'
                    , cond_params)
                count = cursor.fetchone()[0]
                if count > 0:
                    parts = []
                    if 'day' in parsed:
                        parts.append(str(int(parsed['day'])))
                    if 'month' in parsed:
                        months = ['January', 'February', 'March', 'April',
                            'May', 'June', 'July', 'August', 'September',
                            'October', 'November', 'December']
                        parts.append(months[int(parsed['month']) - 1])
                    if 'year' in parsed:
                        parts.append(parsed['year'])
                    label = ' '.join(parts)
                    suggestions.append({'type': 'date', 'id': label,
                        'label': label, 'description':
                        f'Date Filter ({count} photos)'})
        conn.close()
    return jsonify(suggestions)

@misc_bp.route('/api/people')
@cache_api(timeout=30)
def get_people():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, p.name, p.cover_face_id, 
               SUM(CASE WHEN ph.trashed_at IS NULL AND f.id IS NOT NULL THEN 1 ELSE 0 END) as face_count
        FROM people p
        LEFT JOIN faces f ON f.person_id = p.id
        LEFT JOIN photos ph ON f.photo_path = ph.path
        GROUP BY p.id
        HAVING face_count > 0
        ORDER BY face_count DESC
    """
        )
    rows = cursor.fetchall()
    conn.close()
    people = []
    for r in rows:
        people.append({'id': r[0], 'name': r[1] if r[1] else
            f'Person {r[0]}', 'cover_face_id': r[2], 'face_count': r[3]})
    return jsonify(people)

@misc_bp.route('/api/people/rename', methods=['POST'])
def rename_person():
    data = request.json
    conn = None
    try:
        try:
            p_id = int(data.get('id'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid or missing ID format'}), 400
        new_name = data.get('name', '').strip()
        if not new_name:
            return jsonify({'error': 'Missing name'}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM people WHERE name = ? AND id != ?',
            (new_name, p_id))
        existing = cursor.fetchone()
        if existing:
            target_p_id = existing[0]
            cursor.execute('UPDATE faces SET person_id = ? WHERE person_id = ?'
                , (target_p_id, p_id))
            cursor.execute('DELETE FROM people WHERE id = ?', (p_id,))
            message = 'Merged into existing person'
            merged_id = target_p_id
        else:
            cursor.execute('UPDATE people SET name = ? WHERE id = ?', (
                new_name, p_id))
            message = 'Renamed successfully'
            merged_id = None
        conn.commit()
        conn.close()
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({'success': True, 'message': message, 'merged_id':
            merged_id})
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        print(f'Error in rename_person: {e}')
        return jsonify({'error': str(e)}), 500

@misc_bp.route('/api/people/unname', methods=['POST'])
def unname_person():
    data = request.json
    conn = None
    try:
        try:
            p_id = int(data.get('id'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid or missing ID format'}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE people SET name = ? WHERE id = ?', (
            f'Person {p_id}', p_id))
        conn.commit()
        conn.close()
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({'success': True})
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        print(f'Error in unname_person: {e}')
        return jsonify({'error': str(e)}), 500

@misc_bp.route('/api/people/delete', methods=['POST'])
def delete_person():
    data = request.json
    conn = None
    try:
        try:
            p_id = int(data.get('id'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid or missing ID format'}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE faces SET person_id = NULL WHERE person_id = ?',
            (p_id,))
        cursor.execute('DELETE FROM people WHERE id = ?', (p_id,))
        conn.commit()
        conn.close()
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({'success': True})
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        print(f'Error in delete_person: {e}')
        return jsonify({'error': str(e)}), 500

@misc_bp.route('/api/people/set-cover', methods=['POST'])
def set_person_cover():
    data = request.json
    try:
        person_id = int(data.get('person_id'))
        face_id = int(data.get('face_id'))
    except (ValueError, TypeError):
        return jsonify({'error':
            'Invalid or missing person_id or face_id format'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT person_id FROM faces WHERE id = ?', (face_id,))
    row = cursor.fetchone()
    db_person_id = int(row[0]) if row and row[0] is not None else None
    if not row or db_person_id != person_id:
        conn.close()
        return jsonify({'error':
            f"Face does not belong to specified person. DB person: {row[0] if row else 'None'}, Request person: {person_id}"
            }), 400
    try:
        cursor.execute('UPDATE people SET cover_face_id = ? WHERE id = ?',
            (face_id, person_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@misc_bp.route('/api/duplicates')
def get_duplicates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT hash, COUNT(*) as count 
        FROM photos 
        WHERE hash IS NOT NULL AND hash != '' AND trashed_at IS NULL
        GROUP BY hash 
        HAVING count > 1
    """
        )
    dup_hashes = [r[0] for r in cursor.fetchall()]
    duplicates = []
    for h in dup_hashes:
        cursor.execute(
            """
            SELECT path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash 
            FROM photos 
            WHERE hash = ? AND trashed_at IS NULL
        """
            , (h,))
        rows = cursor.fetchall()
        clusters = []
        for r in rows:
            path = r[0]
            size = r[5]
            is_vid = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            placed = False
            for cluster in clusters:
                rep = cluster[0]
                rep_path = rep[0]
                rep_size = rep[5]
                rep_is_vid = rep_path.lower().endswith(('.mp4', '.mov',
                    '.m4v', '.hevc'))
                if is_vid != rep_is_vid:
                    continue
                ratio = max(size, rep_size) / max(min(size, rep_size), 1)
                abs_diff = abs(size - rep_size)
                if ratio <= 2.0 or abs_diff <= 102400:
                    cluster.append(r)
                    placed = True
                    break
            if not placed:
                clusters.append([r])
        valid_clusters = [c for c in clusters if len(c) > 1]
        for cluster_idx, cluster in enumerate(valid_clusters):
            analyzed = []
            for r in cluster:
                clean_name, is_copy = analyze_filename(r[1])
                score = get_metadata_score(r)
                analyzed.append({'row': r, 'clean_name': clean_name,
                    'is_copy': is_copy, 'score': score})

            def sort_key(item):
                r = item['row']
                return item['score'], -1 if item['is_copy'] else 1, r[5], r[3
                    ] * r[4]
            analyzed.sort(key=sort_key, reverse=True)
            keep_item = analyzed[0]
            delete_items = analyzed[1:]
            action = 'KEEP_AS_IS'
            reason = ''
            if keep_item['is_copy']:
                non_copies = [x for x in delete_items if not x['is_copy']]
                if non_copies:
                    action = 'KEEP_AND_RENAME'
                    reason = (
                        'Kept copy due to better metadata; duplicate suffix will be removed.'
                        )
                else:
                    reason = 'Kept copy as original (only copies exist).'
            else:
                copies = [x for x in delete_items if x['is_copy']]
                if copies:
                    reason = 'Kept original; suggested deleting copies.'
                else:
                    reason = 'Kept highest quality original.'

            def format_photo(r):
                return {'path': r[0], 'filename': r[1], 'date_taken': r[2],
                    'width': r[3], 'height': r[4], 'size': r[5],
                    'file_type': r[6], 'latitude': r[7], 'longitude': r[8],
                    'place_name': r[9]}
            group_hash = f'{h}_{cluster_idx}'
            duplicates.append({'hash': group_hash, 'keep': format_photo(
                keep_item['row']), 'delete': [format_photo(x['row']) for x in
                delete_items], 'action': action, 'reason': reason})
    conn.close()
    return jsonify(duplicates)

@misc_bp.route('/api/duplicates/resolve', methods=['POST'])
def resolve_duplicates():
    data = request.json
    resolutions = data.get('resolutions', [])
    if not resolutions:
        return jsonify({'error': 'No resolutions provided'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    deleted_paths = []
    renamed_paths = []
    try:
        for res in resolutions:
            del_path = res.get('delete_path')
            if del_path and os.path.exists(del_path):
                success, trash_path, err = send_file_to_trash(del_path)
                cursor.execute(
                    'UPDATE photos SET trashed_at = ? WHERE path = ?', (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), del_path))
                deleted_paths.append(del_path)
        conn.commit()
        for res in resolutions:
            action = res.get('action')
            if action == 'KEEP_AND_RENAME':
                keep_path = res.get('keep_path')
                if keep_path and os.path.exists(keep_path):
                    filename = os.path.basename(keep_path)
                    clean_name, _ = analyze_filename(filename)
                    new_path = os.path.join(os.path.dirname(keep_path),
                        clean_name)
                    if not os.path.exists(new_path
                        ) or new_path in deleted_paths:
                        try:
                            shutil.move(keep_path, new_path)
                            renamed_paths.append((keep_path, new_path))
                            old_thumb = get_thumbnail_path(keep_path)
                            new_thumb = get_thumbnail_path(new_path)
                            if os.path.exists(old_thumb):
                                if os.path.exists(new_thumb):
                                    os.remove(new_thumb)
                                shutil.move(old_thumb, new_thumb)
                            cursor.execute(
                                'UPDATE faces SET photo_path = ? WHERE photo_path = ?'
                                , (new_path, keep_path))
                            cursor.execute(
                                'UPDATE album_photos SET photo_path = ? WHERE photo_path = ?'
                                , (new_path, keep_path))
                            cursor.execute(
                                'UPDATE photos SET path = ?, filename = ? WHERE path = ?'
                                , (new_path, clean_name, keep_path))
                        except Exception as rename_err:
                            print(
                                f'Error renaming resolved duplicate {keep_path} to {new_path}: {rename_err}'
                                )
        conn.commit()
        success = True
        error = None
    except Exception as e:
        conn.rollback()
        success = False
        error = str(e)
    finally:
        conn.close()
    if not success:
        return jsonify({'error': f'Failed to resolve duplicates: {error}'}
            ), 500
    return jsonify({'success': True, 'deleted': len(deleted_paths),
        'renamed': len(renamed_paths)})

@misc_bp.route('/api/people/<int:person_id>/faces', methods=['GET'])
def get_person_faces(person_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT f.id, f.photo_path
        FROM faces f
        JOIN photos ph ON f.photo_path = ph.path
        WHERE f.person_id = ? AND ph.trashed_at IS NULL
    """
        , (person_id,))
    faces = [{'id': r[0], 'photo_path': r[1]} for r in cursor.fetchall()]
    conn.close()
    return jsonify({'faces': faces})

@misc_bp.route('/api/people/merge', methods=['POST'])
def merge_people():
    data = request.json
    unknown_face_id = data.get('unknown_face_id')
    person_id = data.get('person_id')
    if not unknown_face_id or not person_id:
        return jsonify({'error': 'Missing parameters'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE faces SET person_id = ?, is_manual = 1 WHERE id = ?'
        , (person_id, unknown_face_id))
    conn.commit()
    conn.close()
    threading.Thread(target=run_incremental_clustering, daemon=True).start()
    return jsonify({'success': True})

@misc_bp.route('/api/cache/rebuild', methods=['POST'])
def rebuild_cache_and_mapping():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        root_dir = row[0] if row else None

    def rebuild_task():
        global scan_status
        with scan_lock:
            scan_status['status'] = 'scanning'
            scan_status['cancel_requested'] = False
            scan_status['phase'] = 'Rebuilding Mapping & Cache'
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
                    real_root = os.path.realpath(current_root)
                    if real_root in scanned_roots:
                        continue
                    scanned_roots.add(real_root)
                    for root, dirs, files in os.walk(current_root):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
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
            with scan_lock:
                scan_status['phase'] = 'Wiping Cache Directories'
            import shutil
            for item in os.listdir(THUMBNAILS_DIR):
                item_path = os.path.join(THUMBNAILS_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f'Failed to delete cache file {item_path}: {e}')
            for item in os.listdir(FACES_DIR):
                item_path = os.path.join(FACES_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f'Failed to delete face cache file {item_path}: {e}')
        except Exception as e:
            print(f'Error in cache rebuild: {e}')
        finally:
            conn.close()
            with scan_lock:
                scan_status['status'] = 'idle'
    threading.Thread(target=rebuild_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Cache rebuild started'})

@misc_bp.route('/api/memories/curated')
def api_memories_curated():
    conn = get_db_connection()
    c = conn.cursor()
    curated = {'featured_moment': None, 'featured_video': None,
        'album_pick': None}
    c.execute(
        """
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
        ORDER BY RANDOM() LIMIT 1
    """
        )
    row = c.fetchone()
    if row:
        curated['featured_moment'] = {'file_path': row[0], 'file_type': row
            [1], 'date_taken': row[2], 'size': row[3], 'width': row[4],
            'height': row[5], 'phash': row[6]}
    c.execute(
        """
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM')
        ORDER BY RANDOM() LIMIT 1
    """
        )
    row = c.fetchone()
    if row:
        curated['featured_video'] = {'file_path': row[0], 'file_type': row[
            1], 'date_taken': row[2], 'size': row[3], 'width': row[4],
            'height': row[5], 'phash': row[6]}
    c.execute(
        """
        SELECT id, name, cover_photo_path 
        FROM albums 
        WHERE cover_photo_path IS NOT NULL 
        ORDER BY RANDOM() LIMIT 1
    """
        )
    row = c.fetchone()
    if row:
        curated['album_pick'] = {'id': row[0], 'name': row[1],
            'cover_photo_path': row[2]}
    c.execute(
        """
        SELECT strftime('%Y-%m-%d', date_taken) as day
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL 
          AND date_taken >= '2000-01-01'
        GROUP BY day
        HAVING count(*) >= 3
        ORDER BY RANDOM() LIMIT 1
    """
        )
    day_row = c.fetchone()
    spotlight_day_photos = []
    if day_row:
        day_str = day_row[0]
        c.execute(
            """
            SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
            FROM photos
            WHERE trashed_at IS NULL AND archived_at IS NULL 
              AND date_taken LIKE ?
            ORDER BY date_taken ASC
        """
            , (day_str + '%',))
        for p in c.fetchall():
            spotlight_day_photos.append({'file_path': p[0], 'file_type': p[
                1], 'date_taken': p[2], 'size': p[3], 'width': p[4],
                'height': p[5], 'phash': p[6]})
    curated['spotlight_day'
        ] = spotlight_day_photos if spotlight_day_photos else None
    c.execute('SELECT id FROM people WHERE name = "Me" COLLATE NOCASE')
    me_row = c.fetchone()
    if me_row:
        me_id = me_row[0]
    else:
        c.execute(
            """
            SELECT p.id 
            FROM people p
            JOIN faces f ON f.person_id = p.id
            GROUP BY p.id
            ORDER BY count(*) DESC
            LIMIT 1
        """
            )
        me_row2 = c.fetchone()
        me_id = me_row2[0] if me_row2 else -1
    if me_id != -1:
        c.execute(
            """
            SELECT p.id, p.name, p.cover_face_id,
                   (SELECT count(*) FROM faces f1 JOIN faces f2 ON f1.photo_path = f2.photo_path 
                    WHERE f1.person_id = p.id AND f2.person_id = ?) as shared_count,
                   count(f.id) as total_count
            FROM people p
            JOIN faces f ON f.person_id = p.id
            WHERE p.id != ? AND p.name IS NOT NULL AND p.name NOT LIKE 'Person %'
            GROUP BY p.id
            HAVING count(f.id) >= 3 AND shared_count > 0
            ORDER BY RANDOM() LIMIT 1
        """
            , (me_id, me_id))
        person = c.fetchone()
        if not person:
            c.execute(
                """
                SELECT p.id, p.name, p.cover_face_id,
                       0 as shared_count,
                       count(f.id) as total_count
                FROM people p
                JOIN faces f ON f.person_id = p.id
                WHERE p.id != ? AND p.name IS NOT NULL AND p.name NOT LIKE 'Person %'
                GROUP BY p.id
                HAVING count(f.id) >= 3
                ORDER BY RANDOM() LIMIT 1
            """
                , (me_id,))
            person = c.fetchone()
        if person:
            pid, pname, pcover, pshared, ptotal = person
            c.execute(
                """
                SELECT ph.path, ph.date_taken, ph.file_type
                FROM photos ph
                JOIN faces f ON f.photo_path = ph.path
                WHERE f.person_id = ? AND ph.trashed_at IS NULL
                ORDER BY RANDOM() LIMIT 10
            """
                , (pid,))
            person_photos = [{'file_path': r[0], 'date_taken': r[1],
                'file_type': r[2]} for r in c.fetchall()]
            c.execute(
                """
                SELECT ph.path, ph.date_taken, ph.file_type
                FROM photos ph
                JOIN faces f1 ON f1.photo_path = ph.path
                JOIN faces f2 ON f2.photo_path = ph.path
                WHERE f1.person_id = ? AND f2.person_id = ? AND ph.trashed_at IS NULL
                ORDER BY RANDOM() LIMIT 10
            """
                , (pid, me_id))
            shared_photos = [{'file_path': r[0], 'date_taken': r[1],
                'file_type': r[2]} for r in c.fetchall()]
            curated['people_spotlight'] = {'person': {'id': pid, 'name':
                pname, 'cover_face_id': pcover, 'shared_count': pshared,
                'total_count': ptotal}, 'person_photos': person_photos,
                'shared_photos': shared_photos}
    conn.close()
    return jsonify({'success': True, 'curated': curated})

@misc_bp.route('/api/memories/on_this_day')
def api_memories():
    conn = get_db_connection()
    c = conn.cursor()
    today_mm_dd = datetime.now().strftime('%m-%d')
    c.execute(
        """
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos
        WHERE substr(date_taken, 6, 5) = ? AND trashed_at IS NULL
        ORDER BY date_taken DESC
    """
        , (today_mm_dd,))
    photos = c.fetchall()
    conn.close()
    results = {}
    for p in photos:
        if not p[2]:
            continue
        year = p[2][:4]
        if year not in results:
            results[year] = []
        p_dict = {'file_path': p[0], 'file_type': p[1], 'date_taken': p[2],
            'size': p[3], 'width': p[4], 'height': p[5], 'phash': p[6]}
        results[year].append(p_dict)
    return jsonify(results)

@misc_bp.route('/api/memories/welcome')
@cache_api(timeout=300)
def api_memories_welcome():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'hero_album_id'")
    album_row = c.fetchone()
    valid_photos = []
    if album_row and album_row[0]:
        album_id = album_row[0]
        c.execute(
            """
            SELECT p.path as file_path
            FROM photos p
            JOIN album_photos ap ON p.path = ap.photo_path
            WHERE ap.album_id = ? AND p.trashed_at IS NULL
            ORDER BY RANDOM() LIMIT 50
        """
            , (album_id,))
        candidates = c.fetchall()
        valid_photos = [row[0] for row in candidates]
    if not valid_photos:
        overrides = load_hero_overrides()
        whitelist = overrides.get('whitelist', [])
        blacklist = set(overrides.get('blacklist', []))
        if whitelist:
            c.execute(
                f"""
                SELECT path as file_path
                FROM photos
                WHERE trashed_at IS NULL
                  AND archived_at IS NULL
                  AND path IN ({','.join(['?'] * len(whitelist))})
            """
                , whitelist)
            wl_candidates = c.fetchall()
            valid_photos.extend([r[0] for r in wl_candidates])
        if len(valid_photos) < 50:
            c.execute(
                """
                SELECT file_path FROM (
                    SELECT path as file_path
                    FROM photos
                    WHERE trashed_at IS NULL
                      AND archived_at IS NULL
                      AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
                      AND width > height
                      AND path NOT IN (SELECT photo_path FROM faces)
                    ORDER BY date_taken DESC LIMIT 1000
                )
                ORDER BY RANDOM() LIMIT 300
            """
                )
            candidates = c.fetchall()
            from scene_classifier import scene_cache, check_scene, save_scene_cache
            for row in candidates:
                path = row[0]
                if path in blacklist or path in valid_photos:
                    continue
                is_scenic = scene_cache.get(path)
                if is_scenic is None:
                    is_scenic = check_scene(path)
                    scene_cache[path] = is_scenic
                    save_scene_cache()
                if is_scenic:
                    valid_photos.append(path)
                    if len(valid_photos) >= 50:
                        break
        if len(valid_photos) < 5 and 'candidates' in dir():
            for row in candidates:
                if row[0] not in valid_photos and row[0] not in blacklist:
                    valid_photos.append(row[0])
                if len(valid_photos) >= 50:
                    break
    from urllib.parse import quote
    photos_out = []
    if valid_photos:
        placeholders = ','.join(['?'] * len(valid_photos))
        c.execute(
            f'SELECT path, date_taken, place_name FROM photos WHERE path IN ({placeholders})'
            , valid_photos)
        meta_dict = {row[0]: {'date': row[1], 'location': row[2]} for row in
            c.fetchall()}
        for p in valid_photos:
            safe_path = quote(p.replace('\\', '/'))
            url = f'/api/photo/file/{safe_path}'
            meta = meta_dict.get(p, {})
            photos_out.append({'url': url, 'path': p, 'date': meta.get(
                'date'), 'location': meta.get('location')})
    return jsonify({'photos': photos_out})

@misc_bp.route('/api/memories/collections')
def api_memories_collections():
    conn = get_db_connection()
    c = conn.cursor()
    collections = []
    c.execute(
        """
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
        ORDER BY RANDOM() LIMIT 1
    """
        )
    row = c.fetchone()
    if row:
        collections.append({'type': 'featured_moment', 'title':
            'Featured Moment', 'subtitle': 'A trip down memory lane',
            'cover_photo': row[0], 'photos': [{'file_path': row[0],
            'file_type': row[1], 'date_taken': row[2]}]})
    c.execute(
        """
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM')
        ORDER BY RANDOM() LIMIT 1
    """
        )
    row = c.fetchone()
    if row:
        collections.append({'type': 'featured_video', 'title':
            'Featured Video', 'subtitle': 'Press play to relive',
            'cover_photo': row[0], 'photos': [{'file_path': row[0],
            'file_type': row[1], 'date_taken': row[2]}]})
    c.execute(
        """
        SELECT id, name, cover_photo_path 
        FROM albums 
        WHERE cover_photo_path IS NOT NULL 
        ORDER BY RANDOM() LIMIT 1
    """
        )
    row = c.fetchone()
    if row:
        c.execute(
            'SELECT path, file_type, date_taken FROM photos JOIN album_photos ON photos.path = album_photos.photo_path WHERE album_id = ? LIMIT 10'
            , (row[0],))
        album_photos = [{'file_path': r[0], 'file_type': r[1], 'date_taken':
            r[2]} for r in c.fetchall()]
        if album_photos:
            collections.append({'type': 'album_pick', 'title': row[1],
                'subtitle': 'From your albums', 'cover_photo': row[2],
                'photos': album_photos, 'album_id': row[0]})
    c.execute(
        """
        SELECT strftime('%Y-%m-%d', date_taken) as day
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL 
          AND date_taken >= '2000-01-01'
        GROUP BY day
        HAVING count(*) >= 3
        ORDER BY RANDOM() LIMIT 1
    """
        )
    day_row = c.fetchone()
    if day_row:
        day_str = day_row[0]
        c.execute(
            """
            SELECT path as file_path, file_type, date_taken
            FROM photos
            WHERE trashed_at IS NULL AND archived_at IS NULL 
              AND date_taken LIKE ?
            ORDER BY date_taken ASC
            LIMIT 15
        """
            , (day_str + '%',))
        spotlight_photos = [{'file_path': r[0], 'file_type': r[1],
            'date_taken': r[2]} for r in c.fetchall()]
        if spotlight_photos:
            try:
                date_obj = datetime.strptime(day_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d %b %Y')
            except:
                formatted_date = day_str
            collections.append({'type': 'spotlight_day', 'title':
                'Spotlight on a Day', 'subtitle': formatted_date,
                'cover_photo': spotlight_photos[0]['file_path'], 'photos':
                spotlight_photos})
    today_mm_dd = datetime.now().strftime('%m-%d')
    c.execute(
        """
        SELECT path as file_path, file_type, date_taken
        FROM photos
        WHERE substr(date_taken, 6, 5) = ? AND trashed_at IS NULL
        ORDER BY date_taken DESC
        LIMIT 10
    """
        , (today_mm_dd,))
    otd_photos = c.fetchall()
    if otd_photos:
        years = sorted(list(set([r[2][:4] for r in otd_photos if r[2]])))
        if len(years) > 3:
            subtitle = f'{years[0]} - {years[-1]}'
        elif len(years) > 0:
            subtitle = ', '.join(years)
        else:
            subtitle = 'Past Years'
        collections.insert(0, {'type': 'on_this_day', 'title':
            'On This Day', 'subtitle': subtitle, 'cover_photo': otd_photos[
            0][0], 'photos': [{'file_path': r[0], 'file_type': r[1],
            'date_taken': r[2]} for r in otd_photos]})
    today = datetime.now()
    month = today.month
    if month in (12, 1, 2):
        season_months, season_name = ('12', '01', '02'), 'Winter'
    elif month in (3, 4, 5):
        season_months, season_name = ('03', '04', '05'), 'Spring'
    elif month in (6, 7, 8):
        season_months, season_name = ('06', '07', '08'), 'Summer'
    else:
        season_months, season_name = ('09', '10', '11'), 'Autumn'
    c.execute(
        """
        SELECT path, file_type, date_taken 
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL
        AND (substr(date_taken, 6, 2) IN (?, ?, ?))
        AND file_type IN ('JPG', 'JPEG', 'PNG')
        ORDER BY RANDOM() LIMIT 15
    """
        , season_months)
    seasonal = c.fetchall()
    if seasonal:
        collections.append({'type': 'seasonal', 'title':
            f'{season_name} Vibes', 'subtitle': 'Memories from this season',
            'cover_photo': seasonal[0][0], 'photos': [{'file_path': r[0],
            'file_type': r[1], 'date_taken': r[2]} for r in seasonal]})
    if today.month == 1:
        prev_month = today.replace(year=today.year - 1, month=12, day=1)
    else:
        prev_month = today.replace(month=today.month - 1, day=1)
    prev_month_str = prev_month.strftime('%Y-%m')
    prev_month_name = prev_month.strftime('%B')
    c.execute(
        """
        SELECT path, file_type, date_taken
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL
        AND date_taken LIKE ?
        ORDER BY RANDOM() LIMIT 15
    """
        , (prev_month_str + '%',))
    best_of = c.fetchall()
    if best_of:
        collections.append({'type': 'best_of_month', 'title':
            f'Best of {prev_month_name}', 'subtitle':
            'Highlights from last month', 'cover_photo': best_of[0][0],
            'photos': [{'file_path': r[0], 'file_type': r[1], 'date_taken':
            r[2]} for r in best_of]})
    c.execute(
        """
        SELECT p.id, p.name 
        FROM people p
        JOIN faces f ON f.person_id = p.id
        WHERE p.name IS NOT NULL AND p.name NOT LIKE 'Person %' AND p.name != 'Me'
        GROUP BY p.id
        HAVING count(f.id) >= 5
        ORDER BY RANDOM() LIMIT 1
    """
        )
    person = c.fetchone()
    if person:
        pid, pname = person
        c.execute(
            """
            SELECT ph.path, ph.file_type, ph.date_taken
            FROM photos ph
            JOIN faces f ON f.photo_path = ph.path
            WHERE f.person_id = ? AND ph.trashed_at IS NULL
            ORDER BY RANDOM() LIMIT 15
        """
            , (pid,))
        person_photos = c.fetchall()
        if person_photos:
            collections.append({'type': 'with_person', 'title':
                f'With {pname}', 'subtitle': 'Moments together',
                'cover_photo': person_photos[0][0], 'photos': [{'file_path':
                r[0], 'file_type': r[1], 'date_taken': r[2]} for r in
                person_photos]})
    conn.close()
    import random
    random.shuffle(collections)
    return jsonify({'success': True, 'collections': collections})

@misc_bp.route('/api/memories/hero/blacklist', methods=['POST'])
def api_hero_blacklist():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({'error': 'path required'}), 400
    overrides = load_hero_overrides()
    if 'blacklist' not in overrides:
        overrides['blacklist'] = []
    if path not in overrides['blacklist']:
        overrides['blacklist'].append(path)
        save_hero_overrides(overrides)
    return jsonify({'success': True})

@misc_bp.route('/api/memories/hero/scan_more', methods=['POST'])
def api_hero_scan_more():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            SELECT file_path FROM (
                SELECT path as file_path
                FROM photos
                WHERE trashed_at IS NULL
                  AND archived_at IS NULL
                  AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
                  AND width > height
                  AND path NOT IN (SELECT photo_path FROM faces)
                ORDER BY date_taken DESC LIMIT 1000
            )
            ORDER BY RANDOM() LIMIT 200
        """
            )
        candidates = c.fetchall()
        conn.close()
        overrides = load_hero_overrides()
        blacklist = set(overrides.get('blacklist', []))
        from scene_classifier import check_scene, scene_cache, save_scene_cache
        added = 0
        for row in candidates:
            path = row[0]
            if path in blacklist:
                continue
            if path not in scene_cache:
                is_scenic = check_scene(path)
                scene_cache[path] = is_scenic
                if is_scenic:
                    added += 1
                if added >= 50:
                    break
        save_scene_cache()
        return jsonify({'success': True, 'added': added})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

