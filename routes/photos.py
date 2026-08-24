from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

photos_bp = Blueprint('photos', __name__)

@photos_bp.route('/api/photos')
@cache_api(timeout=30)
def get_photos():
    people_filter = request.args.get('people')
    places_filter = request.args.get('places')
    albums_filter = request.args.get('albums')
    type_filter = request.args.get('types')
    search_query = request.args.get('search', '').strip()
    date_query = request.args.get('date_query', '').strip()
    sort_by = request.args.get('sort', 'date_desc')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = (
        'SELECT DISTINCT p.path, p.filename, p.date_taken, p.width, p.height, p.size, p.file_type, p.latitude, p.longitude, p.place_name, p.archived_at, p.is_favorite, p.camera_make, p.camera_model, p.f_stop, p.exposure_time, p.focal_length, p.iso, g.place_name, p.duration, p.fps, p.video_codec FROM photos p LEFT JOIN geocoding_cache g ON ROUND(p.latitude, 3) = g.lat_rounded AND ROUND(p.longitude, 3) = g.lon_rounded'
        )
    joins = []
    where_clauses = []
    params = []
    show_trashed = request.args.get('trashed') == 'true'
    show_archived = request.args.get('archived') == 'true'
    show_favorites = request.args.get('favorites') == 'true'
    if show_trashed:
        where_clauses.append('p.trashed_at IS NOT NULL')
    else:
        where_clauses.append('p.trashed_at IS NULL')
        if show_archived:
            where_clauses.append('p.archived_at IS NOT NULL')
        elif not albums_filter and not show_favorites:
            where_clauses.append('p.archived_at IS NULL')
    if show_favorites:
        where_clauses.append('p.is_favorite = 1')
    if people_filter:
        people_ids = [int(x) for x in people_filter.split(',') if x.isdigit()]
        if people_ids:
            for i, p_id in enumerate(people_ids):
                alias = f'f{i}'
                joins.append(
                    f'JOIN faces {alias} ON p.path = {alias}.photo_path AND {alias}.person_id = ?'
                    )
                params.append(p_id)
    if albums_filter:
        album_ids = [int(x) for x in albums_filter.split(',') if x.isdigit()]
        if album_ids:
            for i, a_id in enumerate(album_ids):
                alias = f'ap{i}'
                joins.append(
                    f'JOIN album_photos {alias} ON p.path = {alias}.photo_path AND {alias}.album_id = ?'
                    )
                params.append(a_id)
    if places_filter:
        places_list = [x.strip() for x in places_filter.split(',') if x.strip()
            ]
        if places_list:
            place_or_clauses = []
            for place in places_list:
                place_or_clauses.append('p.place_name LIKE ?')
                params.append(f'%{place}%')
            where_clauses.append(f"({' OR '.join(place_or_clauses)})")
    if type_filter:
        types_list = [x.strip().upper() for x in type_filter.split(',') if
            x.strip()]
        if types_list:
            placeholders = ','.join(['?'] * len(types_list))
            where_clauses.append(f'p.file_type IN ({placeholders})')
            params.extend(types_list)
    if date_query:
        date_queries = [x.strip() for x in date_query.split(',') if x.strip()]
        years = []
        months = []
        days = []
        exact_dates = []
        for dq in date_queries:
            parsed_dates = parse_smart_dates(dq)
            if not parsed_dates:
                continue
            pd = parsed_dates[0]
            if len(pd) == 1:
                if 'year' in pd:
                    years.append(pd['year'])
                elif 'month' in pd:
                    months.append(pd['month'])
                elif 'day' in pd:
                    days.append(pd['day'])
            else:
                exact_dates.append(pd)
        combined_date_conds = []
        combined_params = []
        if years:
            placeholders = ','.join(['?'] * len(years))
            combined_date_conds.append(
                f"strftime('%Y', p.date_taken) IN ({placeholders})")
            combined_params.extend(years)
        if months:
            placeholders = ','.join(['?'] * len(months))
            combined_date_conds.append(
                f"strftime('%m', p.date_taken) IN ({placeholders})")
            combined_params.extend(months)
        if days:
            placeholders = ','.join(['?'] * len(days))
            combined_date_conds.append(
                f"strftime('%d', p.date_taken) IN ({placeholders})")
            combined_params.extend(days)
        if exact_dates:
            exact_or = []
            for pd in exact_dates:
                c, p = build_date_sql(pd, 'p')
                if c:
                    exact_or.append(f'({c})')
                    combined_params.extend(p)
            if exact_or:
                combined_date_conds.append(f"({' OR '.join(exact_or)})")
        if combined_date_conds:
            where_clauses.append(f"({' AND '.join(combined_date_conds)})")
            params.extend(combined_params)
    if search_query:
        search_terms = search_query.split()
        for term in search_terms:
            term_param = f'%{term}%'
            where_clauses.append(
                """
                (p.filename LIKE ? OR p.place_name LIKE ? OR g.place_name LIKE ? OR p.date_taken LIKE ? OR p.path IN (
                    SELECT f.photo_path FROM faces f JOIN people pe ON f.person_id = pe.id WHERE pe.name LIKE ?
                ) OR fuzzy_match(?, p.filename) = 1 OR fuzzy_match(?, p.place_name) = 1 OR p.path IN (
                    SELECT f.photo_path FROM faces f JOIN people pe ON f.person_id = pe.id WHERE fuzzy_match(?, pe.name) = 1
                ))
            """
                )
            params.extend([term_param, term_param, term_param, term_param, term_param,
                term, term, term])
    if joins:
        query += ' ' + ' '.join(joins)
    if where_clauses:
        query += ' WHERE ' + ' AND '.join(where_clauses)
    if sort_by == 'date_desc':
        query += ' ORDER BY p.date_taken DESC'
    elif sort_by == 'date_asc':
        query += ' ORDER BY p.date_taken ASC'
    elif sort_by == 'size_desc':
        query += ' ORDER BY p.size DESC'
    elif sort_by == 'size_asc':
        query += ' ORDER BY p.size ASC'
    elif sort_by == 'type_asc':
        query += ' ORDER BY p.file_type ASC, p.date_taken DESC'
    elif sort_by == 'name_desc':
        query += ' ORDER BY p.filename DESC'
    elif sort_by == 'name_asc':
        query += ' ORDER BY p.filename ASC'
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    photos = []
    for r in rows:
        photo_dict = {'path': r[0], 'filename': r[1], 'date_taken': r[2],
            'width': r[3], 'height': r[4], 'size': r[5], 'file_type': r[6],
            'latitude': r[7], 'longitude': r[8], 'place_name': r[9],
            'archived_at': r[10], 'is_favorite': bool(r[11]) if r[11] else 
            False, 'camera_make': r[12], 'camera_model': r[13], 'f_stop': r
            [14], 'exposure_time': r[15], 'focal_length': r[16], 'iso': r[
            17], 'duration': r[19], 'fps': r[20], 'video_codec': r[21]}
        full_address = None
        if len(r) > 18 and r[18]:
            try:
                g_data = json.loads(r[18])
                full_address = g_data.get('display_name', r[18])
            except:
                full_address = r[18]
        photo_dict['full_address'] = full_address
        photos.append(photo_dict)
    return jsonify(photos)

