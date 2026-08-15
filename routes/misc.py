from flask import Blueprint, request, jsonify, send_file
from app_globals import *

misc_bp = Blueprint("misc", __name__)

@misc_bp.route('/')
def index():
    return render_template('index.html')


@misc_bp.route('/api/search/suggestions')
def get_search_suggestions():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
        
    parsed_list = parse_smart_dates(q)
    suggestions = []
    
    if parsed_list:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for parsed in parsed_list:
            # Check if any photos exist for this parsed date
            cond_sql, cond_params = build_date_sql(parsed, "photos")
            if cond_sql:
                cursor.execute(f"SELECT COUNT(*) FROM photos WHERE {cond_sql} AND trashed_at IS NULL", cond_params)
                count = cursor.fetchone()[0]
                if count > 0:
                    # Format a nice readable string
                    parts = []
                    if "day" in parsed: parts.append(str(int(parsed["day"])))
                    if "month" in parsed: 
                        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                        parts.append(months[int(parsed["month"])-1])
                    if "year" in parsed: parts.append(parsed["year"])
                    
                    label = " ".join(parts)
                    suggestions.append({
                        "type": "date",
                        "id": label, # We pass the expanded label as ID so clicking it sends the unambiguous label
                        "label": label,
                        "description": f"Date Filter ({count} photos)"
                    })
        conn.close()
        
    return jsonify(suggestions)


@misc_bp.route('/api/duplicates')
def get_duplicates():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Find duplicate hashes
    cursor.execute("""
        SELECT hash, COUNT(*) as count 
        FROM photos 
        WHERE hash IS NOT NULL AND hash != '' AND trashed_at IS NULL
        GROUP BY hash 
        HAVING count > 1
    """)
    dup_hashes = [r[0] for r in cursor.fetchall()]
    
    duplicates = []
    for h in dup_hashes:
        cursor.execute("""
            SELECT path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash 
            FROM photos 
            WHERE hash = ? AND trashed_at IS NULL
        """, (h,))
        rows = cursor.fetchall()
        
        # Partition rows into compatible duplicate clusters
        clusters = []
        for r in rows:
            path = r[0]
            size = r[5]
            is_vid = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            
            placed = False
            for cluster in clusters:
                rep = cluster[0]
                rep_path = rep[0]
                rep_size = rep[5]
                rep_is_vid = rep_path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
                
                # Must be same media type (both videos or both images)
                if is_vid != rep_is_vid:
                    continue
                
                # Must be similar in size: ratio <= 2.0 or absolute difference <= 100 KB
                ratio = max(size, rep_size) / max(min(size, rep_size), 1)
                abs_diff = abs(size - rep_size)
                if ratio <= 2.0 or abs_diff <= 102400:
                    cluster.append(r)
                    placed = True
                    break
            
            if not placed:
                clusters.append([r])
                
        # Filter for actual duplicate clusters (size > 1)
        valid_clusters = [c for c in clusters if len(c) > 1]
        
        for cluster_idx, cluster in enumerate(valid_clusters):
            analyzed = []
            for r in cluster:
                clean_name, is_copy = analyze_filename(r[1])
                score = get_metadata_score(r)
                analyzed.append({
                    "row": r,
                    "clean_name": clean_name,
                    "is_copy": is_copy,
                    "score": score
                })
                
            def sort_key(item):
                r = item["row"]
                return (
                    item["score"],
                    -1 if item["is_copy"] else 1,
                    r[5],
                    r[3] * r[4]
                )
                
            analyzed.sort(key=sort_key, reverse=True)
            keep_item = analyzed[0]
            delete_items = analyzed[1:]
            
            action = "KEEP_AS_IS"
            reason = ""
            
            if keep_item["is_copy"]:
                non_copies = [x for x in delete_items if not x["is_copy"]]
                if non_copies:
                    action = "KEEP_AND_RENAME"
                    reason = "Kept copy due to better metadata; duplicate suffix will be removed."
                else:
                    reason = "Kept copy as original (only copies exist)."
            else:
                copies = [x for x in delete_items if x["is_copy"]]
                if copies:
                    reason = "Kept original; suggested deleting copies."
                else:
                    reason = "Kept highest quality original."
                    
            def format_photo(r):
                return {
                    "path": r[0],
                    "filename": r[1],
                    "date_taken": r[2],
                    "width": r[3],
                    "height": r[4],
                    "size": r[5],
                    "file_type": r[6],
                    "latitude": r[7],
                    "longitude": r[8],
                    "place_name": r[9]
                }
                
            group_hash = f"{h}_{cluster_idx}"
            duplicates.append({
                "hash": group_hash,
                "keep": format_photo(keep_item["row"]),
                "delete": [format_photo(x["row"]) for x in delete_items],
                "action": action,
                "reason": reason
            })
            
    conn.close()
    return jsonify(duplicates)

