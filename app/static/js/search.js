// Stackable Filters Renderer
function updateFiltersUI() {
    elements.activeFiltersList.innerHTML = '';
    let hasFilters = false;
    window._currentChipZIndex = 50;
    window._lastChipType = null;
    
    // Search filter
    if (state.filters.search) {
        createFilterChip('Query', `"${state.filters.search}"`, true, () => {
            state.filters.search = '';
            elements.searchInput.value = '';
            elements.clearSearchBtn.classList.add('hidden');
            applyFilters();
        });
        hasFilters = true;
    }
    
    // Date filter
    state.filters.date_query.forEach((dq, idx, arr) => {
        createFilterChip('Date', `${dq}`, idx === arr.length - 1, () => {
            state.filters.date_query = state.filters.date_query.filter(d => d !== dq);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // People chips
    state.filters.people.forEach((pId, idx, arr) => {
        const person = state.people.find(p => p.id === pId);
        const name = person ? person.name : `Person ${pId}`;
        createFilterChip('Person', name, idx === arr.length - 1, () => {
            state.filters.people = state.filters.people.filter(id => id !== pId);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // Places chips
    state.filters.places.forEach((placeName, idx, arr) => {
        createFilterChip('Place', placeName, idx === arr.length - 1, () => {
            state.filters.places = state.filters.places.filter(name => name !== placeName);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // Albums chips
    state.filters.albums.forEach((albumId, idx, arr) => {
        const album = state.albums.find(a => a.id === albumId);
        const name = album ? album.name : `Album ${albumId}`;
        createFilterChip('Album', name, idx === arr.length - 1, () => {
            state.filters.albums = state.filters.albums.filter(id => id !== albumId);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // File Types chips
    state.filters.types.forEach((type, idx, arr) => {
        createFilterChip('Type', type, idx === arr.length - 1, () => {
            state.filters.types = state.filters.types.filter(t => t !== type);
            applyFilters();
        });
        hasFilters = true;
    });
    
    // Map Area Custom Paths chip
    if (state.filters.customPaths) {
        createFilterChip('Area', 'Map bounds', true, () => {
            state.filters.customPaths = null;
            applyFilters();
        });
        hasFilters = true;
    }
    
    if (hasFilters) {
        elements.filtersPanel.classList.remove('hidden');
        document.querySelector('.view-panel').classList.add('has-filters');
    } else {
        elements.filtersPanel.classList.add('hidden');
        document.querySelector('.view-panel').classList.remove('has-filters');
    }
}

function createFilterChip(type, label, isLast, onRemove) {
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

function hasAnyActiveFilter() {
    return state.filters.search ||
        state.filters.people.length > 0 ||
        state.filters.places.length > 0 ||
        state.filters.albums.length > 0 ||
        state.filters.types.length > 0 ||
        state.filters.date_query.length > 0 ||
        state.filters.customPaths;
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

let smartSearchPromptShown = false;

function applyFilters() {
    updateFiltersUI();
    if (state.currentView !== 'photos' && state.currentView !== 'archive' && state.currentView !== 'favorites') {
        switchView('photos');
    } else {
        loadPhotos();
    }
    
    if (state.filters.search && localStorage.getItem('smart-search-mode') === 'false' && !smartSearchPromptShown) {
        smartSearchPromptShown = true;
        showSmartSearchToast();
    }
}

function showSmartSearchToast() {
    const toast = document.createElement('div');
    toast.className = 'smart-search-toast';
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); cursor: pointer; position: fixed; bottom: 24px; right: 24px; z-index: 9999; transform: translateY(100px); opacity: 0; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.2);">
            <i data-lucide="sparkles" style="color: var(--primary-color);"></i>
            <div>
                <div style="font-weight: 600; font-size: 14px; margin-bottom: 2px;">Smart Search is Off</div>
                <div style="font-size: 12px; color: var(--text-muted);">Click to turn on AI semantic search for better results.</div>
            </div>
            <i data-lucide="x" class="toast-close" style="margin-left: 8px; width: 16px; height: 16px; color: var(--text-muted);"></i>
        </div>
    `;
    document.body.appendChild(toast);
    lucide.createIcons({root: toast});
    
    const toastDiv = toast.firstElementChild;
    
    // Animate in
    setTimeout(() => {
        toastDiv.style.transform = 'translateY(0)';
        toastDiv.style.opacity = '1';
    }, 100);
    
    let hideTimeout = setTimeout(hideToast, 12000); // 12 seconds
    
    function hideToast() {
        toastDiv.style.transform = 'translateY(100px)';
        toastDiv.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }
    
    toastDiv.querySelector('.toast-close').addEventListener('click', (e) => {
        e.stopPropagation();
        clearTimeout(hideTimeout);
        hideToast();
    });
    
    toastDiv.addEventListener('click', () => {
        clearTimeout(hideTimeout);
        hideToast();
        switchView('settings');
        
        setTimeout(() => {
            const settingEl = document.getElementById('setting-smart-search');
            if (settingEl) {
                settingEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Highlight animation
                let count = 0;
                const highlightInterval = setInterval(() => {
                    settingEl.style.transition = 'background-color 0.3s ease';
                    settingEl.style.backgroundColor = 'rgba(99, 102, 241, 0.2)'; // var(--accent-color) with opacity
                    setTimeout(() => {
                        settingEl.style.backgroundColor = 'transparent';
                    }, 400);
                    
                    count++;
                    if (count >= 2) clearInterval(highlightInterval);
                }, 800);
            }
        }, 500); // Wait for view to switch
    });
}

// Fetch & Load Photos
let searchDebounceTimer = null;
function handleSearchInput() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        executeSearchSuggestions();
    }, 300);
}

function showDefaultSearchSuggestions() {
    elements.searchSuggestions.innerHTML = '';
    
    // Top People Row
    const peopleRowContainer = document.createElement('div');
    peopleRowContainer.className = 'search-suggestions-people-row';
    peopleRowContainer.style.display = 'flex';
    peopleRowContainer.style.gap = '12px';
    peopleRowContainer.style.padding = '12px 16px';
    peopleRowContainer.style.borderBottom = '1px solid var(--border-color)';
    peopleRowContainer.style.overflowX = 'auto';
    
    if (typeof state !== 'undefined' && state.people && state.people.length > 0) {
        const topPeople = [...state.people]
            .filter(p => p.name && !p.name.startsWith('Person '))
            .slice(0, 7);
            
        if (topPeople.length > 0) {
            topPeople.forEach(p => {
                const pEl = document.createElement('div');
                pEl.style.display = 'flex';
                pEl.style.flexDirection = 'column';
                pEl.style.alignItems = 'center';
                pEl.style.cursor = 'pointer';
                pEl.style.gap = '6px';
                
                let coverHtml = `<div style="width: 44px; height: 44px; border-radius: 50%; background: var(--hover-color); display: flex; align-items: center; justify-content: center;"><i data-lucide="user" style="width: 20px;"></i></div>`;
                if (p.cover_face_id) {
                    coverHtml = `<img src="/api/photo/crop/${p.cover_face_id}" style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover;">`;
                }
                
                pEl.innerHTML = `
                    ${coverHtml}
                    <span style="font-size: 11px; color: var(--text-muted); max-width: 50px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${p.name.split(' ')[0]}</span>
                `;
                pEl.addEventListener('click', () => {
                    if (!state.filters.people.includes(p.id)) state.filters.people.push(p.id);
                    clearSearchInput();
                    applyFilters();
                });
                peopleRowContainer.appendChild(pEl);
            });
            elements.searchSuggestions.appendChild(peopleRowContainer);
        }
    }
    
    // Suggestions Title
    const title = document.createElement('div');
    title.style.padding = '12px 16px 4px';
    title.style.fontSize = '12px';
    title.style.fontWeight = '600';
    title.style.color = 'var(--text-muted)';
    title.style.textTransform = 'uppercase';
    title.innerText = 'Suggested Searches';
    elements.searchSuggestions.appendChild(title);
    
    // Suggest some Themes
    const commonTags = ["concert", "wedding", "nature", "party", "car", "beach", "dogs", "food", "mountains", "architecture"];
    commonTags.sort(() => 0.5 - Math.random());
    const tagsToSuggest = commonTags.slice(0, 2);
    
    tagsToSuggest.forEach(tag => {
        createSuggestionItem('search', tag, 'Theme', () => {
            state.filters.search = tag;
            const searchInputEl = document.getElementById('search-input');
            if (searchInputEl) searchInputEl.value = tag;
            const clearBtn = document.getElementById('clear-search-btn');
            if (clearBtn) clearBtn.classList.remove('hidden');
            elements.searchSuggestions.classList.add('hidden');
            applyFilters();
        });
    });
    
    // Suggest some Places
    let allPlaces = [];
    if (typeof state !== 'undefined' && state.places) {
        state.places.forEach(country => {
            if (country.places) country.places.forEach(p => allPlaces.push(p.name));
            else allPlaces.push(country.name);
        });
    }
    
    if (allPlaces.length > 0) {
        allPlaces.sort(() => 0.5 - Math.random());
        const placesToSuggest = allPlaces.slice(0, 2);
        placesToSuggest.forEach(place => {
            createSuggestionItem('map-pin', place, 'Place', () => {
                if (!state.filters.places.includes(place)) {
                    state.filters.places.push(place);
                }
                clearSearchInput();
                applyFilters();
            });
        });
    } else {
        createSuggestionItem('map-pin', 'Haryana', 'Place', () => {
            state.filters.search = 'Haryana';
            const searchInputEl = document.getElementById('search-input');
            if (searchInputEl) searchInputEl.value = 'Haryana';
            applyFilters();
            elements.searchSuggestions.classList.add('hidden');
        });
    }
    
    elements.searchSuggestions.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
}

async function executeSearchSuggestions() {
    const val = elements.searchInput.value.trim().toLowerCase();
    
    if (val.length > 0) {
        elements.clearSearchBtn.classList.remove('hidden');
    } else {
        elements.clearSearchBtn.classList.add('hidden');
        showDefaultSearchSuggestions();
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
    const allPlaces = state.places && state.places.length > 0 && state.places[0].city ? state.places.flatMap(g => g.places) : state.places;
    const matchedPlaces = allPlaces.filter(p => p && p.name && p.name.toLowerCase().includes(val)).slice(0, 4);
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
    
    // 3.5 Matches AI Tags
    const allAiTags = new Set();
    if (typeof state !== 'undefined' && state.photos) {
        state.photos.forEach(photo => {
            if (photo.ai_tags && Array.isArray(photo.ai_tags)) {
                photo.ai_tags.forEach(tag => {
                    if (typeof tag !== 'string') return;
                    
                    // Split complex tags like "egyptian cat" into individual words
                    const words = tag.toLowerCase().split(/\s+/);
                    words.forEach(w => {
                        // Only add words that are 3 characters or longer to avoid noisy 2-letter words
                        if (w.length >= 3) allAiTags.add(w);
                    });
                    // Also add the full tag in case they want to search the exact phrase
                    allAiTags.add(tag.toLowerCase());
                });
            }
        });
    }
    // Only match tags that START with the search value or exactly equal it
    // This prevents "cat" from matching "polecat" or "catamaran" in the suggestions
    const matchedAiTags = Array.from(allAiTags).filter(tag => tag === val || tag.startsWith(val + ' ')).slice(0, 4);
    
    // Actually, we want to suggest tags that exactly equal or start with the value
    let filteredTags = Array.from(allAiTags).filter(tag => tag.startsWith(val));
    
    // Sort them so shorter tags (like "cat") appear before longer ones (like "catamaran")
    filteredTags.sort((a, b) => a.length - b.length);
    filteredTags = filteredTags.slice(0, 4);
    matchedAiTags.forEach(tag => {
        createSuggestionItem('tag', tag, 'AI Tag', () => {
            state.filters.search = tag;
            const searchInputEl = document.getElementById('search-input');
            if (searchInputEl) searchInputEl.value = tag;
            const clearBtn = document.getElementById('clear-search-btn');
            if (clearBtn) clearBtn.classList.remove('hidden');
            elements.searchSuggestions.classList.add('hidden');
            applyFilters();
        });
    });
    
    
    // Matches Full Address Parts
    const allAddressParts = new Set();
    if (typeof state !== 'undefined' && state.photos) {
        state.photos.forEach(photo => {
            if (photo.full_address) {
                photo.full_address.split(',').forEach(part => {
                    const p = part.trim();
                    if (p && !/^\\d{4,10}$/.test(p)) {
                        allAddressParts.add(p);
                    }
                });
            }
        });
    }
    
    const matchedParts = Array.from(allAddressParts)
        .filter(part => part.toLowerCase().includes(val) && !matchedPlaces.some(mp => mp.name === part))
        .slice(0, 4);
        
    matchedParts.forEach(part => {
        createSuggestionItem('map-pin', part, 'Location', () => {
            state.filters.search = part;
            const searchInputEl = document.getElementById('search-input');
            if (searchInputEl) searchInputEl.value = part;
            const clearBtn = document.getElementById('clear-search-btn');
            if (clearBtn) clearBtn.classList.remove('hidden');
            elements.searchSuggestions.classList.add('hidden');
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
        iconHtml = `<img src="${imgUrl}" alt="Thumbnail" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover; margin-right: 8px;">`;
    }
    
    const filtersActive = hasAnyActiveFilter();
    
    div.innerHTML = `
        ${iconHtml}
        <span>${text}</span>
        <span class="type-badge">${type}</span>
        ${filtersActive ? `<button class="suggestion-append-btn" title="Add to active filters"><i data-lucide="plus"></i></button>` : ''}
    `;
    
    if (filtersActive) {
        // Main click area still replaces/sets the filter
        div.addEventListener('click', (e) => {
            if (e.target.closest('.suggestion-append-btn')) return;
            onClick();
        });
        // The + button appends without clearing existing filters
        const appendBtn = div.querySelector('.suggestion-append-btn');
        if (appendBtn) {
            appendBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                onClick();
            });
        }
    } else {
        div.addEventListener('click', onClick);
    }
    
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
