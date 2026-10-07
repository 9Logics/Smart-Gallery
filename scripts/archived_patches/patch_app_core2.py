import re

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''        cursor.execute(
            """
        SELECT p.id, f.embedding 
        FROM faces f 
        JOIN people p ON f.person_id = p.id
        WHERE f.embedding IS NOT NULL
        """
        )''',
    '''        cursor.execute(
            """
        SELECT p.id, fe.embedding 
        FROM faces f 
        JOIN people p ON f.person_id = p.id
        JOIN face_embeddings fe ON f.id = fe.face_id
        WHERE fe.embedding IS NOT NULL
        """
        )'''
)

with open('app/app_core.py', 'w', encoding='utf-8') as f:
    f.write(content)
