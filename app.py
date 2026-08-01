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
    print("[WARNING] pillow-heif is not installed; HEIC/HEIF files will not be supported.")

# Import face recognition module
import face_processor

app = Flask(__name__, template_folder='templates', static_folder='static')


from functools import wraps
import time
from flask import Response

API_CACHE = {}

def get_cache_key():
    from flask import request
    return request.path + "?" + request.query_string.decode('utf-8')

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
                API_CACHE[key] = (time.time(), resp.get_data(), resp.mimetype)
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
    if "database is locked" in str(e).lower():
        reason = "Database is locked because of an active scan."
        if scan_status.get("status") == "scanning":
            phase = scan_status.get("phase", "Processing")
            current = scan_status.get("current_file", "")
            reason = f"Database is locked by scanner: {phase}. Currently on: {current} ({scan_status.get('processed', 0)}/{scan_status.get('total', 0)}). Please wait a few moments and try again."
            
        return jsonify({
            "success": False, 
            "error": reason
        }), 423 # 423 Locked
    return jsonify({"success": False, "error": str(e)}), 500

# Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, ".cache")
THUMBNAILS_DIR = os.path.join(CACHE_DIR, "thumbnails")
FACES_DIR = os.path.join(CACHE_DIR, "faces")
TRASH_DIR = os.path.join(CACHE_DIR, "trash")
DB_PATH = os.path.join(CACHE_DIR, "gallery.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(TRASH_DIR, exist_ok=True)

def completely_delete_photo_data(cursor, photo_path):
    # 1. Fetch face IDs to delete physical thumbnails
    cursor.execute("SELECT id FROM faces WHERE photo_path = ?", (photo_path,))
    face_ids = [r[0] for r in cursor.fetchall()]
    
    # 2. Delete physical face thumbnails
    for fid in face_ids:
        face_path = os.path.join(FACES_DIR, f"{fid}.jpg")
        if os.path.exists(face_path):
            try:
                os.remove(face_path)
            except:
                pass
                
    # 3. Delete photo thumbnail
    thumb_path = get_thumbnail_path(photo_path)
    if os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except:
            pass
            
    # 4. Delete photo from DB (cascades to faces and album_photos if foreign_keys = ON)
    cursor.execute("DELETE FROM photos WHERE path = ?", (photo_path,))

# Scan state
scan_lock = threading.Lock()
scan_status = {
    "status": "idle", # 'idle', 'scanning'
    "processed": 0,
    "total": 0,
    "current_file": "",
    "phase": ""
}

# Geocoding rate limiter lock
geocode_lock = threading.Lock()
last_geocode_time = 0

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    
    # settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # photos
    cursor.execute("""
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
        archived_at TEXT
    )
    """)
    try:
        cursor.execute("ALTER TABLE photos ADD COLUMN archived_at TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE photos ADD COLUMN is_favorite INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    # faces
    cursor.execute("""
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
    """)
    
    # people
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cover_face_id INTEGER
    )
    """)
    
    # albums
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        cover_photo_path TEXT,
        created_at TEXT
    )
    """)
    
    # album_photos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS album_photos (
        album_id INTEGER,
        photo_path TEXT,
        PRIMARY KEY(album_id, photo_path),
        FOREIGN KEY(album_id) REFERENCES albums(id) ON DELETE CASCADE,
        FOREIGN KEY(photo_path) REFERENCES photos(path) ON DELETE CASCADE
    )
    """)
    
    # geocoding_cache
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS geocoding_cache (
        lat_rounded REAL,
        lon_rounded REAL,
        place_name TEXT,
        PRIMARY KEY(lat_rounded, lon_rounded)
    )
    """)
    
    # Ensure column is added to older databases
    try:
        cursor.execute("ALTER TABLE photos ADD COLUMN trashed_at TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE faces ADD COLUMN is_manual INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
        
    # Performance Optimization Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_faces_photo_path ON faces(photo_path)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_faces_person_id ON faces(person_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photos_trashed_at ON photos(trashed_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photos_archived_at ON photos(archived_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photos_date_taken ON photos(date_taken)")
        
    conn.commit()
    conn.close()
    
    # Run database migration to ensure all files have visual dhashes in the background
    threading.Thread(target=migrate_database, daemon=True).start()

def migrate_database():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM photos WHERE hash IS NULL OR hash = ''")
    rows = cursor.fetchall()
    
    if rows:
        total = len(rows)
        print(f"Migrating {total} photos to compute visual hashes...")
        for i, row in enumerate(rows):
            path = row[0]
            if os.path.exists(path):
                dhash = calculate_dhash(path)
                cursor.execute("UPDATE photos SET hash = ? WHERE path = ?", (dhash, path))
            
            if (i + 1) % 10 == 0:
                conn.commit()
                time.sleep(0.02) # Yield database lock control
                
            if (i + 1) % 100 == 0:
                print(f"Migrating hashes: {i + 1}/{total} ({(i + 1) * 100 // total}%)")
        conn.commit()
        print("Hash migration complete!")
    conn.close()

def cleanup_expired_trash():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT path FROM photos WHERE trashed_at IS NOT NULL AND trashed_at < ?", (thirty_days_ago,))
    expired_paths = [r[0] for r in cursor.fetchall()]
    
    if expired_paths:
        print(f"Purging {len(expired_paths)} expired Recycle Bin files...")
        for p in expired_paths:
            file_hash = hashlib.md5(p.encode('utf-8')).hexdigest()
            ext = os.path.splitext(p)[1]
            trash_path = os.path.join(TRASH_DIR, file_hash + ext)
            
            try:
                # Remove file from trash folder
                if os.path.exists(trash_path):
                    os.remove(trash_path)
                # Remove thumbnail
                thumb = get_thumbnail_path(p)
                if os.path.exists(thumb):
                    os.remove(thumb)
                # Remove database records completely
                cursor.execute("DELETE FROM photos WHERE path = ?", (p,))
            except Exception as e:
                print(f"Error purging expired trash file {p}: {e}")
                
        conn.commit()
    conn.close()

# EXIF Helpers
def get_decimal_from_dms(dms, ref):
    if not dms or not ref:
        return None
    try:
        # Convert fractions to floats
        d = float(dms[0])
        m = float(dms[1])
        s = float(dms[2])
        decimal = d + (m / 60.0) + (s / 3600.0)
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
            return ""
            
        with Image.open(target_path) as img:
            # Resize to 9x8, convert to grayscale
            img_gray = img.convert('L').resize((9, 8), Image.Resampling.BILINEAR)
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
                if (index % 8) == 7:
                    hex_string.append(hex(decimal_value)[2:].zfill(2))
                    decimal_value = 0
            return "".join(hex_string)
    except Exception as e:
        print(f"Error computing dhash for {photo_path}: {e}")
        return ""

def extract_metadata(photo_path):
    ext = os.path.splitext(photo_path)[1].lower()
    is_video = ext in ['.mp4', '.mov', '.m4v', '.hevc']
    
    metadata = {
        "date_taken": None,
        "width": 0,
        "height": 0,
        "size": os.path.getsize(photo_path),
        "file_type": ext[1:].upper(),
        "latitude": None,
        "longitude": None,
        "place_name": None,
        "hash": "",
        "camera_make": None,
        "camera_model": None,
        "f_stop": None,
        "exposure_time": None,
        "focal_length": None,
        "iso": None
    }
    
    if is_video:
        # Generate video thumbnail first because we need it to calculate visual dhash
        thumb_path = get_thumbnail_path(photo_path)
        generate_video_thumbnail(photo_path, thumb_path)
        metadata["hash"] = calculate_dhash(thumb_path)
        
        # Extract video dimensions
        try:
            import cv2
            cap = cv2.VideoCapture(photo_path)
            if cap.isOpened():
                vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Check generated thumbnail to see if OpenCV auto-rotated the frame
                if os.path.exists(thumb_path):
                    with Image.open(thumb_path) as img:
                        tw, th = img.size
                        # If thumbnail is tall but video stream is wide (or vice versa), swap dimensions
                        if (th > tw and vw > vh) or (tw > th and vh > vw):
                            metadata["width"] = vh
                            metadata["height"] = vw
                        else:
                            metadata["width"] = vw
                            metadata["height"] = vh
                else:
                    metadata["width"] = vw
                    metadata["height"] = vh
            cap.release()
        except Exception as e:
            print(f"Error reading video dimensions for {photo_path}: {e}")
            
        # Extract GPS coordinates from video container atoms (e.g. ©xyz atom)
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
                if data[idx:idx+5] == b'\xc2\xa9xyz':
                    start = idx + 5
                block = data[start:start+50].decode('utf-8', errors='ignore')
                match = re.search(r'([+-]\d+\.\d+)([+-]\d+\.\d+)', block)
                if match:
                    lat = float(match.group(1))
                    lon = float(match.group(2))
                    metadata["latitude"] = lat
                    metadata["longitude"] = lon
                    print(f"Successfully extracted video GPS coordinates from container for {photo_path}: {lat}, {lon}")
        except Exception as e:
            print(f"Error parsing GPS coordinates from video container {photo_path}: {e}")
    else:
        # Calculate visual dhash for duplicate detection on image files
        metadata["hash"] = calculate_dhash(photo_path)
        
        try:
            with Image.open(photo_path) as img:
                metadata["width"], metadata["height"] = img.size
                
                exif = None
                try:
                    if hasattr(img, 'getexif'):
                        exif = img.getexif()
                    elif hasattr(img, '_getexif'):
                        exif = img._getexif()
                except Exception as exif_err:
                    print(f"Error calling getexif on {photo_path}: {exif_err}")
                
                if exif:
                    # 1. Date Taken Extraction
                    for tag, value in exif.items():
                        # 36867 = DateTimeOriginal, 36868 = DateTimeDigitized, 306 = DateTime
                        if tag in [36867, 36868, 306]:
                            try:
                                dt = datetime.strptime(str(value).strip(), "%Y:%m:%d %H:%M:%S")
                                metadata["date_taken"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                                break
                            except Exception:
                                pass
                    
                    # 2. GPS Location Extraction (tag 34853)
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
                            lat_dms = gps_info.get(2) # GPSLatitude
                            lat_ref = gps_info.get(1) # GPSLatitudeRef
                            lon_dms = gps_info.get(4) # GPSLongitude
                            lon_ref = gps_info.get(3) # GPSLongitudeRef
                            
                            lat = get_decimal_from_dms(lat_dms, lat_ref)
                            lon = get_decimal_from_dms(lon_dms, lon_ref)
                            if lat is not None and lon is not None:
                                metadata["latitude"] = lat
                                metadata["longitude"] = lon
                    except Exception as gps_err:
                        print(f"Error reading GPS details from EXIF for {photo_path}: {gps_err}")
                                
                    # 3. Camera details extraction
                    try:
                        metadata["camera_make"] = str(exif.get(271)).strip() if exif.get(271) else None
                        metadata["camera_model"] = str(exif.get(272)).strip() if exif.get(272) else None
                        
                        exif_ifd = None
                        if hasattr(exif, 'get_ifd'):
                            try:
                                exif_ifd = exif.get_ifd(34665)
                            except Exception:
                                pass
                        
                        if exif_ifd and isinstance(exif_ifd, dict):
                            # F-stop (33437)
                            f_val = exif_ifd.get(33437)
                            if f_val is not None:
                                metadata["f_stop"] = round(float(f_val), 1)
                                
                            # Exposure Time (33434)
                            exp_val = exif_ifd.get(33434)
                            if exp_val is not None:
                                if hasattr(exp_val, 'numerator') and hasattr(exp_val, 'denominator') and exp_val.denominator > 0:
                                    if exp_val.numerator == 1:
                                        metadata["exposure_time"] = f"1/{exp_val.denominator}"
                                    else:
                                        metadata["exposure_time"] = str(round(float(exp_val), 3))
                                else:
                                    metadata["exposure_time"] = str(exp_val)
                                    
                            # Focal Length (37386)
                            foc_val = exif_ifd.get(37386)
                            if foc_val is not None:
                                metadata["focal_length"] = round(float(foc_val), 1)
                                
                            # ISO (34855)
                            iso_val = exif_ifd.get(34855)
                            if iso_val is not None:
                                metadata["iso"] = int(iso_val) if isinstance(iso_val, (int, float)) else None
                    except Exception as cam_err:
                        print(f"Error reading Camera details from EXIF for {photo_path}: {cam_err}")
                        
        except Exception as img_err:
            print(f"Error opening image file {photo_path}: {img_err}")
            
    # Fallback date to file creation/modification time if EXIF is missing
    if not metadata["date_taken"]:
        try:
            ctime = os.path.getctime(photo_path)
            mtime = os.path.getmtime(photo_path)
            oldest_time = min(ctime, mtime)
            dt = datetime.fromtimestamp(oldest_time)
            metadata["date_taken"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                mtime = os.path.getmtime(photo_path)
                dt = datetime.fromtimestamp(mtime)
                metadata["date_taken"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                metadata["date_taken"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    return metadata

def reverse_geocode(lat, lon):
    """Performs reverse geocoding with local cache using OpenStreetMap Nominatim."""
    if lat is None or lon is None:
        return None
    
    lat_r = round(lat, 3)
    lon_r = round(lon, 3)
    
    # Check cache
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT place_name FROM geocoding_cache WHERE lat_rounded = ? AND lon_rounded = ?", (lat_r, lon_r))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        try:
            return json.loads(row[0]).get("display_name")
        except Exception:
            return row[0]
        
    # Online check (rate limited to 1 req/sec)
    global last_geocode_time
    with geocode_lock:
        elapsed = time.time() - last_geocode_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        
        place_name = None
        try:
            # Call OpenStreetMap Nominatim with building-level zoom
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'LocalSmartGalleryApp/1.0 (contact@anurag.dev)'}
            )
            last_geocode_time = time.time()
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                place_name = json.dumps(data) # Store full JSON for smart tagging
            
            if place_name:
                # Cache result
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO geocoding_cache (lat_rounded, lon_rounded, place_name) VALUES (?, ?, ?)",
                               (lat_r, lon_r, place_name))
                conn.commit()
                conn.close()
                return data.get("display_name")
        except Exception as e:
            print(f"Online reverse geocoding failed: {e}")
            
        return None
def update_smart_location_tags(threshold=3):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.path, c.place_name 
        FROM photos p
        JOIN geocoding_cache c 
          ON round(p.latitude, 3) = c.lat_rounded AND round(p.longitude, 3) = c.lon_rounded
        WHERE p.latitude IS NOT NULL AND c.place_name LIKE '{%'
    """)
    rows = cursor.fetchall()
    
    valid_keys = [
        'amenity', 'building', 'shop', 'office', 'historic', 'tourism', 'leisure', 'aeroway',
        'neighbourhood', 'suburb', 'village', 'hamlet', 'town', 'city_district', 'borough',
        'city', 'county', 'state_district', 'state', 'country'
    ]
    
    photo_hierarchies = {}
    tag_frequencies = {}
    
    for path, json_str in rows:
        try:
            data = json.loads(json_str)
            addr = data.get('address', {})
            hierarchy = []
            for k in valid_keys:
                if k in addr:
                    tag = addr[k]
                    if tag not in hierarchy:
                        hierarchy.append(tag)
                        
            photo_hierarchies[path] = hierarchy
            
            for tag in hierarchy:
                tag_frequencies[tag] = tag_frequencies.get(tag, 0) + 1
        except Exception:
            continue
            
    for path, hierarchy in photo_hierarchies.items():
        chosen_tag = None
        for tag in hierarchy:
            if tag_frequencies.get(tag, 0) >= threshold:
                chosen_tag = tag
                break
                
        if not chosen_tag and hierarchy:
            chosen_tag = hierarchy[0]
            
        if chosen_tag:
            cursor.execute("UPDATE photos SET place_name = ? WHERE path = ?", (chosen_tag, path))
            
    conn.commit()
    conn.close()


def get_thumbnail_path(photo_path):
    h = hashlib.md5(photo_path.encode('utf-8')).hexdigest()
    return os.path.join(THUMBNAILS_DIR, h + ".webp")

def generate_thumbnail(photo_path, thumb_path):
    try:
        with Image.open(photo_path) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail((360, 360))
            img.save(thumb_path, "WEBP", quality=80)
            return True
    except Exception as e:
        print(f"Failed to generate thumbnail for {photo_path}: {e}")
        return False

def generate_video_thumbnail(video_path, thumb_path):
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        target_frame = min(max(10, int(frame_count * 0.1)), frame_count - 1) if frame_count > 10 else 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((360, 360))
            img.save(thumb_path, "WEBP", quality=80)
            return True
    except Exception as e:
        print(f"Error thumbnailing video {video_path}: {e}")
    return False

# Clustering logic
def run_incremental_clustering():
    """Matches new faces to named centroids and clusters the remainder using DBSCAN."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Load named centroids
    cursor.execute("""
        SELECT p.id, f.embedding 
        FROM faces f 
        JOIN people p ON f.person_id = p.id
        WHERE f.embedding IS NOT NULL
    """)
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
        
    # 2. Get unassigned faces
    cursor.execute("SELECT id, embedding FROM faces WHERE person_id IS NULL AND embedding IS NOT NULL AND (is_manual != -1 OR is_manual IS NULL)")
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
        
    # 3. Match against centroids first (threshold: 0.38 cosine distance)
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
            cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (best_person_id, f_id))
        else:
            still_unassigned_ids.append(f_id)
            still_unassigned_embeddings.append(emb)
            
    # 4. Run DBSCAN on the remaining faces
    if still_unassigned_embeddings:
        labels = face_processor.dbscan_clustering(still_unassigned_embeddings, eps=0.45, min_samples=2)
        
        # Determine the next available 'Person N' index
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
                # Create a new unnamed person sequentially
                cursor.execute("INSERT INTO people (name) VALUES (?)", (f"Person {next_person_num}",))
                p_id = cursor.lastrowid
                cluster_to_person[label] = p_id
                next_person_num += 1
                
            p_id = cluster_to_person[label]
            cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (p_id, f_id))
            
    # 5. Set cover face IDs for people who don't have one
    cursor.execute("SELECT id FROM people WHERE cover_face_id IS NULL")
    people_without_covers = [r[0] for r in cursor.fetchall()]
    for p_id in people_without_covers:
        cursor.execute("SELECT id FROM faces WHERE person_id = ? LIMIT 1", (p_id,))
        face_row = cursor.fetchone()
        if face_row:
            cursor.execute("UPDATE people SET cover_face_id = ? WHERE id = ?", (face_row[0], p_id))
            
    conn.commit()
    conn.close()

