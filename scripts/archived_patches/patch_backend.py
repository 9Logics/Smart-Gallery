import re

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

old_cluster_query = '''        # Find a cluster/moment (day with most photos)
        cursor.execute("""
            SELECT substr(date_taken, 1, 13) as hour_cluster, COUNT(*) as c
            FROM photos
            WHERE date_taken LIKE ?
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%'
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY hour_cluster
            ORDER BY c DESC
            LIMIT 1
        """, (date_filter,))
        day_row = cursor.fetchone()'''

new_cluster_query = '''        # Find a cluster/moment (day with most photos) EXCLUDING the iconic place to prevent duplicate slides
        exclude_place = "AND (place_name != ? OR place_name IS NULL)" if iconic_place else ""
        params_cluster = (date_filter, iconic_place) if iconic_place else (date_filter,)
        
        cursor.execute(f"""
            SELECT substr(date_taken, 1, 13) as hour_cluster, COUNT(*) as c
            FROM photos
            WHERE date_taken LIKE ?
              {exclude_place}
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%'
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY hour_cluster
            ORDER BY c DESC
            LIMIT 1
        """, params_cluster)
        day_row = cursor.fetchone()
        
        # Fallback if excluding iconic place leaves them with 0 photos
        if not day_row or day_row[1] == 0:
            cursor.execute("""
                SELECT substr(date_taken, 1, 13) as hour_cluster, COUNT(*) as c
                FROM photos
                WHERE date_taken LIKE ?
                  AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%'
                  AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                GROUP BY hour_cluster
                ORDER BY c DESC
                LIMIT 1
            """, (date_filter,))
            day_row = cursor.fetchone()'''

py = py.replace(old_cluster_query, new_cluster_query)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print('Patched backend to mutually exclude moment and place')
