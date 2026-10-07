js_path = 'app/static/js/lightbox.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

target = '''            if (!faces || faces.length === 0) {
                if (section) section.style.display = 'none';
            } else {
                if (section) section.style.display = 'block';'''

replacement = '''            if (!faces || faces.length === 0) {
                if (section) section.style.display = 'block';
                elements.lightboxFacesList.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; font-style: italic; padding: 4px 0;">No people detected</div>';
            } else {
                if (section) section.style.display = 'block';'''

js = js.replace(target, replacement)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched lightbox.js to keep People section visible")
