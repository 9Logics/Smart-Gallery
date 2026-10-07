import re

with open('app/routes/faces.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. First NULL embedding (line ~126)
content = content.replace('''        cursor.execute(
            """
            INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
            VALUES (?, 0, 0, 0, 0, NULL, ?, 1)
        """
            , (path, p_id))''', '''        cursor.execute(
            """
            INSERT INTO faces (photo_path, x, y, w, h, person_id, is_manual)
            VALUES (?, 0, 0, 0, 0, ?, 1)
        """
            , (path, p_id))''')

# 2. Second NULL embedding (line ~166)
content = content.replace('''    cursor.execute(
        """
        INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
        VALUES (?, ?, ?, ?, ?, NULL, ?, 1)
    """
        , (path, int(x), int(y), int(w), int(h), p_id))''', '''    cursor.execute(
        """
        INSERT INTO faces (photo_path, x, y, w, h, person_id, is_manual)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """
        , (path, int(x), int(y), int(w), int(h), p_id))''')

# 3. Third with emb_bytes (line ~262)
content = content.replace('''                            cursor.execute(
                                """
                                INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id, is_manual)
                                VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
                            """
                                , (path, bbox[0], bbox[1], bbox[2], bbox[3],
                                emb_bytes))''', '''                            cursor.execute(
                                """
                                INSERT INTO faces (photo_path, x, y, w, h, person_id, is_manual)
                                VALUES (?, ?, ?, ?, ?, NULL, 0)
                            """
                                , (path, bbox[0], bbox[1], bbox[2], bbox[3]))
                            new_face_id = cursor.lastrowid
                            cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))''')

# 4. Fourth with emb_bytes (line ~357)
content = content.replace('''                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, embedding, is_manual)
                            VALUES (?, ?, ?, ?, ?, ?, 0)
                        """
                            , (p, bx, by, bw, bh, emb_bytes))''', '''                        cursor.execute(
                            """
                            INSERT INTO faces (photo_path, x, y, w, h, is_manual)
                            VALUES (?, ?, ?, ?, ?, 0)
                        """
                            , (p, bx, by, bw, bh))
                        new_face_id = cursor.lastrowid
                        cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))''')

# SELECT queries
content = content.replace(
    '''cursor.execute(
        """
        SELECT f.id, f.embedding, f.photo_path, p.name, p.id
        FROM faces f
        JOIN people p ON f.person_id = p.id
        WHERE p.name != 'Unknown' AND f.embedding IS NOT NULL
        """
    )''',
    '''cursor.execute(
        """
        SELECT f.id, fe.embedding, f.photo_path, p.name, p.id
        FROM faces f
        JOIN people p ON f.person_id = p.id
        JOIN face_embeddings fe ON f.id = fe.face_id
        WHERE p.name != 'Unknown' AND fe.embedding IS NOT NULL
        """
    )'''
)

content = content.replace(
    '''cursor.execute(
        """
        SELECT f.id, f.embedding, f.photo_path
        FROM faces f
        WHERE f.embedding IS NOT NULL
        """
    )''',
    '''cursor.execute(
        """
        SELECT f.id, fe.embedding, f.photo_path
        FROM faces f
        JOIN face_embeddings fe ON f.id = fe.face_id
        WHERE fe.embedding IS NOT NULL
        """
    )'''
)

with open('app/routes/faces.py', 'w', encoding='utf-8') as f:
    f.write(content)
