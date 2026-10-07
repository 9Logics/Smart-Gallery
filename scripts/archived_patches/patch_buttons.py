import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

target = '''        <div class="recap-nav-left" onclick="prevRecapSlide()"></div>
        <div class="recap-nav-right" onclick="nextRecapSlide()"></div>'''

replacement = '''        <div class="recap-bottom-controls">
            <button class="recap-nav-btn" onclick="prevRecapSlide()">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                Previous
            </button>
            <button class="recap-nav-btn" onclick="nextRecapSlide()">
                Next
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </button>
        </div>'''

html = html.replace(target, replacement)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated HTML buttons")
