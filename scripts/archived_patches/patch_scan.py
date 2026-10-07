import re

with open('app/routes/scan.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''        cursor.execute(
            """
            SELECT p.id, f.embedding
            FROM faces f
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL AND f.is_manual != -1
        """
            )''',
    '''        cursor.execute(
            """
            SELECT p.id, fe.embedding
            FROM faces f
            JOIN people p ON f.person_id = p.id
            JOIN face_embeddings fe ON f.id = fe.face_id
            WHERE p.name NOT LIKE 'Person %' AND fe.embedding IS NOT NULL AND f.is_manual != -1
        """
            )'''
)

content = content.replace(
    '''        cursor.execute(
            """
            SELECT f.id, f.person_id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL 
              AND (f.is_manual = 0 OR f.is_manual IS NULL)
        """
            )''',
    '''        cursor.execute(
            """
            SELECT f.id, f.person_id, fe.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            JOIN face_embeddings fe ON f.id = fe.face_id
            WHERE p.name NOT LIKE 'Person %' AND fe.embedding IS NOT NULL 
              AND (f.is_manual = 0 OR f.is_manual IS NULL)
        """
            )'''
)

with open('app/routes/scan.py', 'w', encoding='utf-8') as f:
    f.write(content)
