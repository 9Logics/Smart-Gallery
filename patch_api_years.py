import os
import re

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

# Inject the new endpoint right before the generate recap endpoint
new_endpoint = '''@photos_bp.route('/api/recap/years', methods=['GET'])
def get_recap_years():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT substr(date_taken, 1, 4) as year, COUNT(*) as count 
            FROM photos 
            WHERE date_taken IS NOT NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'mp4', 'mov', 'avi')
            GROUP BY year 
            HAVING CAST(year AS INTEGER) >= 2000 AND count >= 5
            ORDER BY year DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        years = [r[0] for r in rows]
        return jsonify({'success': True, 'years': years})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/api/recap/generate/<year>')'''

py = py.replace("@photos_bp.route('/api/recap/generate/<year>')", new_endpoint)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Added /api/recap/years endpoint!")
