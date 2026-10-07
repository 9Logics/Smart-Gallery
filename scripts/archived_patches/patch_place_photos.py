import os
import re

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

# I need to find where iconic_place is queried and add a query for its photos.
old_place_query = '''        cursor.execute("""
            SELECT place_name, COUNT(*) as c 
            FROM photos 
            WHERE date_taken LIKE ? AND place_name IS NOT NULL AND place_name != '' AND place_name != 'Unknown'
            GROUP BY place_name 
            ORDER BY c DESC 
            LIMIT 1
        """, (date_filter,))
        place_row = cursor.fetchone()
        iconic_place = place_row[0] if place_row else None'''

new_place_query = '''        cursor.execute("""
            SELECT place_name, COUNT(*) as c 
            FROM photos 
            WHERE date_taken LIKE ? AND place_name IS NOT NULL AND place_name != '' AND place_name != 'Unknown'
            GROUP BY place_name 
            ORDER BY c DESC 
            LIMIT 1
        """, (date_filter,))
        place_row = cursor.fetchone()
        iconic_place = place_row[0] if place_row else None
        
        iconic_place_photos = []
        if iconic_place:
            cursor.execute("""
                SELECT path FROM photos
                WHERE date_taken LIKE ? AND place_name = ? AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM() LIMIT 3
            """, (date_filter, iconic_place))
            iconic_place_photos = [r[0] for r in cursor.fetchall()]'''

py = py.replace(old_place_query, new_place_query)

old_return = '''            'top_person': top_person,
            'iconic_place': iconic_place,
            'memorable_moment': memorable_moment,'''

new_return = '''            'top_person': top_person,
            'iconic_place': iconic_place,
            'iconic_place_photos': iconic_place_photos,
            'memorable_moment': memorable_moment,'''

py = py.replace(old_return, new_return)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Updated backend to fetch place-specific photos!")
