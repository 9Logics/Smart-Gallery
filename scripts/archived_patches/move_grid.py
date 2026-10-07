import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract story-grid-view
grid_view_pattern = re.compile(r'(<!-- Story Grid View -->\s*<div id="story-grid-view".*?</div>\s*</div>)', re.DOTALL)
match = grid_view_pattern.search(html)

if match:
    # Wait, the closing div might be tricky. Let's just do it precisely by string splitting.
    pass
