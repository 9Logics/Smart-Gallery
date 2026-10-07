import sqlite3
import json
import os

DB_PATH = '.cache/gallery.db'

def fix_json_locations():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find all photos where place_name looks like a JSON string
    cursor.execute("SELECT path, place_name FROM photos WHERE place_name LIKE '{%'")
    rows = cursor.fetchall()
    
    fixed_count = 0
    for path, place_name in rows:
        try:
            data = json.loads(place_name)
            # Try to get a smart hierarchy name, or fallback to display_name
            valid_keys = [
                'amenity', 'building', 'shop', 'office', 'historic', 'tourism', 'leisure', 'aeroway',
                'neighbourhood', 'suburb', 'village', 'hamlet', 'town', 'city_district', 'borough',
                'city', 'county', 'state_district', 'state', 'country'
            ]
            addr = data.get('address', {})
            fallback = data.get('display_name', '')
            
            for k in valid_keys:
                if k in addr:
                    fallback = addr[k]
                    break
                    
            cursor.execute("UPDATE photos SET place_name = ? WHERE path = ?", (fallback, path))
            fixed_count += 1
        except Exception as e:
            print(f"Failed to parse {path}: {e}")
            
    conn.commit()
    conn.close()
    print(f"Fixed {fixed_count} photos that had raw JSON locations.")

if __name__ == "__main__":
    fix_json_locations()
