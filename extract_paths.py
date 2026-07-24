import hashlib
import json
import os
import string

def extract_strings(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    current_string = bytearray()
    strings = set()
    
    # Print printable characters
    for byte in data:
        if 32 <= byte <= 126:
            current_string.append(byte)
        else:
            if len(current_string) > 20:
                try:
                    s = current_string.decode('ascii')
                    if 'D:\\Anurag\\Google Drive\\' in s:
                        # Extract the exact path by finding the substring
                        idx = s.find('D:\\Anurag\\Google Drive\\')
                        if idx != -1:
                            # The string might end with valid extensions like .jpg, .heic, .mp4, etc.
                            # We can try to split by known extensions or just keep it
                            path = s[idx:]
                            # Trim trailing spaces or non-path characters if any
                            # Actually, since it's ascii printable, it might include nearby text
                            # Let's try to match a valid filename structure
                            import re
                            m = re.match(r'(D:\\Anurag\\Google Drive\\[a-zA-Z0-9_\-\\ \(\)\.]+\.(jpg|jpeg|png|heic|webp|mp4|gif))', path, re.IGNORECASE)
                            if m:
                                strings.add(m.group(1))
                except:
                    pass
            current_string = bytearray()
    return strings

paths = extract_strings('.cache/gallery.db') | extract_strings('.cache/gallery.db-wal')
print(f"Extracted {len(paths)} unique paths.")

hash_map = {}
for p in paths:
    h = hashlib.md5(p.encode('utf-8')).hexdigest()
    hash_map[h] = p

with open('all_possible_paths_hash_map.json', 'w', encoding='utf-8') as f:
    json.dump(hash_map, f, indent=2)

print("Saved all_possible_paths_hash_map.json")
