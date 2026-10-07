py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

target = '''        # 3. Top Person
        cursor.execute("""
            SELECT p.name, COUNT(*) as c 
            FROM people p 
            JOIN faces f ON f.person_id = p.id 
            JOIN photos ph ON f.photo_path = ph.path 
            WHERE ph.date_taken LIKE ? AND ph.trashed_at IS NULL AND ph.archived_at IS NULL AND ph.path NOT LIKE '%\\Archive\\%' AND ph.path NOT LIKE '%/Archive/%' AND ph.path NOT LIKE '%\\Trash\\%' AND ph.path NOT LIKE '%/Trash/%' AND ph.path NOT LIKE '%\\Deleted\\%' AND ph.path NOT LIKE '%/Deleted/%' AND p.name != 'Me' AND p.name IS NOT NULL AND p.name != 'Unknown'
            GROUP BY p.name 
            ORDER BY c DESC 
            LIMIT 1
        """, (date_filter,))
        person_row = cursor.fetchone()
        top_person = person_row[0] if person_row else None'''

if target in py:
    replacement = '''        # 3. Top Person & Runners Up
        cursor.execute("""
            SELECT p.name, COUNT(*) as c, p.cover_face_id
            FROM people p 
            JOIN faces f ON f.person_id = p.id 
            JOIN photos ph ON f.photo_path = ph.path 
            WHERE ph.date_taken LIKE ? AND ph.trashed_at IS NULL AND ph.archived_at IS NULL AND ph.path NOT LIKE '%\\Archive\\%' AND ph.path NOT LIKE '%/Archive/%' AND ph.path NOT LIKE '%\\Trash\\%' AND ph.path NOT LIKE '%/Trash/%' AND ph.path NOT LIKE '%\\Deleted\\%' AND ph.path NOT LIKE '%/Deleted/%' AND p.name != 'Me' AND p.name IS NOT NULL AND p.name != 'Unknown'
            GROUP BY p.name 
            ORDER BY c DESC 
            LIMIT 15
        """, (date_filter,))
        person_rows = cursor.fetchall()
        top_person = person_rows[0][0] if person_rows else None
        runners_up = [{'name': r[0], 'cover_face_id': r[2]} for r in person_rows]
'''
    py = py.replace(target, replacement)
else:
    print("Target not found, falling back to manual insertion before top_person_photos")
    # if it's already partly replaced?
    if 'runners_up = ' not in py:
        py = py.replace('top_person_photos = []', 'runners_up = []\n        top_person_photos = []')
        
with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Patched runners_up assignment")
