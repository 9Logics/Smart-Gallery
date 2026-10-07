path = 'app/templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

target = """                preloader.style.display = 'flex';
                preloader.style.opacity = '1';
                progressEl.style.width = '0%';"""

replacement = """                preloader.style.opacity = '0';
                preloader.style.display = 'flex';
                progressEl.style.width = '0%';
                
                // Force reflow so transition works from display: none
                void preloader.offsetWidth;
                preloader.style.opacity = '1';"""

html = html.replace(target, replacement)

# Bump cache to v=401
html = html.replace("v=400", "v=401")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched index.html")
