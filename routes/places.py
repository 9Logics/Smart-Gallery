from flask import Blueprint, request, jsonify, send_file
from app_globals import *

places_bp = Blueprint("places", __name__)

@places_bp.route('/api/places')
@cache_api(timeout=30)
def get_places():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT place_name, COUNT(path) as count, MIN(path) as sample_path
        FROM photos 
        WHERE place_name IS NOT NULL AND trashed_at IS NULL
        GROUP BY place_name 
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    places = [{"name": r[0], "count": r[1], "sample_path": r[2]} for r in rows]
    return jsonify(places)


@places_bp.route('/api/places/map_data')
def get_places_map_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT path, latitude, longitude, place_name 
        FROM photos 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND trashed_at IS NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    
    data = []
    for r in rows:
        data.append({
            "path": r[0],
            "latitude": r[1],
            "longitude": r[2],
            "place_name": r[3]
        })
    return jsonify(data)


@places_bp.route('/api/places/rework_grouping', methods=['POST'])
def rework_places_grouping():
    data = request.json or {}
    threshold = int(data.get('threshold', 3))
    
    try:
        update_smart_location_tags(threshold=threshold)
        return jsonify({"success": True, "threshold": threshold})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Albums APIs