def send_file_to_trash(path):
    """
    Tags a file for deletion by returning success.
    The actual physical file is not moved until the user purges it.
    Returns: (success_bool, original_path, error_str_or_None)
    """
    if not os.path.exists(path):
        return False, None, "File does not exist on disk"
        
    try:
        # We no longer move the file to an internal trash dir.
        # Just return the original path so the DB record can be updated with trashed_at.
        return True, path, None
    except Exception as e:
        print(f"Error trashing file {path}: {e}")
        return False, None, str(e)


@misc_bp.route('/api/duplicates/resolve', methods=['POST'])
def resolve_duplicates():
    data = request.json
    resolutions = data.get('resolutions', [])
    
    if not resolutions:
        return jsonify({"error": "No resolutions provided"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    deleted_paths = []
    renamed_paths = []
    
    try:
        # First, move all files scheduled for deletion to Recycle Bin
        for res in resolutions:
            del_path = res.get('delete_path')
            if del_path and os.path.exists(del_path):
                success, trash_path, err = send_file_to_trash(del_path)
                # Mark as trashed in database regardless of physical move success to keep UI responsive
                cursor.execute("UPDATE photos SET trashed_at = ? WHERE path = ?", 
                               (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), del_path))
                deleted_paths.append(del_path)
                
        # Commit deletions to ensure paths are cleared
        conn.commit()
        
        # Second, perform renames if requested
        for res in resolutions:
            action = res.get('action')
            if action == 'KEEP_AND_RENAME':
                keep_path = res.get('keep_path')
                if keep_path and os.path.exists(keep_path):
                    filename = os.path.basename(keep_path)
                    clean_name, _ = analyze_filename(filename)
                    new_path = os.path.join(os.path.dirname(keep_path), clean_name)
                    
                    # Safety check: ensure target does not exist or was just moved to trash
                    if not os.path.exists(new_path) or new_path in deleted_paths:
                        try:
                            shutil.move(keep_path, new_path)
                            renamed_paths.append((keep_path, new_path))
                            
                            # Rename thumbnail
                            old_thumb = get_thumbnail_path(keep_path)
                            new_thumb = get_thumbnail_path(new_path)
                            if os.path.exists(old_thumb):
                                if os.path.exists(new_thumb):
                                    os.remove(new_thumb)
                                shutil.move(old_thumb, new_thumb)
                                
                            # Update database records manually
                            cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (new_path, keep_path))
                            cursor.execute("UPDATE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, keep_path))
                            cursor.execute("UPDATE photos SET path = ?, filename = ? WHERE path = ?", (new_path, clean_name, keep_path))
                        except Exception as rename_err:
                            print(f"Error renaming resolved duplicate {keep_path} to {new_path}: {rename_err}")
                            
        conn.commit()
        success = True
        error = None
    except Exception as e:
        conn.rollback()
        success = False
        error = str(e)
    finally:
        conn.close()
        
    if not success:
        return jsonify({"error": f"Failed to resolve duplicates: {error}"}), 500
        
    return jsonify({"success": True, "deleted": len(deleted_paths), "renamed": len(renamed_paths)})


@misc_bp.route('/api/archive/move', methods=['POST'])
def archive_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        try:
            cursor.execute("UPDATE photos SET archived_at = ? WHERE path = ?", 
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), path))
            success_count += 1
        except Exception as e:
            print(f"Error archiving {path}: {e}")
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})


@misc_bp.route('/api/archive/restore', methods=['POST'])
def unarchive_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        try:
            cursor.execute("UPDATE photos SET archived_at = NULL WHERE path = ?", (path,))
            success_count += 1
        except Exception as e:
            print(f"Error unarchiving {path}: {e}")
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})


@misc_bp.route('/api/trash/move', methods=['POST'])
def trash_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        if os.path.exists(path):
            success, trash_path, err = send_file_to_trash(path)
            # Mark as trashed in database regardless of physical move success to keep UI responsive
            cursor.execute("UPDATE photos SET trashed_at = ? WHERE path = ?", 
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), path))
            success_count += 1
                
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})


