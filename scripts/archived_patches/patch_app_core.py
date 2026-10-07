import re

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''        cursor.execute(
            """
        SELECT p.id, f.embedding 
        FROM people p
        JOIN faces f ON p.cover_face_id = f.id
        WHERE f.embedding IS NOT NULL
        """
        )''',
    '''        cursor.execute(
            """
        SELECT p.id, fe.embedding 
        FROM people p
        JOIN faces f ON p.cover_face_id = f.id
        JOIN face_embeddings fe ON f.id = fe.face_id
        WHERE fe.embedding IS NOT NULL
        """
        )'''
)

content = content.replace(
    '''    cursor.execute(
        'SELECT id, embedding FROM faces WHERE person_id IS NULL AND embedding IS NOT NULL AND (is_manual != -1 OR is_manual IS NULL)'
        )''',
    '''    cursor.execute(
        'SELECT f.id, fe.embedding FROM faces f JOIN face_embeddings fe ON f.id = fe.face_id WHERE f.person_id IS NULL AND fe.embedding IS NOT NULL AND (f.is_manual != -1 OR f.is_manual IS NULL)'
        )'''
)

content = content.replace(
    '''                            cursor.execute(
                                """
                                INSERT INTO faces (photo_path, x, y, w, h, embedding, person_id)
                                VALUES (?, ?, ?, ?, ?, ?, NULL)
                            """
                                , (path, bbox[0], bbox[1], bbox[2], bbox[3],
                                emb_bytes))''',
    '''                            cursor.execute(
                                """
                                INSERT INTO faces (photo_path, x, y, w, h, person_id)
                                VALUES (?, ?, ?, ?, ?, NULL)
                            """
                                , (path, bbox[0], bbox[1], bbox[2], bbox[3]))
                            new_face_id = cursor.lastrowid
                            cursor.execute("INSERT INTO face_embeddings (face_id, embedding) VALUES (?, ?)", (new_face_id, emb_bytes))'''
)

with open('app/app_core.py', 'w', encoding='utf-8') as f:
    f.write(content)
