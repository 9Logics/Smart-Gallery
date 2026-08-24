from scene_classifier import check_scene
import os
import shutil
import sys
import sqlite3
import json
import hashlib
import threading
import time
import urllib.request
from io import BytesIO
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
from PIL import Image, ImageOps
import numpy as np
import re
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print(
        '[WARNING] pillow-heif is not installed; HEIC/HEIF files will not be supported.'
        )
import face_processor
app = Flask(__name__, template_folder='templates', static_folder='static')
from functools import wraps
import time
from flask import Response
API_CACHE = {}


def get_cache_key():
    from flask import request
    return request.path + '?' + request.query_string.decode('utf-8')


def cache_api(timeout=60):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = get_cache_key()
            cached = API_CACHE.get(key)
            if cached and time.time() - cached[0] < timeout:
                return Response(cached[1], mimetype=cached[2])
            resp = f(*args, **kwargs)
            if resp.status_code == 200:
                API_CACHE[key] = time.time(), resp.get_data(), resp.mimetype
            return resp
        return decorated_function
    return decorator


def clear_cache():
    API_CACHE.clear()


@app.after_request
def auto_clear_cache(response):
    from flask import request
    if request.method in ['POST', 'PUT', 'DELETE']:
        clear_cache()
    return response


@app.errorhandler(sqlite3.OperationalError)
def handle_sqlite_error(e):
    if 'database is locked' in str(e).lower():
        reason = 'Database is locked because of an active scan.'
        if scan_status.get('status') == 'scanning':
            phase = scan_status.get('phase', 'Processing')
            current = scan_status.get('current_file', '')
            reason = (
                f"Database is locked by scanner: {phase}. Currently on: {current} ({scan_status.get('processed', 0)}/{scan_status.get('total', 0)}). Please wait a few moments and try again."
                )
        return jsonify({'success': False, 'error': reason}), 423
    return jsonify({'success': False, 'error': str(e)}), 500


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, '.cache')
THUMBNAILS_DIR = os.path.join(CACHE_DIR, 'thumbnails')
FACES_DIR = os.path.join(CACHE_DIR, 'faces')
TRASH_DIR = os.path.join(CACHE_DIR, 'trash')
DB_PATH = os.path.join(CACHE_DIR, 'gallery.db')
import difflib


def sqlite_fuzzy_match(query, target):
    if not target or not query:
        return 0
    q = str(query).lower()
    t = str(target).lower()
    if q in t:
        return 1
    it = iter(t)
    if all(c in it for c in q.replace(' ', '')):
        return 1
    return 1 if difflib.SequenceMatcher(None, q, t).ratio() > 0.65 else 0


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.create_function('fuzzy_match', 2, sqlite_fuzzy_match)
    return conn


os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(TRASH_DIR, exist_ok=True)


def completely_delete_photo_data(cursor, photo_path):
    cursor.execute('SELECT id FROM faces WHERE photo_path = ?', (photo_path,))
    face_ids = [r[0] for r in cursor.fetchall()]
    for fid in face_ids:
        face_path = os.path.join(FACES_DIR, f'{fid}.jpg')
        if os.path.exists(face_path):
            try:
                os.remove(face_path)
            except:
                pass
    thumb_path = get_thumbnail_path(photo_path)
    if os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except:
            pass
    cursor.execute('DELETE FROM photos WHERE path = ?', (photo_path,))


scan_lock = threading.Lock()
scan_status = {'status': 'idle', 'processed': 0, 'total': 0, 'current_file':
    '', 'phase': '', 'cancel_requested': False}
geocode_lock = threading.Lock()
last_geocode_time = 0


