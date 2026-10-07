import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = re.compile(r'(<button id="story-mute-btn" class="btn-icon story-bottom-btn hidden"><i data-lucide="volume-2"></i></button>\s*</div>)\s*<button id="story-mute-btn" class="btn-icon story-bottom-btn"><i data-lucide="volume-2"></i></button>\s*</div>', re.DOTALL)

html, count = pattern.subn(r'\1', html)
if count > 0:
    print(f"Fixed {count} instances of broken HTML divs!")
else:
    print("Target not found with regex!")

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
