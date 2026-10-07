import os
import datetime

js_path = 'app/app_core.py'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

target = """
              cursor.execute(
                  \"\"\"
                  INSERT OR REPLACE INTO photos 
                  (path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash, 
trashed_at, camera_make, camera_model, f_stop, exposure_time, focal_length, iso, duration, fps, video_codec)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              \"\"\"
                  , (path, filename, meta['date_taken'], meta['width'], meta[
                  'height'], meta['size'], meta['file_type'], meta['latitude'
                  ], meta['longitude'], meta['camera_make'], meta[
                  'camera_model'], meta['f_stop'], meta['exposure_time'],
                  meta['focal_length'], meta['iso'], meta['duration'], meta[
                  'fps'], meta['video_codec']))
"""

replacement = """
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
                  (path, filename, date_taken, width, height, size, file_type, latitude, longitude, place_name, hash, 
trashed_at, archived_at, camera_make, camera_model, f_stop, exposure_time, focal_length, iso, duration, fps, video_codec)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              \"\"\"
                  , (path, filename, meta['date_taken'], meta['width'], meta[
                  'height'], meta['size'], meta['file_type'], meta['latitude'
                  ], meta['longitude'], archived_time, meta['camera_make'], meta[
                  'camera_model'], meta['f_stop'], meta['exposure_time'],
                  meta['focal_length'], meta['iso'], meta['duration'], meta[
                  'fps'], meta['video_codec']))
"""

# Try to find exactly where to replace
if "INSERT OR REPLACE INTO photos" in code:
    start_idx = code.find("cursor.execute(")
    
    # We actually need to search for the specific insert in the loop
    # Let's just use string replace but without the strict exact match of the python script variable
    # We will split and reconstruct
    
    parts = code.split('scan_status[\'current_file\'] = os.path.basename(path)')
    if len(parts) > 1:
        part2 = parts[1]
        
        insert_idx = part2.find('cursor.execute(')
        end_idx = part2.find('if idx % 10 == 0:', insert_idx)
        
        if insert_idx != -1 and end_idx != -1:
            new_part2 = part2[:insert_idx] + replacement.strip('\n') + '\n              ' + part2[end_idx:]
            code = parts[0] + 'scan_status[\'current_file\'] = os.path.basename(path)' + new_part2
            
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print("SUCCESSFULLY REPLACED")
        else:
            print("COULD NOT FIND INDICES")
    else:
        print("COULD NOT FIND SPLIT POINT")
