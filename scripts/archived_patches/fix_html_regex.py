import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace slide-place
html = re.sub(r'<div class="recap-slide[^>]*id="slide-place".*?(?=<div class="recap-slide[^>]*id="slide-hero")', '', html, flags=re.DOTALL)

# Replace slide-hero
replacement = '''            <div class="recap-slide siena-depth" id="slide-top-places">
                <h1 class="siena-layer places-master-title" data-depth="40">YOUR EPIC JOURNEYS</h1>
                <div class="places-accordion-container siena-layer" data-depth="20" id="places-accordion">
                    <!-- Injected by JS -->
                </div>
            </div>
'''
html = re.sub(r'<div class="recap-slide[^>]*id="slide-hero".*?(?=<div class="recap-slide[^>]*id="slide-finale")', replacement, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Regex patched index.html to insert slide-top-places and remove legacy slides")
