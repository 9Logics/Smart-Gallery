import sqlite3

conn = sqlite3.connect('.cache/gallery.db')
cursor = conn.cursor()

# 1. Un-assign ALL auto-faces to clear pollution
cursor.execute("UPDATE faces SET person_id = NULL WHERE is_manual = 0")
unassigned_count = cursor.rowcount
print(f"Unassigned {unassigned_count} auto faces.")

# 2. Find people who have NO manual faces and delete them
cursor.execute("""
    SELECT id FROM people 
    WHERE id NOT IN (
        SELECT DISTINCT person_id FROM faces WHERE is_manual = 1 AND person_id IS NOT NULL
    )
""")
empty_people = [r[0] for r in cursor.fetchall()]

for p_id in empty_people:
    cursor.execute("DELETE FROM people WHERE id = ?", (p_id,))
    
print(f"Deleted {len(empty_people)} polluted auto-people.")

conn.commit()
conn.close()
