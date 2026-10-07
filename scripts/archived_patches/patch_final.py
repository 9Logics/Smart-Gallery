import re

with open('app/routes/faces.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''            SELECT f.id, f.embedding, f.photo_path, p.name, p.id
            FROM faces f
            JOIN people p ON f.person_id = p.id
            WHERE p.name != 'Unknown' AND f.embedding IS NOT NULL
            LIMIT 50''',
    '''            SELECT f.id, fe.embedding, f.photo_path, p.name, p.id
            FROM faces f
            JOIN people p ON f.person_id = p.id
            JOIN face_embeddings fe ON f.id = fe.face_id
            WHERE p.name != 'Unknown' AND fe.embedding IS NOT NULL
            LIMIT 50'''
)

content = content.replace(
    '''            SELECT f.id, f.embedding, f.photo_path
            FROM faces f
            WHERE f.embedding IS NOT NULL
              AND (f.person_id IS NULL OR f.person_id IN (SELECT id FROM people WHERE name = 'Unknown'))
            LIMIT 200''',
    '''            SELECT f.id, fe.embedding, f.photo_path
            FROM faces f
            JOIN face_embeddings fe ON f.id = fe.face_id
            WHERE fe.embedding IS NOT NULL
              AND (f.person_id IS NULL OR f.person_id IN (SELECT id FROM people WHERE name = 'Unknown'))
            LIMIT 200'''
)

with open('app/routes/faces.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''        SELECT p.id, f.embedding 
        FROM faces f 
        JOIN people p ON f.person_id = p.id
        WHERE f.embedding IS NOT NULL''',
    '''        SELECT p.id, fe.embedding 
        FROM faces f 
        JOIN people p ON f.person_id = p.id
        JOIN face_embeddings fe ON f.id = fe.face_id
        WHERE fe.embedding IS NOT NULL'''
)

with open('app/app_core.py', 'w', encoding='utf-8') as f:
    f.write(content)