@misc_bp.route('/api/trash/restore', methods=['POST'])
def restore_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for path in photo_paths:
        file_hash = hashlib.md5(path.encode('utf-8')).hexdigest()
        ext = os.path.splitext(path)[1]
        trash_path = os.path.join(TRASH_DIR, file_hash + ext)
        
        if os.path.exists(trash_path):
            # Ensure target parent folder exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                # Physically move back
                os.rename(trash_path, path)
                # Clear trashed_at in DB
                cursor.execute("UPDATE photos SET trashed_at = NULL WHERE path = ?", (path,))
                success_count += 1
            except Exception as e:
                print(f"Error restoring {path} from trash: {e}")
                
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})


@misc_bp.route('/api/trash/empty', methods=['POST'])
def empty_trash():
    return jsonify({"error": "Empty trash is disabled. Delete items individually."}), 400


@misc_bp.route('/api/trash/purge', methods=['POST'])
def purge_photos():
    data = request.json
    photo_paths = data.get('photos', [])
    if not photo_paths:
        return jsonify({"error": "No photos provided"}), 400
        
    success_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    
    import send2trash
    
    for path in photo_paths:
        try:
            # Send original file to Windows Recycle Bin
            if os.path.exists(path):
                send2trash.send2trash(path)
            # Delete thumbnail, face crops, and DB records
            completely_delete_photo_data(cursor, path)
            success_count += 1
        except Exception as e:
            print(f"Error purging file {path}: {e}")
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "count": success_count})


@misc_bp.route('/api/metadata/rescan', methods=['POST'])
def manual_metadata_rescan():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        root_dir = row[0] if row else None
        
    def rescan_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Tracking moved/missing files"
            scan_status["processed"] = 0
            scan_status["total"] = 0
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT path, filename, size FROM photos")
            photos = cursor.fetchall()
            
            missing_photos = []
            for p, f, s in photos:
                if not os.path.exists(p):
                    missing_photos.append((p, f, s))
                    
            if root_dir and missing_photos:
                # Map available files in root_dir
                print("Scanning for moved files...")
                available_files = {}
                roots_to_scan = [root_dir]
                scanned_roots = set()
                
                shell = None
                try:
                    import win32com.client
                    import pythoncom
                    pythoncom.CoInitialize()
                    shell = win32com.client.Dispatch("WScript.Shell")
                except ImportError:
                    pass
                    
                while roots_to_scan:
                    current_root = roots_to_scan.pop(0)
                    real_root = os.path.realpath(current_root)
                    if real_root in scanned_roots:
                        continue
                    scanned_roots.add(real_root)
                    
                    for root, dirs, files in os.walk(current_root):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
                            ext = os.path.splitext(file)[1].lower()
                            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mp4', '.mov', '.m4v', '.hevc']:
                                p = os.path.join(root, file)
                                try:
                                    s = os.path.getsize(p)
                                    available_files[(file, s)] = p
                                except:
                                    pass
                            elif ext == '.lnk' and shell:
                                try:
                                    shortcut = shell.CreateShortCut(os.path.join(root, file))
                                    if os.path.isdir(shortcut.Targetpath):
                                        roots_to_scan.append(shortcut.Targetpath)
                                except Exception:
                                    pass
                                
                for old_path, fname, fsize in missing_photos:
                    new_path = available_files.get((fname, fsize))
                    if new_path:
                        print(f"Moved file found: {old_path} -> {new_path}")
                        cursor.execute("SELECT 1 FROM photos WHERE path = ?", (new_path,))
                        if cursor.fetchone():
                            # new_path is already in DB! Merge data to it.
                            cursor.execute("UPDATE OR IGNORE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE OR IGNORE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            completely_delete_photo_data(cursor, old_path)
                        else:
                            cursor.execute("UPDATE photos SET path = ? WHERE path = ?", (new_path, old_path))
                            cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                    else:
                        print(f"File permanently deleted: {old_path}")
                        completely_delete_photo_data(cursor, old_path)
                conn.commit()
            
            # Now trigger a full metadata re-extraction for everything? That might be slow.
            # The prompt said "Forces a re-extraction of date_taken and place_name for all files"
            cursor.execute("SELECT path FROM photos")
            all_paths = [r[0] for r in cursor.fetchall()]
            
            with scan_lock:
                scan_status["phase"] = "Refreshing EXIF & Dates"
                scan_status["total"] = len(all_paths)
                
            for i, p in enumerate(all_paths):
                if os.path.exists(p):
                    meta = extract_metadata(p)
                    # Don't overwrite place if it's already there? Wait, the user wants to refresh places later.
                    cursor.execute("UPDATE photos SET date_taken = ?, width = ?, height = ?, size = ?, file_type = ?, latitude = ?, longitude = ? WHERE path = ?", 
                                   (meta["date_taken"], meta["width"], meta["height"], meta["size"], meta["file_type"], meta["latitude"], meta["longitude"], p))
                with scan_lock:
                    scan_status["processed"] = i + 1
                    
            conn.commit()
        except Exception as e:
            print(f"Error in metadata rescan: {e}")
        finally:
            conn.close()
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=rescan_task, daemon=True).start()
    return jsonify({"success": True, "message": "Metadata rescan started"})



