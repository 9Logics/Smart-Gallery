import re

py_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\routes\photos.py"
with open(py_path, "r", encoding="utf-8") as f:
    py_code = f.read()

# 1. month-counts
py_code = py_code.replace(
    "WHERE date_taken LIKE ?",
    "WHERE date_taken LIKE ? \n              AND trashed_at IS NULL AND archived_at IS NULL"
)

# 2. recap/years
py_code = py_code.replace(
    "WHERE date_taken IS NOT NULL",
    "WHERE date_taken IS NOT NULL \n              AND trashed_at IS NULL AND archived_at IS NULL"
)

# 3. generate_recap
# We have multiple queries here. Let's find them all.
py_code = py_code.replace(
    "WHERE date_taken LIKE ? AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')",
    "WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'gif')"
)

py_code = py_code.replace(
    "WHERE date_taken LIKE ? AND LOWER(file_type) IN ('mp4', 'mov', 'avi', 'mkv', 'webm')",
    "WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('mp4', 'mov', 'avi', 'mkv', 'webm')"
)

# top person
py_code = py_code.replace(
    "WHERE ph.date_taken LIKE ? AND p.name != 'Me'",
    "WHERE ph.date_taken LIKE ? AND ph.trashed_at IS NULL AND ph.archived_at IS NULL AND p.name != 'Me'"
)

# top person photos
py_code = py_code.replace(
    "WHERE ph.date_taken LIKE ? AND p.name = ?",
    "WHERE ph.date_taken LIKE ? AND ph.trashed_at IS NULL AND ph.archived_at IS NULL AND p.name = ?"
)

# iconic place
py_code = py_code.replace(
    "WHERE date_taken LIKE ? AND place_name IS NOT NULL",
    "WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND place_name IS NOT NULL"
)

# iconic place photos
py_code = py_code.replace(
    "WHERE date_taken LIKE ? AND place_name = ? AND LOWER(file_type)",
    "WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND place_name = ? AND LOWER(file_type)"
)

# memorable moment / gallery photos
py_code = py_code.replace(
    "WHERE date_taken LIKE ? AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')",
    "WHERE date_taken LIKE ? AND trashed_at IS NULL AND archived_at IS NULL AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')"
)


with open(py_path, "w", encoding="utf-8") as f:
    f.write(py_code)

print("Applied trashed_at IS NULL AND archived_at IS NULL filters to all recap queries.")
