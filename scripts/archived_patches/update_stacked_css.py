import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    d = f.read()

target = """.filter-chip.stacked-chip {
    margin-left: -20px;
    padding-left: 28px;
    background: rgba(255, 255, 255, 0.08); /* slightly darker/different to show layering */
}"""

replacement = """.filter-chip.stacked-chip {
    margin-left: -28px;
    padding-left: 38px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
    background: rgba(255, 255, 255, 0.08); /* slightly darker/different to show layering */
}"""

if target in d:
    d = d.replace(target, replacement)
else:
    print("WARNING: Could not find target CSS")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(d)
