py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

idx_start = py.find('# 4. Iconic Place')
idx_end = py.find('# Generate AI-like comment based on stats')

if idx_start != -1 and idx_end != -1:
    new_logic = '''# 4. Top Places (Combining Iconic Place & Hero Moment)
        cursor.execute("""
            SELECT place_name, COUNT(*) as c 
            FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%' AND place_name IS NOT NULL AND place_name != '' AND place_name != 'Unknown'
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
                  AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%' AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                ORDER BY RANDOM() LIMIT 15
            """, (date_filter, p_name))
            p_photos = [r[0] for r in cursor.fetchall()]
            if p_photos:
                top_places.append({'name': p_name, 'photos': p_photos})
                
        # 5. Gallery Photos
        cursor.execute("""
            SELECT path FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%' AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            ORDER BY RANDOM() LIMIT 30
        """, (date_filter,))
        moment_rows = cursor.fetchall()
        gallery_photos = [r[0] for r in moment_rows] if moment_rows else []
        
        '''
    py = py[:idx_start] + new_logic + py[idx_end:]
    
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(py)
    print("Successfully patched top_places and gallery_photos!")
else:
    print(f"Could not find indices: start={idx_start}, end={idx_end}")

