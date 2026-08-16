from flask import Blueprint, request, jsonify, send_file
from app_globals import *

memories_bp = Blueprint("memories", __name__)

@memories_bp.route('/api/memories/curated')
def api_memories_curated():
    conn = get_db_connection()
    c = conn.cursor()
    
    curated = {
        "featured_moment": None,
        "featured_video": None,
        "album_pick": None
    }
    
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        curated['featured_moment'] = {
            "file_path": row[0], "file_type": row[1], "date_taken": row[2],
            "size": row[3], "width": row[4], "height": row[5], "phash": row[6]
        }
        
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM')
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        curated['featured_video'] = {
            "file_path": row[0], "file_type": row[1], "date_taken": row[2],
            "size": row[3], "width": row[4], "height": row[5], "phash": row[6]
        }
        
    c.execute('''
        SELECT id, name, cover_photo_path 
        FROM albums 
        WHERE cover_photo_path IS NOT NULL 
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        curated['album_pick'] = {
            "id": row[0], "name": row[1], "cover_photo_path": row[2]
        }
        
    # Spotlight on a Day (random day >= 2000 with at least 3 photos)
    c.execute('''
        SELECT strftime('%Y-%m-%d', date_taken) as day
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL 
          AND date_taken >= '2000-01-01'
        GROUP BY day
        HAVING count(*) >= 3
        ORDER BY RANDOM() LIMIT 1
    ''')
    day_row = c.fetchone()
    spotlight_day_photos = []
    if day_row:
        day_str = day_row[0]
        c.execute('''
            SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
            FROM photos
            WHERE trashed_at IS NULL AND archived_at IS NULL 
              AND date_taken LIKE ?
            ORDER BY date_taken ASC
        ''', (day_str + '%',))
        
        for p in c.fetchall():
            spotlight_day_photos.append({
                "file_path": p[0], "file_type": p[1], "date_taken": p[2],
                "size": p[3], "width": p[4], "height": p[5], "phash": p[6]
            })
    curated['spotlight_day'] = spotlight_day_photos if spotlight_day_photos else None
        
    # --- People Spotlight ---
    c.execute('SELECT id FROM people WHERE name = "Me" COLLATE NOCASE')
    me_row = c.fetchone()
    if me_row:
        me_id = me_row[0]
    else:
        c.execute('''
            SELECT p.id 
            FROM people p
            JOIN faces f ON f.person_id = p.id
            GROUP BY p.id
            ORDER BY count(*) DESC
            LIMIT 1
        ''')
        me_row2 = c.fetchone()
        me_id = me_row2[0] if me_row2 else -1

    if me_id != -1:
        c.execute('''
            SELECT p.id, p.name, p.cover_face_id,
                   (SELECT count(*) FROM faces f1 JOIN faces f2 ON f1.photo_path = f2.photo_path 
                    WHERE f1.person_id = p.id AND f2.person_id = ?) as shared_count,
                   count(f.id) as total_count
            FROM people p
            JOIN faces f ON f.person_id = p.id
            WHERE p.id != ? AND p.name IS NOT NULL AND p.name NOT LIKE 'Person %'
            GROUP BY p.id
            HAVING count(f.id) >= 3 AND shared_count > 0
            ORDER BY RANDOM() LIMIT 1
        ''', (me_id, me_id))
        person = c.fetchone()
        if not person:
            c.execute('''
                SELECT p.id, p.name, p.cover_face_id,
                       0 as shared_count,
                       count(f.id) as total_count
                FROM people p
                JOIN faces f ON f.person_id = p.id
                WHERE p.id != ? AND p.name IS NOT NULL AND p.name NOT LIKE 'Person %'
                GROUP BY p.id
                HAVING count(f.id) >= 3
                ORDER BY RANDOM() LIMIT 1
            ''', (me_id,))
            person = c.fetchone()
            
        if person:
            pid, pname, pcover, pshared, ptotal = person
            
            c.execute('''
                SELECT ph.path, ph.date_taken, ph.file_type
                FROM photos ph
                JOIN faces f ON f.photo_path = ph.path
                WHERE f.person_id = ? AND ph.trashed_at IS NULL
                ORDER BY RANDOM() LIMIT 10
            ''', (pid,))
            person_photos = [{"file_path": r[0], "date_taken": r[1], "file_type": r[2]} for r in c.fetchall()]
            
            c.execute('''
                SELECT ph.path, ph.date_taken, ph.file_type
                FROM photos ph
                JOIN faces f1 ON f1.photo_path = ph.path
                JOIN faces f2 ON f2.photo_path = ph.path
                WHERE f1.person_id = ? AND f2.person_id = ? AND ph.trashed_at IS NULL
                ORDER BY RANDOM() LIMIT 10
            ''', (pid, me_id))
            shared_photos = [{"file_path": r[0], "date_taken": r[1], "file_type": r[2]} for r in c.fetchall()]
            
            curated['people_spotlight'] = {
                "person": {"id": pid, "name": pname, "cover_face_id": pcover, "shared_count": pshared, "total_count": ptotal},
                "person_photos": person_photos,
                "shared_photos": shared_photos
            }

    conn.close()
    return jsonify({"success": True, "curated": curated})


@memories_bp.route('/api/memories/on_this_day')
def api_memories():
    conn = get_db_connection()
    c = conn.cursor()
    today_mm_dd = datetime.now().strftime('%m-%d')
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos
        WHERE substr(date_taken, 6, 5) = ? AND trashed_at IS NULL
        ORDER BY date_taken DESC
    ''', (today_mm_dd,))
    photos = c.fetchall()
    conn.close()
    
    results = {}
    for p in photos:
        # p: (path, file_type, date_taken, size, width, height, hash)
        if not p[2]: continue
        year = p[2][:4]
        if year not in results:
            results[year] = []
        p_dict = {
            "file_path": p[0],
            "file_type": p[1],
            "date_taken": p[2],
            "size": p[3],
            "width": p[4],
            "height": p[5],
            "phash": p[6]
        }
        results[year].append(p_dict)
    return jsonify(results)


