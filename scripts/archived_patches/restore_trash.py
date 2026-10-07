import os
import json
import shutil

with open('all_possible_paths_hash_map.json', 'r', encoding='utf-8') as f:
    hash_map = json.load(f)

trash_dir = '.cache/trash'
files = os.listdir(trash_dir)

restored_count = 0
skipped_count = 0

for file in files:
    # Extract hash (remove extension and timestamp if any)
    name, ext = os.path.splitext(file)
    # The file might just be the hash (32 chars)
    file_hash = name.split('_')[0] if '_' in name else name
    
    if file_hash in hash_map:
        original_path = hash_map[file_hash]
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        
        # Avoid overwriting existing files
        final_path = original_path
        counter = 1
        while os.path.exists(final_path):
            base, original_ext = os.path.splitext(original_path)
            final_path = f"{base}_recovered_{counter}{original_ext}"
            counter += 1
            
        source_path = os.path.join(trash_dir, file)
        shutil.move(source_path, final_path)
        print(f"Restored {file} -> {final_path}")
        restored_count += 1
    else:
        print(f"No mapping found for {file}")
        skipped_count += 1

print(f"Successfully restored {restored_count} files!")
print(f"Skipped {skipped_count} files (no mapping found).")