def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """
        )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS photos (
        path TEXT PRIMARY KEY,
        filename TEXT,
        date_taken TEXT,
        width INTEGER,
        height INTEGER,
        size INTEGER,
        file_type TEXT,
        latitude REAL,
        longitude REAL,
        place_name TEXT,
        hash TEXT,
        trashed_at TEXT,
        archived_at TEXT,
        is_favorite INTEGER DEFAULT 0,
        camera_make TEXT,
        camera_model TEXT,
        f_stop REAL,
        exposure_time TEXT,
        focal_length REAL,
        iso INTEGER,
        duration REAL,
        fps REAL,
        video_codec TEXT
    )
    """
        )
    try:
        cursor.execute('ALTER TABLE photos ADD COLUMN iso INTEGER')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE photos ADD COLUMN duration REAL')
        cursor.execute('ALTER TABLE photos ADD COLUMN fps REAL')
        cursor.execute('ALTER TABLE photos ADD COLUMN video_codec TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE photos ADD COLUMN archived_at TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute(
            'ALTER TABLE photos ADD COLUMN is_favorite INTEGER DEFAULT 0')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_path TEXT,
        x INTEGER,
        y INTEGER,
        w INTEGER,
        h INTEGER,
        embedding BLOB,
        person_id INTEGER,
        FOREIGN KEY(photo_path) REFERENCES photos(path) ON DELETE CASCADE,
        FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE SET NULL
    )
    """
        )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cover_face_id INTEGER
    )
    """
        )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        cover_photo_path TEXT,
        created_at TEXT
    )
    """
        )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS album_photos (
        album_id INTEGER,
        photo_path TEXT,
        PRIMARY KEY(album_id, photo_path),
        FOREIGN KEY(album_id) REFERENCES albums(id) ON DELETE CASCADE,
        FOREIGN KEY(photo_path) REFERENCES photos(path) ON DELETE CASCADE
    )
    """
        )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS geocoding_cache (
        lat_rounded REAL,
        lon_rounded REAL,
        place_name TEXT,
        PRIMARY KEY(lat_rounded, lon_rounded)
    )
    """
        )
    try:
        cursor.execute('ALTER TABLE photos ADD COLUMN trashed_at TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute(
            'ALTER TABLE faces ADD COLUMN is_manual INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_faces_photo_path ON faces(photo_path)')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_faces_person_id ON faces(person_id)')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_photos_trashed_at ON photos(trashed_at)'
        )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_photos_archived_at ON photos(archived_at)'
        )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_photos_date_taken ON photos(date_taken)'
        )
    conn.commit()
    conn.close()
    threading.Thread(target=migrate_database, daemon=True).start()


def migrate_database():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM photos WHERE hash IS NULL OR hash = ''")
    rows = cursor.fetchall()
    if rows:
        total = len(rows)
        print(f'Migrating {total} photos to compute visual hashes...')
        for i, row in enumerate(rows):
            path = row[0]
            if os.path.exists(path):
                dhash = calculate_dhash(path)
                cursor.execute('UPDATE photos SET hash = ? WHERE path = ?',
                    (dhash, path))
            if (i + 1) % 10 == 0:
                conn.commit()
                time.sleep(0.02)
            if (i + 1) % 100 == 0:
                print(
                    f'Migrating hashes: {i + 1}/{total} ({(i + 1) * 100 // total}%)'
                    )
        conn.commit()
        print('Hash migration complete!')
    conn.close()


def cleanup_expired_trash():
    conn = get_db_connection()
    cursor = conn.cursor()
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime(
        '%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'SELECT path FROM photos WHERE trashed_at IS NOT NULL AND trashed_at < ?'
        , (thirty_days_ago,))
    expired_paths = [r[0] for r in cursor.fetchall()]
    if expired_paths:
        print(f'Purging {len(expired_paths)} expired Recycle Bin files...')
        for p in expired_paths:
            file_hash = hashlib.md5(p.encode('utf-8')).hexdigest()
            ext = os.path.splitext(p)[1]
            trash_path = os.path.join(TRASH_DIR, file_hash + ext)
            try:
                if os.path.exists(trash_path):
                    os.remove(trash_path)
                thumb = get_thumbnail_path(p)
                if os.path.exists(thumb):
                    os.remove(thumb)
                cursor.execute('DELETE FROM photos WHERE path = ?', (p,))
            except Exception as e:
                print(f'Error purging expired trash file {p}: {e}')
        conn.commit()
    conn.close()


def get_decimal_from_dms(dms, ref):
    if not dms or not ref:
        return None
    try:
        d = float(dms[0])
        m = float(dms[1])
        s = float(dms[2])
        decimal = d + m / 60.0 + s / 3600.0
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return None


def calculate_dhash(photo_path):
    try:
        ext = os.path.splitext(photo_path)[1].lower()
        is_video = ext in ['.mp4', '.mov', '.m4v', '.hevc']
        target_path = photo_path
        if is_video:
            target_path = get_thumbnail_path(photo_path)
            if not os.path.exists(target_path):
                generate_video_thumbnail(photo_path, target_path)
        if not os.path.exists(target_path):
            return ''
        with Image.open(target_path) as img:
            img_gray = img.convert('L').resize((9, 8), Image.Resampling.
                BILINEAR)
            pixels = list(img_gray.getdata())
            diff = []
            for row in range(8):
                for col in range(8):
                    pixel_left = pixels[row * 9 + col]
                    pixel_right = pixels[row * 9 + col + 1]
                    diff.append(pixel_left > pixel_right)
            decimal_value = 0
            hex_string = []
            for index, value in enumerate(diff):
                if value:
                    decimal_value += 2 ** (index % 8)
                if index % 8 == 7:
                    hex_string.append(hex(decimal_value)[2:].zfill(2))
                    decimal_value = 0
            return ''.join(hex_string)
    except Exception as e:
        print(f'Error computing dhash for {photo_path}: {e}')
        return ''


def extract_metadata(photo_path):
    ext = os.path.splitext(photo_path)[1].lower()
    is_video = ext in ['.mp4', '.mov', '.m4v', '.hevc']
    metadata = {'date_taken': None, 'width': 0, 'height': 0, 'size': os.
        path.getsize(photo_path), 'file_type': ext[1:].upper(), 'latitude':
        None, 'longitude': None, 'place_name': None, 'hash': '',
        'camera_make': None, 'camera_model': None, 'f_stop': None,
        'exposure_time': None, 'focal_length': None, 'iso': None,
        'duration': None, 'fps': None, 'video_codec': None}
    if is_video:
        thumb_path = get_thumbnail_path(photo_path)
        generate_video_thumbnail(photo_path, thumb_path)
        metadata['hash'] = calculate_dhash(thumb_path)
        try:
            import cv2
            cap = cv2.VideoCapture(photo_path)
            if cap.isOpened():
                vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps and fps > 0:
                    metadata['fps'] = round(fps, 2)
                    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    if frames and frames > 0:
                        metadata['duration'] = round(frames / fps, 2)
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                if fourcc:
                    codec = ''.join([chr(fourcc >> 8 * i & 255) for i in
                        range(4)]).strip()
                    metadata['video_codec'] = codec.upper() if codec else None
                if os.path.exists(thumb_path):
                    with Image.open(thumb_path) as img:
                        tw, th = img.size
                        if th > tw and vw > vh or tw > th and vh > vw:
                            metadata['width'] = vh
                            metadata['height'] = vw
                        else:
                            metadata['width'] = vw
                            metadata['height'] = vh
                else:
                    metadata['width'] = vw
                    metadata['height'] = vh
            cap.release()
        except Exception as e:
            print(f'Error reading video dimensions for {photo_path}: {e}')
        try:
            size = os.path.getsize(photo_path)
            chunk_size = min(size, 2048 * 1024)
            with open(photo_path, 'rb') as f:
                data = f.read(chunk_size)
                if size > chunk_size:
                    f.seek(size - chunk_size)
                    data += f.read(chunk_size)
            idx = data.find(b'\xa9xyz')
            if idx == -1:
                idx = data.find(b'\xc2\xa9xyz')
            if idx != -1:
                start = idx + 4
                if data[idx:idx + 5] == b'\xc2\xa9xyz':
                    start = idx + 5
                block = data[start:start + 50].decode('utf-8', errors='ignore')
                match = re.search('([+-]\\d+\\.\\d+)([+-]\\d+\\.\\d+)', block)
                if match:
                    lat = float(match.group(1))
                    lon = float(match.group(2))
                    metadata['latitude'] = lat
                    metadata['longitude'] = lon
                    print(
                        f'Successfully extracted video GPS coordinates from container for {photo_path}: {lat}, {lon}'
                        )
        except Exception as e:
            print(
                f'Error parsing GPS coordinates from video container {photo_path}: {e}'
                )
    else:
        metadata['hash'] = calculate_dhash(photo_path)
        try:
            with Image.open(photo_path) as img:
                metadata['width'], metadata['height'] = img.size
                exif = None
                try:
                    if hasattr(img, 'getexif'):
                        exif = img.getexif()
                    elif hasattr(img, '_getexif'):
                        exif = img._getexif()
                except Exception as exif_err:
                    print(f'Error calling getexif on {photo_path}: {exif_err}')
                if exif:
                    for tag, value in exif.items():
                        if tag in [36867, 36868, 306]:
                            try:
                                dt = datetime.strptime(str(value).strip(),
                                    '%Y:%m:%d %H:%M:%S')
                                metadata['date_taken'] = dt.strftime(
                                    '%Y-%m-%d %H:%M:%S')
                                break
                            except Exception:
                                pass
                    try:
                        gps_info = None
                        if hasattr(exif, 'get_ifd'):
                            try:
                                gps_info = exif.get_ifd(34853)
                            except Exception:
                                pass
                        if not gps_info:
                            gps_info = exif.get(34853)
                        if gps_info and isinstance(gps_info, dict):
                            lat_dms = gps_info.get(2)
                            lat_ref = gps_info.get(1)
                            lon_dms = gps_info.get(4)
                            lon_ref = gps_info.get(3)
                            lat = get_decimal_from_dms(lat_dms, lat_ref)
                            lon = get_decimal_from_dms(lon_dms, lon_ref)
                            if lat is not None and lon is not None:
                                metadata['latitude'] = lat
                                metadata['longitude'] = lon
                    except Exception as gps_err:
                        print(
                            f'Error reading GPS details from EXIF for {photo_path}: {gps_err}'
                            )
                    try:
                        metadata['camera_make'] = str(exif.get(271)).strip(
                            ) if exif.get(271) else None
                        metadata['camera_model'] = str(exif.get(272)).strip(
                            ) if exif.get(272) else None
                        exif_ifd = None
                        if hasattr(exif, 'get_ifd'):
                            try:
                                exif_ifd = exif.get_ifd(34665)
                            except Exception:
                                pass
                        if exif_ifd and isinstance(exif_ifd, dict):
                            f_val = exif_ifd.get(33437)
                            if f_val is not None:
                                metadata['f_stop'] = round(float(f_val), 1)
                            exp_val = exif_ifd.get(33434)
                            if exp_val is not None:
                                if hasattr(exp_val, 'numerator') and hasattr(
                                    exp_val, 'denominator'
                                    ) and exp_val.denominator > 0:
                                    if exp_val.numerator == 1:
                                        metadata['exposure_time'
                                            ] = f'1/{exp_val.denominator}'
                                    else:
                                        metadata['exposure_time'] = str(round(
                                            float(exp_val), 3))
                                else:
                                    metadata['exposure_time'] = str(exp_val)
                            foc_val = exif_ifd.get(37386)
                            if foc_val is not None:
                                metadata['focal_length'] = round(float(
                                    foc_val), 1)
                            iso_val = exif_ifd.get(34855)
                            if iso_val is not None:
                                metadata['iso'] = int(iso_val) if isinstance(
                                    iso_val, (int, float)) else None
                    except Exception as cam_err:
                        print(
                            f'Error reading Camera details from EXIF for {photo_path}: {cam_err}'
                            )
        except Exception as img_err:
            print(f'Error opening image file {photo_path}: {img_err}')
    if not metadata['date_taken']:
        try:
            ctime = os.path.getctime(photo_path)
            mtime = os.path.getmtime(photo_path)
            oldest_time = min(ctime, mtime)
            dt = datetime.fromtimestamp(oldest_time)
            metadata['date_taken'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            try:
                mtime = os.path.getmtime(photo_path)
                dt = datetime.fromtimestamp(mtime)
                metadata['date_taken'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                metadata['date_taken'] = datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')
    return metadata


def extract_smart_location(data):
    addr = data.get('address', {})
    valid_keys = ['amenity', 'building', 'shop', 'office', 'historic',
        'tourism', 'leisure', 'aeroway', 'neighbourhood', 'suburb',
        'village', 'hamlet', 'town', 'city_district', 'borough', 'city',
        'county', 'state_district', 'state', 'country']
    for k in valid_keys:
        if k in addr:
            return addr[k]
    if 'road' in addr and 'highway' not in addr['road'].lower():
        return addr['road']
    return data.get('display_name', '').split(',')[0]


def reverse_geocode(lat, lon):
    global last_geocode_time
    lat_r = round(lat, 3)
    lon_r = round(lon, 3)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT place_name FROM geocoding_cache WHERE lat_rounded = ? AND lon_rounded = ?'
        , (lat_r, lon_r))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            data = json.loads(row[0])
            return extract_smart_location(data)
        except:
            return row[0]
    elapsed = time.time() - last_geocode_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    place_name = None
    try:
        url = (
            f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'
            )
        req = urllib.request.Request(url, headers={'User-Agent':
            'LocalSmartGalleryApp/1.0 (contact@anurag.dev)'})
        last_geocode_time = time.time()
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            place_name = json.dumps(data)
        if place_name:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO geocoding_cache (lat_rounded, lon_rounded, place_name) VALUES (?, ?, ?)'
                , (lat_r, lon_r, place_name))
            conn.commit()
            conn.close()
            return extract_smart_location(data)
    except Exception as e:
        print(f'Online reverse geocoding failed: {e}')
    return None


def update_smart_location_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.path, c.place_name 
        FROM photos p
        JOIN geocoding_cache c 
          ON round(p.latitude, 3) = c.lat_rounded AND round(p.longitude, 3) = c.lon_rounded
        WHERE p.latitude IS NOT NULL AND c.place_name LIKE '{%'
    """
        )
    rows = cursor.fetchall()
    for path, json_str in rows:
        try:
            data = json.loads(json_str)
            smart_tag = extract_smart_location(data)
            if smart_tag:
                cursor.execute(
                    'UPDATE photos SET place_name = ? WHERE path = ?', (
                    smart_tag, path))
        except Exception:
            continue
    conn.commit()
    conn.close()


