import re

def refactor_init_db():
    with open('app/app_core.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_init_db = """def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    cursor = conn.cursor()
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    '''
        )
    cursor.execute(
        '''
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
        video_codec TEXT,
        ai_tags TEXT
    )
    '''
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
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE photos ADD COLUMN ai_tags TEXT')
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
        '''
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_path TEXT,
        x INTEGER,
        y INTEGER,
        w INTEGER,
        h INTEGER,
        person_id INTEGER,
        FOREIGN KEY(photo_path) REFERENCES photos(path) ON DELETE CASCADE,
        FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE SET NULL
    )
    '''
        )
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cover_face_id INTEGER
    )
    '''
        )
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        cover_photo_path TEXT,
        created_at TEXT
    )
    '''
        )
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS album_photos (
        album_id INTEGER,
        photo_path TEXT,
        PRIMARY KEY(album_id, photo_path),
        FOREIGN KEY(album_id) REFERENCES albums(id) ON DELETE CASCADE,
        FOREIGN KEY(photo_path) REFERENCES photos(path) ON DELETE CASCADE
    )
    '''
        )
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS geocoding_cache (
        lat_rounded REAL,
        lon_rounded REAL,
        place_name TEXT,
        PRIMARY KEY(lat_rounded, lon_rounded)
    )
    '''
        )
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS photo_embeddings (
        photo_path TEXT PRIMARY KEY,
        clip_embedding BLOB
    )
    '''
        )
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS face_embeddings (
        face_id INTEGER PRIMARY KEY,
        embedding BLOB
    )
    '''
        )
    cursor.execute(
        '''
    CREATE VIRTUAL TABLE IF NOT EXISTS photos_fts USING fts5(
        path UNINDEXED, 
        ai_tags, 
        place_name
    )
    '''
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
        
    cursor.execute("PRAGMA table_info(photos)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'clip_embedding' in cols:
        cursor.execute("INSERT OR REPLACE INTO photo_embeddings(photo_path, clip_embedding) SELECT path, clip_embedding FROM photos WHERE clip_embedding IS NOT NULL")
        cursor.execute("ALTER TABLE photos DROP COLUMN clip_embedding")

    cursor.execute("PRAGMA table_info(faces)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'embedding' in cols:
        cursor.execute("INSERT OR REPLACE INTO face_embeddings(face_id, embedding) SELECT id, embedding FROM faces WHERE embedding IS NOT NULL")
        cursor.execute("ALTER TABLE faces DROP COLUMN embedding")
        
    cursor.execute("SELECT COUNT(*) FROM photos_fts")
    fts_count = cursor.fetchone()[0]
    if fts_count == 0:
        cursor.execute("INSERT INTO photos_fts(path, ai_tags, place_name) SELECT path, ai_tags, place_name FROM photos")

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
    threading.Thread(target=migrate_database, daemon=True).start()"""
    
    # We will find the boundaries of init_db
    pattern = r"def init_db\(\):.*?threading\.Thread\(target=migrate_database, daemon=True\)\.start\(\)"
    new_content = re.sub(pattern, new_init_db, content, flags=re.DOTALL)
    
    with open('app/app_core.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

refactor_init_db()
