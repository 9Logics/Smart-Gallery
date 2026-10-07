import os

file_path = 'app/app_core.py'
with open(file_path, 'r', encoding='utf-8') as f:
    src = f.read()

bad_chunk = """
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
"""

good_chunk = """
        import concurrent.futures
"""

global_func = """
def _process_thumb_global(row):
    import os
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

def scan_directory(root_dir):
"""

src = src.replace("def scan_directory(root_dir):", global_func)
src = src.replace(bad_chunk, good_chunk)
src = src.replace("_process_thumb", "_process_thumb_global")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Fixed pickle error in app_core.py")