@memories_bp.route('/api/memories/welcome')
@cache_api(timeout=300)
def api_memories_welcome():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT value FROM settings WHERE key = 'hero_album_id'")
    album_row = c.fetchone()
    valid_photos = []

    if album_row and album_row[0]:
        album_id = album_row[0]
        c.execute("""
            SELECT p.path as file_path
            FROM photos p
            JOIN album_photos ap ON p.path = ap.photo_path
            WHERE ap.album_id = ? AND p.trashed_at IS NULL
            ORDER BY RANDOM() LIMIT 50
        """, (album_id,))
        candidates = c.fetchall()
        valid_photos = [row[0] for row in candidates]
        
    if not valid_photos:
        # Fallback to AI logic + Overrides
        overrides = load_hero_overrides()
        whitelist = overrides.get('whitelist', [])
        blacklist = set(overrides.get('blacklist', []))
        
        # 1. Add all valid whitelisted photos
        if whitelist:
            c.execute(f"""
                SELECT path as file_path
                FROM photos
                WHERE trashed_at IS NULL
                  AND archived_at IS NULL
                  AND path IN ({','.join(['?']*len(whitelist))})
            """, whitelist)
            wl_candidates = c.fetchall()
            valid_photos.extend([r[0] for r in wl_candidates])

        # 2. Get standard candidates
        if len(valid_photos) < 50:
            c.execute("""
                SELECT path as file_path
                FROM photos
                WHERE trashed_at IS NULL
                  AND archived_at IS NULL
                  AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
                  AND width > height
                  AND path NOT IN (SELECT photo_path FROM faces)
                ORDER BY (date_taken >= '2020-01-01') DESC, RANDOM() LIMIT 300
            """)
            candidates = c.fetchall()
            from scene_classifier import scene_cache
            for row in candidates:
                path = row[0]
                if path in blacklist or path in valid_photos:
                    continue
                if scene_cache.get(path) is True:
                    valid_photos.append(path)
                    if len(valid_photos) >= 50:
                        break

        # Fallback if too few nature/animal photos
        if len(valid_photos) < 5 and 'candidates' in dir():
            for row in candidates:
                if row[0] not in valid_photos and row[0] not in blacklist:
                    valid_photos.append(row[0])
                if len(valid_photos) >= 50:
                    break
    # Format URLs using quote (to handle spaces and special chars safely)
    from urllib.parse import quote
    photos_out = []
    for p in valid_photos:
        # We need to serve the high-res file
        safe_path = quote(p.replace('\\', '/'))
        photos_out.append(f"/api/photo/file/{safe_path}")
        
    return jsonify({"photos": photos_out})



