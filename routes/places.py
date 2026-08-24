from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template
import os, json, sqlite3, time, datetime, shutil
from app_core import *

places_bp = Blueprint('places', __name__)

@places_bp.route('/api/places')
@cache_api(timeout=30)
def get_places():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.place_name, MIN(p.path), COUNT(p.path), c.place_name 
        FROM photos p
        LEFT JOIN geocoding_cache c ON round(p.latitude, 3) = c.lat_rounded AND round(p.longitude, 3) = c.lon_rounded
        WHERE p.place_name IS NOT NULL 
          AND p.trashed_at IS NULL
          AND NOT (p.latitude = 0 AND p.longitude = 0)
        GROUP BY p.place_name
    """
        )
    rows = cursor.fetchall()
    conn.close()
    cities = {}
    for place_name, sample_path, count, json_str in rows:
        city = 'Unknown Location'
        if json_str:
            try:
                data = json.loads(json_str)
                addr = data.get('address', {})
                for k in ['city', 'county', 'state_district', 'state']:
                    if k in addr:
                        city = addr[k]
                        break
            except:
                pass
        if city not in cities:
            cities[city] = []
        cities[city].append({'name': place_name, 'count': count,
            'sample_path': sample_path})
    result = []
    for city, places in cities.items():
        places.sort(key=lambda x: x['count'], reverse=True)
        result.append({'city': city, 'places': places, 'total_count': sum(p
            ['count'] for p in places)})
    result.sort(key=lambda x: x['total_count'], reverse=True)
    return jsonify(result)

@places_bp.route('/api/places/map_data')
def get_places_map_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT path, latitude, longitude, place_name 
        FROM photos 
        WHERE latitude IS NOT NULL 
          AND longitude IS NOT NULL 
          AND trashed_at IS NULL
          AND NOT (latitude = 0 AND longitude = 0)
    """
        )
    rows = cursor.fetchall()
    conn.close()
    data = []
    for r in rows:
        data.append({'path': r[0], 'latitude': r[1], 'longitude': r[2],
            'place_name': r[3]})
    return jsonify(data)

@places_bp.route('/api/places/rework_grouping', methods=['POST'])
def rework_places_grouping():
    data = request.json or {}
    threshold = int(data.get('threshold', 3))
    try:
        update_smart_location_tags(threshold=threshold)
        return jsonify({'success': True, 'threshold': threshold})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