def get_thumbnail_path(photo_path):
    h = hashlib.md5(photo_path.encode('utf-8')).hexdigest()
    return os.path.join(THUMBNAILS_DIR, h + '.webp')


def generate_thumbnail(photo_path, thumb_path):
    try:
        with Image.open(photo_path) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail((360, 360))
            img.save(thumb_path, 'WEBP', quality=80)
            return True
    except Exception as e:
        print(f'Failed to generate thumbnail for {photo_path}: {e}')
        return False


def generate_video_thumbnail(video_path, thumb_path):
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        target_frame = min(max(10, int(frame_count * 0.1)), frame_count - 1
            ) if frame_count > 10 else 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()
        if ret and frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((360, 360))
            img.save(thumb_path, 'WEBP', quality=80)
            return True
    except Exception as e:
        print(f'Error thumbnailing video {video_path}: {e}')
    return False


def run_incremental_clustering():
    """Matches new faces to named centroids and clusters the remainder using DBSCAN."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, f.embedding 
        FROM faces f 
        JOIN people p ON f.person_id = p.id
        WHERE f.embedding IS NOT NULL
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
    cursor.execute(
        'SELECT id, embedding FROM faces WHERE person_id IS NULL AND embedding IS NOT NULL AND (is_manual != -1 OR is_manual IS NULL)'
        )
    unassigned_rows = cursor.fetchall()
    if not unassigned_rows:
        conn.close()
        return
    unassigned_faces = []
    unassigned_embeddings = []
    for f_id, emb_blob in unassigned_rows:
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        unassigned_faces.append(f_id)
        unassigned_embeddings.append(emb)
    still_unassigned_ids = []
    still_unassigned_embeddings = []
    for f_id, emb in zip(unassigned_faces, unassigned_embeddings):
        best_person_id = None
        best_dist = 1.0
        for p_id, centroid in centroids.items():
            dist = face_processor.compute_cosine_distance(emb, centroid)
            if dist < best_dist:
                best_dist = dist
                best_person_id = p_id
        if best_dist < 0.45 and best_person_id is not None:
            cursor.execute('UPDATE faces SET person_id = ? WHERE id = ?', (
                best_person_id, f_id))
        else:
            still_unassigned_ids.append(f_id)
            still_unassigned_embeddings.append(emb)
    if still_unassigned_embeddings:
        labels = face_processor.dbscan_clustering(still_unassigned_embeddings,
            eps=0.45, min_samples=2)
        cursor.execute("SELECT name FROM people WHERE name LIKE 'Person %'")
        existing_nums = []
        for r in cursor.fetchall():
            try:
                num = int(r[0].replace('Person ', ''))
                existing_nums.append(num)
            except ValueError:
                pass
        next_person_num = max(existing_nums) + 1 if existing_nums else 1
        cluster_to_person = {}
        for f_id, label in zip(still_unassigned_ids, labels):
            if label == -1:
                continue
            if label not in cluster_to_person:
                cursor.execute('INSERT INTO people (name) VALUES (?)', (
                    f'Person {next_person_num}',))
                p_id = cursor.lastrowid
                cluster_to_person[label] = p_id
                next_person_num += 1
            p_id = cluster_to_person[label]
            cursor.execute('UPDATE faces SET person_id = ? WHERE id = ?', (
                p_id, f_id))
    cursor.execute('SELECT id FROM people WHERE cover_face_id IS NULL')
    people_without_covers = [r[0] for r in cursor.fetchall()]
    for p_id in people_without_covers:
        cursor.execute('SELECT id FROM faces WHERE person_id = ? LIMIT 1',
            (p_id,))
        face_row = cursor.fetchone()
        if face_row:
            cursor.execute('UPDATE people SET cover_face_id = ? WHERE id = ?',
                (face_row[0], p_id))
    conn.commit()
    conn.close()


def scan_directory(root_dir):
    global scan_status
    print(f'Starting phased scan of: {root_dir}')
    supported_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp',
        '.heic', '.heif', '.tiff', '.tif', '.mp4', '.mov', '.m4v', '.hevc')
    file_list = []
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
                ext = file.lower()
                if ext.endswith(supported_extensions):
                    file_list.append(os.path.join(root, file))
                elif ext == '.lnk' and shell:
                    try:
                        shortcut = shell.CreateShortCut(os.path.join(root,
                            file))
                        if os.path.isdir(shortcut.Targetpath):
                            roots_to_scan.append(shortcut.Targetpath)
                    except Exception:
                        pass
    video_exts = '.mp4', '.mov', '.m4v', '.hevc'
    file_list.sort(key=lambda x: 1 if x.lower().endswith(video_exts) else 0)
    total_files = len(file_list)
    print(f'Found {total_files} files to check.')
    conn = get_db_connection()
    cursor = conn.cursor()
    new_files = []
    for path in file_list:
        cursor.execute('SELECT path FROM photos WHERE path = ?', (path,))
        if not cursor.fetchone():
            new_files.append(path)
    if new_files:
        scan_status['phase'] = 'Phase 1/3: Rapid Metadata Discovery'
        scan_status['total'] = len(new_files)
        scan_status['processed'] = 0
        for idx, path in enumerate(new_files):
            with scan_lock:
                if scan_status.get('cancel_requested'):
                    break
            scan_status['processed'] = idx + 1
            scan_status['current_file'] = os.path.basename(path)
            meta = extract_metadata(path)
            filename = os.path.basename(path)
            cursor.execute(
                """
                INSERT OR REPLACE INTO photos 
                (path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash, trashed_at, camera_make, camera_model, f_stop, exposure_time, focal_length, iso, duration, fps, video_codec)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
                , (path, filename, meta['date_taken'], meta['width'], meta[
                'height'], meta['size'], meta['file_type'], meta['latitude'
                ], meta['longitude'], meta['camera_make'], meta[
                'camera_model'], meta['f_stop'], meta['exposure_time'],
                meta['focal_length'], meta['iso'], meta['duration'], meta[
                'fps'], meta['video_codec']))
            if idx % 10 == 0:
                conn.commit()
        conn.commit()
    cursor.execute(
        'SELECT path, latitude, longitude, place_name FROM photos WHERE trashed_at IS NULL'
        )
    all_indexed_photos = cursor.fetchall()
    thumbnail_todo = []
    for row in all_indexed_photos:
        path = row[0]
        thumb_path = get_thumbnail_path(path)
        if not os.path.exists(thumb_path):
            thumbnail_todo.append(row)
    geocoding_todo = [row for row in all_indexed_photos if row[1] is not
        None and row[2] is not None and row[3] is None]
    phase2_total = len(thumbnail_todo) + len(geocoding_todo)
    if phase2_total > 0:
        scan_status['phase'] = 'Phase 2/3: Thumbnail & Location Processing'
        scan_status['total'] = phase2_total
        scan_status['processed'] = 0
        processed_count = 0
        for row in thumbnail_todo:
            path = row[0]
            processed_count += 1
            scan_status['processed'] = processed_count
            scan_status['current_file'
                ] = f'Thumbnail: {os.path.basename(path)}'
            thumb_path = get_thumbnail_path(path)
            is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            try:
                if is_video:
                    generate_video_thumbnail(path, thumb_path)
                else:
                    generate_thumbnail(path, thumb_path)
            except Exception as e:
                print(f'Error generating thumbnail for {path}: {e}')
        for row in geocoding_todo:
            path, lat, lon, _ = row
            processed_count += 1
            scan_status['processed'] = processed_count
            scan_status['current_file'
                ] = f'Geocoding: {os.path.basename(path)}'
            try:
                place_name = reverse_geocode(lat, lon)
                if place_name:
                    cursor.execute(
                        'UPDATE photos SET place_name = ? WHERE path = ?',
                        (place_name, path))
            except Exception as e:
                print(f'Error reverse geocoding for {path}: {e}')
            if processed_count % 5 == 0:
                conn.commit()
        conn.commit()
    cursor.execute(
        'SELECT path, file_type FROM photos WHERE hash IS NULL AND trashed_at IS NULL'
        )
    ai_todo = cursor.fetchall()
    if ai_todo:
        scan_status['phase'] = 'Phase 3/3: AI Faces & Duplicates Scan'
        scan_status['total'] = len(ai_todo)
        scan_status['processed'] = 0
        processor = None
        try:
            processor = face_processor.FaceProcessor()
        except Exception as e:
            print(f'Error initializing face detector: {e}')
        for idx, (path, file_type) in enumerate(ai_todo):
            scan_status['processed'] = idx + 1
            scan_status['current_file'
                ] = f'AI Analysis: {os.path.basename(path)}'
            meta = extract_metadata(path)
            dhash = meta.get('hash')
            cursor.execute('UPDATE photos SET hash = ? WHERE path = ?', (
                dhash, path))
            if processor:
                thumb_path = get_thumbnail_path(path)
                is_video = path.lower().endswith(('.mp4', '.mov', '.m4v',
                    '.hevc'))
                detect_path = path
                if os.path.exists(detect_path):
                    try:
                        faces = processor.detect_and_extract_faces(detect_path,
                            min_confidence=0.8)
                        for face in faces:
                            bbox = face['bbox']
                            emb_bytes = face['embedding'].tobytes()
                            cursor.execute(
                                """
                                INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id)
                                VALUES (?, ?, ?, ?, ?, ?, NULL)
                            """
                                , (path, bbox[0], bbox[1], bbox[2], bbox[3],
                                emb_bytes))
                    except Exception as e:
                        print(f'Error extracting faces for {path}: {e}')
            if idx % 10 == 0:
                conn.commit()
        conn.commit()
        print('Running incremental face clustering...')
        try:
            run_incremental_clustering()
        except Exception as e:
            print(f'Error in face clustering: {e}')
        try:
            update_smart_location_tags()
        except Exception as e:
            print(f'Failed to update smart location tags: {e}')
    conn.close()
    print('Scan completed successfully.')
    scan_status['status'] = 'idle'
    scan_status['phase'] = ''


