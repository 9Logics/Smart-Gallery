import os

sidebar_path = 'app/templates/partials/sidebar.html'
with open(sidebar_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the literal <truncated 3 lines>
old_top = '''<truncated 3 lines>
                <span class="logo-text">Gallery</span>
            </div>'''

new_top = '''        <aside class="sidebar" id="sidebar">
            <div class="logo-container">
                <span class="logo-text" style="color: white; margin-right: 6px;">Smart</span>
                <span class="logo-text">Gallery</span>
            </div>'''

html = html.replace(old_top, new_top)

with open(sidebar_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Restored missing logo text and sidebar tags!")
