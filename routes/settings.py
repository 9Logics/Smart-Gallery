from flask import Blueprint, request, jsonify, send_file
from app_globals import *

settings_bp = Blueprint("settings", __name__)

@settings_bp.route('/api/settings/scan-folder', methods=['POST'])
def save_scan_folder():
    data = request.json
    folder = data.get('folder', '').strip()
    if not folder or not os.path.exists(folder):
        return jsonify({"error": "Invalid folder path or folder does not exist"}), 400
        
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('scan_folder', ?)", (folder,))
    conn.commit()
    conn.close()
    
    # Trigger scanning
    started = start_scan_thread(folder)
    return jsonify({"success": True, "started": started})


@settings_bp.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json or {}
        for k, v in data.items():
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    else:
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        conn.close()
        settings_dict = {r[0]: r[1] for r in rows}
        if "scan_folder" not in settings_dict:
            settings_dict["scan_folder"] = ""
        if "google_maps_key" not in settings_dict:
            settings_dict["google_maps_key"] = ""
        return jsonify(settings_dict)

def parse_smart_dates(query):
    query = query.lower().strip()
    results = []
    
    # 1. Year: exactly 4 digits
    if re.match(r'^\d{4}$', query):
        results.append({"year": query})
        
    # 2. Month name prefix
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    if query.isalpha():
        for i, m in enumerate(months):
            if m.startswith(query):
                results.append({"month": f"{i+1:02d}"})
                
    if results:
        return results
            
    # 3. Day + Month (e.g. 25th august, august 25, 10a, a 10)
    day_month_regex = re.match(r'^(\d{1,2})(?:st|nd|rd|th)?\s*([a-z]+)$', query)
    month_day_regex = re.match(r'^([a-z]+)\s*(\d{1,2})(?:st|nd|rd|th)?$', query)
    
    d_str = None
    m_str = None
    
    if day_month_regex:
        d_str, m_str = day_month_regex.groups()
    elif month_day_regex:
        m_str, d_str = month_day_regex.groups()
        
    if d_str and m_str:
        d = f"{int(d_str):02d}"
        for i, m in enumerate(months):
            if m.startswith(m_str):
                results.append({"month": f"{i+1:02d}", "day": d})
                
    if results:
        return results

    # 4. DD-MM-YYYY or MM-DD-YYYY or YYYY-MM-DD
    date_match = re.match(r'^(\d{2})[-/.](\d{2})[-/.](\d{4})$', query)
    if date_match:
        p1, p2, p3 = date_match.groups()
        # assume DD-MM-YYYY
        results.append({"year": p3, "month": p2, "day": p1})
        
    date_match_rev = re.match(r'^(\d{4})[-/.](\d{2})[-/.](\d{2})$', query)
    if date_match_rev:
        p1, p2, p3 = date_match_rev.groups()
        results.append({"year": p1, "month": p2, "day": p3})

    # 5. Condensed format like 121024 or 12-01-2004 without hyphens
    cond_match = re.match(r'^(\d{2})(\d{2})(\d{2})$', query)
    if cond_match:
        d, m, y = cond_match.groups()
        # Assume 2000s for two digit year
        results.append({"year": "20" + y, "month": m, "day": d})

    # 6. Single 1-2 digit number -> Day
    if re.match(r'^\d{1,2}$', query) or re.match(r'^\d{1,2}(?:st|nd|rd|th)$', query):
        d = re.sub(r'\D', '', query)
        results.append({"day": f"{int(d):02d}"})
        
    return results

def build_date_sql(parsed_date, table_alias="p"):
    if not parsed_date:
        return None, []
    
    conds = []
    params = []
    if "year" in parsed_date:
        conds.append(f"strftime('%Y', {table_alias}.date_taken) = ?")
        params.append(parsed_date["year"])
    if "month" in parsed_date:
        conds.append(f"strftime('%m', {table_alias}.date_taken) = ?")
        params.append(parsed_date["month"])
    if "day" in parsed_date:
        conds.append(f"strftime('%d', {table_alias}.date_taken) = ?")
        params.append(parsed_date["day"])
        
    if conds:
        return " AND ".join(conds), params
    return None, []


import json

OVERRIDES_CACHE_FILE = os.path.join(CACHE_DIR, 'hero_overrides.json')

def load_hero_overrides():
    if os.path.exists(OVERRIDES_CACHE_FILE):
        try:
            with open(OVERRIDES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"whitelist": [], "blacklist": []}
    return {"whitelist": [], "blacklist": []}

def save_hero_overrides(data):
    with open(OVERRIDES_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)


@settings_bp.route('/api/settings/hero_overrides', methods=['GET'])
def get_hero_overrides():
    return jsonify(load_hero_overrides())


@settings_bp.route('/api/settings/hero_override', methods=['POST'])
def add_hero_override():
    data = request.json
    path = data.get('path')
    status = data.get('status') # 'whitelist' or 'blacklist' or 'remove'
    if not path or not status:
        return jsonify({"error": "Missing path or status"}), 400
    
    overrides = load_hero_overrides()
    if path in overrides['whitelist']: overrides['whitelist'].remove(path)
    if path in overrides['blacklist']: overrides['blacklist'].remove(path)
    
    if status == 'whitelist':
        overrides['whitelist'].append(path)
    elif status == 'blacklist':
        overrides['blacklist'].append(path)
        
    save_hero_overrides(overrides)
    return jsonify({"success": True})


@settings_bp.route('/api/settings/hero_scenic_photos')
def get_hero_scenic_photos():
    """Return all photos the AI scene classifier has indexed as scenic/nature."""
    from scene_classifier import scene_cache
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    
    scenic_paths = [p for p, v in scene_cache.items() if v is True]
    total = len(scenic_paths)
    start = (page - 1) * per_page
    end = start + per_page
    paged = scenic_paths[start:end]
    
    return jsonify({"photos": [{"path": p} for p in paged], "total": total, "page": page})


@settings_bp.route('/api/settings/hero_all_photos')
def get_hero_all_photos():
    """Return paginated photos for hero whitelist picker."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    search = request.args.get('search', '').strip()
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    c = conn.cursor()
    
    if search:
        c.execute("""
            SELECT path, filename FROM photos 
            WHERE trashed_at IS NULL AND archived_at IS NULL
              AND (filename LIKE ? OR path LIKE ? OR place_name LIKE ?)
            ORDER BY date_taken DESC LIMIT ? OFFSET ?
        """, (f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
    else:
        c.execute("""
            SELECT path, filename FROM photos 
            WHERE trashed_at IS NULL AND archived_at IS NULL
            ORDER BY date_taken DESC LIMIT ? OFFSET ?
        """, (per_page, offset))
    
    rows = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM photos WHERE trashed_at IS NULL AND archived_at IS NULL")
    total = c.fetchone()[0]
    conn.close()
    
    return jsonify({"photos": [{"path": r[0], "filename": r[1]} for r in rows], "total": total, "page": page})


