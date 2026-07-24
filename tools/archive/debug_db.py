import sqlite3

conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()

c.execute("SELECT id, name FROM people")
people = c.fetchall()

c.execute("SELECT person_id, is_manual, COUNT(*) FROM faces WHERE person_id IS NOT NULL GROUP BY person_id, is_manual")
face_counts = c.fetchall()

print("People:")
for p in people:
    print(p)

print("\nFace counts (person_id, is_manual, count):")
for f in face_counts:
    print(f)
    
conn.close()
