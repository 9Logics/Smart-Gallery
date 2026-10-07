import os

sidebar_path = 'app/templates/partials/sidebar.html'
with open(sidebar_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the word Smart to not be overridden by logo-text transparent fill
old = '<span class="logo-text" style="color: white; margin-right: 6px;">Smart</span>'
new = '<span class="logo-text" style="color: white; -webkit-text-fill-color: initial; background: none; margin-right: 6px;">Smart</span>'

html = html.replace(old, new)

with open(sidebar_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed 'Smart' text coloring!")
