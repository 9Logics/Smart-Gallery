from flask import Blueprint, request, jsonify, send_file
from app_globals import *

albums_bp = Blueprint("albums", __name__)

@albums_bp.route('/api/albums')
@cache_api(timeout=30)
def get_albums():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
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
    """)
    rows = cursor.fetchall()
    
    albums = []
    for r in rows:
        cover = r[2]
        if cover:
            cursor.execute("SELECT trashed_at FROM photos WHERE path = ?", (cover,))
            c_row = cursor.fetchone()
            if c_row and c_row[0] is not None:
                # Cover photo is trashed! Select a non-trashed cover photo instead
                cursor.execute("SELECT ap.photo_path FROM album_photos ap JOIN photos p ON ap.photo_path = p.path WHERE ap.album_id = ? AND p.trashed_at IS NULL LIMIT 1", (r[0],))
                new_cover = cursor.fetchone()
                cover = new_cover[0] if new_cover else None
                
        albums.append({
            "id": r[0],
            "name": r[1],
            "cover_photo_path": cover,
            "video_count": r[3],
            "image_count": r[4],
            "total_count": r[5],
            "photo_count": r[5] # keep for backwards compatibility if needed
        })
    conn.close()
    return jsonify(albums)


@albums_bp.route('/api/albums/create', methods=['POST'])
def create_album():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "Album name cannot be empty"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO albums (name, created_at) VALUES (?, ?)", (name, created_at))
        conn.commit()
        album_id = cursor.lastrowid
        success = True
        error = None
    except sqlite3.IntegrityError:
        success = False
        error = "An album with this name already exists"
        album_id = None
    finally:
        conn.close()
        
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "album_id": album_id})


@albums_bp.route('/api/albums/add', methods=['POST'])
def add_to_album():
    data = request.json
    album_id = data.get('album_id')
    photo_paths = data.get('photos', [])
    
    if not album_id or not photo_paths:
        return jsonify({"error": "Missing album_id or photos"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert mappings
    for path in photo_paths:
        cursor.execute("INSERT OR IGNORE INTO album_photos (album_id, photo_path) VALUES (?, ?)", (album_id, path))
        
    # Update cover image for album if not set
    cursor.execute("SELECT cover_photo_path FROM albums WHERE id = ?", (album_id,))
    row = cursor.fetchone()
    if row and not row[0] and photo_paths:
        cursor.execute("UPDATE albums SET cover_photo_path = ? WHERE id = ?", (photo_paths[0], album_id))
        
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@albums_bp.route('/api/albums/remove', methods=['POST'])
def remove_from_album():
    data = request.json
    album_id = data.get('album_id')
    photo_paths = data.get('photos', [])
    
    if not album_id or not photo_paths:
        return jsonify({"error": "Missing album_id or photos"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        cursor.execute("DELETE FROM album_photos WHERE album_id = ? AND photo_path = ?", (album_id, path))
        
    # If the removed photo was the cover, pick another cover photo
    cursor.execute("SELECT cover_photo_path FROM albums WHERE id = ?", (album_id,))
    row = cursor.fetchone()
    if row and row[0] in photo_paths:
        cursor.execute("SELECT photo_path FROM album_photos WHERE album_id = ? LIMIT 1", (album_id,))
        new_cover_row = cursor.fetchone()
        new_cover = new_cover_row[0] if new_cover_row else None
        cursor.execute("UPDATE albums SET cover_photo_path = ? WHERE id = ?", (new_cover, album_id))
        
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@albums_bp.route('/api/albums/delete', methods=['POST'])
def delete_album():
    data = request.json
    album_id = data.get('album_id')
    if not album_id:
        return jsonify({"error": "Missing album_id"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM albums WHERE id = ?", (album_id,))
    cursor.execute("DELETE FROM album_photos WHERE album_id = ?", (album_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@albums_bp.route('/api/albums/rename', methods=['POST'])
def rename_album():
    data = request.json
    album_id = data.get('album_id')
    new_name = data.get('new_name')
    if not album_id or not new_name:
        return jsonify({"error": "Missing album_id or new_name"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE albums SET name = ? WHERE id = ?", (new_name.strip(), album_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "An album with that name already exists"}), 400
    conn.close()
    return jsonify({"success": True})


@albums_bp.route('/api/albums/set-cover', methods=['POST'])
def set_album_cover():
    data = request.json
    album_id = data.get('album_id')
    photo_path = data.get('photo_path')
    if not album_id or not photo_path:
        return jsonify({"error": "Missing album_id or photo_path"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE albums SET cover_photo_path = ? WHERE id = ?", (photo_path, album_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

def analyze_filename(filename):
    name_without_ext, ext = os.path.splitext(filename)
    pattern = r'(\s*\(\d+\)|\s*-\s*Copy(\s*\(\d+\))?)+$'
    if re.search(pattern, name_without_ext, re.IGNORECASE):
        clean_name = re.sub(pattern, '', name_without_ext, flags=re.IGNORECASE)
        return clean_name + ext, True
    return filename, False

def get_metadata_score(photo_row):
    date_taken = photo_row[2]
    latitude = photo_row[7]
    longitude = photo_row[8]
    place_name = photo_row[9]
    score = 0
    if date_taken:
        score += 1
    if latitude is not None and longitude is not None:
        score += 2
    if place_name:
        score += 1
    return score