@photos_bp.route('/api/photo/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({'error': 'Missing path'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_favorite FROM photos WHERE path = ?', (path,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Photo not found'}), 404
    new_val = 0 if row[0] else 1
    cursor.execute('UPDATE photos SET is_favorite = ? WHERE path = ?', (
        new_val, path))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_favorite': bool(new_val)})

@photos_bp.route('/api/photo/refresh_if_changed', methods=['POST'])
def refresh_photo_if_changed():
    data = request.json
    path = data.get('path')
    expected_size = data.get('expected_size')
    if not path or not os.path.exists(path):
        return jsonify({'changed': False, 'error': 'file missing'})
    try:
        current_size = os.path.getsize(path)
        if current_size != expected_size:
            print(
                f'refresh_if_changed triggered for {path}. current: {current_size}, expected: {expected_size}'
                )
            meta = extract_metadata(path)
            thumb_path = get_thumbnail_path(path)
            if os.path.exists(thumb_path):
                try:
                    os.remove(thumb_path)
                except:
                    pass
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT date_taken, latitude, longitude, duration, fps, video_codec, width, height, camera_make, camera_model, f_stop, exposure_time, focal_length, iso FROM photos WHERE path = ?'
                , (path,))
            existing = cursor.fetchone()
            if existing:
                (e_date, e_lat, e_lon, e_dur, e_fps, e_codec, e_w, e_h,
                    e_cmake, e_cmod, e_fs, e_et, e_fl, e_iso) = existing
                if meta['date_taken'] is None:
                    meta['date_taken'] = e_date
                if meta['latitude'] is None:
                    meta['latitude'] = e_lat
                if meta['longitude'] is None:
                    meta['longitude'] = e_lon
                if meta['duration'] is None:
                    meta['duration'] = e_dur
                if meta['fps'] is None:
                    meta['fps'] = e_fps
                if meta['video_codec'] is None:
                    meta['video_codec'] = e_codec
                if meta['width'] == 0 or meta['width'] is None:
                    meta['width'] = e_w
                if meta['height'] == 0 or meta['height'] is None:
                    meta['height'] = e_h
                if meta['camera_make'] is None:
                    meta['camera_make'] = e_cmake
                if meta['camera_model'] is None:
                    meta['camera_model'] = e_cmod
                if meta['f_stop'] is None:
                    meta['f_stop'] = e_fs
                if meta['exposure_time'] is None:
                    meta['exposure_time'] = e_et
                if meta['focal_length'] is None:
                    meta['focal_length'] = e_fl
                if meta['iso'] is None:
                    meta['iso'] = e_iso
            cursor.execute(
                """
                UPDATE photos SET 
                date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, 
                latitude = ?, longitude = ?, camera_make = ?, camera_model = ?, 
                f_stop = ?, exposure_time = ?, focal_length = ?, iso = ?, 
                duration = ?, fps = ?, video_codec = ? 
                WHERE path = ?
            """
                , (meta['date_taken'], meta['width'], meta['height'], meta[
                'size'], meta['file_type'], meta['latitude'], meta[
                'longitude'], meta['camera_make'], meta['camera_model'],
                meta['f_stop'], meta['exposure_time'], meta['focal_length'],
                meta['iso'], meta['duration'], meta['fps'], meta[
                'video_codec'], path))
            conn.commit()
            cursor.execute(
                """
                SELECT p.path, p.filename, p.date_taken, p.width, p.height, p.size, p.file_type, 
                       p.latitude, p.longitude, p.place_name, p.archived_at, p.is_favorite, 
                       p.camera_make, p.camera_model, p.f_stop, p.exposure_time, p.focal_length, p.iso, 
                       g.place_name as g_place, p.duration, p.fps, p.video_codec 
                FROM photos p 
                LEFT JOIN geocoding_cache g ON ROUND(p.latitude, 3) = g.lat_rounded AND ROUND(p.longitude, 3) = g.lon_rounded 
                WHERE p.path = ?
            """
                , (path,))
            r = cursor.fetchone()
            conn.close()
            if r:
                full_address = r[18]
                if r[18]:
                    try:
                        g_data = json.loads(r[18])
                        full_address = g_data.get('display_name', r[18])
                    except:
                        full_address = r[18]
                photo_dict = {'path': r[0], 'filename': r[1], 'date_taken':
                    r[2], 'width': r[3], 'height': r[4], 'size': r[5],
                    'file_type': r[6], 'latitude': r[7], 'longitude': r[8],
                    'place_name': r[9], 'archived_at': r[10], 'is_favorite':
                    bool(r[11]) if r[11] else False, 'camera_make': r[12],
                    'camera_model': r[13], 'f_stop': r[14], 'exposure_time':
                    r[15], 'focal_length': r[16], 'iso': r[17],
                    'full_address': full_address, 'duration': r[19], 'fps':
                    r[20], 'video_codec': r[21]}
                return jsonify({'changed': True, 'photo': photo_dict})
    except Exception as e:
        print(f'Error checking file modification: {e}')
    return jsonify({'changed': False})

@photos_bp.route('/api/photo/file/<path:photo_path>')
def serve_photo_file(photo_path):
    photo_path = os.path.normpath(photo_path)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return 'Not authorized', 403
    scan_folder = os.path.normpath(row[0])
    print(f'DEBUG: serve_photo_file requested for: {photo_path}')
    print(f'DEBUG: scan_folder is: {scan_folder}')
    print(
        f'DEBUG: startswith check: {photo_path.lower().startswith(scan_folder.lower())}'
        )
    if not photo_path.lower().startswith(scan_folder.lower()):
        print('DEBUG: Access denied')
        return 'Access denied', 403
    print(f'DEBUG: os.path.exists check: {os.path.exists(photo_path)}')
    if not os.path.exists(photo_path):
        return 'File not found', 404
    print('DEBUG: Serving file...')
    if photo_path.lower().endswith(('.heic', '.heif', '.tiff', '.tif')):
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
            with Image.open(photo_path) as img:
                img_io = BytesIO()
                img = ImageOps.exif_transpose(img)
                img.save(img_io, 'JPEG', quality=85)
                img_io.seek(0)
                return send_file(img_io, mimetype='image/jpeg')
        except Exception as e:
            print(f'Error converting unsupported image format on the fly: {e}')
            return serve_photo_thumbnail(photo_path)
    return send_file(photo_path)

@photos_bp.route('/api/photo/thumbnail/<path:photo_path>')
def serve_photo_thumbnail(photo_path):
    thumb_path = get_thumbnail_path(photo_path)
    if not os.path.exists(thumb_path):
        is_video = photo_path.lower().endswith(('.mp4', '.mov', '.m4v',
            '.hevc'))
        if is_video:
            success = generate_video_thumbnail(photo_path, thumb_path)
        else:
            success = generate_thumbnail(photo_path, thumb_path)
        if not success:
            return 'Thumbnail generation failed', 500
    return send_file(thumb_path)

@photos_bp.route('/api/photo/open-system', methods=['POST'])
def open_photo_system():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        os.startfile(photo_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/photo/open-folder', methods=['POST'])
def open_photo_folder():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        import subprocess
        abs_path = os.path.abspath(photo_path)
        subprocess.Popen(f'explorer.exe /select,"{abs_path}"')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/photo/refresh-metadata', methods=['POST'])
def refresh_photo_metadata():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        meta = extract_metadata(photo_path)
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT date_taken, latitude, longitude, duration, fps, video_codec, width, height, camera_make, camera_model, f_stop, exposure_time, focal_length, iso FROM photos WHERE path = ?'
            , (photo_path,))
        existing = cursor.fetchone()
        if existing:
            (e_date, e_lat, e_lon, e_dur, e_fps, e_codec, e_w, e_h, e_cmake,
                e_cmod, e_fs, e_et, e_fl, e_iso) = existing
            if meta['date_taken'] is None:
                meta['date_taken'] = e_date
            if meta['latitude'] is None:
                meta['latitude'] = e_lat
            if meta['longitude'] is None:
                meta['longitude'] = e_lon
            if meta['duration'] is None:
                meta['duration'] = e_dur
            if meta['fps'] is None:
                meta['fps'] = e_fps
            if meta['video_codec'] is None:
                meta['video_codec'] = e_codec
            if meta['width'] == 0 or meta['width'] is None:
                meta['width'] = e_w
            if meta['height'] == 0 or meta['height'] is None:
                meta['height'] = e_h
            if meta['camera_make'] is None:
                meta['camera_make'] = e_cmake
            if meta['camera_model'] is None:
                meta['camera_model'] = e_cmod
            if meta['f_stop'] is None:
                meta['f_stop'] = e_fs
            if meta['exposure_time'] is None:
                meta['exposure_time'] = e_et
            if meta['focal_length'] is None:
                meta['focal_length'] = e_fl
            if meta['iso'] is None:
                meta['iso'] = e_iso
        place_name = None
        if existing:
            old_lat = e_lat
            old_lon = e_lon
            cursor.execute('SELECT place_name FROM photos WHERE path = ?',
                (photo_path,))
            old_place = cursor.fetchone()[0]
            if meta['latitude'] is not None and meta['longitude'] is not None:
                if old_lat != meta['latitude'] or old_lon != meta['longitude'
                    ] or not old_place:
                    place_name = reverse_geocode(meta['latitude'], meta[
                        'longitude'])
            if not place_name and old_place:
                place_name = old_place
        cursor.execute(
            """
            UPDATE photos
            SET date_taken = ?, width = ?, height = ?, size = ?, file_type = ?,
                latitude = ?, longitude = ?, place_name = ?,
                camera_make = ?, camera_model = ?, f_stop = ?, exposure_time = ?, focal_length = ?, iso = ?,
                duration = ?, fps = ?, video_codec = ?
            WHERE path = ?
        """
            , (meta['date_taken'], meta['width'], meta['height'], meta[
            'size'], meta['file_type'], meta['latitude'], meta['longitude'],
            place_name or meta['place_name'], meta.get('camera_make'), meta
            .get('camera_model'), meta.get('f_stop'), meta.get(
            'exposure_time'), meta.get('focal_length'), meta.get('iso'),
            meta.get('duration'), meta.get('fps'), meta.get('video_codec'),
            photo_path))
        conn.commit()
        try:
            detect_path = photo_path
            if os.path.exists(detect_path):
                processor = face_processor.FaceProcessor()
                detected_faces = processor.detect_and_extract_faces(detect_path
                    , min_confidence=0.8)
                cursor.execute(
                    'SELECT x, y, w, h FROM faces WHERE photo_path = ?', (
                    photo_path,))
                existing_boxes = cursor.fetchall()
                new_faces_added = False
                for face in detected_faces:
                    bx, by, bw, bh = face['bbox']
                    is_duplicate = False
                    for ex, ey, ew, eh in existing_boxes:
                        ix = max(bx, ex)
                        iy = max(by, ey)
                        iw = min(bx + bw, ex + ew) - ix
                        ih = min(by + bh, ey + eh) - iy
                        if iw > 0 and ih > 0:
                            intersection_area = iw * ih
                            box_area = bw * bh
                            ex_area = ew * eh
                            iou = intersection_area / float(box_area +
                                ex_area - intersection_area)
                            if iou > 0.3 or intersection_area / float(box_area
                                ) > 0.5:
                                is_duplicate = True
                                break
                    if not is_duplicate:
                        emb_bytes = face['embedding'].tobytes()
                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
                        """
                            , (photo_path, bx, by, bw, bh, emb_bytes))
                        new_faces_added = True
                if new_faces_added:
                    conn.commit()
                    run_incremental_clustering()
        except Exception as face_err:
            print(f'Error in aggressive face preview search: {face_err}')
        cursor.execute(
            """
            SELECT p.path, p.filename, p.date_taken, p.width, p.height, p.size, p.file_type, 
                   p.latitude, p.longitude, p.place_name, p.archived_at, p.is_favorite, 
                   p.camera_make, p.camera_model, p.f_stop, p.exposure_time, p.focal_length, p.iso, 
                   g.place_name as g_place, p.duration, p.fps, p.video_codec 
            FROM photos p 
            LEFT JOIN geocoding_cache g ON ROUND(p.latitude, 3) = g.lat_rounded AND ROUND(p.longitude, 3) = g.lon_rounded 
            WHERE p.path = ?
        """
            , (photo_path,))
        updated_row = cursor.fetchone()
        conn.close()
        if updated_row:
            r = updated_row
            filename = os.path.basename(photo_path)
            filename_date = None
            has_date_mismatch = False
            match = re.search(
                '(\\d{4})(\\d{2})(\\d{2})_(\\d{2})(\\d{2})(\\d{2})', filename)
            if match:
                try:
                    year, month, day, hour, col, sec = match.groups()
                    dt_file = datetime(int(year), int(month), int(day), int
                        (hour), int(col), int(sec))
                    filename_date = dt_file.strftime('%Y-%m-%d %H:%M:%S')
                    db_date = r[2]
                    if db_date:
                        try:
                            dt_db = datetime.strptime(db_date,
                                '%Y-%m-%d %H:%M:%S')
                            if abs((dt_file - dt_db).total_seconds()) > 60:
                                has_date_mismatch = True
                        except ValueError:
                            has_date_mismatch = True
                    else:
                        has_date_mismatch = True
                except Exception:
                    pass
            full_address = r[18]
            if r[18]:
                try:
                    g_data = json.loads(r[18])
                    full_address = g_data.get('display_name', r[18])
                except:
                    full_address = r[18]
            return jsonify({'success': True, 'photo': {'path': r[0],
                'filename': r[1], 'date_taken': r[2], 'width': r[3],
                'height': r[4], 'size': r[5], 'file_type': r[6], 'latitude':
                r[7], 'longitude': r[8], 'place_name': r[9], 'archived_at':
                r[10], 'is_favorite': bool(r[11]) if r[11] else False,
                'camera_make': r[12], 'camera_model': r[13], 'f_stop': r[14
                ], 'exposure_time': r[15], 'focal_length': r[16], 'iso': r[
                17], 'full_address': full_address, 'duration': r[19], 'fps':
                r[20], 'video_codec': r[21]}, 'filename_date':
                filename_date, 'has_date_mismatch': has_date_mismatch})
        return jsonify({'error': 'Failed to retrieve updated record'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/photo/rename', methods=['POST'])
def api_photo_rename():
    data = request.json
    photo_path = data.get('photo_path')
    new_filename = data.get('new_filename')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'Original file not found'}), 404
    if not new_filename:
        return jsonify({'error': 'New filename required'}), 400
    dir_name = os.path.dirname(photo_path)
    old_ext = os.path.splitext(photo_path)[1]
    if not new_filename.lower().endswith(old_ext.lower()):
        new_filename += old_ext
    new_path = os.path.join(dir_name, new_filename)
    if os.path.exists(new_path) and new_path.lower() != photo_path.lower():
        return jsonify({'error': 'A file with that name already exists'}), 409
    try:
        os.rename(photo_path, new_path)
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('PRAGMA foreign_keys=OFF')
        c.execute('BEGIN TRANSACTION')
        c.execute('UPDATE photos SET path=?, filename=? WHERE path=?', (
            new_path, new_filename, photo_path))
        c.execute('UPDATE faces SET photo_path=? WHERE photo_path=?', (
            new_path, photo_path))
        c.execute('UPDATE album_photos SET photo_path=? WHERE photo_path=?',
            (new_path, photo_path))
        c.execute('COMMIT')
        c.execute('PRAGMA foreign_keys=ON')
        conn.commit()
        return jsonify({'success': True, 'new_path': new_path,
            'new_filename': new_filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/photo/fix-date-from-filename', methods=['POST'])
def fix_photo_date_from_filename():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'File not found'}), 404
    filename = os.path.basename(photo_path)
    match = re.search('(\\d{4})(\\d{2})(\\d{2})_(\\d{2})(\\d{2})(\\d{2})',
        filename)
    if not match:
        return jsonify({'error':
            'Filename does not match standard date pattern'}), 400
    try:
        year, month, day, hour, col, sec = match.groups()
        dt_file = datetime(int(year), int(month), int(day), int(hour), int(
            col), int(sec))
        new_date_str = dt_file.strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('UPDATE photos SET date_taken = ? WHERE path = ?', (
            new_date_str, photo_path))
        conn.commit()
        conn.close()
        save_date_to_file_and_system(photo_path, new_date_str)
        return jsonify({'success': True, 'date_taken': new_date_str})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/photo/crop/<int:face_id>')
def serve_face_crop(face_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT photo_path, x, y, w, h FROM faces WHERE id = ?',
        (face_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return 'Face not found', 404
    photo_path, x, y, w, h = row
    is_video = photo_path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
    source_path = get_thumbnail_path(photo_path) if is_video else photo_path
    if not os.path.exists(source_path):
        return 'Source photo not found', 404
    try:
        from io import BytesIO
        with Image.open(source_path) as img_raw:
            img = ImageOps.exif_transpose(img_raw)
            img_w, img_h = img.size
            center_x = x + w // 2
            center_y = y + h // 2
            size_limit = max(w, h)
            crop_size = int(size_limit * 2.0)
            crop_size = min(crop_size, img_w, img_h)
            left = center_x - crop_size // 2
            top = center_y - crop_size // 2
            if left < 0:
                left = 0
            elif left + crop_size > img_w:
                left = img_w - crop_size
            if top < 0:
                top = 0
            elif top + crop_size > img_h:
                top = img_h - crop_size
            cropped = img.crop((left, top, left + crop_size, top + crop_size))
            cropped = cropped.resize((150, 150), Image.Resampling.LANCZOS)
            if cropped.mode in ('RGBA', 'P', 'LA'):
                cropped = cropped.convert('RGB')
            img_io = BytesIO()
            cropped.save(img_io, 'JPEG', quality=85)
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        print(f'Error cropping face {face_id}: {e}')
        return 'Failed to crop face', 500

@photos_bp.route('/api/photo/faces/<path:photo_path>')
def get_photo_faces(photo_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT f.id, f.x, f.y, f.w, f.h, p.id, p.name, p.cover_face_id 
        FROM faces f 
        LEFT JOIN people p ON f.person_id = p.id 
        WHERE f.photo_path = ? AND (f.is_manual != -1 OR f.is_manual IS NULL)
    """
        , (photo_path,))
    rows = cursor.fetchall()
    conn.close()
    faces = []
    for r in rows:
        faces.append({'face_id': r[0], 'x': r[1], 'y': r[2], 'w': r[3], 'h':
            r[4], 'person_id': r[5], 'person_name': r[6] if r[6] else 
            f'Person {r[5]}' if r[5] is not None else
            f'Unnamed Person {r[0]}', 'cover_face_id': r[7]})
    return jsonify(faces)

