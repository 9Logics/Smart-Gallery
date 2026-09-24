import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add script tag
if 'recap_player.js' not in html:
    html = html.replace('<script src="/static/js/core.js', '<script src="/static/js/recap_player.js?v=275"></script>\n    <script src="/static/js/core.js')
    
# Update hero card click
html = html.replace('<div class="rewind-hero-card">', '<div class="rewind-hero-card" onclick="openRecapPlayer(this, \'2026\')">')

# Update year cards
html = html.replace('<div class="rewind-mini-card year-card">', '<div class="rewind-mini-card year-card" onclick="openRecapPlayer(this, this.innerText.trim())">')

# Update monthly cards
html = html.replace('<div class="rewind-mini-card">', '<div class="rewind-mini-card" onclick="openRecapPlayer(this, new Date().getFullYear())">')

html = html.replace('v=274', 'v=275')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Injected JS tag and onclick events to index.html!")
