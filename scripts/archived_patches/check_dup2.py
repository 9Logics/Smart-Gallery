import sqlite3
conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()
c.execute("SELECT COUNT(path), REPLACE(LOWER(path), '\', '/') FROM photos GROUP BY REPLACE(LOWER(path), '\', '/') HAVING COUNT(path) > 1 LIMIT 5;")
print(c.fetchall())