@photos_bp.route('/api/photo/albums/<path:photo_path>')
def get_photo_albums(photo_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.id, a.name 
        FROM albums a 
        JOIN album_photos ap ON a.id = ap.album_id 
        WHERE ap.photo_path = ?
    """
        , (photo_path,))
    rows = cursor.fetchall()
    conn.close()
    albums = []
    for r in rows:
        albums.append({'id': r[0], 'name': r[1]})
    return jsonify(albums)

@photos_bp.route('/api/photos/copy', methods=['POST'])
def copy_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    destination = data.get('destination', '').strip()
    if not photo_paths:
        return jsonify({'error': 'No photos provided'}), 400
    if not destination:
        return jsonify({'error': 'No destination folder path provided'}), 400
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
        except Exception as e:
            return jsonify({'error':
                f'Failed to create destination folder: {str(e)}'}), 400
    import shutil
    success_count = 0
    errors = []
    for path in photo_paths:
        if os.path.exists(path):
            filename = os.path.basename(path)
            dest_path = os.path.join(destination, filename)
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(destination, f'{base}_{counter}{ext}')
                counter += 1
            try:
                shutil.copy2(path, dest_path)
                success_count += 1
            except Exception as e:
                errors.append(f'{filename}: {str(e)}')
    if errors:
        return jsonify({'success': True, 'count': success_count, 'errors':
            errors})
    return jsonify({'success': True, 'count': success_count})

@photos_bp.route('/api/photo/edit_metadata', methods=['POST'])
def edit_metadata():
    data = request.json
    path = data.get('photo_path')
    if not path:
        return jsonify({'error': 'Missing photo path'}), 400
    date_taken = data.get('date_taken')
    place_name = data.get('place_name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM photos WHERE path = ?', (path,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Photo not found'}), 404
    updates = []
    params = []
    if date_taken is not None:
        updates.append('date_taken = ?')
        params.append(date_taken.strip() if date_taken else None)
    if place_name is not None:
        updates.append('place_name = ?')
        params.append(place_name.strip() if place_name else None)
    if latitude is not None:
        updates.append('latitude = ?')
        try:
            params.append(float(latitude) if latitude != '' else None)
        except ValueError:
            conn.close()
            return jsonify({'error': 'Latitude must be a number'}), 400
    if longitude is not None:
        updates.append('longitude = ?')
        try:
            params.append(float(longitude) if longitude != '' else None)
        except ValueError:
            conn.close()
            return jsonify({'error': 'Longitude must be a number'}), 400
    if not updates:
        conn.close()
        return jsonify({'error': 'No update values provided'}), 400
    params.append(path)
    cursor.execute(f"UPDATE photos SET {', '.join(updates)} WHERE path = ?",
        params)
    conn.commit()
    conn.close()
    if date_taken is not None and date_taken.strip():
        try:
            save_date_to_file_and_system(path, date_taken)
        except Exception as e:
            print(f'Failed to save date to EXIF/attributes for {path}: {e}')
    return jsonify({'success': True})

@photos_bp.route('/api/photo/deep-scan', methods=['POST'])
def deep_scan_photo():
    data = request.json
    photo_path = data.get('path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT x, y, w, h FROM faces WHERE photo_path = ?',
            (photo_path,))
        existing_boxes = cursor.fetchall()
        processor = face_processor.FaceProcessor()
        detected_faces = processor.detect_and_extract_faces(photo_path,
            min_confidence=0.47)
        new_faces_added = 0
        new_boxes_this_run = []
        for face in detected_faces:
            bx, by, bw, bh = face['bbox']
            current_box = bx, by, bw, bh
            is_duplicate = False
            for e_box in existing_boxes:
                if compute_iou(current_box, e_box) > 0.3 or compute_iom(
                    current_box, e_box) > 0.6:
                    is_duplicate = True
                    break
            if not is_duplicate:
                for n_box in new_boxes_this_run:
                    if compute_iou(current_box, n_box) > 0.3 or compute_iom(
                        current_box, n_box) > 0.6:
                        is_duplicate = True
                        break
            if not is_duplicate:
                new_boxes_this_run.append(current_box)
                emb_bytes = face['embedding'].tobytes()
                cursor.execute(
                    """
                    INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """
                    , (photo_path, bx, by, bw, bh, emb_bytes))
                new_faces_added += 1
        conn.commit()
        conn.close()
        if new_faces_added > 0:
            run_incremental_clustering()
        return jsonify({'success': True, 'new_faces_count': new_faces_added})
    except Exception as e:
        print(f'Error in deep scan: {e}')
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/photo/find_missing', methods=['POST'])
def find_missing_photo():
    data = request.json
    photo_path = data.get('path')
    search_dir = data.get('search_dir')
    if not photo_path:
        return jsonify({'error': 'Missing path'}), 400
    basename = os.path.basename(photo_path)
    found_path = None
    if search_dir and isinstance(search_dir, str) and os.path.isfile(search_dir
        ):
        found_path = search_dir
    else:
        dirs_to_search = []
        if search_dir and isinstance(search_dir, str) and os.path.isdir(
            search_dir):
            dirs_to_search.append(search_dir)
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT path FROM directories')
            for d, in cursor.fetchall():
                dirs_to_search.append(d)
            conn.close()
        for d in dirs_to_search:
            if not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                if basename in files:
                    potential_path = os.path.join(root, basename)
                    found_path = potential_path
                    break
            if found_path:
                break
    if found_path:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE photos SET path = ? WHERE path = ?', (
            found_path, photo_path))
        cursor.execute('UPDATE faces SET photo_path = ? WHERE photo_path = ?',
            (found_path, photo_path))
        conn.commit()
        conn.close()
        old_thumb = get_thumbnail_path(photo_path)
        new_thumb = get_thumbnail_path(found_path)
        if os.path.exists(old_thumb) and not os.path.exists(new_thumb):
            try:
                os.rename(old_thumb, new_thumb)
            except Exception as e:
                print('Failed to rename thumb:', e)
        return jsonify({'success': True, 'new_path': found_path})
    else:
        return jsonify({'success': False, 'error': 'not_found'})

@photos_bp.route('/api/photo/delete_record', methods=['POST'])
def delete_photo_record():
    data = request.json
    photo_path = data.get('path')
    if not photo_path:
        return jsonify({'error': 'Missing path'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    completely_delete_photo_data(cursor, photo_path)
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@photos_bp.route('/api/photo/refresh', methods=['POST'])
def refresh_single_photo():
    data = request.json
    photo_path = data.get('path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'file_missing'}), 404
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        meta = extract_metadata(photo_path)
        place = None
        if meta['latitude']:
            lat_r = round(meta['latitude'], 4)
            lon_r = round(meta['longitude'], 4)
            cursor.execute(
                'DELETE FROM geocoding_cache WHERE lat_rounded = ? AND lon_rounded = ?'
                , (lat_r, lon_r))
            conn.commit()
            place = reverse_geocode(meta['latitude'], meta['longitude'])
        cursor.execute(
            """
            UPDATE photos 
            SET date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, latitude = ?, longitude = ?, place_name = ?
            WHERE path = ?
        """
            , (meta['date_taken'], meta['width'], meta['height'], meta[
            'size'], meta['file_type'], meta['latitude'], meta['longitude'],
            place, photo_path))
        conn.commit()
        cursor.execute(
            'DELETE FROM faces WHERE photo_path = ? AND is_manual = 0', (
            photo_path,))
        conn.commit()
        cursor.execute('SELECT x, y, w, h FROM faces WHERE photo_path = ?',
            (photo_path,))
        existing_boxes = cursor.fetchall()
        processor = face_processor.FaceProcessor()
        detected_faces = processor.detect_and_extract_faces(photo_path)
        for face in detected_faces:
            bx, by, bw, bh = face['bbox']
            current_box = bx, by, bw, bh
            is_duplicate = False
            for e_box in existing_boxes:
                if compute_iou(current_box, e_box) > 0.3 or compute_iom(
                    current_box, e_box) > 0.6:
                    is_duplicate = True
                    break
            if not is_duplicate:
                emb_bytes = face['embedding'].tobytes()
                cursor.execute(
                    """
                    INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """
                    , (photo_path, bx, by, bw, bh, emb_bytes))
        conn.commit()
        conn.close()
        run_incremental_clustering()
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error refreshing photo: {e}')
        return jsonify({'error': str(e)}), 500