# Scanning Engine
def scan_directory(root_dir):
    global scan_status
    print(f"Starting phased scan of: {root_dir}")
    
    # 1. Collect files
    supported_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic', '.heif', '.tiff', '.tif', '.mp4', '.mov', '.m4v', '.hevc')
    file_list = []
    
    roots_to_scan = [root_dir]
    scanned_roots = set()
    
    shell = None
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
    except ImportError:
        pass
        
    while roots_to_scan:
        current_root = roots_to_scan.pop(0)
        
        real_root = os.path.realpath(current_root)
        if real_root in scanned_roots:
            continue
        scanned_roots.add(real_root)
        
        for root, dirs, files in os.walk(current_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                ext = file.lower()
                if ext.endswith(supported_extensions):
                    file_list.append(os.path.join(root, file))
                elif ext == '.lnk' and shell:
                    try:
                        shortcut = shell.CreateShortCut(os.path.join(root, file))
                        if os.path.isdir(shortcut.Targetpath):
                            roots_to_scan.append(shortcut.Targetpath)
                    except Exception:
                        pass
                        
    # Sort files to prioritize images (faster processing) over videos
    video_exts = ('.mp4', '.mov', '.m4v', '.hevc')
    file_list.sort(key=lambda x: 1 if x.lower().endswith(video_exts) else 0)
                
    total_files = len(file_list)
    print(f"Found {total_files} files to check.")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_files = []
    for path in file_list:
        cursor.execute("SELECT path FROM photos WHERE path = ?", (path,))
        if not cursor.fetchone():
            new_files.append(path)
            
    # PHASE 1: Fast Metadata Indexing (Timeline pop)
    if new_files:
        scan_status["phase"] = "Phase 1/3: Rapid Metadata Discovery"
        scan_status["total"] = len(new_files)
        scan_status["processed"] = 0
        
        for idx, path in enumerate(new_files):
            scan_status["processed"] = idx + 1
            scan_status["current_file"] = os.path.basename(path)
            
            # Fast EXIF extract
            meta = extract_metadata(path)
            filename = os.path.basename(path)
            
            # Insert photo with NULL hash and NULL place_name (filled in later phases)
            cursor.execute("""
                INSERT OR REPLACE INTO photos 
                (path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash, trashed_at, camera_make, camera_model, f_stop, exposure_time, focal_length, iso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?, ?, ?)
            """, (path, filename, meta["date_taken"], meta["width"], meta["height"], meta["size"], meta["file_type"], 
                  meta["latitude"], meta["longitude"], meta["camera_make"], meta["camera_model"], meta["f_stop"], meta["exposure_time"], meta["focal_length"], meta["iso"]))
            
            # Commit periodically to show up in timeline asap
            if idx % 10 == 0:
                conn.commit()
        conn.commit()
    
    # PHASE 2: Thumbnail & Location Processing (Visuals and Places)
    cursor.execute("SELECT path, latitude, longitude, place_name FROM photos WHERE trashed_at IS NULL")
    all_indexed_photos = cursor.fetchall()
    
    thumbnail_todo = []
    for row in all_indexed_photos:
        path = row[0]
        thumb_path = get_thumbnail_path(path)
        if not os.path.exists(thumb_path):
            thumbnail_todo.append(row)
            
    # Geocoding todo (has coordinates but no place_name)
    geocoding_todo = [row for row in all_indexed_photos if row[1] is not None and row[2] is not None and row[3] is None]
    
    phase2_total = len(thumbnail_todo) + len(geocoding_todo)
    if phase2_total > 0:
        scan_status["phase"] = "Phase 2/3: Thumbnail & Location Processing"
        scan_status["total"] = phase2_total
        scan_status["processed"] = 0
        
        processed_count = 0
        # 1. Process thumbnails
        for row in thumbnail_todo:
            path = row[0]
            processed_count += 1
            scan_status["processed"] = processed_count
            scan_status["current_file"] = f"Thumbnail: {os.path.basename(path)}"
            
            thumb_path = get_thumbnail_path(path)
            is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            try:
                if is_video:
                    generate_video_thumbnail(path, thumb_path)
                else:
                    generate_thumbnail(path, thumb_path)
            except Exception as e:
                print(f"Error generating thumbnail for {path}: {e}")
                
        # 2. Process geocoding
        for row in geocoding_todo:
            path, lat, lon, _ = row
            processed_count += 1
            scan_status["processed"] = processed_count
            scan_status["current_file"] = f"Geocoding: {os.path.basename(path)}"
            
            try:
                place_name = reverse_geocode(lat, lon)
                if place_name:
                    cursor.execute("UPDATE photos SET place_name = ? WHERE path = ?", (place_name, path))
            except Exception as e:
                print(f"Error reverse geocoding for {path}: {e}")
                
            if processed_count % 5 == 0:
                conn.commit()
        conn.commit()
        
    # PHASE 3: AI Feature Extraction (Faces & Duplicates)
    cursor.execute("SELECT path, file_type FROM photos WHERE hash IS NULL AND trashed_at IS NULL")
    ai_todo = cursor.fetchall()
    
    if ai_todo:
        scan_status["phase"] = "Phase 3/3: AI Faces & Duplicates Scan"
        scan_status["total"] = len(ai_todo)
        scan_status["processed"] = 0
        
        processor = None
        try:
            processor = face_processor.FaceProcessor()
        except Exception as e:
            print(f"Error initializing face detector: {e}")
            
        for idx, (path, file_type) in enumerate(ai_todo):
            scan_status["processed"] = idx + 1
            scan_status["current_file"] = f"AI Analysis: {os.path.basename(path)}"
            
            # Compute visual hash
            meta = extract_metadata(path)
            dhash = meta.get("hash")
            
            cursor.execute("UPDATE photos SET hash = ? WHERE path = ?", (dhash, path))
            
            # Extract faces (confidence threshold set to 0.5 for better recall!)
            if processor:
                thumb_path = get_thumbnail_path(path)
                is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
                detect_path = path
                
                if os.path.exists(detect_path):
                    try:
                        faces = processor.detect_and_extract_faces(detect_path, min_confidence=0.80)
                        for face in faces:
                            bbox = face["bbox"]
                            emb_bytes = face["embedding"].tobytes()
                            cursor.execute("""
                                INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id)
                                VALUES (?, ?, ?, ?, ?, ?, NULL)
                            """, (path, bbox[0], bbox[1], bbox[2], bbox[3], emb_bytes))
                    except Exception as e:
                        print(f"Error extracting faces for {path}: {e}")
                        
            if idx % 10 == 0:
                conn.commit()
        conn.commit()
        
        # Run face clustering
        print("Running incremental face clustering...")
        try:
            run_incremental_clustering()
        except Exception as e:
            print(f"Error in face clustering: {e}")
            
        # Phase 4: Compute and update smart location tags using the entire dataset
        try:
            update_smart_location_tags()
        except Exception as e:
            print(f"Failed to update smart location tags: {e}")
            
    conn.close()
    print("Scan completed successfully.")
    scan_status["status"] = "idle"
    scan_status["phase"] = ""

def start_scan_thread(root_dir):
    global scan_status
    with scan_lock:
        if scan_status["status"] == "scanning":
            return False
        scan_status["status"] = "scanning"
        scan_status["processed"] = 0
        scan_status["total"] = 0
        
    thread = threading.Thread(target=scan_directory, args=(root_dir,))
    thread.daemon = True
    thread.start()
    return True

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan/status')
def get_scan_status():
    return jsonify(scan_status)

@app.route('/api/settings/scan-folder', methods=['POST'])
def save_scan_folder():
    data = request.json
    folder = data.get('folder', '').strip()
    if not folder or not os.path.exists(folder):
        return jsonify({"error": "Invalid folder path or folder does not exist"}), 400
        
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('scan_folder', ?)", (folder,))
    conn.commit()
    conn.close()
    
    # Trigger scanning
    started = start_scan_thread(folder)
    return jsonify({"success": True, "started": started})

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json or {}
        for k, v in data.items():
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    else:
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        conn.close()
        settings_dict = {r[0]: r[1] for r in rows}
        if "scan_folder" not in settings_dict:
            settings_dict["scan_folder"] = ""
        if "google_maps_key" not in settings_dict:
            settings_dict["google_maps_key"] = ""
        return jsonify(settings_dict)

def parse_smart_dates(query):
    query = query.lower().strip()
    results = []
    
    # 1. Year: exactly 4 digits
    if re.match(r'^\d{4}$', query):
        results.append({"year": query})
        
    # 2. Month name prefix
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    if query.isalpha():
        for i, m in enumerate(months):
            if m.startswith(query):
                results.append({"month": f"{i+1:02d}"})
                
    if results:
        return results
            
    # 3. Day + Month (e.g. 25th august, august 25, 10a, a 10)
    day_month_regex = re.match(r'^(\d{1,2})(?:st|nd|rd|th)?\s*([a-z]+)$', query)
    month_day_regex = re.match(r'^([a-z]+)\s*(\d{1,2})(?:st|nd|rd|th)?$', query)
    
    d_str = None
    m_str = None
    
    if day_month_regex:
        d_str, m_str = day_month_regex.groups()
    elif month_day_regex:
        m_str, d_str = month_day_regex.groups()
        
    if d_str and m_str:
        d = f"{int(d_str):02d}"
        for i, m in enumerate(months):
            if m.startswith(m_str):
                results.append({"month": f"{i+1:02d}", "day": d})
                
    if results:
        return results

    # 4. DD-MM-YYYY or MM-DD-YYYY or YYYY-MM-DD
    date_match = re.match(r'^(\d{2})[-/.](\d{2})[-/.](\d{4})$', query)
    if date_match:
        p1, p2, p3 = date_match.groups()
        # assume DD-MM-YYYY
        results.append({"year": p3, "month": p2, "day": p1})
        
    date_match_rev = re.match(r'^(\d{4})[-/.](\d{2})[-/.](\d{2})$', query)
    if date_match_rev:
        p1, p2, p3 = date_match_rev.groups()
        results.append({"year": p1, "month": p2, "day": p3})

    # 5. Condensed format like 121024 or 12-01-2004 without hyphens
    cond_match = re.match(r'^(\d{2})(\d{2})(\d{2})$', query)
    if cond_match:
        d, m, y = cond_match.groups()
        # Assume 2000s for two digit year
        results.append({"year": "20" + y, "month": m, "day": d})

    # 6. Single 1-2 digit number -> Day
    if re.match(r'^\d{1,2}$', query) or re.match(r'^\d{1,2}(?:st|nd|rd|th)$', query):
        d = re.sub(r'\D', '', query)
        results.append({"day": f"{int(d):02d}"})
        
    return results

def build_date_sql(parsed_date, table_alias="p"):
    if not parsed_date:
        return None, []
    
    conds = []
    params = []
    if "year" in parsed_date:
        conds.append(f"strftime('%Y', {table_alias}.date_taken) = ?")
        params.append(parsed_date["year"])
    if "month" in parsed_date:
        conds.append(f"strftime('%m', {table_alias}.date_taken) = ?")
        params.append(parsed_date["month"])
    if "day" in parsed_date:
        conds.append(f"strftime('%d', {table_alias}.date_taken) = ?")
        params.append(parsed_date["day"])
        
    if conds:
        return " AND ".join(conds), params
    return None, []

@app.route('/api/search/suggestions')
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
            # Check if any photos exist for this parsed date
            cond_sql, cond_params = build_date_sql(parsed, "photos")
            if cond_sql:
                cursor.execute(f"SELECT COUNT(*) FROM photos WHERE {cond_sql} AND trashed_at IS NULL", cond_params)
                count = cursor.fetchone()[0]
                if count > 0:
                    # Format a nice readable string
                    parts = []
                    if "day" in parsed: parts.append(str(int(parsed["day"])))
                    if "month" in parsed: 
                        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                        parts.append(months[int(parsed["month"])-1])
                    if "year" in parsed: parts.append(parsed["year"])
                    
                    label = " ".join(parts)
                    suggestions.append({
                        "type": "date",
                        "id": label, # We pass the expanded label as ID so clicking it sends the unambiguous label
                        "label": label,
                        "description": f"Date Filter ({count} photos)"
                    })
        conn.close()
        
    return jsonify(suggestions)

@app.route('/api/photos')
@cache_api(timeout=30)
def get_photos():
    # Fetch parameters
    people_filter = request.args.get('people') # comma-separated IDs
    places_filter = request.args.get('places') # comma-separated names
    albums_filter = request.args.get('albums') # comma-separated IDs
    type_filter = request.args.get('types') # comma-separated file types
    search_query = request.args.get('search', '').strip()
    date_query = request.args.get('date_query', '').strip()
    sort_by = request.args.get('sort', 'date_desc') # date_desc, date_asc, size_desc, size_asc, type_asc
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT p.path, p.filename, p.date_taken, p.width, p.height, p.size, p.file_type, p.latitude, p.longitude, p.place_name, p.archived_at, p.is_favorite, p.camera_make, p.camera_model, p.f_stop, p.exposure_time, p.focal_length, p.iso FROM photos p"
    joins = []
    where_clauses = []
    params = []
    
    # Filter trashed / archived / favorites
    show_trashed = request.args.get('trashed') == 'true'
    show_archived = request.args.get('archived') == 'true'
    show_favorites = request.args.get('favorites') == 'true'
    
    if show_trashed:
        where_clauses.append("p.trashed_at IS NOT NULL")
    else:
        where_clauses.append("p.trashed_at IS NULL")
        if show_archived:
            where_clauses.append("p.archived_at IS NOT NULL")
        elif not albums_filter and not show_favorites:
            where_clauses.append("p.archived_at IS NULL")
    
    if show_favorites:
        where_clauses.append("p.is_favorite = 1")
    
    # 1. Stackable People Filter
    if people_filter:
        people_ids = [int(x) for x in people_filter.split(',') if x.isdigit()]
        if people_ids:
            for i, p_id in enumerate(people_ids):
                alias = f"f{i}"
                joins.append(f"JOIN faces {alias} ON p.path = {alias}.photo_path AND {alias}.person_id = ?")
                params.append(p_id)
                
    # 2. Stackable Albums Filter
    if albums_filter:
        album_ids = [int(x) for x in albums_filter.split(',') if x.isdigit()]
        if album_ids:
            for i, a_id in enumerate(album_ids):
                alias = f"ap{i}"
                joins.append(f"JOIN album_photos {alias} ON p.path = {alias}.photo_path AND {alias}.album_id = ?")
                params.append(a_id)
                
    # 3. Stackable Places Filter
    if places_filter:
        places_list = [x.strip() for x in places_filter.split(',') if x.strip()]
        if places_list:
            place_or_clauses = []
            for place in places_list:
                place_or_clauses.append("p.place_name LIKE ?")
                params.append(f"%{place}%")
            where_clauses.append(f"({ ' OR '.join(place_or_clauses) })")
            
    # 4. File Type Filter
    if type_filter:
        types_list = [x.strip().upper() for x in type_filter.split(',') if x.strip()]
        if types_list:
            placeholders = ','.join(['?'] * len(types_list))
            where_clauses.append(f"p.file_type IN ({placeholders})")
            params.extend(types_list)
            
    # 4.5 Date Filter (from smart search)
    if date_query:
        date_queries = [x.strip() for x in date_query.split(',') if x.strip()]
        date_or_clauses = []
        date_params = []
        for dq in date_queries:
            parsed_dates = parse_smart_dates(dq)
            if parsed_dates:
                # Taking the first match because date suggestions send the exact resolved label (e.g. "August")
                cond_sql, cond_params = build_date_sql(parsed_dates[0], "p")
                if cond_sql:
                    date_or_clauses.append(f"({cond_sql})")
                    date_params.extend(cond_params)
                    
        if date_or_clauses:
            where_clauses.append(f"({ ' OR '.join(date_or_clauses) })")
            params.extend(date_params)
            
    # 5. Search Bar Query (People names, Place names, Filenames, Dates)
    if search_query:
        search_terms = search_query.split()
        for term in search_terms:
            term_param = f"%{term}%"
            # Search matches filename, place, date, or person name
            where_clauses.append("""
                (p.filename LIKE ? OR p.place_name LIKE ? OR p.date_taken LIKE ? OR p.path IN (
                    SELECT f.photo_path FROM faces f JOIN people pe ON f.person_id = pe.id WHERE pe.name LIKE ?
                ))
            """)
            params.extend([term_param, term_param, term_param, term_param])
            
    # Assemble Query
    if joins:
        query += " " + " ".join(joins)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    # Sorting
    if sort_by == 'date_desc':
        query += " ORDER BY p.date_taken DESC"
    elif sort_by == 'date_asc':
        query += " ORDER BY p.date_taken ASC"
    elif sort_by == 'size_desc':
        query += " ORDER BY p.size DESC"
    elif sort_by == 'size_asc':
        query += " ORDER BY p.size ASC"
    elif sort_by == 'type_asc':
        query += " ORDER BY p.file_type ASC, p.date_taken DESC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    photos = []
    for r in rows:
        photos.append({
            "path": r[0],
            "filename": r[1],
            "date_taken": r[2],
            "width": r[3],
            "height": r[4],
            "size": r[5],
            "file_type": r[6],
            "latitude": r[7],
            "longitude": r[8],
            "place_name": r[9],
            "archived_at": r[10],
            "is_favorite": bool(r[11]) if r[11] else False,
            "camera_make": r[12],
            "camera_model": r[13],
            "f_stop": r[14],
            "exposure_time": r[15],
            "focal_length": r[16],
            "iso": r[17]
        })
        
    return jsonify(photos)

@app.route('/api/photo/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"error": "Missing path"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM photos WHERE path = ?", (path,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Photo not found"}), 404
    new_val = 0 if row[0] else 1
    cursor.execute("UPDATE photos SET is_favorite = ? WHERE path = ?", (new_val, path))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "is_favorite": bool(new_val)})

