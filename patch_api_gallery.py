import os
import re

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

# Replace the memorable moment fetching logic to fetch 6 random photos instead
old_moment_logic = '''    # 5. Memorable Moment (Favorite photo from that year, or just a random photo)
    cursor.execute("""
        SELECT path FROM photos 
        WHERE date_taken LIKE ? AND is_favorite = 1 
        ORDER BY RANDOM() LIMIT 1
    """, (f"{year}-%",))
    moment_row = cursor.fetchone()
    if not moment_row:
        cursor.execute("SELECT path FROM photos WHERE date_taken LIKE ? ORDER BY RANDOM() LIMIT 1", (f"{year}-%",))
        moment_row = cursor.fetchone()
        
    memorable_moment = moment_row[0] if moment_row else None'''

new_moment_logic = '''    # 5. Memorable Moment + Gallery
    cursor.execute("""
        SELECT path FROM photos 
        WHERE date_taken LIKE ? AND file_type IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
        ORDER BY RANDOM() LIMIT 6
    """, (f"{year}-%",))
    moment_rows = cursor.fetchall()
    gallery_photos = [r[0] for r in moment_rows] if moment_rows else []
    memorable_moment = gallery_photos[0] if gallery_photos else None'''

if 'gallery_photos' not in py:
    py = py.replace(old_moment_logic, new_moment_logic)
    
    # Update jsonify
    old_json = '''        'memorable_moment': memorable_moment,
        'ai_comment': ai_comment
    })'''
    new_json = '''        'memorable_moment': memorable_moment,
        'gallery_photos': gallery_photos,
        'ai_comment': ai_comment
    })'''
    py = py.replace(old_json, new_json)

    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(py)
    print("Updated backend API for gallery photos!")
else:
    print("Backend already has gallery photos.")
