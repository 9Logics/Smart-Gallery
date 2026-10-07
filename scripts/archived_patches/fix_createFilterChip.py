import re

with open('app/static/js/search.js', 'r', encoding='utf-8') as f:
    d = f.read()

# Find the start of createFilterChip
start_idx = d.find("function createFilterChip(type, label, onRemove) {")
if start_idx != -1:
    # Find the end of the function. We know it's followed by `function hasAnyActiveFilter()`
    end_idx = d.find("function hasAnyActiveFilter() {", start_idx)
    if end_idx != -1:
        new_func = """function createFilterChip(type, label, isLast, onRemove) {
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    
    let btnHtml = isLast ? `<button><i data-lucide="x"></i></button>` : '';
    
    if (!isLast) {
        chip.classList.add('stack-parent');
    }
    
    // Stacking logic
    if (window._lastChipType === type) {
        chip.classList.add('stacked-chip');
        chip.style.zIndex = window._currentChipZIndex--;
        chip.innerHTML = `
            <span>${label}</span>
            ${btnHtml}
        `;
    } else {
        chip.style.zIndex = window._currentChipZIndex--;
        chip.innerHTML = `
            <span class="type">${type}:</span>
            <span>${label}</span>
            ${btnHtml}
        `;
    }
    
    window._lastChipType = type;
    
    if (isLast) {
        chip.querySelector('button').addEventListener('click', onRemove);
    }
    
    elements.activeFiltersList.appendChild(chip);
    if (isLast) {
        lucide.createIcons({root: chip});
    }
}

"""
        d = d[:start_idx] + new_func + d[end_idx:]
        with open('app/static/js/search.js', 'w', encoding='utf-8') as f:
            f.write(d)
        print("Successfully replaced createFilterChip")
    else:
        print("Could not find end of function")
else:
    print("Could not find start of function")
