import re

with open('app/routes/photos.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """def refresh_single_photo():
    data = request.json
    photo_path = data.get('path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'file_missing'}), 404
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        meta = extract_metadata(photo_path)
        place = None"""

replacement = """def refresh_single_photo():
    data = request.json
    photo_path = data.get('path')
    if not photo_path or not os.path.exists(photo_path):
        return jsonify({'error': 'file_missing'}), 404
    try:
        # 1. Delete existing thumbnail so it regenerates
        thumb_path = get_thumbnail_path(photo_path)
        if os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except:
                pass
                
        conn = get_db_connection()
        cursor = conn.cursor()
        meta = extract_metadata(photo_path)
        place = None"""

if target in py:
    py = py.replace(target, replacement)
    print("Replaced refresh_single_photo")
else:
    print("Target not found in photos.py!")

with open('app/routes/photos.py', 'w', encoding='utf-8') as f:
    f.write(py)
