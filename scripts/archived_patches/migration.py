import sqlite3
import os
import time

DB_PATH = 'd:\\DevelopmentAppTest Folder\\Project Gallery One\\.cache\\gallery.db'

def test_migration():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    cursor = conn.cursor()
    
    # 1. Create sidecar tables
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS photo_embeddings (
        photo_path TEXT PRIMARY KEY,
        clip_embedding BLOB
    )
    """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS face_embeddings (
        face_id INTEGER PRIMARY KEY,
        embedding BLOB
    )
    """
    )
    
    # 2. Create FTS5 table
    cursor.execute(
        """
    CREATE VIRTUAL TABLE IF NOT EXISTS photos_fts USING fts5(
        path UNINDEXED, 
        ai_tags, 
        place_name
    )
    """
    )
    
    # 3. Check if clip_embedding is in photos
    cursor.execute("PRAGMA table_info(photos)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'clip_embedding' in cols:
        print("Migrating clip_embedding...")
        cursor.execute("INSERT OR REPLACE INTO photo_embeddings(photo_path, clip_embedding) SELECT path, clip_embedding FROM photos WHERE clip_embedding IS NOT NULL")
        cursor.execute("ALTER TABLE photos DROP COLUMN clip_embedding")
        print("Migrated clip_embedding")
    
    # 4. Check if embedding is in faces
    cursor.execute("PRAGMA table_info(faces)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'embedding' in cols:
        print("Migrating face embedding...")
        cursor.execute("INSERT OR REPLACE INTO face_embeddings(face_id, embedding) SELECT id, embedding FROM faces WHERE embedding IS NOT NULL")
        cursor.execute("ALTER TABLE faces DROP COLUMN embedding")
        print("Migrated face embedding")
        
    # 5. Populate FTS5 table if it's empty but photos exists
    cursor.execute("SELECT COUNT(*) FROM photos_fts")
    fts_count = cursor.fetchone()[0]
    if fts_count == 0:
        print("Populating FTS5 table...")
        cursor.execute("INSERT INTO photos_fts(path, ai_tags, place_name) SELECT path, ai_tags, place_name FROM photos")
        print("Populated FTS5 table")

    conn.commit()
    conn.close()

test_migration()
