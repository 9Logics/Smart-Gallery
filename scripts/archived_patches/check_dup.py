import sqlite3
conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()
c.execute("SELECT COUNT(path), LOWER(path) FROM photos GROUP BY LOWER(path) HAVING COUNT(path) > 1 LIMIT 5;")
print(c.fetchall())
c.execute("SELECT COUNT(*) FROM photos")
print("Total rows:", c.fetchone()[0])
