import re

with open('app/static/js/views/memories.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace dashboard albums skeleton
js = re.sub(
    r'\$\{Array\(3\)\.fill\('"'<div class=\"skeleton-card\" style=\"aspect-ratio: 1; border-radius: 12px; flex: 1; min-width: 0;\"></div>'"'\)\.join\('"'\""'\)\}',
    r'\$\{Array(6).fill(\'<div class="skeleton-card" style="width: 140px; height: 140px; border-radius: 12px; flex: 0 0 auto;"></div>\').join(\'\')\}',
    js
)

# Replace people spotlight skeleton
js = re.sub(
    r'<div class=\"skeleton-card\" style=\"width: 250px; height: 160px; border-radius: 12px; flex-shrink: 0;\"></div>\s*<div class=\"skeleton-card\" style=\"flex: 1; height: 160px; border-radius: 12px;\"></div>',
    r'\$\{Array(6).fill(\'<div class="skeleton-card" style="width: 100px; height: 140px; border-radius: 12px; flex: 0 0 auto;"></div>\').join(\'\')\}',
    js
)

with open('app/static/js/views/memories.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('Done!')
