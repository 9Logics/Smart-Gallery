import re
path = 'app/static/style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace rewind-mini-card block to inject transition
css = re.sub(r'(\.rewind-mini-card\s*\{[^}]*?scroll-snap-align:\s*start;\s*)(\})', r'\1    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;\n\2', css)

# Replace rewind-hero-card block to inject transition
css = re.sub(r'(\.rewind-hero-card\s*\{[^}]*?box-shadow:\s*0\s+20px\s+50px\s+rgba\(0,0,0,0\.6\);\s*)(\})', r'\1    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;\n\2', css)

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Injected transitions using regex")
