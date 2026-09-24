import os

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

new_route = '''
@photos_bp.route('/api/recap/generate/<year>')
def generate_recap(year):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total Photos
    cursor.execute("SELECT COUNT(*) FROM photos WHERE date_taken LIKE ? AND file_type IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')", (f"{year}-%",))
    total_photos = cursor.fetchone()[0] or 0
    
    # 2. Total Videos
    cursor.execute("SELECT COUNT(*) FROM photos WHERE date_taken LIKE ? AND file_type IN ('mp4', 'mov', 'avi', 'mkv', 'webm')", (f"{year}-%",))
    total_videos = cursor.fetchone()[0] or 0
    
    # 3. Top Person
    cursor.execute("""
        SELECT p.name, COUNT(*) as c 
        FROM people p 
        JOIN faces f ON f.person_id = p.id 
        JOIN photos ph ON f.photo_path = ph.path 
        WHERE ph.date_taken LIKE ? AND p.name != 'Me' AND p.name IS NOT NULL AND p.name != 'Unknown'
        GROUP BY p.name 
        ORDER BY c DESC 
        LIMIT 1
    """, (f"{year}-%",))
    person_row = cursor.fetchone()
    top_person = person_row[0] if person_row else None
    
    # 4. Iconic Place
    cursor.execute("""
        SELECT place_name, COUNT(*) as c 
        FROM photos 
        WHERE date_taken LIKE ? AND place_name IS NOT NULL AND place_name != '' AND place_name != 'Unknown'
        GROUP BY place_name 
        ORDER BY c DESC 
        LIMIT 1
    """, (f"{year}-%",))
    place_row = cursor.fetchone()
    iconic_place = place_row[0] if place_row else None
    
    # 5. Memorable Moment (Favorite photo from that year, or just a random photo)
    cursor.execute("""
        SELECT path FROM photos 
        WHERE date_taken LIKE ? AND is_favorite = 1 
        ORDER BY RANDOM() LIMIT 1
    """, (f"{year}-%",))
    moment_row = cursor.fetchone()
    if not moment_row:
        cursor.execute("SELECT path FROM photos WHERE date_taken LIKE ? ORDER BY RANDOM() LIMIT 1", (f"{year}-%",))
        moment_row = cursor.fetchone()
        
    memorable_moment = moment_row[0] if moment_row else None
    
    # Generate AI-like comment based on stats
    comments = []
    if total_photos > 1000:
        comments.append(f"What a massive year! You captured {total_photos} incredible moments.")
    elif total_photos > 0:
        comments.append(f"This year was a wild ride! You saved {total_photos} special memories.")
    else:
        comments.append(f"A quiet year in the gallery, but every moment counts.")
        
    if iconic_place:
        comments.append(f"From exploring {iconic_place} to everyday life,")
        
    if top_person:
        comments.append(f"you spent a lot of time with {top_person}.")
        
    ai_comment = " ".join(comments)
    
    return jsonify({
        'year': year,
        'total_photos': total_photos,
        'total_videos': total_videos,
        'top_person': top_person,
        'iconic_place': iconic_place,
        'memorable_moment': memorable_moment,
        'ai_comment': ai_comment
    })
'''

# Insert the route before the last route or just at the end of the file.
if '@photos_bp.route(\'/api/recap/generate/<year>\')' not in py:
    py += new_route
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(py)
    print("Added /api/recap/generate/<year> route!")
else:
    print("Route already exists!")
