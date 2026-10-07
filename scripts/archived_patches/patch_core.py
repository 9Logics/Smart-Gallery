import re
path = 'app/static/js/core.js'
with open(path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace direct references with safe references
replacements = [
    ('elements.multiArchiveBtn.addEventListener(\'click\', archiveSelectedPhotos);',
     'if (typeof archiveSelectedPhotos !== "undefined") elements.multiArchiveBtn.addEventListener(\'click\', archiveSelectedPhotos);'),
    ('elements.multiTrashBtn.addEventListener(\'click\', trashSelectedPhotos);',
     'if (typeof trashSelectedPhotos !== "undefined") elements.multiTrashBtn.addEventListener(\'click\', trashSelectedPhotos);'),
    ('elements.lightboxArchiveBtn.addEventListener(\'click\', toggleLightboxPhotoArchive);',
     'if (typeof toggleLightboxPhotoArchive !== "undefined") elements.lightboxArchiveBtn.addEventListener(\'click\', toggleLightboxPhotoArchive);'),
    ('elements.lightboxTrashBtn.addEventListener(\'click\', trashCurrentLightboxPhoto);',
     'if (typeof trashCurrentLightboxPhoto !== "undefined") elements.lightboxTrashBtn.addEventListener(\'click\', trashCurrentLightboxPhoto);')
]

for old, new in replacements:
    js = js.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched core.js to be robust against missing selection functions")
