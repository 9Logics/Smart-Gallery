import re

with open('app/routes/photos.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """        conn.close()
        run_incremental_clustering()
        return jsonify({'success': True})"""

replacement = """        cursor.execute("SELECT * FROM photos WHERE path = ?", (photo_path,))
        updated_row = cursor.fetchone()
        updated_dict = {}
        if updated_row:
            columns = [column[0] for column in cursor.description]
            updated_dict = dict(zip(columns, updated_row))
            
        conn.close()
        run_incremental_clustering()
        return jsonify({'success': True, 'photo': updated_dict})"""

if target in py:
    py = py.replace(target, replacement)
    print("Replaced return successfully")
else:
    print("Target not found!")

with open('app/routes/photos.py', 'w', encoding='utf-8') as f:
    f.write(py)
