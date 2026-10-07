import re

py_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\routes\photos.py"
with open(py_path, "r", encoding="utf-8") as f:
    py_code = f.read()

# Replace backend gallery logic to also fetch moment_photos
old_py = """        cursor.execute(\"\"\"
            SELECT file_name FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            ORDER BY RANDOM() LIMIT 24
        \"\"\", (date_filter,))
        moment_rows = cursor.fetchall()
        gallery_photos = [r[0] for r in moment_rows] if moment_rows else []
        memorable_moment = gallery_photos[0] if gallery_photos else None"""

new_py = """        cursor.execute(\"\"\"
            SELECT file_name FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            ORDER BY RANDOM() LIMIT 24
        \"\"\", (date_filter,))
        moment_rows = cursor.fetchall()
        gallery_photos = [r[0] for r in moment_rows] if moment_rows else []
        
        # Find a cluster/moment (day with most photos)
        cursor.execute(\"\"\"
            SELECT substr(date_taken, 1, 10) as day, COUNT(*) as c
            FROM photos
            WHERE date_taken LIKE ?
              AND trashed_at IS NULL AND archived_at IS NULL
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY day
            ORDER BY c DESC
            LIMIT 1
        \"\"\", (date_filter,))
        day_row = cursor.fetchone()
        
        moment_photos = []
        if day_row and day_row[0]:
            cursor.execute(\"\"\"
                SELECT file_name FROM photos
                WHERE date_taken LIKE ?
                  AND trashed_at IS NULL AND archived_at IS NULL
                  AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM()
                LIMIT 4
            \"\"\", (day_row[0] + '%',))
            moment_photos = [r[0] for r in cursor.fetchall()]
        
        memorable_moment = moment_photos[0] if moment_photos else (gallery_photos[0] if gallery_photos else None)"""

if old_py in py_code:
    py_code = py_code.replace(old_py, new_py)
else:
    print("Warning: could not find old_py block")

# Inject into the return dict
py_code = py_code.replace("'memorable_moment': memorable_moment,", "'memorable_moment': memorable_moment, 'moment_photos': moment_photos,")

with open(py_path, "w", encoding="utf-8") as f:
    f.write(py_code)

print("Backend moment cluster query patched!")
