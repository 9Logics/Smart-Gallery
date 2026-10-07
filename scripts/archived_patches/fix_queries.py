import re

py_path = r'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py_code = f.read()

# Fix get_recap_years()
old_years = '''cursor.execute("""
            SELECT 
                substr(date_taken, 1, 4) as year, 
                COUNT(*) as count,
                MAX(path) as cover_photo
            FROM photos 
            WHERE date_taken IS NOT NULL 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY year 
            HAVING CAST(year AS INTEGER) >= 2000 AND count >= 5
            ORDER BY year DESC
        """)'''

new_years = '''cursor.execute("""
            WITH YearGroups AS (
                SELECT substr(date_taken, 1, 4) as year, COUNT(*) as count
                FROM photos 
                WHERE date_taken IS NOT NULL 
                  AND trashed_at IS NULL AND archived_at IS NULL 
                  AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%'
                  AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%'
                  AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%'
                  AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                GROUP BY substr(date_taken, 1, 4)
                HAVING CAST(substr(date_taken, 1, 4) AS INTEGER) >= 2000 AND count >= 5
            )
            SELECT yg.year, yg.count,
                   (SELECT path FROM photos p2 
                    WHERE substr(p2.date_taken, 1, 4) = yg.year 
                      AND p2.trashed_at IS NULL AND p2.archived_at IS NULL
                      AND p2.path NOT LIKE '%\\Archive\\%' AND p2.path NOT LIKE '%/Archive/%'
                      AND p2.path NOT LIKE '%\\Trash\\%' AND p2.path NOT LIKE '%/Trash/%'
                      AND p2.path NOT LIKE '%\\Deleted\\%' AND p2.path NOT LIKE '%/Deleted/%'
                      AND LOWER(p2.file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                    ORDER BY p2.is_favorite DESC, RANDOM() LIMIT 1) as cover_photo
            FROM YearGroups yg
            ORDER BY yg.year DESC
        """)'''

# Fix get_recap_month_counts()
old_months = '''cursor.execute("""
            SELECT 
                substr(date_taken, 6, 2) as month, 
                COUNT(*) as count,
                MAX(path) as cover_photo
            FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY month 
        """, (date_filter,))'''

new_months = '''cursor.execute("""
            WITH MonthGroups AS (
                SELECT substr(date_taken, 6, 2) as month, COUNT(*) as count
                FROM photos 
                WHERE date_taken LIKE ? 
                  AND trashed_at IS NULL AND archived_at IS NULL 
                  AND path NOT LIKE '%\\Archive\\%' AND path NOT LIKE '%/Archive/%'
                  AND path NOT LIKE '%\\Trash\\%' AND path NOT LIKE '%/Trash/%'
                  AND path NOT LIKE '%\\Deleted\\%' AND path NOT LIKE '%/Deleted/%'
                  AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                GROUP BY substr(date_taken, 6, 2)
            )
            SELECT mg.month, mg.count,
                   (SELECT path FROM photos p2 
                    WHERE date_taken LIKE ? || '-' || mg.month || '-%'
                      AND p2.trashed_at IS NULL AND p2.archived_at IS NULL
                      AND p2.path NOT LIKE '%\\Archive\\%' AND p2.path NOT LIKE '%/Archive/%'
                      AND p2.path NOT LIKE '%\\Trash\\%' AND p2.path NOT LIKE '%/Trash/%'
                      AND p2.path NOT LIKE '%\\Deleted\\%' AND p2.path NOT LIKE '%/Deleted/%'
                      AND LOWER(p2.file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
                    ORDER BY p2.is_favorite DESC, RANDOM() LIMIT 1) as cover_photo
            FROM MonthGroups mg
        """, (date_filter, date_filter.replace('-%', '')))'''

if old_years in py_code:
    py_code = py_code.replace(old_years, new_years)
    print("Patched years!")
else:
    print("Could not find old_years")

if old_months in py_code:
    py_code = py_code.replace(old_months, new_months)
    print("Patched months!")
else:
    print("Could not find old_months")

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py_code)