@memories_bp.route('/api/memories/collections')
def api_memories_collections():
    conn = get_db_connection()
    c = conn.cursor()
    
    collections = []
    
    # 1. Featured Moment
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        collections.append({
            "type": "featured_moment",
            "title": "Featured Moment",
            "subtitle": "A trip down memory lane",
            "cover_photo": row[0],
            "photos": [{"file_path": row[0], "file_type": row[1], "date_taken": row[2]}]
        })

    # 2. Featured Video
    c.execute('''
        SELECT path as file_path, file_type, date_taken, size, width, height, hash as phash
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL AND file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM')
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        collections.append({
            "type": "featured_video",
            "title": "Featured Video",
            "subtitle": "Press play to relive",
            "cover_photo": row[0],
            "photos": [{"file_path": row[0], "file_type": row[1], "date_taken": row[2]}]
        })

    # 3. Album Pick
    c.execute('''
        SELECT id, name, cover_photo_path 
        FROM albums 
        WHERE cover_photo_path IS NOT NULL 
        ORDER BY RANDOM() LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        c.execute('SELECT path, file_type, date_taken FROM photos JOIN album_photos ON photos.path = album_photos.photo_path WHERE album_id = ? LIMIT 10', (row[0],))
        album_photos = [{"file_path": r[0], "file_type": r[1], "date_taken": r[2]} for r in c.fetchall()]
        if album_photos:
            collections.append({
                "type": "album_pick",
                "title": row[1],
                "subtitle": "From your albums",
                "cover_photo": row[2],
                "photos": album_photos,
                "album_id": row[0]
            })

    # 4. Spotlight on a Day
    c.execute('''
        SELECT strftime('%Y-%m-%d', date_taken) as day
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL 
          AND date_taken >= '2000-01-01'
        GROUP BY day
        HAVING count(*) >= 3
        ORDER BY RANDOM() LIMIT 1
    ''')
    day_row = c.fetchone()
    if day_row:
        day_str = day_row[0]
        c.execute('''
            SELECT path as file_path, file_type, date_taken
            FROM photos
            WHERE trashed_at IS NULL AND archived_at IS NULL 
              AND date_taken LIKE ?
            ORDER BY date_taken ASC
            LIMIT 15
        ''', (day_str + '%',))
        spotlight_photos = [{"file_path": r[0], "file_type": r[1], "date_taken": r[2]} for r in c.fetchall()]
        if spotlight_photos:
            try:
                date_obj = datetime.strptime(day_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d %b %Y')
            except:
                formatted_date = day_str
            collections.append({
                "type": "spotlight_day",
                "title": "Spotlight on a Day",
                "subtitle": formatted_date,
                "cover_photo": spotlight_photos[0]['file_path'],
                "photos": spotlight_photos
            })

    # 5. On This Day
    today_mm_dd = datetime.now().strftime('%m-%d')
    c.execute('''
        SELECT path as file_path, file_type, date_taken
        FROM photos
        WHERE substr(date_taken, 6, 5) = ? AND trashed_at IS NULL
        ORDER BY date_taken DESC
        LIMIT 10
    ''', (today_mm_dd,))
    otd_photos = c.fetchall()
    if otd_photos:
        years = sorted(list(set([r[2][:4] for r in otd_photos if r[2]])))
        if len(years) > 3:
            subtitle = f"{years[0]} - {years[-1]}"
        elif len(years) > 0:
            subtitle = ", ".join(years)
        else:
            subtitle = "Past Years"
            
        collections.append({
            "type": "on_this_day",
            "title": "On This Day",
            "subtitle": subtitle,
            "cover_photo": otd_photos[0][0],
            "photos": [{"file_path": r[0], "file_type": r[1], "date_taken": r[2]} for r in otd_photos]
        })

    # 6. Seasonal Vibes
    today = datetime.now()
    month = today.month
    if month in (12, 1, 2): 
        season_months, season_name = ('12', '01', '02'), 'Winter'
    elif month in (3, 4, 5): 
        season_months, season_name = ('03', '04', '05'), 'Spring'
    elif month in (6, 7, 8): 
        season_months, season_name = ('06', '07', '08'), 'Summer'
    else: 
        season_months, season_name = ('09', '10', '11'), 'Autumn'
        
    c.execute('''
        SELECT path, file_type, date_taken 
        FROM photos 
        WHERE trashed_at IS NULL AND archived_at IS NULL
        AND (substr(date_taken, 6, 2) IN (?, ?, ?))
        AND file_type IN ('JPG', 'JPEG', 'PNG')
        ORDER BY RANDOM() LIMIT 15
    ''', season_months)
    seasonal = c.fetchall()
    if seasonal:
        collections.append({
            "type": "seasonal",
            "title": f"{season_name} Vibes",
            "subtitle": "Memories from this season",
            "cover_photo": seasonal[0][0],
            "photos": [{"file_path": r[0], "file_type": r[1], "date_taken": r[2]} for r in seasonal]
        })

    # 7. Best of [Previous Month]
    from dateutil.relativedelta import relativedelta
    prev_month = today - relativedelta(months=1)
    prev_month_str = prev_month.strftime('%Y-%m')
    prev_month_name = prev_month.strftime('%B')
    c.execute('''
        SELECT path, file_type, date_taken
        FROM photos
        WHERE trashed_at IS NULL AND archived_at IS NULL
        AND date_taken LIKE ?
        ORDER BY RANDOM() LIMIT 15
    ''', (prev_month_str + '%',))
    best_of = c.fetchall()
    if best_of:
        collections.append({
            "type": "best_of_month",
            "title": f"Best of {prev_month_name}",
            "subtitle": "Highlights from last month",
            "cover_photo": best_of[0][0],
            "photos": [{"file_path": r[0], "file_type": r[1], "date_taken": r[2]} for r in best_of]
        })

    # 8. With Person
    c.execute('''
        SELECT p.id, p.name 
        FROM people p
        JOIN faces f ON f.person_id = p.id
        WHERE p.name IS NOT NULL AND p.name NOT LIKE 'Person %' AND p.name != 'Me'
        GROUP BY p.id
        HAVING count(f.id) >= 5
        ORDER BY RANDOM() LIMIT 1
    ''')
    person = c.fetchone()
    if person:
        pid, pname = person
        c.execute('''
            SELECT ph.path, ph.file_type, ph.date_taken
            FROM photos ph
            JOIN faces f ON f.photo_path = ph.path
            WHERE f.person_id = ? AND ph.trashed_at IS NULL
            ORDER BY RANDOM() LIMIT 15
        ''', (pid,))
        person_photos = c.fetchall()
        if person_photos:
            collections.append({
                "type": "with_person",
                "title": f"With {pname}",
                "subtitle": "Moments together",
                "cover_photo": person_photos[0][0],
                "photos": [{"file_path": r[0], "file_type": r[1], "date_taken": r[2]} for r in person_photos]
            })

    conn.close()
    
    # Shuffle slightly so they don't always appear in exact order, but maybe keep some order
    import random
    random.shuffle(collections)
    
    return jsonify({"success": True, "collections": collections})
