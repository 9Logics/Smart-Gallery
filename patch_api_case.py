import os

py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

# Fix case-sensitivity in file_type
py = py.replace(
    "AND file_type IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')", 
    "AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')"
)
py = py.replace(
    "AND file_type IN ('mp4', 'mov', 'avi', 'mkv', 'webm')", 
    "AND LOWER(file_type) IN ('mp4', 'mov', 'avi', 'mkv', 'webm')"
)
py = py.replace(
    "AND file_type IN ('jpg', 'jpeg', 'png', 'heic', 'webp')",
    "AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')"
)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Fixed API file_type case sensitivity!")