@misc_bp.route('/api/metadata/refresh_places', methods=['POST'])
def manual_refresh_places():
    def refresh_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Refreshing Places Geocoding"
            scan_status["processed"] = 0
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Clear geocoding cache to force fresh pull
            cursor.execute("DELETE FROM geocoding_cache")
            conn.commit()
            
            cursor.execute("SELECT path, latitude, longitude FROM photos WHERE latitude IS NOT NULL")
            photos = cursor.fetchall()
            
            with scan_lock:
                scan_status["total"] = len(photos)
                
            for i, (p, lat, lon) in enumerate(photos):
                place = reverse_geocode(lat, lon)
                if place:
                    cursor.execute("UPDATE photos SET place_name = ? WHERE path = ?", (place, p))
                    conn.commit()
                with scan_lock:
                    scan_status["processed"] = i + 1
        except Exception as e:
            print(f"Error in refreshing places: {e}")
        finally:
            conn.close()
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=refresh_task, daemon=True).start()
    return jsonify({"success": True, "message": "Places refresh started"})


@misc_bp.route('/api/cache/rebuild', methods=['POST'])
def rebuild_cache_and_mapping():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        root_dir = row[0] if row else None
        
    def rebuild_task():
        global scan_status
        with scan_lock:
            scan_status["status"] = "scanning"
            scan_status["phase"] = "Rebuilding Mapping & Cache"
            scan_status["processed"] = 0
            scan_status["total"] = 0
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Update mappings / remove deleted files
            cursor.execute("SELECT path, filename, size FROM photos")
            photos = cursor.fetchall()
            
            missing_photos = []
            for p, f, s in photos:
                if not os.path.exists(p):
                    missing_photos.append((p, f, s))
                    
            if root_dir and missing_photos:
                print("Scanning for moved files...")
                available_files = {}
                roots_to_scan = [root_dir]
                scanned_roots = set()
                
                shell = None
                try:
                    import win32com.client
                    import pythoncom
                    pythoncom.CoInitialize()
                    shell = win32com.client.Dispatch("WScript.Shell")
                except ImportError:
                    pass
                    
                while roots_to_scan:
                    current_root = roots_to_scan.pop(0)
                    real_root = os.path.realpath(current_root)
                    if real_root in scanned_roots:
                        continue
                    scanned_roots.add(real_root)
                    
                    for root, dirs, files in os.walk(current_root):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
                            ext = os.path.splitext(file)[1].lower()
                            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mp4', '.mov', '.m4v', '.hevc']:
                                p = os.path.join(root, file)
                                try:
                                    s = os.path.getsize(p)
                                    available_files[(file, s)] = p
                                except:
                                    pass
                            elif ext == '.lnk' and shell:
                                try:
                                    shortcut = shell.CreateShortCut(os.path.join(root, file))
                                    if os.path.isdir(shortcut.Targetpath):
                                        roots_to_scan.append(shortcut.Targetpath)
                                except Exception:
                                    pass
                                
                for old_path, fname, fsize in missing_photos:
                    new_path = available_files.get((fname, fsize))
                    if new_path:
                        print(f"Moved file found: {old_path} -> {new_path}")
                        cursor.execute("SELECT 1 FROM photos WHERE path = ?", (new_path,))
                        if cursor.fetchone():
                            # new_path is already in DB! Merge data to it.
                            cursor.execute("UPDATE OR IGNORE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE OR IGNORE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            completely_delete_photo_data(cursor, old_path)
                        else:
                            cursor.execute("UPDATE photos SET path = ? WHERE path = ?", (new_path, old_path))
                            cursor.execute("UPDATE faces SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                            cursor.execute("UPDATE album_photos SET photo_path = ? WHERE photo_path = ?", (new_path, old_path))
                    else:
                        print(f"File permanently deleted: {old_path}")
                        completely_delete_photo_data(cursor, old_path)
                conn.commit()
            
            # 2. Rebuild Physical Cache (Wipe directories)
            with scan_lock:
                scan_status["phase"] = "Wiping Cache Directories"
            
            import shutil
            # Wipe thumbnails
            for item in os.listdir(THUMBNAILS_DIR):
                item_path = os.path.join(THUMBNAILS_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Failed to delete cache file {item_path}: {e}")
                    
            # Wipe faces
            for item in os.listdir(FACES_DIR):
                item_path = os.path.join(FACES_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Failed to delete face cache file {item_path}: {e}")

        except Exception as e:
            print(f"Error in cache rebuild: {e}")
        finally:
            conn.close()
            with scan_lock:
                scan_status["status"] = "idle"
                
    threading.Thread(target=rebuild_task, daemon=True).start()
    return jsonify({"success": True, "message": "Cache rebuild started"})


@misc_bp.route('/api/stats/heatmap')
def api_stats_heatmap():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return jsonify({})
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT substr(date_taken, 9, 2) as day, count(*)
        FROM photos 
        WHERE substr(date_taken, 1, 4) = ? AND substr(date_taken, 6, 2) = ? AND trashed_at IS NULL 
        GROUP BY day
    ''', (year, month.zfill(2)))
    
    data = c.fetchall()
    conn.close()
    
    return jsonify({row[0]: row[1] for row in data})





@misc_bp.route('/api/stats/calendar')
def api_stats_calendar():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT substr(date_taken, 1, 10) as day, count(*)
        FROM photos 
        WHERE date_taken IS NOT NULL AND date_taken != 'Undated' AND trashed_at IS NULL AND archived_at IS NULL AND date_taken >= '1999-01-01'
        GROUP BY day
        ORDER BY day ASC
    ''')
    data = c.fetchall()
    conn.close()
    return jsonify({row[0]: row[1] for row in data})


@misc_bp.route('/api/stats')
@cache_api(timeout=30)
def api_stats():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT substr(date_taken, 1, 4) as year, substr(date_taken, 6, 2) as month, file_type, count(*), sum(size)
        FROM photos 
        WHERE date_taken IS NOT NULL AND date_taken != 'Undated' 
        GROUP BY year, month, file_type
    ''')
    monthly_data = c.fetchall()
    
    c.execute('''
        SELECT 
            SUM(CASE WHEN file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN 1 ELSE 0 END) as total_videos,
            SUM(CASE WHEN file_type NOT IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN 1 ELSE 0 END) as total_photos,
            SUM(CASE WHEN file_type IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN size ELSE 0 END) as total_video_size,
            SUM(CASE WHEN file_type NOT IN ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC') THEN size ELSE 0 END) as total_photo_size
        FROM photos
    ''')
    totals = c.fetchone()
    conn.close()
    
    stats = {
        'total_photos': totals[1] if totals and totals[1] else 0,
        'total_videos': totals[0] if totals and totals[0] else 0,
        'total_photo_size': totals[3] if totals and totals[3] else 0,
        'total_video_size': totals[2] if totals and totals[2] else 0,
        'yearly': {}
    }
    
    for row in monthly_data:
        year = row[0]
        month = row[1]
        ftype = row[2]
        count = row[3]
        size = row[4] or 0
        
        if not year or len(year) != 4 or not year.isdigit():
            continue
        if not month or len(month) != 2 or not month.isdigit():
            continue
            
        if year not in stats['yearly']:
            stats['yearly'][year] = {'photos': 0, 'videos': 0, 'storage_photos': 0, 'storage_videos': 0, 'months': {}}
            for m in range(1, 13):
                stats['yearly'][year]['months'][f"{m:02d}"] = {'photos': 0, 'videos': 0, 'storage_photos': 0, 'storage_videos': 0}
                
        if ftype in ('MP4', 'MOV', 'AVI', 'MKV', 'WEBM', 'WMV', 'FLV', 'HEVC'):
            stats['yearly'][year]['videos'] += count
            stats['yearly'][year]['storage_videos'] += size
            stats['yearly'][year]['months'][month]['videos'] += count
            stats['yearly'][year]['months'][month]['storage_videos'] += size
        else:
            stats['yearly'][year]['photos'] += count
            stats['yearly'][year]['storage_photos'] += size
            stats['yearly'][year]['months'][month]['photos'] += count
            stats['yearly'][year]['months'][month]['storage_photos'] += size
            
    return jsonify(stats)



