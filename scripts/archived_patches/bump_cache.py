with open("app/templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
# Find the highest version number currently in use
match = re.search(r'\?v=(\d+)', content)
if match:
    old_v = match.group(1)
    new_v = str(int(old_v) + 1)
    content = content.replace(f"?v={old_v}", f"?v={new_v}")
    
    with open("app/templates/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Bumped cache version from {old_v} to {new_v}")
else:
    print("Could not find cache version")
