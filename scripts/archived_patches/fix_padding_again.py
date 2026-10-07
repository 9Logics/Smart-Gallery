import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    d = f.read()

target1 = """.filter-chip.stack-parent {
    padding-right: 32px !important;
}"""

replacement1 = """.filter-chip.stack-parent {
    padding-right: 24px !important;
}"""

target2 = """.filter-chip.stacked-chip {
    margin-left: -28px;
    padding-left: 16px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
    background: rgba(255, 255, 255, 0.08); /* slightly darker/different to show layering */
}"""

replacement2 = """.filter-chip.stacked-chip {
    margin-left: -28px;
    padding-left: 44px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
    background: rgba(255, 255, 255, 0.08); /* slightly darker/different to show layering */
}"""

if target1 in d:
    d = d.replace(target1, replacement1)
else:
    print("WARNING: target1 not found")

if target2 in d:
    d = d.replace(target2, replacement2)
else:
    print("WARNING: target2 not found")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(d)