def start_scan_thread(root_dir):
    global scan_status
    with scan_lock:
        if scan_status['status'] == 'scanning':
            return False
        scan_status['status'] = 'scanning'
        scan_status['cancel_requested'] = False
        scan_status['processed'] = 0
        scan_status['total'] = 0
        scan_status['current_file'] = ''
    thread = threading.Thread(target=scan_directory, args=(root_dir,))
    thread.daemon = True
    thread.start()
    return True


def parse_smart_dates(query):
    query = query.lower().strip()
    results = []
    if re.match('^\\d{4}$', query):
        results.append({'year': query})
    months = ['january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december']
    if query.isalpha():
        for i, m in enumerate(months):
            if m.startswith(query):
                results.append({'month': f'{i + 1:02d}'})
    if results:
        return results
    day_month_regex = re.match('^(\\d{1,2})(?:st|nd|rd|th)?\\s*([a-z]+)$',
        query)
    month_day_regex = re.match('^([a-z]+)\\s*(\\d{1,2})(?:st|nd|rd|th)?$',
        query)
    d_str = None
    m_str = None
    if day_month_regex:
        d_str, m_str = day_month_regex.groups()
    elif month_day_regex:
        m_str, d_str = month_day_regex.groups()
    if d_str and m_str:
        d = f'{int(d_str):02d}'
        for i, m in enumerate(months):
            if m.startswith(m_str):
                results.append({'month': f'{i + 1:02d}', 'day': d})
    if results:
        return results
    date_match = re.match('^(\\d{2})[-/.](\\d{2})[-/.](\\d{4})$', query)
    if date_match:
        p1, p2, p3 = date_match.groups()
        results.append({'year': p3, 'month': p2, 'day': p1})
    date_match_rev = re.match('^(\\d{4})[-/.](\\d{2})[-/.](\\d{2})$', query)
    if date_match_rev:
        p1, p2, p3 = date_match_rev.groups()
        results.append({'year': p1, 'month': p2, 'day': p3})
    cond_match = re.match('^(\\d{2})(\\d{2})(\\d{2})$', query)
    if cond_match:
        d, m, y = cond_match.groups()
        results.append({'year': '20' + y, 'month': m, 'day': d})
    if re.match('^\\d{1,2}$', query) or re.match('^\\d{1,2}(?:st|nd|rd|th)$',
        query):
        d = re.sub('\\D', '', query)
        results.append({'day': f'{int(d):02d}'})
    return results


