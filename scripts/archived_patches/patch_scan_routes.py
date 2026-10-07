import os

file_path = 'app/routes/scan.py'
with open(file_path, 'r', encoding='utf-8') as f:
    src = f.read()

hero_old = """
            from app.scene_classifier import hero_cache, check_hero_scene, save_hero_cache
            video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v',
                '.hevc', '.wmv', '.flv')
            unscanned = [p for p in all_paths if not p.lower().endswith(
                video_exts)]
            with scan_lock:
                scan_status['total'] = len(unscanned)
            for p in unscanned:
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
                    scan_status['processed'] += 1
                    scan_status['current_file'] = os.path.basename(p)
                is_scenic = check_hero_scene(p)
                hero_cache[p] = is_scenic
            save_hero_cache()
"""

hero_new = """
            from app.scene_classifier import hero_cache, check_hero_scene_batch, save_hero_cache
            video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
            unscanned = [p for p in all_paths if not p.lower().endswith(video_exts)]
            with scan_lock:
                scan_status['total'] = len(unscanned)
            
            batch_size = 16
            for i in range(0, len(unscanned), batch_size):
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
                    
                batch = unscanned[i:i+batch_size]
                with scan_lock:
                    scan_status['current_file'] = f"Batch processing {len(batch)} images..."
                    
                results = check_hero_scene_batch(batch)
                
                with scan_lock:
                    scan_status['processed'] += len(batch)
                    
                for p, is_scenic in zip(batch, results):
                    hero_cache[p] = is_scenic
                    
                # Save periodically or at the end
                if i % (batch_size * 4) == 0:
                    save_hero_cache()
            save_hero_cache()
"""

obj_old = """
            from app.scene_classifier import get_image_tags
            video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
            unscanned = [p for p in all_paths if not p.lower().endswith(video_exts)]
            
            with scan_lock:
                scan_status['total'] = len(unscanned)
                
            for p in unscanned:
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
                    scan_status['processed'] += 1
                    scan_status['current_file'] = os.path.basename(p)
                    
                tags, embedding = get_image_tags(p)
                if embedding is not None:
                    tags_str = ",".join(tags) if tags else ""
                    emb_bytes = embedding.tobytes()
                    cursor.execute('UPDATE photos SET ai_tags = ? WHERE path = ?', (tags_str, p))
                    cursor.execute('INSERT OR REPLACE INTO photo_embeddings (photo_path, clip_embedding) VALUES (?, ?)', (p, emb_bytes))
                    cursor.execute('DELETE FROM photos_fts WHERE path = ?', (p,))
                    cursor.execute('INSERT INTO photos_fts(path, ai_tags, place_name) SELECT path, ai_tags, place_name FROM photos WHERE path = ?', (p,))
                    # Commit frequently so if it's interrupted, progress is saved
                    if scan_status['processed'] % 10 == 0:
                        conn.commit()
"""

obj_new = """
            from app.scene_classifier import get_image_tags_batch
            video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
            unscanned = [p for p in all_paths if not p.lower().endswith(video_exts)]
            
            with scan_lock:
                scan_status['total'] = len(unscanned)
                
            batch_size = 32
            for i in range(0, len(unscanned), batch_size):
                with scan_lock:
                    if scan_status.get('cancel_requested'):
                        break
                
                batch = unscanned[i:i+batch_size]
                with scan_lock:
                    scan_status['current_file'] = f"Batch processing {len(batch)} images..."
                    
                results = get_image_tags_batch(batch)
                
                with scan_lock:
                    scan_status['processed'] += len(batch)
                    
                for p, (tags, embedding) in zip(batch, results):
                    if embedding is not None:
                        tags_str = ",".join(tags) if tags else ""
                        emb_bytes = embedding.tobytes()
                        cursor.execute('UPDATE photos SET ai_tags = ? WHERE path = ?', (tags_str, p))
                        cursor.execute('INSERT OR REPLACE INTO photo_embeddings (photo_path, clip_embedding) VALUES (?, ?)', (p, emb_bytes))
                        cursor.execute('DELETE FROM photos_fts WHERE path = ?', (p,))
                        cursor.execute('INSERT INTO photos_fts(path, ai_tags, place_name) SELECT path, ai_tags, place_name FROM photos WHERE path = ?', (p,))
                
                conn.commit()
"""

src = src.replace(hero_old, hero_new)
src = src.replace(obj_old, obj_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(src)
print("scan.py patched.")
