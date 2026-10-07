import sqlite3
conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='photos';")
print(c.fetchone()[0])
