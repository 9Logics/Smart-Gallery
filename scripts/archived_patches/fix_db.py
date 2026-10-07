import sqlite3
import os

conn = sqlite3.connect('.cache/gallery.db')
c = conn.cursor()

c.execute("SELECT * FROM photos")
rows = c.fetchall()

columns = [desc[0] for desc in c.description]
path_idx = columns.index('path')

# Group by normalized lowercase path
groups = {}
for row in rows:
    path = row[path_idx]
    norm_path = os.path.normpath(path)
    key = norm_path.lower()
    if key not in groups:
        groups[key] = []
    groups[key].append(dict(zip(columns, row)))

# Merge and update
to_delete = []
to_upsert = []

for key, group in groups.items():
    if len(group) == 1:
        # Just normalize the path if it's different
        orig_path = group[0]['path']
        norm_path = os.path.normpath(orig_path)
        if orig_path != norm_path:
            merged = group[0].copy()
            merged['path'] = norm_path
            to_upsert.append(merged)
            to_delete.append(orig_path)
        continue
    
    # We have duplicates! Merge them.
    merged = group[0].copy()
    merged['path'] = os.path.normpath(merged['path']) # Use normalized path
    
    for row in group[1:]:
        # Merge non-null fields
        for col in columns:
            if merged[col] is None or merged[col] == '' or merged[col] == 0:
                if row[col] is not None and row[col] != '' and row[col] != 0:
                    merged[col] = row[col]
        # Always delete the old ones
        to_delete.append(row['path'])
    
    to_delete.append(group[0]['path']) # Delete the first one too, we will re-insert it
    to_upsert.append(merged)

# Execute deletes
for path in set(to_delete):
    c.execute("DELETE FROM photos WHERE path = ?", (path,))

# Execute inserts
for merged in to_upsert:
    placeholders = ", ".join(["?"] * len(columns))
    cols = ", ".join(columns)
    values = [merged[col] for col in columns]
    c.execute(f"INSERT OR REPLACE INTO photos ({cols}) VALUES ({placeholders})", values)

conn.commit()
print(f"Deleted {len(set(to_delete))} old paths, upserted {len(to_upsert)} normalized paths.")
conn.close()
