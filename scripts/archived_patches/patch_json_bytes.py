import re

with open('app/routes/photos.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """            updated_dict = dict(zip(columns, updated_row))
            
        conn.close()
        run_incremental_clustering()
        return jsonify({'success': True, 'photo': updated_dict})"""

replacement = """            updated_dict = dict(zip(columns, updated_row))
            # Fix JSON serialization of bytes (e.g. from EXIF strings stored as BLOB)
            for k, v in updated_dict.items():
                if isinstance(v, bytes):
                    try:
                        updated_dict[k] = v.decode('utf-8', errors='ignore')
                    except:
                        updated_dict[k] = v.hex()
            
        conn.close()
        run_incremental_clustering()
        return jsonify({'success': True, 'photo': updated_dict})"""

if target in py:
    py = py.replace(target, replacement)
    print("Replaced JSON serialization successfully")
else:
    print("Target not found!")

with open('app/routes/photos.py', 'w', encoding='utf-8') as f:
    f.write(py)