def build_date_sql(parsed_date, table_alias='p'):
    if not parsed_date:
        return None, []
    conds = []
    params = []
    if 'year' in parsed_date:
        conds.append(f"strftime('%Y', {table_alias}.date_taken) = ?")
        params.append(parsed_date['year'])
    if 'month' in parsed_date:
        conds.append(f"strftime('%m', {table_alias}.date_taken) = ?")
        params.append(parsed_date['month'])
    if 'day' in parsed_date:
        conds.append(f"strftime('%d', {table_alias}.date_taken) = ?")
        params.append(parsed_date['day'])
    if conds:
        return ' AND '.join(conds), params
    return None, []


import json
OVERRIDES_CACHE_FILE = os.path.join(CACHE_DIR, 'hero_overrides.json')


def load_hero_overrides():
    if os.path.exists(OVERRIDES_CACHE_FILE):
        try:
            with open(OVERRIDES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {'whitelist': [], 'blacklist': []}
    return {'whitelist': [], 'blacklist': []}


def save_hero_overrides(data):
    with open(OVERRIDES_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def save_date_to_file_and_system(photo_path, new_date_str):
    if not new_date_str:
        return
    try:
        dt_file = datetime.strptime(new_date_str.strip(), '%Y-%m-%d %H:%M:%S')
    except Exception as parse_err:
        print(
            f'Error parsing date {new_date_str} for system update: {parse_err}'
            )
        return
    ext = os.path.splitext(photo_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.heic', '.heif']:
        try:
            exif_date_str = dt_file.strftime('%Y:%m:%d %H:%M:%S')
            with Image.open(photo_path) as img:
                fmt = img.format
                exif = img.getexif()
                exif[36867] = exif_date_str
                exif[36868] = exif_date_str
                exif[306] = exif_date_str
                if fmt == 'HEIF' or ext in ['.heic', '.heif']:
                    img.save(photo_path, format='HEIF', exif=exif, quality=95)
                elif fmt == 'JPEG' or ext in ['.jpg', '.jpeg']:
                    img.save(photo_path, format='JPEG', exif=exif, quality=
                        95, subsampling=0)
                else:
                    img.save(photo_path, exif=exif)
            print(f'Direct EXIF tags successfully written to {photo_path}')
        except Exception as exif_err:
            print(f'Direct EXIF save failed on {photo_path}: {exif_err}')
    try:
        import ctypes
        from ctypes import wintypes
        filetime_val = int((dt_file.timestamp() + 11644473600) * 10000000)


        class FILETIME(ctypes.Structure):
            _fields_ = [('dwLowDateTime', wintypes.DWORD), (
                'dwHighDateTime', wintypes.DWORD)]
        ft = FILETIME(filetime_val & 4294967295, filetime_val >> 32)
        handle = ctypes.windll.kernel32.CreateFileW(photo_path, 1073741824,
            1 | 2, None, 3, 33554432 | 128, None)
        if handle != -1 and handle != 18446744073709551615:
            success = ctypes.windll.kernel32.SetFileTime(handle, ctypes.
                byref(ft), ctypes.byref(ft), ctypes.byref(ft))
            ctypes.windll.kernel32.CloseHandle(handle)
            if not success:
                raise Exception('SetFileTime returned 0 (failure)')
            print(
                f'Windows system file dates successfully updated to match {new_date_str}'
                )
        else:
            raise Exception('CreateFileW returned INVALID_HANDLE_VALUE')
    except Exception as fs_err:
        print(f'Windows native timestamp update failed: {fs_err}')
        try:
            timestamp = dt_file.timestamp()
            os.utime(photo_path, (timestamp, timestamp))
        except Exception:
            pass


def analyze_filename(filename):
    name_without_ext, ext = os.path.splitext(filename)
    pattern = '(\\s*\\(\\d+\\)|\\s*-\\s*Copy(\\s*\\(\\d+\\))?)+$'
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


def send_file_to_trash(path):
    """
    Tags a file for deletion by returning success.
    The actual physical file is not moved until the user purges it.
    Returns: (success_bool, original_path, error_str_or_None)
    """
    if not os.path.exists(path):
        return False, None, 'File does not exist on disk'
    try:
        return True, path, None
    except Exception as e:
        print(f'Error trashing file {path}: {e}')
        return False, None, str(e)


def compute_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    ixA = max(x1, x2)
    iyA = max(y1, y2)
    ixB = min(x1 + w1, x2 + w2)
    iyB = min(y1 + h1, y2 + h2)
    inter_area = max(0, ixB - ixA) * max(0, iyB - iyA)
    box1_area = w1 * h1
    box2_area = w2 * h2
    denominator = float(box1_area + box2_area - inter_area)
    return inter_area / denominator if denominator > 0 else 0


def compute_iom(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    ixA = max(x1, x2)
    iyA = max(y1, y2)
    ixB = min(x1 + w1, x2 + w2)
    iyB = min(y1 + h1, y2 + h2)
    inter_area = max(0, ixB - ixA) * max(0, iyB - iyA)
    box1_area = w1 * h1
    box2_area = w2 * h2
    min_area = min(box1_area, box2_area)
    return inter_area / min_area if min_area > 0 else 0
