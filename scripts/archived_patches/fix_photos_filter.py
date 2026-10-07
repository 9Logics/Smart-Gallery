with open("app/static/js/views/photos.js", "r", encoding="utf-8") as f:
    content = f.read()

import re
content = re.sub(r"\['mp4','mov','avi','mkv','webm'\]", "['.mp4','.mov','.avi','.mkv','.webm','mp4','mov','avi','mkv','webm']", content)

with open("app/static/js/views/photos.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Regex replaced videos filter.")
