
import sqlite3

conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()

c.execute('SELECT ai_tags FROM photos WHERE ai_tags IS NOT NULL LIMIT 5')
res = c.fetchall()
print(f'Sample ai_tags: {res}')

