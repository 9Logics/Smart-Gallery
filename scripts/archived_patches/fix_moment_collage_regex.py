import re

py_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\routes\photos.py"
with open(py_path, "r", encoding="utf-8") as f:
    py_code = f.read()

new_block = """            SELECT path FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            ORDER BY RANDOM() LIMIT 30
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

# Use regex to find the block
py_code = re.sub(
    r"SELECT path FROM photos.*?LIMIT 30.*?moment_rows = cursor.fetchall\(\).*?memorable_moment = gallery_photos\[0\] if gallery_photos else None",
    new_block,
    py_code,
    flags=re.DOTALL
)

with open(py_path, "w", encoding="utf-8") as f:
    f.write(py_code)

print("Patched python cluster!")
