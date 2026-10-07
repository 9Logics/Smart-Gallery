import sqlite3
import os

DB_PATH = 'd:\\DevelopmentAppTest Folder\\Project Gallery One\\.cache\\gallery.db'

def test_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(photos)")
    cols = [r[1] for r in cursor.fetchall()]
    print("photos columns:", cols)

    cursor.execute("PRAGMA table_info(faces)")
    cols = [r[1] for r in cursor.fetchall()]
    print("faces columns:", cols)

test_migration()
