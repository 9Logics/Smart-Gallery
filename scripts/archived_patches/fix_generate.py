import re
py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace plain ones
code = code.replace(
    'AND trashed_at IS NULL AND archived_at IS NULL',
    "AND trashed_at IS NULL AND archived_at IS NULL AND path NOT LIKE '%\\\\Archive\\\\%' AND path NOT LIKE '%/Archive/%' AND path NOT LIKE '%\\\\Trash\\\\%' AND path NOT LIKE '%/Trash/%' AND path NOT LIKE '%\\\\Deleted\\\\%' AND path NOT LIKE '%/Deleted/%'"
)

# Replace ph ones
code = code.replace(
    'AND ph.trashed_at IS NULL AND ph.archived_at IS NULL',
    "AND ph.trashed_at IS NULL AND ph.archived_at IS NULL AND ph.path NOT LIKE '%\\\\Archive\\\\%' AND ph.path NOT LIKE '%/Archive/%' AND ph.path NOT LIKE '%\\\\Trash\\\\%' AND ph.path NOT LIKE '%/Trash/%' AND ph.path NOT LIKE '%\\\\Deleted\\\\%' AND ph.path NOT LIKE '%/Deleted/%'"
)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(code)
print('Patched generate_recap exclusions')
