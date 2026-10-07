import os

file_path = 'app/app_core.py'
with open(file_path, 'r', encoding='utf-8') as f:
    src = f.read()

p3_old = """
        for idx, (path, file_type) in enumerate(ai_todo):
            if scan_status.get('cancel_requested'):
                break
            scan_status['processed'] = idx + 1
            scan_status['current_file'
                ] = f'AI Analysis: {os.path.basename(path)}'
            meta = extract_metadata(path)
            dhash = meta.get('hash')
            cursor.execute('UPDATE photos SET hash = ? WHERE path = ?', (
                dhash, path))
            if processor:
                thumb_path = get_thumbnail_path(path)
                is_video = path.lower().endswith(('.mp4', '.mov', '.m4v',
                    '.hevc'))
                detect_path = path
                if os.path.exists(detect_path):
                    try:
                        faces = processor.detect_and_extract_faces(detect_path,
                            min_confidence=0.8)
                        for face in faces:
                            bbox = face['bbox']
                            emb_bytes = face['embedding'].tobytes()
                            cursor.execute(
                                \"\"\"
                                INSERT INTO faces (photo_path, x, y, w, h, person_id)
                                VALUES (?, ?, ?, ?, ?, NULL)
                            \"\"\"
                                , (path, bbox[0], bbox[1], bbox[2], bbox[3]))
                            new_face_id = cursor.lastrowid
                            cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))
                    except Exception as e:
                        print(f'Error extracting faces for {path}: {e}')
            if idx % 10 == 0:
                conn.commit()
"""

p3_new = """
        batch_size = 16
        for i in range(0, len(ai_todo), batch_size):
            if scan_status.get('cancel_requested'):
                break
                
            batch = ai_todo[i:i+batch_size]
            with scan_lock:
                scan_status['current_file'] = f'AI Analysis: Batch of {len(batch)}'
                
            batch_paths = []
            for path, file_type in batch:
                meta = extract_metadata(path)
                dhash = meta.get('hash')
                cursor.execute('UPDATE photos SET hash = ? WHERE path = ?', (dhash, path))
                batch_paths.append(path)
                
            if processor:
                try:
                    # FaceProcessor doesn't have a native batched detect via YUNet API, but we batch the Python loop
                    for path in batch_paths:
                        if os.path.exists(path):
                            faces = processor.detect_and_extract_faces(path, min_confidence=0.8)
                            for face in faces:
                                bbox = face['bbox']
                                emb_bytes = face['embedding'].tobytes()
                                cursor.execute(
                                    \"\"\"
                                    INSERT INTO faces (photo_path, x, y, w, h, person_id)
                                    VALUES (?, ?, ?, ?, ?, NULL)
                                \"\"\"
                                    , (path, bbox[0], bbox[1], bbox[2], bbox[3]))
                                new_face_id = cursor.lastrowid
                                cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))
                except Exception as e:
                    print(f'Error extracting faces for batch: {e}')
                    
            with scan_lock:
                scan_status['processed'] += len(batch)
            conn.commit()
"""

src = src.replace(p3_old, p3_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Phase 3 app_core.py patched.")
