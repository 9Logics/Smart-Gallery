import sqlite3
conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()
c.execute("SELECT path FROM photos WHERE filename = '0314.mp4';")
print(c.fetchall())
