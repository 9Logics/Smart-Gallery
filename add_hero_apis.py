import sys

def modify_app():
    with open('app.py', 'r', encoding='utf-8') as f:
        text = f.read()
        
    # 1. Update /api/photo/refresh
    refresh_addition = \"\"\"
        # 5. Clear thumbnails
        from file_ops import get_thumbnail_path
        thumb_path = get_thumbnail_path(photo_path)
        if os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except:
                pass
                
        # 6. Re-run Hero AI
        from scene_classifier import check_scene, scene_cache, save_scene_cache
        is_scenic = check_scene(photo_path)
        scene_cache[photo_path] = is_scenic
        save_scene_cache()
        
        return jsonify({"success": True})\"\"\"
    
    text = text.replace('        return jsonify({"success": True})', refresh_addition, 1)
    
    # 2. Add new endpoints
    new_endpoints = \"\"\"
@app.route('/api/memories/hero/blacklist', methods=['POST'])
def api_hero_blacklist():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"error": "path required"}), 400
        
    overrides = load_hero_overrides()
    if 'blacklist' not in overrides:
        overrides['blacklist'] = []
    if path not in overrides['blacklist']:
        overrides['blacklist'].append(path)
        save_hero_overrides(overrides)
        
    return jsonify({"success": True})

@app.route('/api/memories/hero/scan_more', methods=['POST'])
def api_hero_scan_more():
    # Silently scan up to 50 more photos for the hero banner
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT file_path FROM (
                SELECT path as file_path
                FROM photos
                WHERE trashed_at IS NULL
                  AND archived_at IS NULL
                  AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
                  AND width > height
                  AND path NOT IN (SELECT photo_path FROM faces)
                ORDER BY date_taken DESC LIMIT 1000
            )
            ORDER BY RANDOM() LIMIT 200
        ''')
        candidates = c.fetchall()
        conn.close()
        
        overrides = load_hero_overrides()
        blacklist = set(overrides.get('blacklist', []))
        
        from scene_classifier import check_scene, scene_cache, save_scene_cache
        added = 0
        for row in candidates:
            path = row[0]
            if path in blacklist:
                continue
            if path not in scene_cache:
                is_scenic = check_scene(path)
                scene_cache[path] = is_scenic
                if is_scenic:
                    added += 1
                if added >= 50:
                    break
        save_scene_cache()
        return jsonify({"success": True, "added": added})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
\"\"\"
    
    text += new_endpoints
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(text)
        
if __name__ == '__main__':
    modify_app()
