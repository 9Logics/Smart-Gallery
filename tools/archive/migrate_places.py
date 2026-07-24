import sqlite3
import time
import json
import urllib.request
import os

DB_PATH = '.cache/gallery.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def migrate_places():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get all unique lat/lon pairs from photos table
    cursor.execute("SELECT DISTINCT round(latitude, 3), round(longitude, 3) FROM photos WHERE latitude IS NOT NULL")
    locations = cursor.fetchall()
    
    print(f"Found {len(locations)} unique locations to migrate.")
    
    # 2. Clear old geocoding cache (it just had string names)
    cursor.execute("DELETE FROM geocoding_cache")
    conn.commit()
    
    # 3. Fetch full JSON for each location and populate cache
    for lat_r, lon_r in locations:
        if lat_r is None or lon_r is None:
            continue
            
        print(f"Fetching JSON for {lat_r}, {lon_r}...")
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat_r}&lon={lon_r}&zoom=18&addressdetails=1"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'LocalSmartGalleryApp/1.0 (contact@anurag.dev)'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                place_json = json.dumps(data)
                
                cursor.execute(
                    "INSERT INTO geocoding_cache (lat_rounded, lon_rounded, place_name) VALUES (?, ?, ?)",
                    (lat_r, lon_r, place_json)
                )
                conn.commit()
        except Exception as e:
            print(f"Failed for {lat_r}, {lon_r}: {e}")
            
        # Respect Nominatim 1 req/sec limit
        time.sleep(1.2)
        
    conn.close()
    
    # 4. Run the smart tagging algorithm
    print("Running smart tagging algorithm...")
    from app import update_smart_location_tags
    update_smart_location_tags()
    
    print("Migration complete!")

if __name__ == "__main__":
    migrate_places()
