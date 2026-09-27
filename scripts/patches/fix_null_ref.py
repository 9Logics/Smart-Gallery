import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Fix the global scope error
js_code = js_code.replace("let recapCurrentSlide = 0; document.getElementById('slide-montage').style.display = 'none';", "let recapCurrentSlide = 0;")

# Fix the local scope error by ensuring it checks for null first
js_code = js_code.replace("recapCurrentSlide = 0; document.getElementById('slide-montage').style.display = 'none';", "recapCurrentSlide = 0; if(document.getElementById('slide-montage')) document.getElementById('slide-montage').style.display = 'none';")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Fixed null reference in recap_player.js")
