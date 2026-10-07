import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Remove the old margin-left: -16px from .filter-chip
css = re.sub(r'margin-left:\s*-16px;\s*', '', css)

# 2. Remove the old nth-of-type z-index hacks
css = re.sub(r'\.filters-panel > div\.filter-chip:nth-of-type\(\d+\)[^\n]*\n', '', css)

# 3. Add the new animations and stacked-chip class
new_css = '''
@keyframes chipEnter {
    0% { opacity: 0; transform: translateX(20px) scale(0.9); }
    100% { opacity: 1; transform: translateX(0) scale(1); }
}

.filter-chip {
    margin-left: 8px;
    animation: chipEnter 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

.filter-chip:first-child {
    margin-left: 0;
}

.filter-chip.stacked-chip {
    margin-left: -20px;
    padding-left: 28px;
    background: rgba(255, 255, 255, 0.08); /* slightly darker/different to show layering */
}

/* Make sure the text inside the chips is vertically centered */
.filter-chip span {
    display: inline-block;
    line-height: 1;
}
'''
css += new_css

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

