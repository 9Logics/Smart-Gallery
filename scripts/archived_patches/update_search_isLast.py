import re

with open('app/static/js/search.js', 'r', encoding='utf-8') as f:
    d = f.read()

# Replace Search filter
d = d.replace("createFilterChip('Query', `\"${state.filters.search}\"`, () => {", 
              "createFilterChip('Query', `\"${state.filters.search}\"`, true, () => {")

# Replace Date
d = d.replace("state.filters.date_query.forEach(dq => {", "state.filters.date_query.forEach((dq, idx, arr) => {")
d = d.replace("createFilterChip('Date', `${dq}`, () => {", "createFilterChip('Date', `${dq}`, idx === arr.length - 1, () => {")

# Replace People
d = d.replace("state.filters.people.forEach(pId => {", "state.filters.people.forEach((pId, idx, arr) => {")
d = d.replace("createFilterChip('Person', name, () => {", "createFilterChip('Person', name, idx === arr.length - 1, () => {")

# Replace Places
d = d.replace("state.filters.places.forEach(placeName => {", "state.filters.places.forEach((placeName, idx, arr) => {")
d = d.replace("createFilterChip('Place', placeName, () => {", "createFilterChip('Place', placeName, idx === arr.length - 1, () => {")

# Replace Albums
d = d.replace("state.filters.albums.forEach(albumId => {", "state.filters.albums.forEach((albumId, idx, arr) => {")
d = d.replace("createFilterChip('Album', name, () => {", "createFilterChip('Album', name, idx === arr.length - 1, () => {")

# Replace Types
d = d.replace("state.filters.types.forEach(type => {", "state.filters.types.forEach((type, idx, arr) => {")
d = d.replace("createFilterChip('Type', type, () => {", "createFilterChip('Type', type, idx === arr.length - 1, () => {")

# Replace Custom Paths
d = d.replace("createFilterChip('Area', 'Map bounds', () => {", "createFilterChip('Area', 'Map bounds', true, () => {")

# Modify createFilterChip definition
old_def = """function createFilterChip(type, label, onRemove) {
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
    lucide.createIcons({root: chip});
}"""

new_def = """function createFilterChip(type, label, isLast, onRemove) {
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    
    let btnHtml = isLast ? `<button><i data-lucide="x"></i></button>` : '';
    
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
    lucide.createIcons({root: chip});
}"""

d = d.replace(old_def, new_def)

with open('app/static/js/search.js', 'w', encoding='utf-8') as f:
    f.write(d)
