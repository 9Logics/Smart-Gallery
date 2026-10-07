import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(
    r'<div class="recap-slide siena-depth" id="slide-person">.*?<h1 class="siena-layer" data-depth="40" id="recap-stat-person"></h1>\s*</div>',
    '''<div class="recap-slide siena-depth" id="slide-person">
                <h2 class="siena-layer" data-depth="20">You spent the most time with</h2>
                <div id="person-photos-fan" class="siena-layer" data-depth="50"></div>
                <h1 class="siena-layer" data-depth="70" id="recap-stat-person"></h1>
            </div>''',
    html,
    flags=re.DOTALL
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated slide-person HTML structure!")
