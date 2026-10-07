import re

with open('app/routes/photos.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First INSERT (line ~563)
content = content.replace('''                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
                        """
                            , (photo_path, bx, by, bw, bh, emb_bytes))''', '''                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, person_id, is_manual)
                            VALUES (?, ?, ?, ?, ?, NULL, 0)
                        """
                            , (photo_path, bx, by, bw, bh))
                        new_face_id = cursor.lastrowid
                        cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))''')

# Second INSERT (line ~929)
content = content.replace('''                cursor.execute(
                    """
                    INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """
                    , (photo_path, bx, by, bw, bh, emb_bytes))''', '''                cursor.execute(
                    """
                    INSERT INTO faces (photo_path, x, y, w, h, is_manual)
                    VALUES (?, ?, ?, ?, ?, 0)
                """
                    , (photo_path, bx, by, bw, bh))
                new_face_id = cursor.lastrowid
                cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))''')

with open('app/routes/photos.py', 'w', encoding='utf-8') as f:
    f.write(content)