# Serve original image files (restricted to scanned directories for security)
@app.route('/api/photo/file/<path:photo_path>')
def serve_photo_file(photo_path):
    # Standardize path slashes (Windows specific)
    photo_path = os.path.normpath(photo_path)
    
    # Check settings for scanned folder limit
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Not authorized", 403
        
    scan_folder = os.path.normpath(row[0])
    
    # Security: Ensure path is within scan_folder
    # Adding a trailing separator is a robust way to prevent directory traversal
    if not photo_path.startswith(scan_folder):
        return "Access denied", 403
        
    if not os.path.exists(photo_path):
        return "File not found", 404
        
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
            print(f"Error converting unsupported image format on the fly: {e}")
            return serve_photo_thumbnail(photo_path)
            
    return send_file(photo_path)

@app.route('/api/photo/thumbnail/<path:photo_path>')
def serve_photo_thumbnail(photo_path):
    thumb_path = get_thumbnail_path(photo_path)
    if not os.path.exists(thumb_path):
        # Generate on the fly if missing
        is_video = photo_path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
        if is_video:
            success = generate_video_thumbnail(photo_path, thumb_path)
        else:
            success = generate_thumbnail(photo_path, thumb_path)
            
        if not success:
            # Thumbnail generation failed, return an error rather than infinitely looping
            return "Thumbnail generation failed", 500
            
    return send_file(thumb_path)

