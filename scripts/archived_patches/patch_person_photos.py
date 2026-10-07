import os

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

old_person_query = '''        cursor.execute("""
            SELECT p.name, COUNT(*) as c 
            FROM people p 
            JOIN faces f ON f.person_id = p.id 
            JOIN photos ph ON f.photo_path = ph.path 
            WHERE ph.date_taken LIKE ? AND p.name != 'Me' AND p.name IS NOT NULL AND p.name != 'Unknown'
            GROUP BY p.name 
            ORDER BY c DESC 
            LIMIT 1
        """, (date_filter,))
        person_row = cursor.fetchone()
        top_person = person_row[0] if person_row else None'''

new_person_query = '''        cursor.execute("""
            SELECT p.name, COUNT(*) as c 
            FROM people p 
            JOIN faces f ON f.person_id = p.id 
            JOIN photos ph ON f.photo_path = ph.path 
            WHERE ph.date_taken LIKE ? AND p.name != 'Me' AND p.name IS NOT NULL AND p.name != 'Unknown'
            GROUP BY p.name 
            ORDER BY c DESC 
            LIMIT 1
        """, (date_filter,))
        person_row = cursor.fetchone()
        top_person = person_row[0] if person_row else None
        
        top_person_photos = []
        top_person_feature = None
        
        if top_person:
            cursor.execute("""
                SELECT ph.path 
                FROM photos ph 
                JOIN faces f ON f.photo_path = ph.path 
                JOIN people p ON f.person_id = p.id 
                WHERE ph.date_taken LIKE ? AND p.name = ? 
                AND LOWER(ph.file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM() LIMIT 4
            """, (date_filter, top_person))
            top_person_photos = [r[0] for r in cursor.fetchall()]
            
            cursor.execute("""
                SELECT f.photo_path 
                FROM faces f
                JOIN people p ON p.cover_face_id = f.id
                WHERE p.name = ?
            """, (top_person,))
            feat_row = cursor.fetchone()
            if feat_row:
                top_person_feature = feat_row[0]'''

py = py.replace(old_person_query, new_person_query)

old_return = '''            'total_videos': total_videos,
            'top_person': top_person,
            'iconic_place': iconic_place,'''

new_return = '''            'total_videos': total_videos,
            'top_person': top_person,
            'top_person_photos': top_person_photos,
            'top_person_feature': top_person_feature,
            'iconic_place': iconic_place,'''

py = py.replace(old_return, new_return)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Updated backend for person photos!")
