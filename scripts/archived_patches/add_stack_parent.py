import re

with open('app/static/js/search.js', 'r', encoding='utf-8') as f:
    d = f.read()

target = """    if (window._lastChipType === type) {"""
replacement = """    if (!isLast) {
        chip.classList.add('stack-parent');
    }
    
    // Stacking logic
    if (window._lastChipType === type) {"""

if target in d:
    d = d.replace(target, replacement)
else:
    print("WARNING: target not found")

with open('app/static/js/search.js', 'w', encoding='utf-8') as f:
    f.write(d)
