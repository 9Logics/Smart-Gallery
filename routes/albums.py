from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

albums_bp = Blueprint('albums', __name__)

@albums_bp.route('/api/albums')
@cache_api(timeout=30)
def get_albums():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            a.id, 
            a.name, 
            a.cover_photo_path, 
            COUNT(CASE WHEN UPPER(p.file_type) IN ('MP4', 'MOV', 'M4V', 'HEVC', 'WEBM') THEN 1 END) as video_count,
            COUNT(CASE WHEN p.file_type IS NOT NULL AND UPPER(p.file_type) NOT IN ('MP4', 'MOV', 'M4V', 'HEVC', 'WEBM') THEN 1 END) as image_count,
            COUNT(ap.photo_path) as total_count
        FROM albums a
        LEFT JOIN album_photos ap ON a.id = ap.album_id
        LEFT JOIN photos p ON ap.photo_path = p.path AND p.trashed_at IS NULL
        GROUP BY a.id
        ORDER BY a.name ASC
    """
        )
    rows = cursor.fetchall()
    albums = []
    for r in rows:
        cover = r[2]
        if cover:
            cursor.execute('SELECT trashed_at FROM photos WHERE path = ?',
                (cover,))
            c_row = cursor.fetchone()
            if c_row and c_row[0] is not None:
                cursor.execute(
                    'SELECT ap.photo_path FROM album_photos ap JOIN photos p ON ap.photo_path = p.path WHERE ap.album_id = ? AND p.trashed_at IS NULL LIMIT 1'
                    , (r[0],))
                new_cover = cursor.fetchone()
                cover = new_cover[0] if new_cover else None
        albums.append({'id': r[0], 'name': r[1], 'cover_photo_path': cover,
            'video_count': r[3], 'image_count': r[4], 'total_count': r[5],
            'photo_count': r[5]})
    conn.close()
    return jsonify(albums)

@albums_bp.route('/api/albums/create', methods=['POST'])
def create_album():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Album name cannot be empty'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO albums (name, created_at) VALUES (?, ?)',
            (name, created_at))
        conn.commit()
        album_id = cursor.lastrowid
        success = True
        error = None
    except sqlite3.IntegrityError:
        success = False
        error = 'An album with this name already exists'
        album_id = None
    finally:
        conn.close()
    if not success:
        return jsonify({'error': error}), 400
    return jsonify({'success': True, 'album_id': album_id})

@albums_bp.route('/api/albums/add', methods=['POST'])
def add_to_album():
    data = request.json
    album_id = data.get('album_id')
    photo_paths = data.get('photos', [])
    if not album_id or not photo_paths:
        return jsonify({'error': 'Missing album_id or photos'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    for path in photo_paths:
        cursor.execute(
            'INSERT OR IGNORE INTO album_photos (album_id, photo_path) VALUES (?, ?)'
            , (album_id, path))
    cursor.execute('SELECT cover_photo_path FROM albums WHERE id = ?', (
        album_id,))
    row = cursor.fetchone()
    if row and not row[0] and photo_paths:
        cursor.execute('UPDATE albums SET cover_photo_path = ? WHERE id = ?',
            (photo_paths[0], album_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@albums_bp.route('/api/albums/remove', methods=['POST'])
def remove_from_album():
    data = request.json
    album_id = data.get('album_id')
    photo_paths = data.get('photos', [])
    if not album_id or not photo_paths:
        return jsonify({'error': 'Missing album_id or photos'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    for path in photo_paths:
        cursor.execute(
            'DELETE FROM album_photos WHERE album_id = ? AND photo_path = ?',
            (album_id, path))
    cursor.execute('SELECT cover_photo_path FROM albums WHERE id = ?', (
        album_id,))
    row = cursor.fetchone()
    if row and row[0] in photo_paths:
        cursor.execute(
            'SELECT photo_path FROM album_photos WHERE album_id = ? LIMIT 1',
            (album_id,))
        new_cover_row = cursor.fetchone()
        new_cover = new_cover_row[0] if new_cover_row else None
        cursor.execute('UPDATE albums SET cover_photo_path = ? WHERE id = ?',
            (new_cover, album_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@albums_bp.route('/api/albums/delete', methods=['POST'])
def delete_album():
    data = request.json
    album_id = data.get('album_id')
    if not album_id:
        return jsonify({'error': 'Missing album_id'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM albums WHERE id = ?', (album_id,))
    cursor.execute('DELETE FROM album_photos WHERE album_id = ?', (album_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@albums_bp.route('/api/albums/rename', methods=['POST'])
def rename_album():
    data = request.json
    album_id = data.get('album_id')
    new_name = data.get('new_name')
    if not album_id or not new_name:
        return jsonify({'error': 'Missing album_id or new_name'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE albums SET name = ? WHERE id = ?', (new_name
            .strip(), album_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'An album with that name already exists'}
            ), 400
    conn.close()
    return jsonify({'success': True})

@albums_bp.route('/api/albums/set-cover', methods=['POST'])
def set_album_cover():
    data = request.json
    album_id = data.get('album_id')
    photo_path = data.get('photo_path')
    if not album_id or not photo_path:
        return jsonify({'error': 'Missing album_id or photo_path'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE albums SET cover_photo_path = ? WHERE id = ?', (
        photo_path, album_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

