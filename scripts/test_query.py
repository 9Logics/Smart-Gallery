
import sqlite3

conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()

c.execute('''
SELECT substr(date_taken, 1, 4) as year, count(*) as cnt
FROM photos 
WHERE trashed_at IS NULL AND archived_at IS NULL
  AND date_taken IS NOT NULL
  AND file_type IN ('JPG', 'JPEG', 'PNG', 'HEIC', 'WEBP')
  AND ai_tags IS NOT NULL
  AND (ai_tags LIKE '%flower%' OR ai_tags LIKE '%plant%' OR ai_tags LIKE '%tree%' OR ai_tags LIKE '%forest%' OR ai_tags LIKE '%landscape%' OR ai_tags LIKE '%nature%')
  AND ai_tags NOT LIKE '%cat%' AND ai_tags NOT LIKE '%dog%' AND ai_tags NOT LIKE '%pet%' AND ai_tags NOT LIKE '%bird%' AND ai_tags NOT LIKE '%fish%' AND ai_tags NOT LIKE '%horse%' AND ai_tags NOT LIKE '%wild animal%' AND ai_tags NOT LIKE '%animal%'
  AND ai_tags NOT LIKE '%selfie%' AND ai_tags NOT LIKE '%group photo%' AND ai_tags NOT LIKE '%portrait%' AND ai_tags NOT LIKE '%child%' AND ai_tags NOT LIKE '%baby%' AND ai_tags NOT LIKE '%person%' AND ai_tags NOT LIKE '%people%' AND ai_tags NOT LIKE '%man%' AND ai_tags NOT LIKE '%woman%' AND ai_tags NOT LIKE '%human%'
  AND path NOT IN (SELECT photo_path FROM faces)
GROUP BY year
HAVING cnt >= 1
''')
res = c.fetchall()
print(f'Matching years: {res}')