@app.route('/api/photo/open-system', methods=['POST'])
def open_photo_system():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "File not found"}), 404
        
    try:
        os.startfile(photo_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/photo/open-folder', methods=['POST'])
def open_photo_folder():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "File not found"}), 404
        
    try:
        import subprocess
        abs_path = os.path.abspath(photo_path)
        subprocess.Popen(f'explorer.exe /select,"{abs_path}"')
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/photo/refresh-metadata', methods=['POST'])
def refresh_photo_metadata():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "File not found"}), 404
        
    try:
        meta = extract_metadata(photo_path)
        
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("SELECT latitude, longitude, place_name, date_taken FROM photos WHERE path = ?", (photo_path,))
        row = cursor.fetchone()
        
        place_name = None
        if row:
            old_lat, old_lon, old_place, old_date = row
            if meta["latitude"] is not None and meta["longitude"] is not None:
                if old_lat != meta["latitude"] or old_lon != meta["longitude"] or not old_place:
                    place_name = reverse_geocode(meta["latitude"], meta["longitude"])
            if not place_name and old_place:
                place_name = old_place
        
        cursor.execute("""
            UPDATE photos 
            SET date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, 
                latitude = ?, longitude = ?, place_name = ?
            WHERE path = ?
        """, (
            meta["date_taken"], meta["width"], meta["height"], meta["size"], meta["file_type"],
            meta["latitude"], meta["longitude"], place_name or meta["place_name"],
            photo_path
        ))
        conn.commit()
        
        # Aggressive face detector run on preview/viewing (min_confidence=0.40)
        try:
            detect_path = photo_path
            
            if os.path.exists(detect_path):
                processor = face_processor.FaceProcessor()
                detected_faces = processor.detect_and_extract_faces(detect_path, min_confidence=0.80)
                
                cursor.execute("SELECT x, y, w, h FROM faces WHERE photo_path = ?", (photo_path,))
                existing_boxes = cursor.fetchall()
                
                new_faces_added = False
                for face in detected_faces:
                    bx, by, bw, bh = face["bbox"]
                    
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
                            iou = intersection_area / float(box_area + ex_area - intersection_area)
                            if iou > 0.30 or (intersection_area / float(box_area)) > 0.50:
                                is_duplicate = True
                                break
                                
                    if not is_duplicate:
                        emb_bytes = face["embedding"].tobytes()
                        cursor.execute("""
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
                        """, (photo_path, bx, by, bw, bh, emb_bytes))
                        new_faces_added = True
                        
                if new_faces_added:
                    conn.commit()
                    run_incremental_clustering()
        except Exception as face_err:
            print(f"Error in aggressive face preview search: {face_err}")
            
        cursor.execute("""
            SELECT path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, archived_at
            FROM photos WHERE path = ?
        """, (photo_path,))
        updated_row = cursor.fetchone()
        conn.close()
        
        if updated_row:
            r = updated_row
            
            # Check filename for YYYYMMDD_HHMMSS pattern
            filename = os.path.basename(photo_path)
            filename_date = None
            has_date_mismatch = False
            
            match = re.search(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', filename)
            if match:
                try:
                    year, month, day, hour, col, sec = match.groups()
                    dt_file = datetime(int(year), int(month), int(day), int(hour), int(col), int(sec))
                    filename_date = dt_file.strftime("%Y-%m-%d %H:%M:%S")
                    
                    db_date = r[2]
                    if db_date:
                        try:
                            dt_db = datetime.strptime(db_date, "%Y-%m-%d %H:%M:%S")
                            if abs((dt_file - dt_db).total_seconds()) > 60:
                                has_date_mismatch = True
                        except ValueError:
                            has_date_mismatch = True
                    else:
                        has_date_mismatch = True
                except Exception:
                    pass
                    
            return jsonify({
                "success": True,
                "photo": {
                    "path": r[0],
                    "filename": r[1],
                    "date_taken": r[2],
                    "width": r[3],
                    "height": r[4],
                    "size": r[5],
                    "file_type": r[6],
                    "latitude": r[7],
                    "longitude": r[8],
                    "place_name": r[9],
                    "archived_at": r[10]
                },
                "filename_date": filename_date,
                "has_date_mismatch": has_date_mismatch
            })
        return jsonify({"error": "Failed to retrieve updated record"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def save_date_to_file_and_system(photo_path, new_date_str):
    if not new_date_str:
        return
    try:
        dt_file = datetime.strptime(new_date_str.strip(), "%Y-%m-%d %H:%M:%S")
    except Exception as parse_err:
        print(f"Error parsing date {new_date_str} for system update: {parse_err}")
        return

    # 1. Update EXIF tags for standard images (JPG, PNG, HEIC)
    ext = os.path.splitext(photo_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.heic', '.heif']:
        try:
            exif_date_str = dt_file.strftime("%Y:%m:%d %H:%M:%S")
            with Image.open(photo_path) as img:
                fmt = img.format
                exif = img.getexif()
                
                # DateTimeOriginal (36867), DateTimeDigitized (36868), DateTime (306)
                exif[36867] = exif_date_str
                exif[36868] = exif_date_str
                exif[306] = exif_date_str
                
                if fmt == 'HEIF' or ext in ['.heic', '.heif']:
                    img.save(photo_path, format="HEIF", exif=exif, quality=95)
                elif fmt == 'JPEG' or ext in ['.jpg', '.jpeg']:
                    img.save(photo_path, format="JPEG", exif=exif, quality=95, subsampling=0)
                else:
                    img.save(photo_path, exif=exif)
            print(f"Direct EXIF tags successfully written to {photo_path}")
        except Exception as exif_err:
            print(f"Direct EXIF save failed on {photo_path}: {exif_err}")

    # 2. Update Filesystem dates (Creation & Modification times) using Windows APIs
    try:
        import ctypes
        from ctypes import wintypes
        
        # Windows FILETIME expects UTC time. dt_file.timestamp() handles local timezone conversion implicitly.
        # 11644473600 is the difference in seconds between UNIX epoch (1970) and Windows epoch (1601).
        filetime_val = int((dt_file.timestamp() + 11644473600) * 10000000)
        
        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]
            
        ft = FILETIME(filetime_val & 0xFFFFFFFF, filetime_val >> 32)
        
        handle = ctypes.windll.kernel32.CreateFileW(
            photo_path, 0x40000000, 1 | 2, None, 3, 0x02000000 | 0x80, None
        )
        if handle != -1 and handle != 18446744073709551615:
            success = ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(ft), ctypes.byref(ft), ctypes.byref(ft))
            ctypes.windll.kernel32.CloseHandle(handle)
            if not success:
                raise Exception("SetFileTime returned 0 (failure)")
            print(f"Windows system file dates successfully updated to match {new_date_str}")
        else:
            raise Exception("CreateFileW returned INVALID_HANDLE_VALUE")
    except Exception as fs_err:
        print(f"Windows native timestamp update failed: {fs_err}")
        try:
            timestamp = dt_file.timestamp()
            os.utime(photo_path, (timestamp, timestamp))
        except Exception:
            pass


@app.route('/api/photo/rename', methods=['POST'])
def api_photo_rename():
    data = request.json
    photo_path = data.get('photo_path')
    new_filename = data.get('new_filename')
    
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "Original file not found"}), 404
        
    if not new_filename:
        return jsonify({"error": "New filename required"}), 400
        
    dir_name = os.path.dirname(photo_path)
    old_ext = os.path.splitext(photo_path)[1]
    
    # Ensure new filename has correct extension if not provided
    if not new_filename.lower().endswith(old_ext.lower()):
        new_filename += old_ext
        
    new_path = os.path.join(dir_name, new_filename)
    
    if os.path.exists(new_path) and new_path.lower() != photo_path.lower():
        return jsonify({"error": "A file with that name already exists"}), 409
        
    try:
        # Rename physical file
        os.rename(photo_path, new_path)
        
        # Update database with foreign keys temporarily off
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('PRAGMA foreign_keys=OFF')
        c.execute('BEGIN TRANSACTION')
        
        c.execute('UPDATE photos SET path=?, filename=? WHERE path=?', (new_path, new_filename, photo_path))
        c.execute('UPDATE faces SET photo_path=? WHERE photo_path=?', (new_path, photo_path))
        c.execute('UPDATE album_photos SET photo_path=? WHERE photo_path=?', (new_path, photo_path))
        
        c.execute('COMMIT')
        c.execute('PRAGMA foreign_keys=ON')
        conn.commit()
        
        return jsonify({"success": True, "new_path": new_path, "new_filename": new_filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/photo/fix-date-from-filename', methods=['POST'])
def fix_photo_date_from_filename():
    data = request.json
    photo_path = data.get('photo_path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "File not found"}), 404
        
    filename = os.path.basename(photo_path)
    match = re.search(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', filename)
    if not match:
        return jsonify({"error": "Filename does not match standard date pattern"}), 400
        
    try:
        year, month, day, hour, col, sec = match.groups()
        dt_file = datetime(int(year), int(month), int(day), int(hour), int(col), int(sec))
        new_date_str = dt_file.strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Update Database
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("UPDATE photos SET date_taken = ? WHERE path = ?", (new_date_str, photo_path))
        conn.commit()
        conn.close()
        
        # 2. Update EXIF and system file attributes
        save_date_to_file_and_system(photo_path, new_date_str)
                
        return jsonify({"success": True, "date_taken": new_date_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/photo/crop/<int:face_id>')
def serve_face_crop(face_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT photo_path, x, y, w, h FROM faces WHERE id = ?", (face_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Face not found", 404
        
    photo_path, x, y, w, h = row
    
    # If video, the face detection was run on its thumbnail frame. Crop from the thumbnail.
    is_video = photo_path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
    source_path = get_thumbnail_path(photo_path) if is_video else photo_path
    
    if not os.path.exists(source_path):
        return "Source photo not found", 404
        
    try:
        from io import BytesIO
        with Image.open(source_path) as img_raw:
            # Transpose orientation FIRST to match transposed face coordinates!
            img = ImageOps.exif_transpose(img_raw)
            img_w, img_h = img.size
            
            # Find center of the face bounding box
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Target square crop size zoomed out (2.0x maximum side)
            size_limit = max(w, h)
            crop_size = int(size_limit * 2.0)
            
            # Keep crop square size within absolute boundaries
            crop_size = min(crop_size, img_w, img_h)
            
            # Top-left corner coordinates
            left = center_x - crop_size // 2
            top = center_y - crop_size // 2
            
            # Boundary shift offsets (prevent clipping out of bounds)
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
            
            # Save cropped face to RAM to send directly
            img_io = BytesIO()
            cropped.save(img_io, 'JPEG', quality=85)
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error cropping face {face_id}: {e}")
        return "Failed to crop face", 500

@app.route('/api/photo/faces/<path:photo_path>')
def get_photo_faces(photo_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, f.x, f.y, f.w, f.h, p.id, p.name, p.cover_face_id 
        FROM faces f 
        LEFT JOIN people p ON f.person_id = p.id 
        WHERE f.photo_path = ? AND (f.is_manual != -1 OR f.is_manual IS NULL)
    """, (photo_path,))
    rows = cursor.fetchall()
    conn.close()
    
    faces = []
    for r in rows:
        faces.append({
            "face_id": r[0],
            "x": r[1],
            "y": r[2],
            "w": r[3],
            "h": r[4],
            "person_id": r[5],
            "person_name": r[6] if r[6] else (f"Person {r[5]}" if r[5] is not None else f"Unnamed Person {r[0]}"),
            "cover_face_id": r[7]
        })
    return jsonify(faces)

@app.route('/api/photo/albums/<path:photo_path>')
def get_photo_albums(photo_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.name 
        FROM albums a 
        JOIN album_photos ap ON a.id = ap.album_id 
        WHERE ap.photo_path = ?
    """, (photo_path,))
    rows = cursor.fetchall()
    conn.close()
    
    albums = []
    for r in rows:
        albums.append({
            "id": r[0],
            "name": r[1]
        })
    return jsonify(albums)

@app.route('/api/people')
@cache_api(timeout=30)
def get_people():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get people with count of faces on non-trashed photos, including empty people
    cursor.execute("""
        SELECT p.id, p.name, p.cover_face_id, 
               SUM(CASE WHEN ph.trashed_at IS NULL AND f.id IS NOT NULL THEN 1 ELSE 0 END) as face_count
        FROM people p
        LEFT JOIN faces f ON f.person_id = p.id
        LEFT JOIN photos ph ON f.photo_path = ph.path
        GROUP BY p.id
        HAVING face_count > 0
        ORDER BY face_count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    people = []
    for r in rows:
        people.append({
            "id": r[0],
            "name": r[1] if r[1] else f"Person {r[0]}",
            "cover_face_id": r[2],
            "face_count": r[3]
        })
    return jsonify(people)

@app.route('/api/people/rename', methods=['POST'])
def rename_person():
    data = request.json
    conn = None
    try:
        try:
            p_id = int(data.get('id'))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing ID format"}), 400
            
        new_name = data.get('name', '').strip()
        if not new_name:
            return jsonify({"error": "Missing name"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if a person with this name already exists
        cursor.execute("SELECT id FROM people WHERE name = ? AND id != ?", (new_name, p_id))
        existing = cursor.fetchone()
        
        if existing:
            # Merge operation! If they exist, merge this person's faces into the existing person
            target_p_id = existing[0]
            cursor.execute("UPDATE faces SET person_id = ? WHERE person_id = ?", (target_p_id, p_id))
            cursor.execute("DELETE FROM people WHERE id = ?", (p_id,))
            message = "Merged into existing person"
            merged_id = target_p_id
        else:
            cursor.execute("UPDATE people SET name = ? WHERE id = ?", (new_name, p_id))
            message = "Renamed successfully"
            merged_id = None
            
        conn.commit()
        conn.close()
        
        # Re-run centroids after renaming/merging
        threading.Thread(target=run_incremental_clustering).start()
        
        return jsonify({"success": True, "message": message, "merged_id": merged_id})
    except Exception as e:
        if conn:
            try: conn.close()
            except: pass
        print(f"Error in rename_person: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/people/unname', methods=['POST'])
def unname_person():
    data = request.json
    conn = None
    try:
        try:
            p_id = int(data.get('id'))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing ID format"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE people SET name = ? WHERE id = ?", (f"Person {p_id}", p_id))
        conn.commit()
        conn.close()
        
        # Re-run centroids after unnaming
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({"success": True})
    except Exception as e:
        if conn:
            try: conn.close()
            except: pass
        print(f"Error in unname_person: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/people/delete', methods=['POST'])
def delete_person():
    data = request.json
    conn = None
    try:
        try:
            p_id = int(data.get('id'))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing ID format"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE faces SET person_id = NULL WHERE person_id = ?", (p_id,))
        cursor.execute("DELETE FROM people WHERE id = ?", (p_id,))
        conn.commit()
        conn.close()
        
        # Re-run centroids after deletion
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({"success": True})
    except Exception as e:
        if conn:
            try: conn.close()
            except: pass
        print(f"Error in delete_person: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/faces/edit-tag', methods=['POST'])
def edit_face_tag():
    data = request.json
    conn = None
    try:
        try:
            face_id = int(data.get('face_id'))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing face_id format"}), 400
            
        new_name = data.get('new_name', '').strip()
        
        # Add timeout to prevent database locks
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Verify if face exists
        cursor.execute("SELECT photo_path, person_id FROM faces WHERE id = ?", (face_id,))
        face_row = cursor.fetchone()
        if not face_row:
            conn.close()
            return jsonify({"error": "Face not found"}), 404
            
        photo_path, old_person_id = face_row
        
        if not new_name:
            # Create a new unnamed person to branch off this face separately
            cursor.execute("INSERT INTO people (name) VALUES (NULL)")
            new_person_id = cursor.lastrowid
            cursor.execute("UPDATE people SET name = ? WHERE id = ?", (f"Person {new_person_id}", new_person_id))
            cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (new_person_id, face_id))
            print(f"Isolated face {face_id} to new separate unnamed Person {new_person_id}")
        else:
            # Check if named person already exists (case-insensitive)
            cursor.execute("SELECT id FROM people WHERE LOWER(name) = LOWER(?)", (new_name,))
            existing_person = cursor.fetchone()
            
            if existing_person:
                new_person_id = existing_person[0]
                cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (new_person_id, face_id))
                print(f"Merged face {face_id} into existing person ID {new_person_id} ({new_name})")
            else:
                # Create new named person
                cursor.execute("INSERT INTO people (name) VALUES (?)", (new_name,))
                new_person_id = cursor.lastrowid
                cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (new_person_id, face_id))
                print(f"Created new person ID {new_person_id} ({new_name}) and tagged face {face_id} to it")
                
        # Set a cover face for the new person group if none exists
        cursor.execute("SELECT cover_face_id FROM people WHERE id = ?", (new_person_id,))
        existing_cover = cursor.fetchone()
        if existing_cover and existing_cover[0] is None:
            cursor.execute("SELECT id FROM faces WHERE person_id = ? LIMIT 1", (new_person_id,))
            cov_face = cursor.fetchone()
            if cov_face:
                cursor.execute("UPDATE people SET cover_face_id = ? WHERE id = ?", (cov_face[0], new_person_id))
            
        # Clean up old person if they have no faces left and were unnamed/Person X
        if old_person_id is not None:
            try:
                old_person_id_int = int(old_person_id)
                cursor.execute("SELECT COUNT(*) FROM faces WHERE person_id = ?", (old_person_id_int,))
                rem_count = cursor.fetchone()[0]
                if rem_count == 0:
                    cursor.execute("SELECT name FROM people WHERE id = ?", (old_person_id_int,))
                    old_name_row = cursor.fetchone()
                    if old_name_row and (old_name_row[0] is None or old_name_row[0].startswith('Person ')):
                        cursor.execute("DELETE FROM people WHERE id = ?", (old_person_id_int,))
                        print(f"Deleted empty unnamed person ID {old_person_id_int}")
            except Exception as clean_err:
                print(f"Cleanup of old person {old_person_id} failed: {clean_err}")
                
        conn.commit()
        conn.close()
        # Run clustering asynchronously to update centroids
        threading.Thread(target=run_incremental_clustering).start()
        return jsonify({"success": True, "person_id": new_person_id})
    except Exception as e:
        if conn:
            try: conn.close()
            except: pass
        print(f"Error in edit_face_tag: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/people/set-cover', methods=['POST'])
def set_person_cover():
    data = request.json
    try:
        person_id = int(data.get('person_id'))
        face_id = int(data.get('face_id'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid or missing person_id or face_id format"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify face belongs to person
    cursor.execute("SELECT person_id FROM faces WHERE id = ?", (face_id,))
    row = cursor.fetchone()
    db_person_id = int(row[0]) if (row and row[0] is not None) else None
    if not row or db_person_id != person_id:
        conn.close()
        return jsonify({"error": f"Face does not belong to specified person. DB person: {row[0] if row else 'None'}, Request person: {person_id}"}), 400
        
    try:
        cursor.execute("UPDATE people SET cover_face_id = ? WHERE id = ?", (face_id, person_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/places')
@cache_api(timeout=30)
def get_places():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT place_name, COUNT(path) as count, MIN(path) as sample_path
        FROM photos 
        WHERE place_name IS NOT NULL AND trashed_at IS NULL
        GROUP BY place_name 
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    places = [{"name": r[0], "count": r[1], "sample_path": r[2]} for r in rows]
    return jsonify(places)

@app.route('/api/places/map_data')
def get_places_map_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT path, latitude, longitude, place_name 
        FROM photos 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND trashed_at IS NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    
    data = []
    for r in rows:
        data.append({
            "path": r[0],
            "latitude": r[1],
            "longitude": r[2],
            "place_name": r[3]
        })
    return jsonify(data)

@app.route('/api/places/rework_grouping', methods=['POST'])
def rework_places_grouping():
    data = request.json or {}
    threshold = int(data.get('threshold', 3))
    
    try:
        update_smart_location_tags(threshold=threshold)
        return jsonify({"success": True, "threshold": threshold})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Albums APIs
@app.route('/api/albums')
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

@app.route('/api/albums/create', methods=['POST'])
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

@app.route('/api/albums/add', methods=['POST'])
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

@app.route('/api/albums/remove', methods=['POST'])
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

@app.route('/api/albums/delete', methods=['POST'])
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

@app.route('/api/albums/rename', methods=['POST'])
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

@app.route('/api/albums/set-cover', methods=['POST'])
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

@app.route('/api/duplicates')
def get_duplicates():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Find duplicate hashes
    cursor.execute("""
        SELECT hash, COUNT(*) as count 
        FROM photos 
        WHERE hash IS NOT NULL AND hash != '' AND trashed_at IS NULL
        GROUP BY hash 
        HAVING count > 1
    """)
    dup_hashes = [r[0] for r in cursor.fetchall()]
    
    duplicates = []
    for h in dup_hashes:
        cursor.execute("""
            SELECT path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash 
            FROM photos 
            WHERE hash = ? AND trashed_at IS NULL
        """, (h,))
        rows = cursor.fetchall()
        
        # Partition rows into compatible duplicate clusters
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
                rep_is_vid = rep_path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
                
                # Must be same media type (both videos or both images)
                if is_vid != rep_is_vid:
                    continue
                
                # Must be similar in size: ratio <= 2.0 or absolute difference <= 100 KB
                ratio = max(size, rep_size) / max(min(size, rep_size), 1)
                abs_diff = abs(size - rep_size)
                if ratio <= 2.0 or abs_diff <= 102400:
                    cluster.append(r)
                    placed = True
                    break
            
            if not placed:
                clusters.append([r])
                
        # Filter for actual duplicate clusters (size > 1)
        valid_clusters = [c for c in clusters if len(c) > 1]
        
        for cluster_idx, cluster in enumerate(valid_clusters):
            analyzed = []
            for r in cluster:
                clean_name, is_copy = analyze_filename(r[1])
                score = get_metadata_score(r)
                analyzed.append({
                    "row": r,
                    "clean_name": clean_name,
                    "is_copy": is_copy,
                    "score": score
                })
                
            def sort_key(item):
                r = item["row"]
                return (
                    item["score"],
                    -1 if item["is_copy"] else 1,
                    r[5],
                    r[3] * r[4]
                )
                
            analyzed.sort(key=sort_key, reverse=True)
            keep_item = analyzed[0]
            delete_items = analyzed[1:]
            
            action = "KEEP_AS_IS"
            reason = ""
            
            if keep_item["is_copy"]:
                non_copies = [x for x in delete_items if not x["is_copy"]]
                if non_copies:
                    action = "KEEP_AND_RENAME"
                    reason = "Kept copy due to better metadata; duplicate suffix will be removed."
                else:
                    reason = "Kept copy as original (only copies exist)."
            else:
                copies = [x for x in delete_items if x["is_copy"]]
                if copies:
                    reason = "Kept original; suggested deleting copies."
                else:
                    reason = "Kept highest quality original."
                    
            def format_photo(r):
                return {
                    "path": r[0],
                    "filename": r[1],
                    "date_taken": r[2],
                    "width": r[3],
                    "height": r[4],
                    "size": r[5],
                    "file_type": r[6],
                    "latitude": r[7],
                    "longitude": r[8],
                    "place_name": r[9]
                }
                
            group_hash = f"{h}_{cluster_idx}"
            duplicates.append({
                "hash": group_hash,
                "keep": format_photo(keep_item["row"]),
                "delete": [format_photo(x["row"]) for x in delete_items],
                "action": action,
                "reason": reason
            })
            
    conn.close()
    return jsonify(duplicates)

def send_file_to_trash(path):
    """
    Tags a file for deletion by returning success.
    The actual physical file is not moved until the user purges it.
    Returns: (success_bool, original_path, error_str_or_None)
    """
    if not os.path.exists(path):
        return False, None, "File does not exist on disk"
        
    try:
        # We no longer move the file to an internal trash dir.
        # Just return the original path so the DB record can be updated with trashed_at.
        return True, path, None
    except Exception as e:
        print(f"Error trashing file {path}: {e}")
        return False, None, str(e)

@app.route('/api/duplicates/resolve', methods=['POST'])
def resolve_duplicates():
    data = request.json
    resolutions = data.get('resolutions', [])
    
    if not resolutions:
        return jsonify({"error": "No resolutions provided"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    deleted_paths = []
    renamed_paths = []
    
    try:
        # First, move all files scheduled for deletion to Recycle Bin
        for res in resolutions:
            del_path = res.get('delete_path')
            if del_path and os.path.exists(del_path):
                success, trash_path, err = send_file_to_trash(del_path)
                # Mark as trashed in database regardless of physical move success to keep UI responsive
                cursor.execute("UPDATE photos SET trashed_at = ? WHERE path = ?", 
                               (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), del_path))
                deleted_paths.append(del_path)
                
        # Commit deletions to ensure paths are cleared
        conn.commit()
        
        # Second, perform renames if requested
        for res in resolutions:
            action = res.get('action')
            if action == 'KEEP_AND_RENAME':
                keep_path = res.get('keep_path')
                if keep_path and os.path.exists(keep_path):
                    filename = os.path.basename(keep_path)
                    clean_name, _ = analyze_filename(filename)
                    new_path = os.path.join(os.path.dirname(keep_path), clean_name)
                    
                    # Safety check: ensure target does not exist or was just moved to trash
                    if not os.path.exists(new_path) or new_path in deleted_paths:
                        try:
                            shutil.move(keep_path, new_path)
                            renamed_paths.append((keep_path, new_path))
                            
                            # Rename thumbnail
                            old_thumb = get_thumbnail_path(keep_path)
                            new_thumb = get_thumbnail_path(new_path)
                            if os.path.exists(old_thumb):
                                if os.path.exists(new_thumb):
                                    os.remove(new_thumb)
                                shutil.move(old_thumb, new_thumb)
                                
                            # Update database records manually
                            cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (new_path, keep_path))
                            cursor.execute("UPDATE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, keep_path))
                            cursor.execute("UPDATE photos SET path = ?, filename = ? WHERE path = ?", (new_path, clean_name, keep_path))
                        except Exception as rename_err:
                            print(f"Error renaming resolved duplicate {keep_path} to {new_path}: {rename_err}")
                            
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
        return jsonify({"error": f"Failed to resolve duplicates: {error}"}), 500
        
    return jsonify({"success": True, "deleted": len(deleted_paths), "renamed": len(renamed_paths)})

@app.route('/api/archive/move', methods=['POST'])
def archive_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        try:
            cursor.execute("UPDATE photos SET archived_at = ? WHERE path = ?", 
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), path))
            success_count += 1
        except Exception as e:
            print(f"Error archiving {path}: {e}")
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})

@app.route('/api/archive/restore', methods=['POST'])
def unarchive_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        try:
            cursor.execute("UPDATE photos SET archived_at = NULL WHERE path = ?", (path,))
            success_count += 1
        except Exception as e:
            print(f"Error unarchiving {path}: {e}")
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})

@app.route('/api/trash/move', methods=['POST'])
def trash_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        if os.path.exists(path):
            success, trash_path, err = send_file_to_trash(path)
            # Mark as trashed in database regardless of physical move success to keep UI responsive
            cursor.execute("UPDATE photos SET trashed_at = ? WHERE path = ?", 
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), path))
            success_count += 1
                
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})

@app.route('/api/photos/copy', methods=['POST'])
def copy_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    destination = data.get('destination', '').strip()
    
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
    if not destination:
        return jsonify({"error": "No destination folder path provided"}), 400
        
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
        except Exception as e:
            return jsonify({"error": f"Failed to create destination folder: {str(e)}"}), 400
            
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
                dest_path = os.path.join(destination, f"{base}_{counter}{ext}")
                counter += 1
                
            try:
                shutil.copy2(path, dest_path)
                success_count += 1
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
                
    if errors:
        return jsonify({"success": True, "count": success_count, "errors": errors})
    return jsonify({"success": True, "count": success_count})

@app.route('/api/trash/restore', methods=['POST'])
def restore_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        file_hash = hashlib.md5(path.encode('utf-8')).hexdigest()
        ext = os.path.splitext(path)[1]
        trash_path = os.path.join(TRASH_DIR, file_hash + ext)
        
        if os.path.exists(trash_path):
            # Ensure target parent folder exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                # Physically move back
                os.rename(trash_path, path)
                # Clear trashed_at in DB
                cursor.execute("UPDATE photos SET trashed_at = NULL WHERE path = ?", (path,))
                success_count += 1
            except Exception as e:
                print(f"Error restoring {path} from trash: {e}")
                
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})

@app.route('/api/trash/empty', methods=['POST'])
def empty_trash():
    return jsonify({"error": "Empty trash is disabled. Delete items individually."}), 400

@app.route('/api/trash/purge', methods=['POST'])
def purge_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    import send2trash
    
    for path in photo_paths:
        try:
            # Send original file to Windows Recycle Bin
            if os.path.exists(path):
                send2trash.send2trash(path)
            # Delete thumbnail, face crops, and DB records
            completely_delete_photo_data(cursor, path)
            success_count += 1
        except Exception as e:
            print(f"Error purging file {path}: {e}")
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})

@app.route('/api/photo/edit_metadata', methods=['POST'])
def edit_metadata():
    data = request.json
    path = data.get('photo_path')
    if not path:
        return jsonify({"error": "Missing photo path"}), 400
        
    date_taken = data.get('date_taken')
    place_name = data.get('place_name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify if photo exists
    cursor.execute("SELECT path FROM photos WHERE path = ?", (path,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Photo not found"}), 404
        
    updates = []
    params = []
    
    if date_taken is not None:
        updates.append("date_taken = ?")
        params.append(date_taken.strip() if date_taken else None)
        
    if place_name is not None:
        updates.append("place_name = ?")
        params.append(place_name.strip() if place_name else None)
        
    if latitude is not None:
        updates.append("latitude = ?")
        try:
            params.append(float(latitude) if latitude != "" else None)
        except ValueError:
            conn.close()
            return jsonify({"error": "Latitude must be a number"}), 400
            
    if longitude is not None:
        updates.append("longitude = ?")
        try:
            params.append(float(longitude) if longitude != "" else None)
        except ValueError:
            conn.close()
            return jsonify({"error": "Longitude must be a number"}), 400
            
    if not updates:
        conn.close()
        return jsonify({"error": "No update values provided"}), 400
        
    params.append(path)
    cursor.execute(f"UPDATE photos SET {', '.join(updates)} WHERE path = ?", params)
    conn.commit()
    conn.close()
    
    if date_taken is not None and date_taken.strip():
        try:
            save_date_to_file_and_system(path, date_taken)
        except Exception as e:
            print(f"Failed to save date to EXIF/attributes for {path}: {e}")
            
    return jsonify({"success": True})

@app.route('/api/faces/add_to_video', methods=['POST'])
def add_person_to_video():
    """Tag an existing named person in a video without a bounding box crop."""
    data = request.json
    path = data.get('video_path')
    person_id = data.get('person_id')

    if not path or not person_id:
        return jsonify({"error": "Missing required fields (video_path, person_id)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        p_id = int(person_id)
        # Check person exists
        cursor.execute("SELECT id FROM people WHERE id = ?", (p_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Person not found"}), 404

        # Check if already tagged in this video
        cursor.execute("SELECT id FROM faces WHERE photo_path = ? AND person_id = ?", (path, p_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": True, "already_exists": True})

        # Insert with zero bounding box and is_manual=1 so it shows up in the faces list
        cursor.execute("""
            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
            VALUES (?, 0, 0, 0, 0, NULL, ?, 1)
        """, (path, p_id))

        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/faces/add_manual', methods=['POST'])
def add_manual_face():
    data = request.json
    path = data.get('photo_path')
    # Absolute coordinates mapped relative to 360x360 thumbnail
    x = data.get('x')
    y = data.get('y')
    w = data.get('w')
    h = data.get('h')
    person_id = data.get('person_id')
    raw_name = data.get('person_name')
    person_name = raw_name.strip() if raw_name else ''
    
    if not path or x is None or y is None or w is None or h is None:
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    p_id = None
    if person_id:
        p_id = int(person_id)
    elif person_name:
        cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
        p_row = cursor.fetchone()
        if p_row:
            p_id = p_row[0]
        else:
            cursor.execute("INSERT INTO people (name) VALUES (?)", (person_name,))
            p_id = cursor.lastrowid
            
    cursor.execute("""
        INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
        VALUES (?, ?, ?, ?, ?, NULL, ?, 1)
    """, (path, int(x), int(y), int(w), int(h), p_id))
    
    face_id = cursor.lastrowid
    
    if p_id:
        cursor.execute("SELECT cover_face_id FROM people WHERE id = ?", (p_id,))
        cov_row = cursor.fetchone()
        if cov_row and not cov_row[0]:
            cursor.execute("UPDATE people SET cover_face_id = ? WHERE id = ?", (face_id, p_id))
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "face_id": face_id, "person_id": p_id})

@app.route('/api/faces/delete', methods=['POST'])
def delete_face():
    data = request.json
    face_id = data.get('face_id')
    if not face_id:
        return jsonify({"error": "Missing face ID"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT person_id FROM faces WHERE id = ?", (face_id,))
    f_row = cursor.fetchone()
    if f_row and f_row[0]:
        p_id = f_row[0]
        cursor.execute("SELECT cover_face_id FROM people WHERE id = ?", (p_id,))
        cov_row = cursor.fetchone()
        if cov_row and cov_row[0] == face_id:
            cursor.execute("SELECT id FROM faces WHERE person_id = ? AND id != ? LIMIT 1", (p_id, face_id))
            other_face = cursor.fetchone()
            new_cover = other_face[0] if other_face else None
            cursor.execute("UPDATE people SET cover_face_id = ? WHERE id = ?", (new_cover, p_id))
            
    # Instead of deleting, mark it as rejected (is_manual = -1) so auto-scan ignores it
    # but the deep scan button can still explicitly override and find it.
    cursor.execute("UPDATE faces SET person_id = NULL, is_manual = -1 WHERE id = ?", (face_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/faces/rescan', methods=['POST'])
def rescan_faces():
    global scan_status
    with scan_lock:
        if scan_status["status"] == "scanning":
            return jsonify({"error": "A scan is already in progress"}), 400
        scan_status["status"] = "scanning"
        scan_status["total"] = 0
        scan_status["processed"] = 0
        scan_status["current_file"] = "Initializing face rescan..."
        scan_status["phase"] = "Rescanning Faces (Recall Optimized)"
        
    def run_rescan():
        try:
            processor = face_processor.FaceProcessor()
        except Exception as e:
            print(f"Error initializing face detector: {e}")
            scan_status["status"] = "idle"
            scan_status["phase"] = ""
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all photos
        cursor.execute("SELECT path FROM photos WHERE trashed_at IS NULL")
        photos = [r[0] for r in cursor.fetchall()]
        scan_status["total"] = len(photos)
        
        # Delete only automatic faces (is_manual = 0 or is_manual IS NULL)
        cursor.execute("DELETE FROM faces WHERE is_manual = 0 OR is_manual IS NULL")
        
        # Delete unreferenced people (keep named people and those referenced by manual faces)
        cursor.execute("""
            DELETE FROM people 
            WHERE id NOT IN (SELECT DISTINCT person_id FROM faces WHERE person_id IS NOT NULL)
            AND (name IS NULL OR name LIKE 'Person %')
        """)
        conn.commit()
        
        for idx, path in enumerate(photos):
            scan_status["processed"] = idx + 1
            scan_status["current_file"] = os.path.basename(path)
            
            thumb_path = get_thumbnail_path(path)
            is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            detect_path = path
            
            if os.path.exists(detect_path):
                try:
                    # Confidence threshold set to 0.5 for better recall
                    faces = processor.detect_and_extract_faces(detect_path, min_confidence=0.5)
                    for face in faces:
                        bbox = face["bbox"]
                        emb_bytes = face["embedding"].tobytes()
                        cursor.execute("""
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
                        """, (path, bbox[0], bbox[1], bbox[2], bbox[3], emb_bytes))
                except Exception as e:
                    print(f"Error in face rescan extraction for {path}: {e}")
                    
            if idx % 10 == 0:
                conn.commit()
                
        conn.commit()
        
        # Run clustering
        print("Running incremental face clustering after rescan...")
        try:
            run_incremental_clustering()
        except Exception as e:
            print(f"Error in face clustering: {e}")
            
        conn.close()
        scan_status["status"] = "idle"
        scan_status["phase"] = ""
        print("Face rescan completed.")
        
    threading.Thread(target=run_rescan, daemon=True).start()
    return jsonify({"success": True})




@app.route('/api/scan/reevaluate_faces', methods=['POST'])
def reevaluate_faces():
    """
    Recalculate centroids for named people and reassign automatic faces if they match
    another named person significantly better, or unassign if they no longer match.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Get all named people and their centroids (including manual faces for accurate centroids)
        cursor.execute("""
            SELECT p.id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL AND f.is_manual != -1
        """)
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
            return jsonify({"success": True, "reassigned": 0, "unassigned": 0})
            
        # 2. Get all automatic faces assigned to named people
        cursor.execute("""
            SELECT f.id, f.person_id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL 
              AND (f.is_manual = 0 OR f.is_manual IS NULL)
        """)
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
                    
            # Logic: If it matches another person much better
            if best_other_person_id is not None and best_other_dist < 0.40 and best_other_dist < (current_dist - 0.05):
                cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (best_other_person_id, f_id))
                reassigned_count += 1
            # Logic: If it doesn't match its own person anymore, and no other person is a good match
            elif current_dist > 0.48:
                cursor.execute("UPDATE faces SET person_id = NULL WHERE id = ?", (f_id,))
                unassigned_count += 1
                
        conn.commit()
        
    return jsonify({"success": True, "reassigned": reassigned_count, "unassigned": unassigned_count})


@app.route('/api/scan_directory', methods=['POST'])
def manual_scan_directory():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "No directory set"}), 400
        root_dir = row[0]
        
    def scan_task():
        scan_directory(root_dir)
        
    threading.Thread(target=scan_task, daemon=True).start()
    return jsonify({"success": True, "message": "Directory scan started"})

@app.route('/api/metadata/rescan', methods=['POST'])
def manual_metadata_rescan():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        root_dir = row[0] if row else None
        
    def rescan_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Tracking moved/missing files"
            scan_status["processed"] = 0
            scan_status["total"] = 0
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT path, filename, size FROM photos")
            photos = cursor.fetchall()
            
            missing_photos = []
            for p, f, s in photos:
                if not os.path.exists(p):
                    missing_photos.append((p, f, s))
                    
            if root_dir and missing_photos:
                # Map available files in root_dir
                print("Scanning for moved files...")
                available_files = {}
                roots_to_scan = [root_dir]
                scanned_roots = set()
                
                shell = None
                try:
                    import win32com.client
                    import pythoncom
                    pythoncom.CoInitialize()
                    shell = win32com.client.Dispatch("WScript.Shell")
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
                            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mp4', '.mov', '.m4v', '.hevc']:
                                p = os.path.join(root, file)
                                try:
                                    s = os.path.getsize(p)
                                    available_files[(file, s)] = p
                                except:
                                    pass
                            elif ext == '.lnk' and shell:
                                try:
                                    shortcut = shell.CreateShortCut(os.path.join(root, file))
                                    if os.path.isdir(shortcut.Targetpath):
                                        roots_to_scan.append(shortcut.Targetpath)
                                except Exception:
                                    pass
                                
                for old_path, fname, fsize in missing_photos:
                    new_path = available_files.get((fname, fsize))
                    if new_path:
                        print(f"Moved file found: {old_path} -> {new_path}")
                        cursor.execute("SELECT 1 FROM photos WHERE path = ?", (new_path,))
                        if cursor.fetchone():
                            # new_path is already in DB! Merge data to it.
                            cursor.execute("UPDATE OR IGNORE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE OR IGNORE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            completely_delete_photo_data(cursor, old_path)
                        else:
                            cursor.execute("UPDATE photos SET path = ? WHERE path = ?", (new_path, old_path))
                            cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                    else:
                        print(f"File permanently deleted: {old_path}")
                        completely_delete_photo_data(cursor, old_path)
                conn.commit()
            
            # Now trigger a full metadata re-extraction for everything? That might be slow.
            # The prompt said "Forces a re-extraction of date_taken and place_name for all files"
            cursor.execute("SELECT path FROM photos")
            all_paths = [r[0] for r in cursor.fetchall()]
            
            with scan_lock:
                scan_status["phase"] = "Refreshing EXIF & Dates"
                scan_status["total"] = len(all_paths)
                
            for i, p in enumerate(all_paths):
                if os.path.exists(p):
                    meta = extract_metadata(p)
                    # Don't overwrite place if it's already there? Wait, the user wants to refresh places later.
                    cursor.execute("UPDATE photos SET date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, latitude = ?, longitude = ? WHERE path = ?", 
                                   (meta["date_taken"], meta["width"], meta["height"], meta["size"], meta["file_type"], meta["latitude"], meta["longitude"], p))
                with scan_lock:
                    scan_status["processed"] = i + 1
                    
            conn.commit()
        except Exception as e:
            print(f"Error in metadata rescan: {e}")
        finally:
            conn.close()
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=rescan_task, daemon=True).start()
    return jsonify({"success": True, "message": "Metadata rescan started"})


@app.route('/api/metadata/refresh_places', methods=['POST'])
def manual_refresh_places():
    def refresh_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Refreshing Places Geocoding"
            scan_status["processed"] = 0
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Clear geocoding cache to force fresh pull
            cursor.execute("DELETE FROM geocoding_cache")
            conn.commit()
            
            cursor.execute("SELECT path, latitude, longitude FROM photos WHERE latitude IS NOT NULL")
            photos = cursor.fetchall()
            
            with scan_lock:
                scan_status["total"] = len(photos)
                
            for i, (p, lat, lon) in enumerate(photos):
                place = reverse_geocode(lat, lon)
                if place:
                    cursor.execute("UPDATE photos SET place_name = ? WHERE path = ?", (place, p))
                    conn.commit()
                with scan_lock:
                    scan_status["processed"] = i + 1
        except Exception as e:
            print(f"Error in refreshing places: {e}")
        finally:
            conn.close()
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=refresh_task, daemon=True).start()
    return jsonify({"success": True, "message": "Places refresh started"})

@app.route('/api/faces/force_cluster', methods=['POST'])
def manual_force_cluster():
    def cluster_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Clustering Faces"
            scan_status["processed"] = 0
            scan_status["total"] = 1
        
        try:
            run_incremental_clustering()
        finally:
            with scan_lock:
                scan_status["processed"] = 1
                scan_status["status"] = "idle"
                
    threading.Thread(target=cluster_task, daemon=True).start()
    return jsonify({"success": True, "message": "Clustering started"})


@app.route('/api/faces/safe_rescan', methods=['POST'])
def manual_safe_rescan():
    def safe_rescan_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Safe Face Rescan (Preserving Names)"
            scan_status["processed"] = 0
            scan_status["total"] = 1
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Instead of deleting faces, we just clear person_id for auto faces, 
            # BUT we save the centroids first!
            # Wait, the easiest way to preserve names is to just NOT delete them, 
            # and just re-run phase 3 (detect_and_extract_faces on missing hashes/photos)
            
            # Since a safe rescan means checking all photos for faces without deleting
            cursor.execute("SELECT path FROM photos WHERE path NOT IN (SELECT DISTINCT photo_path FROM faces)")
            paths_no_faces = [r[0] for r in cursor.fetchall()]
            
            # Sort files to prioritize images over videos
            video_exts = ('.mp4', '.mov', '.m4v', '.hevc')
            paths_no_faces.sort(key=lambda x: 1 if x.lower().endswith(video_exts) else 0)
            
            with scan_lock:
                scan_status["total"] = len(paths_no_faces)
                
            processor = face_processor.FaceProcessor()
            for i, p in enumerate(paths_no_faces):
                if os.path.exists(p):
                    detected = processor.detect_and_extract_faces(p)
                    for face in detected:
                        bx, by, bw, bh = face["bbox"]
                        emb_bytes = face["embedding"].tobytes()
                        cursor.execute("""
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, 0)
                        """, (p, bx, by, bw, bh, emb_bytes))
                with scan_lock:
                    scan_status["processed"] = i + 1
                    
            conn.commit()
            conn.close()
            run_incremental_clustering()
            
        except Exception as e:
            print(f"Error in safe rescan: {e}")
        finally:
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=safe_rescan_task, daemon=True).start()
    return jsonify({"success": True, "message": "Safe face rescan started"})


@app.route('/api/people/<int:person_id>/faces', methods=['GET'])
def get_person_faces(person_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, f.photo_path
        FROM faces f
        JOIN photos ph ON f.photo_path = ph.path
        WHERE f.person_id = ? AND ph.trashed_at IS NULL
    """, (person_id,))
    faces = [{"id": r[0], "photo_path": r[1]} for r in cursor.fetchall()]
    conn.close()
    return jsonify({"faces": faces})


@app.route('/api/faces/training_pairs', methods=['GET'])
def get_training_pairs():
    # Find two faces that are close but not clustered
    # This is a naive implementation: grab two random named people's unassigned faces or just two similar faces
    # For simplicity, we just return two faces that have low distance.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get random faces to pair for UI demonstration, since actual cross-cluster distance logic requires loading all embeddings.
    # We will pick a face from a named person, and an unassigned face.
    cursor.execute("""
        SELECT f.id, f.embedding, f.photo_path, p.name, p.id
        FROM faces f
        JOIN people p ON f.person_id = p.id
        WHERE p.name != 'Unknown'
        LIMIT 50
    """)
    named_faces = cursor.fetchall()
    
    cursor.execute("""
        SELECT f.id, f.embedding, f.photo_path
        FROM faces f
        WHERE f.person_id IS NULL OR f.person_id IN (SELECT id FROM people WHERE name = 'Unknown')
        LIMIT 200
    """)
    unassigned_faces = cursor.fetchall()
    
    conn.close()
    
    pairs = []
    if named_faces and unassigned_faces:
        import numpy as np
        # Find closest pair
        for nf in named_faces[:10]:
            n_emb = np.frombuffer(nf[1], dtype=np.float32)
            for uf in unassigned_faces:
                u_emb = np.frombuffer(uf[1], dtype=np.float32)
                dist = np.linalg.norm(n_emb - u_emb)
                # If distance is just outside clustering threshold (0.5 to 0.7)
                if 0.4 < dist < 0.75:
                    pairs.append({
                        "distance": float(dist),
                        "person_id": nf[4],
                        "person_name": nf[3],
                        "named_face_id": nf[0],
                        "unknown_face_id": uf[0],
                        "named_photo": nf[2],
                        "unknown_photo": uf[2]
                    })
                    if len(pairs) >= 5:
                        break
            if len(pairs) >= 5:
                break
                
    # Sort by distance
    pairs.sort(key=lambda x: x["distance"])
    return jsonify({"pairs": pairs})


@app.route('/api/people/merge', methods=['POST'])
def merge_people():
    data = request.json
    unknown_face_id = data.get('unknown_face_id')
    person_id = data.get('person_id')
    
    if not unknown_face_id or not person_id:
        return jsonify({"error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Assign the face manually
    cursor.execute("UPDATE faces SET person_id = ?, is_manual = 1 WHERE id = ?", (person_id, unknown_face_id))
    conn.commit()
    conn.close()
    
    # Re-run clustering asynchronously to suck in other similar faces!
    threading.Thread(target=run_incremental_clustering, daemon=True).start()
    
    return jsonify({"success": True})




def compute_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    
    ixA = max(x1, x2)
    iyA = max(y1, y2)
    ixB = min(x1+w1, x2+w2)
    iyB = min(y1+h1, y2+h2)
    
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
    ixB = min(x1+w1, x2+w2)
    iyB = min(y1+h1, y2+h2)
    
    inter_area = max(0, ixB - ixA) * max(0, iyB - iyA)
    box1_area = w1 * h1
    box2_area = w2 * h2
    
    min_area = min(box1_area, box2_area)
    return inter_area / min_area if min_area > 0 else 0

@app.route('/api/photo/deep-scan', methods=['POST'])
def deep_scan_photo():
    data = request.json
    photo_path = data.get('path')
    
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "File not found"}), 404
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get existing faces for this photo to avoid duplicates (including rejected ones so we don't redetect them)
        cursor.execute("SELECT x, y, w, h FROM faces WHERE photo_path = ?", (photo_path,))
        existing_boxes = cursor.fetchall()
        
        processor = face_processor.FaceProcessor()
        # Drop confidence to find faint faces (0.47 avoids random objects)
        detected_faces = processor.detect_and_extract_faces(photo_path, min_confidence=0.47)
        
        new_faces_added = 0
        new_boxes_this_run = []
        for face in detected_faces:
            bx, by, bw, bh = face["bbox"]
            current_box = (bx, by, bw, bh)
            
            # Prevent duplicating existing faces
            is_duplicate = False
            for e_box in existing_boxes:
                if compute_iou(current_box, e_box) > 0.3 or compute_iom(current_box, e_box) > 0.6:
                    is_duplicate = True
                    break
            
            # Prevent overlapping duplicate faces found in the current deep scan
            if not is_duplicate:
                for n_box in new_boxes_this_run:
                    if compute_iou(current_box, n_box) > 0.3 or compute_iom(current_box, n_box) > 0.6:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                new_boxes_this_run.append(current_box)
                emb_bytes = face["embedding"].tobytes()
                cursor.execute("""
                    INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (photo_path, bx, by, bw, bh, emb_bytes))
                new_faces_added += 1
                
        conn.commit()
        conn.close()
        
        # Cluster the newly added faces synchronously
        if new_faces_added > 0:
            run_incremental_clustering()
            
        return jsonify({"success": True, "new_faces_count": new_faces_added})
    except Exception as e:
        print(f"Error in deep scan: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/photo/find_missing', methods=['POST'])
def find_missing_photo():
    data = request.json
    photo_path = data.get('path')
    search_dir = data.get('search_dir')
    
    if not photo_path:
        return jsonify({"error": "Missing path"}), 400
        
    basename = os.path.basename(photo_path)
    
    found_path = None
    
    # If search_dir is an exact file path that exists, use it directly
    if search_dir and isinstance(search_dir, str) and os.path.isfile(search_dir):
        found_path = search_dir
    else:
        dirs_to_search = []
        if search_dir and isinstance(search_dir, str) and os.path.isdir(search_dir):
            dirs_to_search.append(search_dir)
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM directories")
            for (d,) in cursor.fetchall():
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
        # Auto heal! Update the database!
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE photos SET path = ? WHERE path = ?", (found_path, photo_path))
        cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (found_path, photo_path))
        conn.commit()
        conn.close()
        
        # Rename thumbnail if necessary
        old_thumb = get_thumbnail_path(photo_path)
        new_thumb = get_thumbnail_path(found_path)
        if os.path.exists(old_thumb) and not os.path.exists(new_thumb):
            try:
                os.rename(old_thumb, new_thumb)
            except Exception as e:
                print("Failed to rename thumb:", e)
                
        return jsonify({"success": True, "new_path": found_path})
    else:
        return jsonify({"success": False, "error": "not_found"})

@app.route('/api/photo/delete_record', methods=['POST'])
def delete_photo_record():
    data = request.json
    photo_path = data.get('path')
    
    if not photo_path:
        return jsonify({"error": "Missing path"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    completely_delete_photo_data(cursor, photo_path)
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})


@app.route('/api/photo/refresh', methods=['POST'])
def refresh_single_photo():
    data = request.json
    photo_path = data.get('path')
    
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({"error": "file_missing"}), 404
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Refresh Metadata (EXIF)
        meta = extract_metadata(photo_path)
        
        # 2. Refresh Geocoding
        place = None
        if meta["latitude"]:
            # Delete cached entry to force fresh geocoding
            lat_r = round(meta["latitude"], 4)
            lon_r = round(meta["longitude"], 4)
            cursor.execute("DELETE FROM geocoding_cache WHERE lat_rounded = ? AND lon_rounded = ?", (lat_r, lon_r))
            conn.commit()
            place = reverse_geocode(meta["latitude"], meta["longitude"])
            
        # Update photo record
        cursor.execute("""
            UPDATE photos 
            SET date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, latitude = ?, longitude = ?, place_name = ?
            WHERE path = ?
        """, (meta["date_taken"], meta["width"], meta["height"], meta["size"], meta["file_type"], 
              meta["latitude"], meta["longitude"], place, photo_path))
        conn.commit()
        
        # 3. Refresh Faces (Delete existing auto faces, re-detect)
        # Note: Do NOT delete manual faces!
        cursor.execute("DELETE FROM faces WHERE photo_path = ? AND is_manual = 0", (photo_path,))
        conn.commit()
        
        cursor.execute("SELECT x, y, w, h FROM faces WHERE photo_path = ?", (photo_path,))
        existing_boxes = cursor.fetchall()
        
        processor = face_processor.FaceProcessor()
        detected_faces = processor.detect_and_extract_faces(photo_path)
        
        for face in detected_faces:
            bx, by, bw, bh = face["bbox"]
            current_box = (bx, by, bw, bh)
            
            is_duplicate = False
            for e_box in existing_boxes:
                if compute_iou(current_box, e_box) > 0.3 or compute_iom(current_box, e_box) > 0.6:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                emb_bytes = face["embedding"].tobytes()
                cursor.execute("""
                    INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (photo_path, bx, by, bw, bh, emb_bytes))
            
        conn.commit()
        conn.close()
        
        # 4. Run clustering synchronously to ensure UI sees the results immediately
        run_incremental_clustering()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error refreshing photo: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/cache/rebuild', methods=['POST'])
def rebuild_cache_and_mapping():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        root_dir = row[0] if row else None
        
    def rebuild_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Rebuilding Mapping & Cache"
            scan_status["processed"] = 0
            scan_status["total"] = 0
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Update mappings / remove deleted files
            cursor.execute("SELECT path, filename, size FROM photos")
            photos = cursor.fetchall()
            
            missing_photos = []
            for p, f, s in photos:
                if not os.path.exists(p):
                    missing_photos.append((p, f, s))
                    
            if root_dir and missing_photos:
                print("Scanning for moved files...")
                available_files = {}
                roots_to_scan = [root_dir]
                scanned_roots = set()
                
                shell = None
                try:
                    import win32com.client
                    import pythoncom
                    pythoncom.CoInitialize()
                    shell = win32com.client.Dispatch("WScript.Shell")
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
                            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mp4', '.mov', '.m4v', '.hevc']:
                                p = os.path.join(root, file)
                                try:
                                    s = os.path.getsize(p)
                                    available_files[(file, s)] = p
                                except:
                                    pass
                            elif ext == '.lnk' and shell:
                                try:
                                    shortcut = shell.CreateShortCut(os.path.join(root, file))
                                    if os.path.isdir(shortcut.Targetpath):
                                        roots_to_scan.append(shortcut.Targetpath)
                                except Exception:
                                    pass
                                
                for old_path, fname, fsize in missing_photos:
                    new_path = available_files.get((fname, fsize))
                    if new_path:
                        print(f"Moved file found: {old_path} -> {new_path}")
                        cursor.execute("SELECT 1 FROM photos WHERE path = ?", (new_path,))
                        if cursor.fetchone():
                            # new_path is already in DB! Merge data to it.
                            cursor.execute("UPDATE OR IGNORE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE OR IGNORE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            completely_delete_photo_data(cursor, old_path)
                        else:
                            cursor.execute("UPDATE photos SET path = ? WHERE path = ?", (new_path, old_path))
                            cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                    else:
                        print(f"File permanently deleted: {old_path}")
                        completely_delete_photo_data(cursor, old_path)
                conn.commit()
            
            # 2. Rebuild Physical Cache (Wipe directories)
            with scan_lock:
                scan_status["phase"] = "Wiping Cache Directories"
            
            import shutil
            # Wipe thumbnails
            for item in os.listdir(THUMBNAILS_DIR):
                item_path = os.path.join(THUMBNAILS_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Failed to delete cache file {item_path}: {e}")
                    
            # Wipe faces
            for item in os.listdir(FACES_DIR):
                item_path = os.path.join(FACES_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Failed to delete face cache file {item_path}: {e}")

        except Exception as e:
            print(f"Error in cache rebuild: {e}")
        finally:
            conn.close()
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=rebuild_task, daemon=True).start()
    return jsonify({"success": True, "message": "Cache rebuild started"})

@app.route('/api/memories/curated')
def api_memories_curated():
    conn = get_db_connection()
    c = conn.cursor()
    
    curated = {
        "featured_moment": None,
        "featured_video": None,
        "album_pick": None
    }
    
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        curated['featured_moment'] = {
            "file_path": row[0], "file_type": row[1], "date_taken": row[2],
            "size": row[3], "width": row[4], "height": row[5], "phash": row[6]
        }
        
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM')
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        curated['featured_video'] = {
            "file_path": row[0], "file_type": row[1], "date_taken": row[2],
            "size": row[3], "width": row[4], "height": row[5], "phash": row[6]
        }
        
    c.execute('''
        SELECT id, name, cover_photo_path 
        FROM albums 
        WHERE cover_photo_path IS NOT NULL 
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        curated['album_pick'] = {
            "id": row[0], "name": row[1], "cover_photo_path": row[2]
        }
        
    # Spotlight on a Day (random day >= 2000 with at least 3 photos)
    c.execute('''
        SELECT strftime('%Y-%m-%d', date_taken) as day
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL 
          AND date_taken >= '2000-01-01'
        GROUP BY day
        HAVING count(*) >= 3
        ORDER BY RANDOM() LIMIT 1
    ''')
    day_row = c.fetchone()
    spotlight_day_photos = []
    if day_row:
        day_str = day_row[0]
        c.execute('''
            SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
            FROM photos
            WHERE trashed_at IS NULL AND archived_at IS NULL 
              AND date_taken LIKE ?
            ORDER BY date_taken ASC
        ''', (day_str + '%',))
        
        for p in c.fetchall():
            spotlight_day_photos.append({
                "file_path": p[0], "file_type": p[1], "date_taken": p[2],
                "size": p[3], "width": p[4], "height": p[5], "phash": p[6]
            })
    curated['spotlight_day'] = spotlight_day_photos if spotlight_day_photos else None
        
    # --- People Spotlight ---
    c.execute('SELECT id FROM people WHERE name = "Me" COLLATE NOCASE')
    me_row = c.fetchone()
    if me_row:
        me_id = me_row[0]
    else:
        c.execute('''
            SELECT p.id 
            FROM people p
            JOIN faces f ON f.person_id = p.id
            GROUP BY p.id
            ORDER BY count(*) DESC
            LIMIT 1
        ''')
        me_row2 = c.fetchone()
        me_id = me_row2[0] if me_row2 else -1

    if me_id != -1:
        c.execute('''
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
        ''', (me_id, me_id))
        person = c.fetchone()
        if not person:
            c.execute('''
                SELECT p.id, p.name, p.cover_face_id,
                       0 as shared_count,
                       count(f.id) as total_count
                FROM people p
                JOIN faces f ON f.person_id = p.id
                WHERE p.id != ? AND p.name IS NOT NULL AND p.name NOT LIKE 'Person %'
                GROUP BY p.id
                HAVING count(f.id) >= 3
                ORDER BY RANDOM() LIMIT 1
            ''', (me_id,))
            person = c.fetchone()
            
        if person:
            pid, pname, pcover, pshared, ptotal = person
            
            c.execute('''
                SELECT ph.path, ph.date_taken, ph.file_type
                FROM photos ph
                JOIN faces f ON f.photo_path = ph.path
                WHERE f.person_id = ? AND ph.trashed_at IS NULL
                ORDER BY RANDOM() LIMIT 10
            ''', (pid,))
            person_photos = [{"file_path": r[0], "date_taken": r[1], "file_type": r[2]} for r in c.fetchall()]
            
            c.execute('''
                SELECT ph.path, ph.date_taken, ph.file_type
                FROM photos ph
                JOIN faces f1 ON f1.photo_path = ph.path
                JOIN faces f2 ON f2.photo_path = ph.path
                WHERE f1.person_id = ? AND f2.person_id = ? AND ph.trashed_at IS NULL
                ORDER BY RANDOM() LIMIT 10
            ''', (pid, me_id))
            shared_photos = [{"file_path": r[0], "date_taken": r[1], "file_type": r[2]} for r in c.fetchall()]
            
            curated['people_spotlight'] = {
                "person": {"id": pid, "name": pname, "cover_face_id": pcover, "shared_count": pshared, "total_count": ptotal},
                "person_photos": person_photos,
                "shared_photos": shared_photos
            }

    conn.close()
    return jsonify({"success": True, "curated": curated})

@app.route('/api/memories/on_this_day')
def api_memories():
    conn = get_db_connection()
    c = conn.cursor()
    today_mm_dd = datetime.now().strftime('%m-%d')
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos
        WHERE substr(date_taken, 6, 5) = ? AND trashed_at IS NULL
        ORDER BY date_taken DESC
    ''', (today_mm_dd,))
    photos = c.fetchall()
    conn.close()
    
    results = {}
    for p in photos:
        # p: (path, file_type, date_taken, size, width, height, hash)
        if not p[2]: continue
        year = p[2][:4]
        if year not in results:
            results[year] = []
        p_dict = {
            "file_path": p[0],
            "file_type": p[1],
            "date_taken": p[2],
            "size": p[3],
            "width": p[4],
            "height": p[5],
            "phash": p[6]
        }
        results[year].append(p_dict)
    return jsonify(results)

@app.route('/api/stats/heatmap')
def api_stats_heatmap():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return jsonify({})
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT substr(date_taken, 9, 2) as day, count(*)
        FROM photos 
        WHERE substr(date_taken, 1, 4) = ? AND substr(date_taken, 6, 2) = ? AND trashed_at IS NULL 
        GROUP BY day
    ''', (year, month.zfill(2)))
    
    data = c.fetchall()
    conn.close()
    
    return jsonify({row[0]: row[1] for row in data})




@app.route('/api/stats/calendar')
def api_stats_calendar():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT substr(date_taken, 1, 10) as day, count(*)
        FROM photos 
        WHERE date_taken IS NOT NULL AND date_taken != 'Undated' AND trashed_at IS NULL AND archived_at IS NULL AND date_taken >= '1999-01-01'
        GROUP BY day
        ORDER BY day ASC
    ''')
    data = c.fetchall()
    conn.close()
    return jsonify({row[0]: row[1] for row in data})

@app.route('/api/stats')
@cache_api(timeout=30)
def api_stats():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT substr(date_taken, 1, 4) as year, substr(date_taken, 6, 2) as month, file_type, count(*), sum(size)
        FROM photos 
        WHERE date_taken IS NOT NULL AND date_taken != 'Undated' 
        GROUP BY year, month, file_type
    ''')
    monthly_data = c.fetchall()
    
    c.execute('''
        SELECT 
            SUM(CASE WHEN file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN 1 ELSE 0 END) as total_videos,
            SUM(CASE WHEN file_type NOT IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN 1 ELSE 0 END) as total_photos,
            SUM(CASE WHEN file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN size ELSE 0 END) as total_video_size,
            SUM(CASE WHEN file_type NOT IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN size ELSE 0 END) as total_photo_size
        FROM photos
    ''')
    totals = c.fetchone()
    conn.close()
    
    stats = {
        'total_photos': totals[1] if totals and totals[1] else 0,
        'total_videos': totals[0] if totals and totals[0] else 0,
        'total_photo_size': totals[3] if totals and totals[3] else 0,
        'total_video_size': totals[2] if totals and totals[2] else 0,
        'yearly': {}
    }
    
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
            stats['yearly'][year] = {'photos': 0, 'videos': 0, 'storage_photos': 0, 'storage_videos': 0, 'months': {}}
            for m in range(1, 13):
                stats['yearly'][year]['months'][f"{m:02d}"] = {'photos': 0, 'videos': 0, 'storage_photos': 0, 'storage_videos': 0}
                
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


@app.route('/api/memories/welcome')
@cache_api(timeout=300)
def api_memories_welcome():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get candidate photos: horizontal, no faces, randomly ordered, limit 50
    c.execute("""
        SELECT path as file_path
        FROM photos 
        WHERE trashed_at IS NULL 
          AND archived_at IS NULL 
          AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
          AND width > height
          AND path NOT IN (SELECT photo_path FROM faces)
        ORDER BY (date_taken >= '2020-01-01') DESC, RANDOM() LIMIT 300
    """)
    
    candidates = c.fetchall()
    valid_photos = []
    
    from scene_classifier import scene_cache
    for row in candidates:
        path = row[0]
        if scene_cache.get(path) is True:
            valid_photos.append(path)
            if len(valid_photos) >= 50:
                break
                
    # Fallback if too few nature/animal photos
    if len(valid_photos) < 5:
        for row in candidates:
            if row[0] not in valid_photos:
                valid_photos.append(row[0])
            if len(valid_photos) >= 50:
                break
                
    # Format URLs using quote (to handle spaces and special chars safely)
    from urllib.parse import quote
    photos_out = []
    for p in valid_photos:
        # We need to serve the high-res file
        safe_path = quote(p.replace('\\', '/'))
        photos_out.append(f"/api/photo/file/{safe_path}")
        
    return jsonify({"photos": photos_out})

if __name__ == '__main__':
    def open_as_app():
        import time, ctypes, os, subprocess
        time.sleep(1.0)
        
        user32 = ctypes.windll.user32
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            user32.SetProcessDPIAware()
        
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        
        target_w_ratio = 1808 / 1920
        target_h_ratio = 1000 / 1080
        win_w = int(screen_w * target_w_ratio)
        win_h = int(screen_h * target_h_ratio)
        
        pos_x = (screen_w - win_w) // 2
        pos_y = (screen_h - win_h) // 2

        size_arg = f"--window-size={win_w},{win_h}"
        pos_arg  = f"--window-position={pos_x},{pos_y}"

        edge_path = os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Microsoft\\Edge\\Application\\msedge.exe")
        chrome_path = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe")
        
        if os.path.exists(edge_path):
            try:
                subprocess.Popen([edge_path, "--app=http://127.0.0.1:5000", size_arg, pos_arg])
                return
            except Exception:
                pass
        elif os.path.exists(chrome_path):
            try:
                subprocess.Popen([chrome_path, "--app=http://127.0.0.1:5000", size_arg, pos_arg])
                return
            except Exception:
                pass
                
        import webbrowser
        webbrowser.open("http://127.0.0.1:5000")
        
    import threading
    threading.Thread(target=open_as_app, daemon=True).start()
    app.run(host='127.0.0.1', debug=False, port=5000)
