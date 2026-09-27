import re

py_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\routes\photos.py"
with open(py_path, "r", encoding="utf-8") as f:
    py_code = f.read()

# Fix total photos query
bad_str_1 = '''cursor.execute("SELECT COUNT(*) FROM photos WHERE date_taken LIKE ? \n              AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')", (date_filter,))'''
good_str_1 = '''cursor.execute("SELECT COUNT(*) FROM photos WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')", (date_filter,))'''
py_code = py_code.replace(bad_str_1, good_str_1)

# Fix total videos query
bad_str_2 = '''cursor.execute("SELECT COUNT(*) FROM photos WHERE date_taken LIKE ? \n              AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('mp4', 'mov', 'avi', 'mkv', 'webm')", (date_filter,))'''
good_str_2 = '''cursor.execute("SELECT COUNT(*) FROM photos WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('mp4', 'mov', 'avi', 'mkv', 'webm')", (date_filter,))'''
py_code = py_code.replace(bad_str_2, good_str_2)

with open(py_path, "w", encoding="utf-8") as f:
    f.write(py_code)
print("Fixed syntax errors in photos.py")
