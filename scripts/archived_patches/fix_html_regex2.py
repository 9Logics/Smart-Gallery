import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

replacement = '''            <div class="recap-slide siena-depth" id="slide-top-places">
                <h1 class="siena-layer places-master-title" data-depth="40">YOUR EPIC JOURNEYS</h1>
                <div class="places-accordion-container siena-layer" data-depth="20" id="places-accordion">
                    <!-- Injected by JS -->
                </div>
            </div>
'''
html = re.sub(r'<div class="recap-slide" id="slide-hero">.*?</div>\s*</div>\s*</div>', replacement + '\n          </div>\n      </div>', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Replaced slide-hero with slide-top-places")
