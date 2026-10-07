import os
import re

def patch_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)
    if content != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {path}")

# app_core.py queries
patch_file('app/app_core.py', [
    (r"SELECT p\.id, f\.embedding\s*FROM people p\s*JOIN faces f ON p\.cover_face_id = f\.id\s*WHERE f\.embedding IS NOT NULL", 
     r"SELECT p.id, fe.embedding FROM people p JOIN faces f ON p.cover_face_id = f.id JOIN face_embeddings fe ON f.id = fe.face_id WHERE fe.embedding IS NOT NULL"),
     
    (r"SELECT id, embedding FROM faces WHERE person_id IS NULL AND embedding IS NOT NULL", 
     r"SELECT f.id, fe.embedding FROM faces f JOIN face_embeddings fe ON f.id = fe.face_id WHERE f.person_id IS NULL AND fe.embedding IS NOT NULL"),
     
    (r"INSERT INTO faces \(photo_path, x, y, w, h, embedding, person_id\)", 
     r"INSERT INTO faces (photo_path, x, y, w, h, person_id)"),
])

# Wait, the INSERT statement returns an ID which I need to insert into face_embeddings!
# If I just replace the SQL string, the python execute tuple will still have `emb_bytes`. This will crash SQLite with mismatched parameters!
