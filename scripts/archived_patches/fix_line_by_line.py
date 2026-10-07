import os

js_path = 'app/app_core.py'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.strip() == "cursor.execute(" and lines[i-1].strip() == "filename = os.path.basename(path)":
        # Found the spot
        # First add our new logic
        new_lines.append("""              import datetime
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
""")
        # Now skip the old block
        while i < len(lines):
            if "meta['video_codec']))" in lines[i]:
                break
            i += 1
    else:
        new_lines.append(line)
    i += 1

with open(js_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS")
