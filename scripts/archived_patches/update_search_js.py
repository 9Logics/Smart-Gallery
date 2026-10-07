import re

with open('app/static/js/search.js', 'r', encoding='utf-8') as f:
    d = f.read()

# 1. Update updateFiltersUI to reset tracking vars
d = d.replace("elements.activeFiltersList.innerHTML = '';\n    let hasFilters = false;", 
"""elements.activeFiltersList.innerHTML = '';
    let hasFilters = false;
    window._currentChipZIndex = 50;
    window._lastChipType = null;""")

# 2. Update createFilterChip
old_create = """function createFilterChip(type, label, onRemove) {
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    chip.innerHTML = `
        <span class="type">${type}:</span>
        <span>${label}</span>
        <button><i data-lucide="x"></i></button>
    `;
    chip.querySelector('button').addEventListener('click', onRemove);
    elements.activeFiltersList.appendChild(chip);
    lucide.createIcons();
}"""

new_create = """function createFilterChip(type, label, onRemove) {
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    
    // Stacking logic
    if (window._lastChipType === type) {
        chip.classList.add('stacked-chip');
        chip.style.zIndex = window._currentChipZIndex--;
        chip.innerHTML = `
            <span>${label}</span>
            <button><i data-lucide="x"></i></button>
        `;
    } else {
        chip.style.zIndex = window._currentChipZIndex--;
        chip.innerHTML = `
            <span class="type">${type}:</span>
            <span>${label}</span>
            <button><i data-lucide="x"></i></button>
        `;
    }
    
    window._lastChipType = type;
    
    chip.querySelector('button').addEventListener('click', onRemove);
    elements.activeFiltersList.appendChild(chip);
    lucide.createIcons();
}"""

if old_create in d:
    d = d.replace(old_create, new_create)
else:
    print("WARNING: Could not find old createFilterChip in search.js")

with open('app/static/js/search.js', 'w', encoding='utf-8') as f:
    f.write(d)
