import re

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

target = '''        # 4. Iconic Place
        cursor.execute("""
            SELECT place_name, COUNT(*) as c 
            FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%' AND place_name IS NOT NULL AND place_name != '' AND place_name != 'Unknown'
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
                WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%' AND place_name = ? AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM() LIMIT 10
            """, (date_filter, iconic_place))
            iconic_place_photos = [r[0] for r in cursor.fetchall()]
        
        # 5. Memorable Moment (A burst of photos taken in the same hour)
        cursor.execute("""
            SELECT strftime('%Y-%m-%d %H', date_taken) as hour_cluster, COUNT(*) as c
            FROM photos
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%' AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
              AND (place_name != ? OR place_name IS NULL)
            GROUP BY hour_cluster
            ORDER BY c DESC
            LIMIT 1
        """, (date_filter, iconic_place))
        moment_row = cursor.fetchone()
        memorable_moment = None
        moment_photos = []
        if moment_row:
            cluster = moment_row[0]
            cursor.execute("""
                SELECT path FROM photos
                WHERE date_taken LIKE ? || '%' 
                  AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%' AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM() LIMIT 24
            """, (cluster,))
            m_photos = [r[0] for r in cursor.fetchall()]
            if m_photos:
                memorable_moment = m_photos[0]
                moment_photos = m_photos
'''

replacement = '''        # 4. Top Places (Combining Iconic Place & Hero Moment)
        cursor.execute("""
            SELECT place_name, COUNT(*) as c 
            FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%' AND place_name IS NOT NULL AND place_name != '' AND place_name != 'Unknown'
            GROUP BY place_name 
            ORDER BY c DESC 
            LIMIT 5
        """, (date_filter,))
        places_rows = cursor.fetchall()
        
        top_places = []
        for pr in places_rows:
            p_name = pr[0]
            cursor.execute("""
                SELECT path FROM photos
                WHERE date_taken LIKE ? AND place_name = ?
                  AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%' AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM() LIMIT 15
            """, (date_filter, p_name))
            p_photos = [r[0] for r in cursor.fetchall()]
            if p_photos:
                top_places.append({'name': p_name, 'photos': p_photos})
'''
py = py.replace(target, replacement)

target2 = '''            'iconic_place': iconic_place,
            'iconic_place_photos': iconic_place_photos,
            'memorable_moment': memorable_moment, 'moment_photos': moment_photos,'''
replacement2 = '''            'top_places': top_places,'''
py = py.replace(target2, replacement2)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Replaced Iconic Place/Hero Moment with top_places in photos.py")
