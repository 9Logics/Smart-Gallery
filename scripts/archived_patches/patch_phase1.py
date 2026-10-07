import os
import re

app_core_path = 'app/app_core.py'
with open(app_core_path, 'r', encoding='utf-8') as f:
    core_src = f.read()

# Phase 1 patching
phase1_old = """
        for idx, path in enumerate(new_files):
            with scan_lock:
                if scan_status.get('cancel_requested'):
                    break
            scan_status['processed'] = idx + 1
            scan_status['current_file'] = os.path.basename(path)
            meta = extract_metadata(path)
            filename = os.path.basename(path)
            import datetime
            path_lower = path.lower()
            filename_lower = filename.lower()
            if 'screenshot' in path_lower or 'screen shot' in path_lower or 'screen_shot' in path_lower or 'screenshot' in filename_lower or 'screen shot' in filename_lower or 'screen_shot' in filename_lower:
                archived_time = datetime.datetime.now().isoformat()
            else:
                archived_time = None
                
            cursor.execute(
                \"\"\"
                INSERT OR REPLACE INTO photos 
                (path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash, trashed_at, archived_at, camera_make, camera_model, f_stop, exposure_time, focal_length, iso, duration, fps, video_codec)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                \"\"\"
                , (path, filename, meta['date_taken'], meta['width'], meta[
                'height'], meta['size'], meta['file_type'], meta['latitude'
                ], meta['longitude'], archived_time, meta['camera_make'], meta[
                'camera_model'], meta['f_stop'], meta['exposure_time'],
                meta['focal_length'], meta['iso'], meta['duration'], meta[
                'fps'], meta['video_codec']))
            if idx % 10 == 0:
                conn.commit()
"""

phase1_new = """
        import concurrent.futures
        import datetime
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_path = {executor.submit(extract_metadata, path): path for path in new_files}
            for idx, future in enumerate(concurrent.futures.as_completed(future_to_path)):
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                path = future_to_path[future]
                scan_status['processed'] = idx + 1
                scan_status['current_file'] = os.path.basename(path)
                try:
                    meta = future.result()
                    filename = os.path.basename(path)
                    path_lower = path.lower()
                    filename_lower = filename.lower()
                    if 'screenshot' in path_lower or 'screen shot' in path_lower or 'screen_shot' in path_lower or 'screenshot' in filename_lower or 'screen shot' in filename_lower or 'screen_shot' in filename_lower:
                        archived_time = datetime.datetime.now().isoformat()
                    else:
                        archived_time = None
                        
                    cursor.execute(
                        \"\"\"
                        INSERT OR REPLACE INTO photos 
                        (path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash, trashed_at, archived_at, camera_make, camera_model, f_stop, exposure_time, focal_length, iso, duration, fps, video_codec)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        \"\"\"
                        , (path, filename, meta['date_taken'], meta['width'], meta['height'], meta['size'], meta['file_type'], meta['latitude'], meta['longitude'], archived_time, meta['camera_make'], meta['camera_model'], meta['f_stop'], meta['exposure_time'], meta['focal_length'], meta['iso'], meta['duration'], meta['fps'], meta['video_codec']))
                except Exception as exc:
                    print(f'{path} generated an exception: {exc}')
                if idx % 10 == 0:
                    conn.commit()
"""

# Phase 2 patching
phase2_old = """
        for row in thumbnail_todo:
            # Cancel was only honoured in Phase 1, so pressing Cancel during the two
            # slow phases did nothing for what could be hours. Breaking out here is
            # safe: the todo lists are rebuilt from "WHERE thumbnail/hash IS NULL" on
            # the next scan, so unprocessed photos are simply picked up again.
            if scan_status.get('cancel_requested'):
                break
            path = row[0]
            processed_count += 1
            scan_status['processed'] = processed_count
            scan_status['current_file'
                ] = f'Thumbnail: {os.path.basename(path)}'
            thumb_path = get_thumbnail_path(path)
            is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            try:
                if is_video:
                    generate_video_thumbnail(path, thumb_path)
                else:
                    generate_thumbnail(path, thumb_path)
            except Exception as e:
                print(f'Error generating thumbnail for {path}: {e}')
"""

phase2_new = """
        def _process_thumb(row):
            path = row[0]
            thumb_path = get_thumbnail_path(path)
            is_video = path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
            if not os.path.exists(thumb_path):
                try:
                    if is_video:
                        generate_video_thumbnail(path, thumb_path)
                    else:
                        generate_thumbnail(path, thumb_path)
                except Exception as e:
                    pass
            return path
            
        import concurrent.futures
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_row = {executor.submit(_process_thumb, row): row for row in thumbnail_todo}
            for future in concurrent.futures.as_completed(future_to_row):
                if scan_status.get('cancel_requested'):
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                path = future.result()
                processed_count += 1
                scan_status['processed'] = processed_count
                scan_status['current_file'] = f'Thumbnail: {os.path.basename(path)}'
"""

core_src = core_src.replace(phase1_old, phase1_new)
core_src = core_src.replace(phase2_old, phase2_new)

with open(app_core_path, 'w', encoding='utf-8') as f:
    f.write(core_src)
print("app_core.py patched.")
