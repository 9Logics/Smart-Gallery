// Stackable Filters Renderer
function updateFiltersUI() {
    elements.activeFiltersList.innerHTML = '';
    let hasFilters = false;
    
    // Search filter
    if (state.filters.search) {
        createFilterChip('search', `Query: "${state.filters.search}"`, () => {
            state.filters.search = '';
            elements.searchInput.value = '';
            elements.clearSearchBtn.classList.add('hidden');
            applyFilters();
        });
        hasFilters = true;
    }
    
    // Date filter
    state.filters.date_query.forEach(dq => {
        createFilterChip('calendar', `Date: ${dq}`, () => {
            state.filters.date_query = state.filters.date_query.filter(d => d !== dq);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // People chips
    state.filters.people.forEach(pId => {
        const person = state.people.find(p => p.id === pId);
        const name = person ? person.name : `Person ${pId}`;
        createFilterChip('person', name, () => {
            state.filters.people = state.filters.people.filter(id => id !== pId);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // Places chips
    state.filters.places.forEach(placeName => {
        createFilterChip('place', placeName, () => {
            state.filters.places = state.filters.places.filter(name => name !== placeName);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // Albums chips
    state.filters.albums.forEach(albumId => {
        const album = state.albums.find(a => a.id === albumId);
        const name = album ? album.name : `Album ${albumId}`;
        createFilterChip('album', name, () => {
            state.filters.albums = state.filters.albums.filter(id => id !== albumId);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // File Types chips
    state.filters.types.forEach(type => {
        createFilterChip('type', type, () => {
            state.filters.types = state.filters.types.filter(t => t !== type);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // Map Area Custom Paths chip
    if (state.filters.customPaths) {
        createFilterChip('place', 'Map Area', () => {
            state.filters.customPaths = null;
            applyFilters();
        });
        hasFilters = true;
    }
    
    if (hasFilters) {
        elements.filtersPanel.classList.remove('hidden');
    } else {
        elements.filtersPanel.classList.add('hidden');
    }
}

function createFilterChip(type, label, onRemove) {
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
}

function clearAllFilters() {
    state.filters = {
        people: [],
        places: [],
        albums: [],
        types: [],
        year: '',
        month: '',
        search: '',
        date_query: [],
        customPaths: null
    };
    elements.searchInput.value = '';
    elements.clearSearchBtn.classList.add('hidden');
    applyFilters();
}

function applyFilters() {
    updateFiltersUI();
    if (state.currentView !== 'photos' && state.currentView !== 'archive' && state.currentView !== 'favorites') {
        switchView('photos');
    } else {
        loadPhotos();
    }
}

// Fetch & Load Photos
let searchDebounceTimer = null;
function handleSearchInput() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        executeSearchSuggestions();
    }, 300);
}

async function executeSearchSuggestions() {
    const val = elements.searchInput.value.trim().toLowerCase();
    
    if (val.length > 0) {
        elements.clearSearchBtn.classList.remove('hidden');
    } else {
        elements.clearSearchBtn.classList.add('hidden');
        elements.searchSuggestions.classList.add('hidden');
        return;
    }
    
    elements.searchSuggestions.innerHTML = '';
    
    // 1. Matches People
    const matchedPeople = state.people.filter(p => p.name.toLowerCase().includes(val)).slice(0, 4);
    matchedPeople.forEach(p => {
        const thumbUrl = p.cover_face_id ? `/api/photo/crop/${p.cover_face_id}` : null;
        createSuggestionItem('users', p.name, 'Person', () => {
            if (!state.filters.people.includes(p.id)) {
                state.filters.people.push(p.id);
            }
            clearSearchInput();
            applyFilters();
        }, thumbUrl);
    });
    
    // 2. Matches Places
    const matchedPlaces = state.places.filter(p => p.name.toLowerCase().includes(val)).slice(0, 4);
    matchedPlaces.forEach(p => {
        createSuggestionItem('map-pin', p.name, 'Place', () => {
            if (!state.filters.places.includes(p.name)) {
                state.filters.places.push(p.name);
            }
            clearSearchInput();
            applyFilters();
        });
    });
    
    // 2.5 Matches Albums
    const matchedAlbums = state.albums.filter(a => a.name.toLowerCase().includes(val)).slice(0, 4);
    matchedAlbums.forEach(a => {
        createSuggestionItem('folder-heart', a.name, 'Album', () => {
            if (!state.filters.albums.includes(a.id)) {
                state.filters.albums.push(a.id);
            }
            clearSearchInput();
            applyFilters();
        });
    });
    
    // 3. File Types suggestions
    const fileTypes = ['JPG', 'JPEG', 'PNG', 'WEBP', 'BMP', 'MP4', 'MOV', 'HEVC'];
    const matchedTypes = fileTypes.filter(t => t.toLowerCase().includes(val));
    matchedTypes.forEach(t => {
        createSuggestionItem('file', t, 'File Type', () => {
            if (!state.filters.types.includes(t)) {
                state.filters.types.push(t);
            }
            clearSearchInput();
            applyFilters();
        });
    });
    
    // 4. Default query option
    createSuggestionItem('search', `Search for "${val}"`, 'Text Query', () => {
        state.filters.search = val;
        elements.searchSuggestions.classList.add('hidden');
        applyFilters();
    });

    // 5. Smart Date Search via Backend API
    try {
        const res = await fetch(`/api/search/suggestions?q=${encodeURIComponent(val)}`);
        if (res.ok) {
            const dateSuggestions = await res.json();
            dateSuggestions.forEach(ds => {
                createSuggestionItem('calendar', ds.label, ds.description, () => {
                    // Clicking a date suggestion applies it as the main search query
                    if (!state.filters.date_query.includes(ds.id)) {
                        state.filters.date_query.push(ds.id);
                    }
                    state.filters.search = ''; // Clear text search
                    elements.searchInput.value = ''; // Clear input to show it became a chip
                    elements.searchSuggestions.classList.add('hidden');
                    elements.clearSearchBtn.classList.add('hidden');
                    applyFilters();
                });
            });
        }
    } catch(err) {
        console.error("Date suggestion fetch failed:", err);
    }
    
    if (elements.searchSuggestions.children.length > 0) {
        elements.searchSuggestions.classList.remove('hidden');
    } else {
        elements.searchSuggestions.classList.add('hidden');
    }
    
    // Performance fix: Batch icon creation instead of running in a loop
    lucide.createIcons();
}

function createSuggestionItem(iconName, text, type, onClick, imgUrl = null) {
    const div = document.createElement('div');
    div.className = 'suggestion-item';
    
    let iconHtml = `<i data-lucide="${iconName}"></i>`;
    if (imgUrl) {
        iconHtml = `<img src="${imgUrl}" alt="Thumbnail" style="width: 18px; height: 18px; border-radius: 50%; object-fit: cover; margin-right: 8px;">`;
    }
    
    div.innerHTML = `
        ${iconHtml}
        <span>${text}</span>
        <span class="type-badge">${type}</span>
    `;
    div.addEventListener('click', onClick);
    elements.searchSuggestions.appendChild(div);
}

function handleSearchKeydown(e) {
    if (e.key === 'Enter') {
        const val = elements.searchInput.value.trim();
        if (val) {
            state.filters.search = val;
            elements.searchSuggestions.classList.add('hidden');
            applyFilters();
        }
    }
}

function clearSearchInput() {
    elements.searchInput.value = '';
    elements.clearSearchBtn.classList.add('hidden');
    elements.searchSuggestions.classList.add('hidden');
}

function clearSearch() {
    clearSearchInput();
    if (state.filters.search) {
        state.filters.search = '';
        applyFilters();
    }
}
