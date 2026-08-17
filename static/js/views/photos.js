function loadPhotos() {
    let url = `/api/photos?sort=${state.sortBy}`;
    
    if (state.currentView === 'archive') {
        url += '&archived=true';
    }
    if (state.currentView === 'favorites') {
        url += '&favorites=true';
    }
    
    if (state.filters.people.length > 0) url += `&people=${state.filters.people.join(',')}`;
    if (state.filters.places.length > 0) url += `&places=${encodeURIComponent(state.filters.places.join(','))}`;
    if (state.filters.albums.length > 0) url += `&albums=${state.filters.albums.join(',')}`;
    if (state.filters.types.length > 0) url += `&types=${state.filters.types.join(',')}`;
    if (state.filters.search) url += `&search=${encodeURIComponent(state.filters.search)}`;
    if (state.filters.date_query.length > 0) url += `&date_query=${encodeURIComponent(state.filters.date_query.join(','))}`;

    if (state.filters.year) url += `&year=${state.filters.year}`;
    if (state.filters.month) url += `&month=${state.filters.month}`;

    
    elements.photosGrid.innerHTML = `
        <div class="skeleton-grid">
            ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
        </div>
    `;
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (state.filters.customPaths) {
                const pathSet = new Set(state.filters.customPaths);
                data = data.filter(p => pathSet.has(p.path));
            }
            state.photos = data;
            state.lightboxPhotos = [...data];
            renderPhotosGrid(data);
        })
        .catch(err => {
            elements.photosGrid.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="alert-triangle"></i>
                    <p>Failed to load photos. Check connection.</p>
                </div>
            `;
            lucide.createIcons();
        });
}

// Justified Grid Layout Algorithm
function applyJustifiedLayout(gridEl, targetHeight = 180) {
    const containerWidth = gridEl.clientWidth;
    if (containerWidth === 0) return; // Hidden or not fully rendered
    
    const gap = 2; // Matches our CSS tight grid gap
    const cards = Array.from(gridEl.querySelectorAll('.photo-card'));
    if (cards.length === 0) return;
    
    let currentRow = [];
    let currentAspectRatioSum = 0;
    
    cards.forEach(card => {
        let ar = parseFloat(card.dataset.ar) || 1;
        if (ar > 3) ar = 3;
        if (ar < 0.3) ar = 0.3;
        
        currentRow.push({ card, ar });
        currentAspectRatioSum += ar;
        
        const estimatedWidth = (targetHeight * currentAspectRatioSum) + (gap * (currentRow.length - 1));
        
        if (estimatedWidth >= containerWidth) {
            const exactHeight = (containerWidth - gap * (currentRow.length - 1)) / currentAspectRatioSum;
            
            currentRow.forEach(item => {
                item.card.style.width = (exactHeight * item.ar) + 'px';
                item.card.style.height = exactHeight + 'px';
                item.card.style.flexGrow = '0';
                item.card.style.flexBasis = 'auto';
            });
            
            currentRow = [];
            currentAspectRatioSum = 0;
        }
    });
    
    // Last row (don't stretch to full width, keep target height)
    if (currentRow.length > 0) {
        currentRow.forEach(item => {
            item.card.style.width = (targetHeight * item.ar) + 'px';
            item.card.style.height = targetHeight + 'px';
            item.card.style.flexGrow = '0';
            item.card.style.flexBasis = 'auto';
        });
    }
}

// Resize Observer for responsive grid
let gridResizeObserver = null;
function setupGridResizeObserver() {
    if (gridResizeObserver) {
        gridResizeObserver.disconnect();
    }
    gridResizeObserver = new ResizeObserver(entries => {
        if (document.body.classList.contains('square-grid-mode')) return;
        
        // Use requestAnimationFrame to avoid ResizeObserver loop limit errors
        requestAnimationFrame(() => {
            const targetHeight = parseInt(localStorage.getItem('grid-thumbnail-size')) || 180;
            const grids = document.querySelectorAll('.photos-grid');
            grids.forEach(grid => {
                if (grid.offsetParent !== null) { // is visible
                    applyJustifiedLayout(grid, targetHeight);
                }
            });
        });
    });
    
    const root = document.getElementById('photos-grid-root');
    if (root) gridResizeObserver.observe(root);
}

// Format date into human readable group headers
function formatGroupDate(dateStr) {
    if (!dateStr || dateStr === 'Undated') return 'Undated';
    try {
        const parts = dateStr.split('-');
        const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        if (dateObj.toDateString() === today.toDateString()) {
            return "Today";
        } else if (dateObj.toDateString() === yesterday.toDateString()) {
            return "Yesterday";
        } else {
            const options = { weekday: 'short', month: 'short', day: 'numeric' };
            if (dateObj.getFullYear() !== today.getFullYear()) {
                options.year = 'numeric';
            }
            return dateObj.toLocaleDateString('en-US', options);
        }
    } catch(e) {
        return dateStr;
    }
}

// Render Photos Grouped by Date (Google Photos Style)
function renderPhotosGrid(photos, targetContainer = elements.photosGrid) {
    if (!photos || photos.length === 0) {
        targetContainer.innerHTML = `
            <div class="empty-state">
                <i data-lucide="image-off"></i>
                <p>No photos found matching the criteria.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    targetContainer.innerHTML = '';
    
    // Group photos by Date and collect locations
    const groups = {};
    const groupLocations = {};
    photos.forEach(photo => {
        let dateKey = 'Undated';
        if (photo.date_taken) {
            dateKey = photo.date_taken.split(' ')[0]; // Extract YYYY-MM-DD
        }
        if (!groups[dateKey]) {
            groups[dateKey] = [];
            groupLocations[dateKey] = new Set();
        }
        groups[dateKey].push(photo);
        if (photo.place_name) {
            groupLocations[dateKey].add(photo.place_name);
        }
    });
    
    // Sort keys based on sort setting (descending dates normally)
    const keys = Object.keys(groups);
    if (state.sortBy.includes('desc')) {
        keys.sort((a, b) => b.localeCompare(a));
    } else {
        keys.sort((a, b) => a.localeCompare(b));
    }
    
    keys.forEach(dateKey => {
        const datePhotos = groups[dateKey];
        const locations = Array.from(groupLocations[dateKey]);
        
        // Group Container
        const groupDiv = document.createElement('div');
        groupDiv.className = 'date-group';
        groupDiv.dataset.year = dateKey.split('-')[0];
        const monthPart = dateKey.split('-')[1];
        if (monthPart) groupDiv.dataset.month = monthPart;
        
        // Group Header
        const header = document.createElement('div');
        header.className = 'date-group-header slim-header';
        
        let locHtml = '';
        if (locations.length > 0) {
            let locText = locations[0];
            if (locations.length > 1) {
                locText += ` & ${locations.length - 1} more`;
            }
            let dropdownItems = locations.map(loc => `<li>${loc}</li>`).join('');
            locHtml = `
                <div class="location-dropdown-wrapper">
                    <span class="location-text">${locText} <i data-lucide="chevron-down" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;"></i></span>
                    <ul class="location-dropdown">
                        ${dropdownItems}
                    </ul>
                </div>
            `;
        }

        header.innerHTML = `
            <div class="date-header-left">
                <div class="date-select-btn" title="Select all photos on this date"><i data-lucide="check-circle" style="width: 20px; height: 20px;"></i></div>
                <span class="date-text">${formatGroupDate(dateKey)}</span>
            </div>
            <div class="date-header-right">
                ${locHtml}
            </div>
        `;
        
        // Select All handler
        const selectBtn = header.querySelector('.date-select-btn');
        selectBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const allSelected = datePhotos.every(p => state.selectedPhotos.has(p.path));
            datePhotos.forEach(p => {
                if (allSelected) {
                    state.selectedPhotos.delete(p.path);
                } else {
                    state.selectedPhotos.add(p.path);
                }
            });
            renderPhotosGrid(state.photos); // Re-render to update checkboxes
            if (typeof updateSelectionBar === 'function') updateSelectionBar();
        });

        groupDiv.appendChild(header);
        
        // Sub Grid
        const grid = document.createElement('div');
        grid.className = 'photos-grid';
        
        datePhotos.forEach(photo => {
            const card = document.createElement('div');
            card.className = `photo-card ${state.selectedPhotos.has(photo.path) ? 'selected' : ''}`;
            card.dataset.path = photo.path;
            
            const aspectRatio = (photo.width && photo.height) ? (photo.width / photo.height).toFixed(3) : 1;
            card.dataset.ar = aspectRatio;
            card.style.flexGrow = '0'; // Let JS handle it or fallback to CSS grid
            
            // Drag and Drop support
            card.draggable = true;
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', photo.path);
                e.dataTransfer.effectAllowed = 'copy';
            });
            
            // Thumbnail image source URL
            const encodedPath = encodeURIComponent(photo.path);
            const ext = photo.path.split('.').pop().toLowerCase();
            const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
            
            card.innerHTML = `
                <img src="/api/photo/thumbnail/${encodedPath}" alt="${photo.filename}" loading="lazy">
                
                <!-- Video indicator badge -->
                ${isVideo ? '<div class="video-badge"><i data-lucide="play"></i></div>' : ''}
                
                <!-- Checkbox Overlay for multi-select -->
                <div class="photo-card-select-overlay">
                    <div class="select-checkbox">
                        <i data-lucide="check"></i>
                    </div>
                </div>
                
                <!-- Badges showing location or faces present -->
                <div class="photo-card-badges">
                    ${photo.place_name ? '<div class="card-badge"><i data-lucide="map-pin"></i></div>' : ''}
                </div>
            `;
            
            // Click checks: if select-overlay clicked, toggle selection. Otherwise open lightbox.
            card.addEventListener('click', (e) => {
                const selectBtn = card.querySelector('.photo-card-select-overlay');
                if (selectBtn && (selectBtn.contains(e.target) || e.ctrlKey || e.shiftKey)) {
                    e.stopPropagation();
                    togglePhotoSelection(photo.path, card, e);
                } else {
                    openLightbox(photo.path);
                }
            });
            
            grid.appendChild(card);
        });
        
        groupDiv.appendChild(grid);
        // Append group to grid
        targetContainer.appendChild(groupDiv);
    });
    
    lucide.createIcons();
    
    // Apply Justified Layout if not in Square Mode
    if (!document.body.classList.contains('square-grid-mode')) {
        const targetHeight = parseInt(localStorage.getItem('grid-thumbnail-size')) || 180;
        const grids = targetContainer.querySelectorAll('.photos-grid');
        grids.forEach(grid => {
            applyJustifiedLayout(grid, targetHeight);
        });
        setupGridResizeObserver();
    }
    
    // Generate timeline dynamically
    if (typeof generateTimelineItems === 'function') {
        generateTimelineItems();
    }
}

