import sqlite3
import os

conn = sqlite3.connect('.cache/gallery.db')
cursor = conn.cursor()

# Find all auto-generated people (Person 1, Person 2, etc.)
cursor.execute("SELECT id, name FROM people WHERE name LIKE 'Person %'")
rows = cursor.fetchall()

# Sort them based on their current number (to preserve relative order)
def extract_num(name):
    try:
        return int(name.replace('Person ', ''))
    except:
        return 9999999

rows.sort(key=lambda r: extract_num(r[1]))

# Rename them sequentially starting from 1
for i, (p_id, old_name) in enumerate(rows):
    new_name = f"Person {i + 1}"
    if old_name != new_name:
        cursor.execute("UPDATE people SET name = ? WHERE id = ?", (new_name, p_id))

conn.commit()
conn.close()
print(f"Renamed {len(rows)} auto-people sequentially.")
