import re
path = 'app/static/style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Add transition to .photo-card img
css = re.sub(
    r'(\.photo-card img\s*\{[^}]*?object-fit:\s*cover;\s*)(\})',
    r'\1    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), filter 0.4s ease;\n\2',
    css
)

# 2. Add transition to .photo-thumbnail
css = re.sub(
    r'(\.photo-thumbnail\s*\{[^}]*?border-radius:\s*8px;\s*)(\})',
    r'\1    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), filter 0.4s ease;\n\2',
    css
)

# 3. Add transition to .album-card, .person-card, .place-card
css = re.sub(
    r'(\.album-card,\s*\.person-card,\s*\.place-card\s*\{[^}]*?box-shadow:[^;]+;\s*)(\})',
    r'\1    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease;\n\2',
    css
)

# 4. Add transition to .hero-bg-container
css = re.sub(
    r'(\.hero-bg-container\s*\{[^}]*?display:\s*flex;\s*)(\})',
    r'\1    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);\n\2',
    css
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)

print("Added fluid transitions to photo cards, album cards, and hero image.")
