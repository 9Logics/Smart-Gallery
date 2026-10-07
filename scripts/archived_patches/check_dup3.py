import sqlite3
conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()
c.execute("SELECT COUNT(*), filename, size FROM photos GROUP BY filename, size HAVING COUNT(*) > 1 LIMIT 10;")
print(c.fetchall())