// Multiselect Selection Handlers
let lastSelectedPhotoPath = null;

function togglePhotoSelection(path, cardEl, event) {
    if (event && event.shiftKey && lastSelectedPhotoPath) {
        const allCards = Array.from(document.querySelectorAll('.photo-card'));
        const currentIndex = allCards.findIndex(c => c.dataset.path === path);
        const lastIndex = allCards.findIndex(c => c.dataset.path === lastSelectedPhotoPath);
        
        if (currentIndex !== -1 && lastIndex !== -1) {
            const start = Math.min(currentIndex, lastIndex);
            const end = Math.max(currentIndex, lastIndex);
            
            // For a shift-click range, we usually select all in range
            for (let i = start; i <= end; i++) {
                const cPath = allCards[i].dataset.path;
                state.selectedPhotos.add(cPath);
                allCards[i].classList.add('selected');
            }
            updateMultiselectBar();
            lastSelectedPhotoPath = path;
            
            // clear text selection if user accidentally selected text while shift-clicking
            window.getSelection().removeAllRanges();
            return;
        }
    }

    if (state.selectedPhotos.has(path)) {
        state.selectedPhotos.delete(path);
        cardEl.classList.remove('selected');
    } else {
        state.selectedPhotos.add(path);
        cardEl.classList.add('selected');
    }
    lastSelectedPhotoPath = path;
    
    updateMultiselectBar();
}

function updateMultiselectBar() {
    const count = state.selectedPhotos.size;
    if (count > 0) {
        elements.selectCount.innerText = `${count} selected`;
        elements.multiselectBar.classList.remove('hidden');
    } else {
        elements.multiselectBar.classList.add('hidden');
    }
}

function clearSelection() {
    state.selectedPhotos.clear();
    // Update all photo card rendering
    document.querySelectorAll('.photo-card.selected').forEach(card => {
        card.classList.remove('selected');
    });
    updateMultiselectBar();
}

// Load Albums
