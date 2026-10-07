import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace backgroundImage with src
js = re.sub(r'item\.style\.backgroundImage\s*=\s*`url\("(.+?)"\)`', r'item.src = `\1`', js)

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Regex replace done!")
