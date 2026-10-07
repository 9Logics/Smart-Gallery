import re

with open('app/static/js/search.js', 'r', encoding='utf-8') as f:
    d = f.read()

target = """    if (hasFilters) {
        const clearBtn = document.createElement('button');
        clearBtn.className = 'btn-clear-all';
        clearBtn.title = 'Clear all filters';
        clearBtn.innerHTML = '<i data-lucide="x"></i>';
        clearBtn.addEventListener('click', clearAllFilters);
        elements.activeFiltersList.appendChild(clearBtn);
        lucide.createIcons({root: elements.activeFiltersList});
        
        elements.filtersPanel.classList.remove('hidden');
        document.querySelector('.view-panel').classList.add('has-filters');
    } else {"""

replacement = """    if (hasFilters) {
        elements.filtersPanel.classList.remove('hidden');
        document.querySelector('.view-panel').classList.add('has-filters');
    } else {"""

if target in d:
    d = d.replace(target, replacement)
else:
    print("WARNING: target not found")

with open('app/static/js/search.js', 'w', encoding='utf-8') as f:
    f.write(d)
