import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Fix Skiper 33
old_33 = "img.style.objectFit = 'cover';\n        img.style.borderRadius = '24px';\n        img.style.transform = 'perspective(1000px) rotateY(90deg) scale(0.5)';"
new_33 = "img.style.objectFit = 'contain';\n        img.style.borderRadius = '24px';\n        img.style.transform = 'perspective(1000px) rotateY(90deg) scale(0.5)';"
js_code = js_code.replace(old_33, new_33)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Fixed Skiper 33 aspect ratio")
