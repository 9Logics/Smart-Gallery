import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

old_block = """                    if (mPhotos.length === 1) {
                        heroContainer.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(mPhotos[0])}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                    }"""

new_block = """                    if (mPhotos.length === 1) {
                        heroContainer.style.display = 'block';
                        heroContainer.style.width = 'max-content';
                        heroContainer.style.height = 'max-content';
                        heroContainer.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(mPhotos[0])}" style="max-width: 80vw; max-height: 70vh; width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                    }"""

js_code = js_code.replace(old_block, new_block)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Single image logic patched!")
