import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove <img> from the month cards
html = re.sub(
    r'card\.innerHTML = `<img src="/static/images/placeholder\.png"/><div class="mini-overlay">\$\{monthName\}</div>`;',
    r'card.innerHTML = `<div class="mini-overlay">${monthName}</div>`;',
    html
)

# 2. Remove <img> from the year cards
html = re.sub(
    r'card\.innerHTML = `<img src="/static/images/placeholder\.png"/><div class="mini-overlay">\$\{year\}</div>`;',
    r'card.innerHTML = `<div class="mini-overlay">${year}</div>`;',
    html
)

# 3. Prevent placeholder.png background images on Hero Container
# We don't actually need to set placeholder backgrounds. Just leave them empty.
html = re.sub(
    r'return `/static/images/placeholder\.png`; // M6: Local fallback instead of picsum',
    r'return ``; // Removed broken placeholder',
    html
)

html = re.sub(
    r'heroImages\.push\(`/static/images/placeholder\.png`\);',
    r'// Removed broken placeholder fallback\n                                      // heroImages.push(...);',
    html
)

# Replace the backgroundImage assignment to check if it's not empty
html = re.sub(
    r'div\.style\.backgroundImage = `url\(\'\$\{src\}\'\)`;',
    r'if(src) div.style.backgroundImage = `url(\'${src}\')`;',
    html
)

# 4. Cache bump
html = html.replace('v=307', 'v=308')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched index.html to remove broken placeholder.png images.")
