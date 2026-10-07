import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Restore the <img> tag in month cards with a transparent 1x1 GIF
html = re.sub(
    r'card\.innerHTML = `<div class="mini-overlay">\$\{monthName\}</div>`;',
    r'card.innerHTML = `<img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="/><div class="mini-overlay">${monthName}</div>`;',
    html
)

# Restore the <img> tag in year cards with a transparent 1x1 GIF
html = re.sub(
    r'card\.innerHTML = `<div class="mini-overlay">\$\{year\}</div>`;',
    r'card.innerHTML = `<img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="/><div class="mini-overlay">${year}</div>`;',
    html
)

# Restore heroImages push
old_hero_push = r'''// Removed broken placeholder fallback\n                                      // heroImages.push\(\.\.\.\);'''
new_hero_push = r"heroImages.push('data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=');"
html = re.sub(old_hero_push, new_hero_push, html)

# Cache bump
html = html.replace('v=310', 'v=311')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Restored async image targets using transparent GIFs.")
