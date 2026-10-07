import sqlite3
import os

DB_PATH = 'd:\\DevelopmentAppTest Folder\\Project Gallery One\\.cache\\gallery.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in cursor.fetchall()])

cursor.execute("SELECT COUNT(*) FROM photo_embeddings")
print("photo_embeddings count:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM face_embeddings")
print("face_embeddings count:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM photos_fts")
print("photos_fts count:", cursor.fetchone()[0])
