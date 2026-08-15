
// --- Session Cache Wrapper ---
const originalFetch = window.fetch;
window.fetch = async (...args) => {
    const request = new Request(...args);
    
    // Only cache GET requests that fetch JSON
    if (request.method !== 'GET' || !request.url.includes('/api/') || request.url.includes('/api/photo/file') || request.url.includes('/api/photo/thumbnail')) {
        // Clear cache on mutations (POST/PUT/DELETE)
        if (['POST', 'PUT', 'DELETE'].includes(request.method)) {
            sessionStorage.clear();
        }
        return originalFetch(...args);
    }

    const cacheKey = 'imgfinder_' + request.url;
    const cachedResponse = sessionStorage.getItem(cacheKey);
    
    if (cachedResponse) {
        try {
            const data = JSON.parse(cachedResponse);
            return new Response(JSON.stringify(data), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (e) {
            sessionStorage.removeItem(cacheKey);
        }
    }

    const response = await originalFetch(...args);
    if (response.ok && response.headers.get('content-type')?.includes('application/json')) {
        const clone = response.clone();
        try {
            const text = await clone.text();
            sessionStorage.setItem(cacheKey, text);
        } catch (e) {
            console.warn("Session cache full or error", e);
            sessionStorage.clear();
        }
    }
    return response;
};
// ------------------------------

// Application State
const state = {
    currentView: 'photos',
    photos: [],
    albums: [],
    people: [],
    places: [],
    placesMapData: [],
    placesMapInstance: null,
    filters: {
        people: [],
        places: [],
        albums: [],
        types: [],
        year: '',
        month: '',
        search: '',
        date_query: [],
        customPaths: null
    },
    sortBy: 'date_desc',
    selectedPhotos: new Set(),
    lightboxIndex: -1,
    lightboxPhotos: [], // Current list of photos shown in lightbox sequence
    map: null,
    mapMarker: null,
    scanFolder: '',
    scanStatus: 'idle',
    isLightboxInfoOpen: true,
    isDrawingMode: false,
    isDrawing: false,
    drawStart: { x: 0, y: 0 },
    drawBox: { x: 0, y: 0, w: 0, h: 0 },
    zoomScale: 1,
    panOffset: { x: 0, y: 0 },
    isPanning: false,
    panStart: { x: 0, y: 0 }
};

// DOM Elements
const elements = {
    lowGraphicsToggle: document.getElementById('low-graphics-mode'),
    navItems: document.querySelectorAll('.nav-item'),
    viewSections: document.querySelectorAll('.view-section'),
    viewPanel: document.querySelector('.view-panel'),
    scrollDateBadge: document.getElementById('scroll-date-badge'),
    photosGrid: document.getElementById('photos-grid-root'),
    albumsGrid: document.getElementById('albums-grid-root'),
    albumsListContainer: document.getElementById('albums-list-container'),
    albumDetailContainer: document.getElementById('album-detail-container'),
    albumDetailGrid: document.getElementById('album-detail-grid'),
    albumDetailTitle: document.getElementById('album-detail-title'),
    albumBackBtn: document.getElementById('album-back-btn'),
    peopleGrid: document.getElementById('people-grid-root'),
    unnamedPeopleGrid: document.getElementById('unnamed-people-grid-root'),
    peopleListContainer: document.getElementById('people-list-container'),
    personDetailContainer: document.getElementById('person-detail-container'),
    personDetailGrid: document.getElementById('person-detail-grid'),
    personDetailTitle: document.getElementById('person-detail-title'),
    personBackBtn: document.getElementById('person-back-btn'),
    placesGrid: document.getElementById('places-grid-root'),
    duplicatesGrid: document.getElementById('duplicates-root'),
    resolveDuplicatesBtn: document.getElementById('resolve-duplicates-btn'),
    searchInput: document.getElementById('search-input'),
    clearSearchBtn: document.getElementById('clear-search-btn'),
    searchSuggestions: document.getElementById('search-suggestions'),
    sortSelect: document.getElementById('sort-select'),

    scanPill: document.getElementById('scan-pill'),
    scanText: document.getElementById('scan-text'),
    filtersPanel: document.getElementById('filters-panel'),
    activeFiltersList: document.getElementById('active-filters-list'),
    clearFiltersBtn: document.getElementById('clear-filters-btn'),
    
    // Multiselect
    multiselectBar: document.getElementById('multiselect-bar'),
    selectCount: document.getElementById('select-count'),
    multiAlbumBtn: document.getElementById('multi-album-btn'),
    multiDeselectBtn: document.getElementById('multi-deselect-btn'),
    
    // Lightbox
    lightbox: document.getElementById('lightbox-modal'),
    lightboxImg: document.getElementById('lightbox-img'),
    lightboxVideo: document.getElementById('lightbox-video'),
    lightboxBgBlur: document.getElementById('lightbox-bg-blur'),
    lightboxClose: document.getElementById('lightbox-close-btn'),
    lightboxPrev: document.getElementById('lightbox-prev-btn'),
    lightboxNext: document.getElementById('lightbox-next-btn'),
    lightboxInfoToggle: document.getElementById('lightbox-info-toggle'),
    lightboxSidebar: document.getElementById('lightbox-sidebar'),
    closeInfoPanelBtn: document.getElementById('close-info-panel-btn'),
    photoTitle: document.getElementById('photo-title'),
    photoPath: document.getElementById('photo-path'),
    photoDate: document.getElementById('photo-date'),
    photoSize: document.getElementById('photo-size'),
    photoResolution: document.getElementById('photo-resolution'),
    photoFormat: document.getElementById('photo-format'),
    lightboxFacesList: document.getElementById('lightbox-faces-list'),
    photoLocation: document.getElementById('photo-location'),
    lightboxAlbumsList: document.getElementById('lightbox-albums-list'),
    lightboxAlbumSelect: document.getElementById('lightbox-album-select'),
    duplicateTypeSelect: document.getElementById('duplicate-type-select'),
    
    // Settings
    scanFolderInput: document.getElementById('scan-folder-input'),
    startScanBtn: document.getElementById('start-scan-btn'),
    scanErrorMsg: document.getElementById('scan-error-msg'),
    scanProgressBox: document.getElementById('scan-progress-box'),
    progressFile: document.getElementById('progress-file'),
    progressPercent: document.getElementById('progress-percent'),
    progressBarFill: document.getElementById('progress-bar-fill'),
    themeToggle: document.getElementById('theme-toggle'),
    
    // Modals
    createAlbumModal: document.getElementById('create-album-modal'),
    newAlbumNameInput: document.getElementById('new-album-name-input'),
    confirmCreateAlbumBtn: document.getElementById('confirm-create-album-btn'),
    cancelCreateAlbumBtn: document.getElementById('cancel-create-album-btn'),
    createAlbumError: document.getElementById('create-album-error'),
    
    addToAlbumModal: document.getElementById('add-to-album-modal'),
    addToAlbumList: document.getElementById('add-to-album-list'),
    addToNewAlbumInput: document.getElementById('add-to-new-album-input'),
    addToAlbumError: document.getElementById('add-to-album-error'),
    confirmAddAlbumBtn: document.getElementById('confirm-add-album-btn'),
    cancelAddAlbumBtn: document.getElementById('cancel-add-album-btn'),
    
    // Trash
    trashGridRoot: document.getElementById('trash-grid-root'),
    restoreAllTrashBtn: document.getElementById('restore-all-trash-btn'),
    trashSortSelect: document.getElementById('trash-sort-select'),
    multiTrashBtn: document.getElementById('multi-trash-btn'),
    multiCopyBtn: document.getElementById('multi-copy-btn'),
    multiArchiveBtn: document.getElementById('multi-archive-btn'),
    lightboxTrashBtn: document.getElementById('lightbox-trash-btn'),
    lightboxCopyBtn: document.getElementById('lightbox-copy-btn'),
    lightboxArchiveBtn: document.getElementById('lightbox-archive-btn'),
    
    // Zoom & Fit configurations
    gridZoomSlider: document.getElementById('grid-zoom-slider'),
    thumbnailFitRatio: document.getElementById('thumbnail-fit-ratio'),
    thumbnailTightGrid: document.getElementById('thumbnail-tight-grid'),
    settingsZoomSlider: document.getElementById('settings-zoom-slider'),
    
    // Rescan & Editing & Manual Faces
    rescanFacesBtn: document.getElementById('rescan-faces-btn'),
    editDateBtn: document.getElementById('edit-date-btn'),
    dateEditorContainer: document.getElementById('date-editor-container'),
    get editDateInput() { return document.getElementById('edit-date-raw') || document.getElementById('edit-date-input'); },
    editDateYear: document.getElementById('edit-date-year'),
    editDateMonth: document.getElementById('edit-date-month'),
    editDateDay: document.getElementById('edit-date-day'),
    editDateHour: document.getElementById('edit-date-hour'),
    editDateMinute: document.getElementById('edit-date-minute'),
    cancelDateBtn: document.getElementById('cancel-date-btn'),
    saveDateBtn: document.getElementById('save-date-btn'),
    dateMismatchAlert: document.getElementById('date-mismatch-alert'),
    mismatchDetectedDate: document.getElementById('mismatch-detected-date'),
    fixDateMismatchBtn: document.getElementById('fix-date-mismatch-btn'),
    editLocationBtn: document.getElementById('edit-location-btn'),
    locationEditorContainer: document.getElementById('location-editor-container'),
    editLocationInput: document.getElementById('edit-location-input'),
    saveLocationBtn: document.getElementById('save-location-btn'),
    addFaceManualBtn: document.getElementById('add-face-manual-btn'),
    manualFaceInstructions: document.getElementById('manual-face-instructions'),
    lightboxMediaContainer: document.getElementById('lightbox-media-container'),
    lightboxDrawingOverlay: document.getElementById('lightbox-drawing-overlay'),
    manualFaceModal: document.getElementById('manual-face-modal'),
    manualFaceNameInput: document.getElementById('manual-face-name-input'),
    manualFaceSelectExisting: document.getElementById('manual-face-select-existing'),
    confirmManualFaceBtn: document.getElementById('confirm-manual-face-btn'),
    cancelManualFaceBtn: document.getElementById('cancel-manual-face-btn'),
    manualFaceError: document.getElementById('manual-face-error'),
    zoomInBtn: document.getElementById('zoom-in-btn'),
    zoomOutBtn: document.getElementById('zoom-out-btn'),
    zoomResetBtn: document.getElementById('zoom-reset-btn'),
    lightboxZoomControls: document.getElementById('lightbox-zoom-controls'),
    openSystemBtn: document.getElementById('open-system-btn'),
    openFolderBtn: document.getElementById('open-folder-btn')
};

// Search Container reference for clicks
const searchContainer = document.querySelector('.search-container');

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
});

function initApp() {
    const isLowGfx = localStorage.getItem('lowGraphicsMode') === 'true';
    if (elements.lowGraphicsToggle) elements.lowGraphicsToggle.checked = isLowGfx;
    if (isLowGfx) document.body.classList.add('low-graphics');

    // Lucide Icons Initialization
    lucide.createIcons();
    
    if (typeof initSettingsView === 'function') initSettingsView();
    
    // Theme setup
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        elements.themeToggle.innerHTML = '<i data-lucide="moon"></i> Dark Theme';
        lucide.createIcons();
    }
    
    // Load metadata references
    loadStaticData();
    
    // Restore saved grid zoom and aspect ratio preferences
    const storedSize = localStorage.getItem('grid-thumbnail-size');
    if (storedSize) {
        document.documentElement.style.setProperty('--thumbnail-size', `${storedSize}px`);
        if (elements.gridZoomSlider) {
            elements.gridZoomSlider.value = storedSize;
        }
        if (elements.settingsZoomSlider) {
            elements.settingsZoomSlider.value = storedSize;
        }
    }
    
    const storedFit = localStorage.getItem('grid-thumbnail-fit');
    if (storedFit === 'true' && elements.photosGrid) {
        elements.photosGrid.classList.add('fit-ratio');
        if (elements.thumbnailFitRatio) {
            elements.thumbnailFitRatio.checked = true;
        }
    }

    const storedTight = localStorage.getItem('grid-thumbnail-tight');
    if (storedTight === 'true' && elements.photosGrid) {
        elements.photosGrid.classList.add('tight-grid');
        if (elements.thumbnailTightGrid) {
            elements.thumbnailTightGrid.checked = true;
        }
    }
    
    
    // Load settings
    fetchSettings();
    
    // Start polling scan status
    pollScanStatus();
    setInterval(pollScanStatus, 1500);
    
    // Enforce default view to memories
    switchView('memories');
}

// Event Listeners
function setupEventListeners() {
    if (elements.lowGraphicsToggle) {
        elements.lowGraphicsToggle.addEventListener('change', (e) => {
            const isLowGfx = e.target.checked;
            localStorage.setItem('lowGraphicsMode', isLowGfx);
            if (isLowGfx) {
                document.body.classList.add('low-graphics');
            } else {
                document.body.classList.remove('low-graphics');
            }
        });
    }

    // Album Back Button
    if (elements.albumBackBtn) {
        elements.albumBackBtn.addEventListener('click', () => {
            elements.albumDetailContainer.classList.add('hidden');
            elements.albumsListContainer.classList.remove('hidden');
            elements.albumDetailGrid.innerHTML = '';
        });
    }

    // Person Back Button
    if (elements.personBackBtn) {
        elements.personBackBtn.addEventListener('click', () => {
            elements.personDetailContainer.classList.add('hidden');
            elements.peopleListContainer.classList.remove('hidden');
            elements.personDetailGrid.innerHTML = '';
        });
    }

    // Sidebar navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Note: Filters are intentionally persisted across views (e.g. going to Places and back to Photos keeps the active filters)
            // If we are navigating to the exact same view we're already on, we might want to clear them, but standard behavior is to persist.
            
            const view = item.getAttribute('data-view');
            switchView(view);
        });
    });
    

    // Date Filters

    
    // Sort logic

    elements.sortSelect.addEventListener('change', () => {
        state.sortBy = elements.sortSelect.value;
        loadPhotos();
    });
    
    // Search Autocomplete
    elements.searchInput.addEventListener('input', handleSearchInput);
    elements.searchInput.addEventListener('focus', handleSearchInput);
    elements.searchInput.addEventListener('keydown', handleSearchKeydown);
    elements.clearSearchBtn.addEventListener('click', clearSearch);
    
    // Document click to close dropdowns and search suggestions
    document.addEventListener('click', (e) => {
        if (searchContainer && !searchContainer.contains(e.target)) {
            elements.searchSuggestions.classList.add('hidden');
        }
        
        // Close album dropdown menus
        if (!e.target.closest('.album-menu-container')) {
            document.querySelectorAll('.album-menu-container .dropdown-menu').forEach(m => {
                m.classList.add('hidden');
            });
        }
    });
    
    // Clear all filters
    elements.clearFiltersBtn.addEventListener('click', clearAllFilters);
    
    // Selection actions
    elements.multiDeselectBtn.addEventListener('click', clearSelection);
    elements.multiAlbumBtn.addEventListener('click', openAddToAlbumModal);
    
    // Settings Scan Folder
    elements.startScanBtn.addEventListener('click', startScan);
    elements.resolveDuplicatesBtn.addEventListener('click', resolveDuplicates);
    elements.duplicateTypeSelect.addEventListener('change', () => renderDuplicates(state.duplicateGroups));
    
    // Theme toggler
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    // Lightbox actions
    elements.lightboxClose.addEventListener('click', closeLightbox);
    elements.lightboxPrev.addEventListener('click', showPrevPhoto);
    elements.lightboxNext.addEventListener('click', showNextPhoto);
    elements.lightboxInfoToggle.addEventListener('click', toggleLightboxInfo);
    if (elements.closeInfoPanelBtn) elements.closeInfoPanelBtn.addEventListener('click', toggleLightboxInfo);
    elements.lightboxAlbumSelect.addEventListener('change', addPhotoToAlbumFromLightbox);
    elements.multiTrashBtn.addEventListener('click', trashSelectedPhotos);
    if (elements.multiCopyBtn) {
        elements.multiCopyBtn.addEventListener('click', copySelectedPhotoToClipboard);
    }
    if (elements.multiArchiveBtn) {
        elements.multiArchiveBtn.addEventListener('click', archiveSelectedPhotos);
    }
    if (elements.lightboxCopyBtn) {
        elements.lightboxCopyBtn.addEventListener('click', copyLightboxPhotoToClipboard);
    }
    if (elements.lightboxArchiveBtn) {
        elements.lightboxArchiveBtn.addEventListener('click', toggleLightboxPhotoArchive);
    }
    const lightboxFavoriteBtn = document.getElementById('lightbox-favorite-btn');
    if (lightboxFavoriteBtn) {
        lightboxFavoriteBtn.addEventListener('click', () => {
            const photo = state.lightboxPhotos[state.lightboxIndex];
            if (!photo) return;
            fetch('/api/photo/favorite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: photo.path })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) return;
                // Update in-memory state
                photo.is_favorite = data.is_favorite;
                const p = state.photos.find(x => x.path === photo.path);
                if (p) p.is_favorite = data.is_favorite;
                // Update button visual
                if (data.is_favorite) {
                    lightboxFavoriteBtn.classList.add('favorited');
                    lightboxFavoriteBtn.title = 'Remove from Favorites';
                } else {
                    lightboxFavoriteBtn.classList.remove('favorited');
                    lightboxFavoriteBtn.title = 'Add to Favorites';
                }
            })
            .catch(() => {});
        });
    }
    elements.lightboxTrashBtn.addEventListener('click', trashCurrentLightboxPhoto);
    elements.restoreAllTrashBtn.addEventListener('click', restoreAllRecycleBin);
    if (elements.trashSortSelect) {
        elements.trashSortSelect.addEventListener('change', () => {
            state.trashSortBy = elements.trashSortSelect.value;
            loadTrashPhotos();
        });
    }
    
    // Zoom and Ratio event listeners
    if (elements.gridZoomSlider) {
        elements.gridZoomSlider.addEventListener('input', () => {
            const size = elements.gridZoomSlider.value;
            document.documentElement.style.setProperty('--thumbnail-size', `${size}px`);
            localStorage.setItem('grid-thumbnail-size', size);
            if (elements.settingsZoomSlider) {
                elements.settingsZoomSlider.value = size;
            }
        });
    }
    if (elements.settingsZoomSlider) {
        elements.settingsZoomSlider.addEventListener('input', () => {
            const size = elements.settingsZoomSlider.value;
            document.documentElement.style.setProperty('--thumbnail-size', `${size}px`);
            localStorage.setItem('grid-thumbnail-size', size);
            if (elements.gridZoomSlider) {
                elements.gridZoomSlider.value = size;
            }
        });
    }
    if (elements.thumbnailFitRatio) {
        elements.thumbnailFitRatio.addEventListener('change', () => {
            const fit = elements.thumbnailFitRatio.checked;
            if (fit) {
                elements.photosGrid.classList.add('fit-ratio');
            } else {
                elements.photosGrid.classList.remove('fit-ratio');
            }
            localStorage.setItem('grid-thumbnail-fit', fit ? 'true' : 'false');
        });
    }

    if (elements.thumbnailTightGrid) {
        elements.thumbnailTightGrid.addEventListener('change', () => {
            const tight = elements.thumbnailTightGrid.checked;
            if (tight) {
                elements.photosGrid.classList.add('tight-grid');
            } else {
                elements.photosGrid.classList.remove('tight-grid');
            }
            localStorage.setItem('grid-thumbnail-tight', tight ? 'true' : 'false');
        });
    }
    
    // Keyboard navigation & Video Player controls for Lightbox
    document.addEventListener('keydown', (e) => {
        if (elements.lightbox.classList.contains('hidden')) return;
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;
        
        const video = elements.lightboxVideo;
        const wrapper = document.getElementById('custom-video-wrapper');
        const isVideoActive = wrapper && !wrapper.classList.contains('hidden');
        
        if (e.key === 'Escape') {
            closeLightbox();
        } else if (e.key === 'ArrowLeft') {
            if (isVideoActive) {
                video.currentTime = Math.max(0, video.currentTime - 5);
                e.preventDefault();
            } else {
                showPrevPhoto();
            }
        } else if (e.key === 'ArrowRight') {
            if (isVideoActive) {
                video.currentTime = Math.min(video.duration || 0, video.currentTime + 5);
                e.preventDefault();
            } else {
                showNextPhoto();
            }
        } else if (e.key === ' ' || e.key === 'Spacebar') {
            if (isVideoActive) {
                if (video.paused) video.play().catch(err => console.log(err));
                else video.pause();
                e.preventDefault();
            }
        } else if (e.key === 'ArrowUp') {
            if (isVideoActive) {
                video.volume = Math.min(1.0, video.volume + 0.1);
                video.muted = false;
                updateVolumeUI();
                e.preventDefault();
            }
        } else if (e.key === 'ArrowDown') {
            if (isVideoActive) {
                video.volume = Math.max(0.0, video.volume - 0.1);
                updateVolumeUI();
                e.preventDefault();
            }
        } else if (e.key.toLowerCase() === 'm') {
            if (isVideoActive) {
                video.muted = !video.muted;
                updateVolumeUI();
                e.preventDefault();
            }
        }
    });

    elements.lightboxVideo.addEventListener('dblclick', () => {
        const wrapper = document.getElementById('custom-video-wrapper');
        if (wrapper && wrapper.requestFullscreen) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                wrapper.requestFullscreen();
            }
        }
    });
    
    // Modal Album Creators
    document.getElementById('new-album-btn').addEventListener('click', openCreateAlbumModal);
    elements.cancelCreateAlbumBtn.addEventListener('click', closeCreateAlbumModal);
    elements.confirmCreateAlbumBtn.addEventListener('click', createAlbum);
    elements.newAlbumNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') createAlbum();
    });
    
    elements.cancelAddAlbumBtn.addEventListener('click', closeAddToAlbumModal);
    elements.confirmAddAlbumBtn.addEventListener('click', addSelectedToAlbum);
    
    // Rework Places Grouping
    const reworkBtn = document.getElementById('rework-grouping-btn');
    if (reworkBtn) {
        reworkBtn.addEventListener('click', () => {
            const thresh = prompt("Enter Minimum Photos Threshold for Smart Grouping:", "3");
            if (thresh === null) return;
            const t = parseInt(thresh);
            if (isNaN(t) || t < 1) {
                alert("Invalid threshold.");
                return;
            }
            const origHtml = reworkBtn.innerHTML;
            reworkBtn.innerHTML = '<i data-lucide="loader-2" class="spin" style="width:16px;height:16px;"></i> Processing...';
            lucide.createIcons();
            
            fetch('/api/places/rework_grouping', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({threshold: t})
            }).then(res => res.json()).then(data => {
                reworkBtn.innerHTML = origHtml;
                lucide.createIcons();
                if (data.success) {
                    alert("Grouping updated successfully!");
                    loadPlaces(); // Reload map and grid
                } else {
                    alert("Failed to update grouping: " + data.error);
                }
            }).catch(err => {
                reworkBtn.innerHTML = origHtml;
                lucide.createIcons();
                alert("Error reworking grouping.");
            });
        });
    }

    // Face Rescan Settings Trigger
    if (elements.rescanFacesBtn) {
        elements.rescanFacesBtn.addEventListener('click', triggerFaceRescan);
    }

    // Metadata Inline Editors
    if (elements.editDateBtn) {
        elements.editDateBtn.addEventListener('click', toggleDateEditor);
    }
    if (elements.saveDateBtn) {
        elements.saveDateBtn.addEventListener('click', savePhotoDate);
    }
    if (elements.fixDateMismatchBtn) {
        elements.fixDateMismatchBtn.addEventListener('click', fixPhotoDateFromFilename);
    }
    if (elements.editLocationBtn) {
        elements.editLocationBtn.addEventListener('click', toggleLocationEditor);
    }
    if (elements.saveLocationBtn) {
        elements.saveLocationBtn.addEventListener('click', savePhotoLocation);
    }
    
    // Manual Face Addition
    if (elements.addFaceManualBtn) {
        elements.addFaceManualBtn.addEventListener('click', toggleManualFaceDrawingMode);
    }
    
    // Drawing Mouse Events on the Lightbox Image Container
    const mediaContainer = elements.lightboxMediaContainer;
    if (mediaContainer) {
        mediaContainer.addEventListener('mousedown', handleDrawStart);
        mediaContainer.addEventListener('mousemove', handleDrawing);
        window.addEventListener('mouseup', handleDrawEnd);
    }
    
    if (elements.cancelManualFaceBtn) {
        elements.cancelManualFaceBtn.addEventListener('click', () => {
            elements.manualFaceModal.classList.add('hidden');
            resetDrawingState();
        });
    }
    if (elements.confirmManualFaceBtn) {
        elements.confirmManualFaceBtn.addEventListener('click', submitManualFaceLabel);
    }
    
    // Zoom control button listeners
    if (elements.zoomInBtn) {
        elements.zoomInBtn.addEventListener('click', () => {
            state.zoomScale = Math.min(5, state.zoomScale + 0.5);
            applyZoomTransform();
        });
    }
    if (elements.zoomOutBtn) {
        elements.zoomOutBtn.addEventListener('click', () => {
            state.zoomScale = Math.max(1, state.zoomScale - 0.5);
            if (state.zoomScale === 1) state.panOffset = { x: 0, y: 0 };
            applyZoomTransform();
        });
    }
    if (elements.zoomResetBtn) {
        elements.zoomResetBtn.addEventListener('click', resetZoom);
    }
    
    // Mouse wheel Zoom on image
    if (mediaContainer) {
        mediaContainer.addEventListener('wheel', (e) => {
            if (state.isDrawingMode) return;
            const img = elements.lightboxImg;
            if (img.classList.contains('hidden')) return;
            
            e.preventDefault();
            const intensity = 0.15;
            if (e.deltaY < 0) {
                state.zoomScale = Math.min(5, state.zoomScale + intensity);
            } else {
                state.zoomScale = Math.max(1, state.zoomScale - intensity);
            }
            
            if (state.zoomScale === 1) {
                state.panOffset = { x: 0, y: 0 };
            }
            applyZoomTransform();
        }, { passive: false });
    }
    
    // Double click image zoom toggle
    if (elements.lightboxImg) {
        elements.lightboxImg.addEventListener('dblclick', (e) => {
            if (state.isDrawingMode) return;
            e.stopPropagation();
            if (state.zoomScale > 1) {
                resetZoom();
            } else {
                state.zoomScale = 2.5;
                applyZoomTransform();
            }
        });
    }
    
    // Open in native system viewer / open folder
    if (elements.openSystemBtn) {
        elements.openSystemBtn.addEventListener('click', () => {
            const photo = state.lightboxPhotos[state.lightboxIndex];
            if (!photo) return;
            fetch('/api/photo/open-system', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ photo_path: photo.path })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) alert("Failed to open file: " + data.error);
            })
            .catch(err => alert("Error opening file: " + err.message));
        });
    }
    
    if (elements.openFolderBtn) {
        elements.openFolderBtn.addEventListener('click', () => {
            const photo = state.lightboxPhotos[state.lightboxIndex];
            if (!photo) return;
            fetch('/api/photo/open-folder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ photo_path: photo.path })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) alert("Failed to reveal folder: " + data.error);
            })
            .catch(err => alert("Error revealing folder: " + err.message));
        });
    }
    
    // Custom HTML5 Video Player Event Listeners
    const video = elements.lightboxVideo;
    const playBtn = document.getElementById('video-play-btn');
    const muteBtn = document.getElementById('video-mute-btn');
    const volumeSlider = document.getElementById('video-volume');
    const timeline = document.getElementById('video-timeline');
    const timeCur = document.getElementById('video-time-cur');
    const timeDur = document.getElementById('video-time-dur');
    const fullscreenBtn = document.getElementById('video-fullscreen-btn');
    
    if (playBtn && video) {
        const togglePlay = () => {
            if (video.paused) {
                video.play().catch(err => console.log("Play failed:", err));
            } else {
                video.pause();
            }
        };
        
        playBtn.addEventListener('click', togglePlay);
        video.addEventListener('click', togglePlay);
        
        video.addEventListener('play', () => {
            playBtn.innerHTML = '<i data-lucide="pause" style="width:18px; height:18px;"></i>';
            lucide.createIcons();
        });
        
        video.addEventListener('pause', () => {
            playBtn.innerHTML = '<i data-lucide="play" style="width:18px; height:18px;"></i>';
            lucide.createIcons();
        });
        
        // Mute Toggle Button
        if (muteBtn) {
            muteBtn.addEventListener('click', () => {
                video.muted = !video.muted;
                updateVolumeUI();
            });
        }
        
        // Seek / Timeline updates
        if (timeline && timeCur && timeDur) {
            video.addEventListener('timeupdate', () => {
                if (video.duration) {
                    const pct = (video.currentTime / video.duration) * 100;
                    timeline.value = pct;
                    timeline.style.background = `linear-gradient(to right, #3b82f6 ${pct}%, rgba(255, 255, 255, 0.3) ${pct}%)`;
                    timeCur.innerText = formatVideoTime(video.currentTime);
                }
            });
            
            video.addEventListener('durationchange', () => {
                timeDur.innerText = formatVideoTime(video.duration);
            });
            
            timeline.addEventListener('input', () => {
                if (video.duration) {
                    video.currentTime = (timeline.value / 100) * video.duration;
                    const pct = timeline.value;
                    timeline.style.background = `linear-gradient(to right, #3b82f6 ${pct}%, rgba(255, 255, 255, 0.3) ${pct}%)`;
                }
            });
        }
        
        // Fullscreen Btn Click
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => {
                const wrapper = document.getElementById('custom-video-wrapper');
                if (!document.fullscreenElement) {
                    wrapper.requestFullscreen().catch(err => console.log(err));
                } else {
                    document.exitFullscreen();
                }
            });
        }
    }
    
    // Floating scroll date indicator
    let scrollTimeout;
    if (elements.viewPanel && elements.scrollDateBadge) {
        elements.viewPanel.addEventListener('scroll', () => {
            if (state.currentView !== 'photos') {
                elements.scrollDateBadge.classList.remove('visible');
                return;
            }
            
            elements.scrollDateBadge.classList.remove('hidden');
            elements.scrollDateBadge.classList.add('visible');
            
            updateScrollingDateLabel();
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                elements.scrollDateBadge.classList.remove('visible');
            }, 1200);
        });
    }
}

// Router
function switchView(view) {
    state.currentView = view;
    
    // Update active navbar item
    elements.navItems.forEach(item => {
        if (item.getAttribute('data-view') === view) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Show correct section (reuse view-photos for archive and favorites tabs)
    const targetView = (view === 'archive' || view === 'favorites') ? 'photos' : view;
    elements.viewSections.forEach(section => {
        if (section.id === `view-${targetView}`) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
    
    // Toggle Zoom Widget Visibility
    const zoomContainer = document.getElementById('zoom-container');
    if (zoomContainer) {
        if (targetView === 'photos' || targetView === 'duplicates' || targetView === 'trash') {
            zoomContainer.style.display = 'flex';
        } else {
            zoomContainer.style.display = 'none';
        }
    }

    // Configure multi-select action button labels
    if (elements.multiArchiveBtn) {
        if (view === 'archive') {
            elements.multiArchiveBtn.innerHTML = '<i data-lucide="archive-restore"></i> Unarchive';
            elements.multiArchiveBtn.title = "Unarchive selected photos";
        } else {
            elements.multiArchiveBtn.innerHTML = '<i data-lucide="archive"></i> Archive';
            elements.multiArchiveBtn.title = "Archive selected photos";
        }
        lucide.createIcons();
    }
    
    // Hide sorting widget on non-photo sections
    const sortingContainer = document.getElementById('sorting-container');
    if (view === 'photos' || view === 'archive' || view === 'favorites') {
        sortingContainer.classList.remove('hidden');
    } else {
        sortingContainer.classList.add('hidden');
    }
    
    // Trigger loader based on view
    if (view === 'photos' || view === 'archive' || view === 'favorites') loadPhotos();
    else if (view === 'albums') loadAlbums();
    else if (view === 'people') loadPeople();
    else if (view === 'places') loadPlaces();
    else if (view === 'duplicates') loadDuplicates();
    else if (view === 'trash') loadTrashPhotos();
    else if (view === 'stats') loadStats();
    else if (view === 'memories') {
        if (window.memoriesInterval) clearInterval(window.memoriesInterval);
        if (typeof loadMemories === 'function') loadMemories();
    }
}

// Theme Switcher
function toggleTheme() {
    if (document.body.classList.contains('dark-theme')) {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        elements.themeToggle.innerHTML = '<i data-lucide="moon"></i> Dark Theme';
        localStorage.setItem('theme', 'light');
    } else {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
        elements.themeToggle.innerHTML = '<i data-lucide="sun"></i> Light Theme';
        localStorage.setItem('theme', 'dark');
    }
    lucide.createIcons();
}

// Load Static Lists for Autocomplete Search
function loadStaticData() {
    fetch('/api/people').then(res => res.json()).then(data => state.people = data);
    fetch('/api/places').then(res => res.json()).then(data => state.places = data);
    fetch('/api/albums').then(res => res.json()).then(data => {
        state.albums = data;
        populateAlbumDropdowns();
    });
}

function populateAlbumDropdowns() {
    // Populate lightbox album selector dropdown
    elements.lightboxAlbumSelect.innerHTML = '<option value="">+ Add to Album...</option>';
    
    const sidebarAlbumsList = document.getElementById('sidebar-albums-list');
    if (sidebarAlbumsList) {
        sidebarAlbumsList.innerHTML = '';
    }
    
    state.albums.forEach(album => {
        // Dropdown option
        const option = document.createElement('option');
        option.value = album.id;
        option.textContent = album.name;
        elements.lightboxAlbumSelect.appendChild(option);
        
        // Sidebar list item (Drop target)
        if (sidebarAlbumsList) {
            const a = document.createElement('a');
            a.className = 'sidebar-sublist-item';
            a.textContent = album.name;
            a.dataset.albumId = album.id;
            
            a.addEventListener('click', (e) => {
                e.preventDefault();
                // If they click on it, navigate to the album
                state.filters.albums = [album.id];
                applyFilters();
            });
            
            // Drag and drop event listeners
            a.addEventListener('dragover', (e) => {
                e.preventDefault(); // Necessary to allow dropping
                a.classList.add('drag-over');
            });
            a.addEventListener('dragleave', () => {
                a.classList.remove('drag-over');
            });
            a.addEventListener('drop', (e) => {
                e.preventDefault();
                a.classList.remove('drag-over');
                const photoPath = e.dataTransfer.getData('text/plain');
                if (photoPath) {
                    fetch('/api/albums/add', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ album_id: album.id, photos: [photoPath] })
                    }).then(res => res.json()).then(data => {
                        if (data.success) {
                            alert(`Added to ${album.name}`);
                        }
                    });
                }
            });
            sidebarAlbumsList.appendChild(a);
        }
    });
}

// Poll Scan Status
function pollScanStatus() {
    fetch('/api/scan/status')
        .then(res => res.json())
        .then(data => {
            const wasScanning = (state.scanStatus === 'scanning');
            state.scanStatus = data.status;
            
            if (data.status === 'scanning') {
                elements.scanPill.className = 'scan-pill scanning';
                elements.scanText.innerText = `Scanning: ${data.processed}/${data.total}`;
                
                // Update progress box in Settings
                elements.scanProgressBox.classList.remove('hidden');
                elements.progressFile.innerText = (data.phase ? `${data.phase}: ` : "") + data.current_file;
                
                const pct = data.total > 0 ? Math.round((data.processed / data.total) * 100) : 0;
                elements.progressPercent.innerText = `${data.processed}/${data.total} (${pct}%)`;
                elements.progressBarFill.style.width = `${pct}%`;
                
                elements.startScanBtn.disabled = true;
                elements.startScanBtn.innerText = 'Scanning...';
                if (elements.rescanFacesBtn) {
                    elements.rescanFacesBtn.disabled = true;
                    elements.rescanFacesBtn.innerText = 'Scanning...';
                }
            } else {
                elements.scanPill.className = 'scan-pill idle';
                elements.scanText.innerText = 'Gallery Idle';
                
                elements.scanProgressBox.classList.add('hidden');
                elements.startScanBtn.disabled = false;
                elements.startScanBtn.innerText = 'Scan Directory';
                if (elements.rescanFacesBtn) {
                    elements.rescanFacesBtn.disabled = false;
                    elements.rescanFacesBtn.innerHTML = '<i data-lucide="scan" style="width:16px; height:16px;"></i> Rescan Faces';
                }
                
                // If scanning just finished, trigger a reload of the current view and references
                if (wasScanning) {
                    loadStaticData();
                    refreshCurrentView();
                    lucide.createIcons();
                }
            }
        });
}

function refreshCurrentView() {
    if (state.currentView === 'photos') loadPhotos();
    else if (state.currentView === 'albums') loadAlbums();
    else if (state.currentView === 'people') loadPeople();
    else if (state.currentView === 'places') loadPlaces();
}

// Fetch Settings
function fetchSettings() {
    fetch('/api/settings')
        .then(res => res.json())
        .then(data => {
            state.scanFolder = data.scan_folder || '';
            elements.scanFolderInput.value = data.scan_folder || '';
            
            // If scanning directory is not configured, redirect to settings
            if (!data.scan_folder) {
                switchView('settings');
            } else {
                loadPhotos();
            }
        });
}

// Trigger Scan
function startScan() {
    const folder = elements.scanFolderInput.value.trim();
    if (!folder) {
        showScanError("Please specify a directory path");
        return;
    }
    
    elements.scanErrorMsg.classList.add('hidden');
    elements.startScanBtn.disabled = true;
    
    fetch('/api/settings/scan-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        state.scanFolder = folder;
        showScanSuccess();
        pollScanStatus();
    })
    .catch(err => {
        showScanError(err.message || "Failed to start directory scan");
        elements.startScanBtn.disabled = false;
    });
}

function showScanError(msg) {
    elements.scanErrorMsg.innerText = msg;
    elements.scanErrorMsg.classList.remove('hidden');
}

function showScanSuccess() {
    elements.scanErrorMsg.className = 'error-text hidden';
}

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

// Lightbox Modal Logic
let timelineHideTimeout = null;

function updateScrollingDateLabel() {
    const viewPanel = elements.viewPanel;
    if (!viewPanel || !elements.scrollDateBadge) return;
    if (typeof state !== 'undefined' && state.currentView === 'memories') {
        const container = document.getElementById('timeline-scrollbar-container');
        if (container) container.classList.remove('visible');
        return;
    }
    
    const dateGroups = document.querySelectorAll('.date-group');
    if (dateGroups.length === 0) return;
    
    const panelRect = viewPanel.getBoundingClientRect();
    
    let visibleDate = '';
    for (let i = 0; i < dateGroups.length; i++) {
        const group = dateGroups[i];
        const rect = group.getBoundingClientRect();
        
        if (rect.bottom > panelRect.top + 60) {
            const header = group.querySelector('.date-group-header');
            if (header) {
                const dateStr = header.innerText;
                const parts = dateStr.split(',');
                if (parts.length > 2) {
                    const year = parts[2].trim();
                    const currentYear = new Date().getFullYear().toString();
                    if (year !== currentYear) {
                        visibleDate = `${parts[1].trim()} ${year}`;
                    } else {
                        visibleDate = parts[1].trim();
                    }
                } else if (parts.length > 1) {
                    visibleDate = parts[1].trim();
                } else {
                    visibleDate = dateStr;
                }
            }
            break;
        }
    }
    
    if (visibleDate) {
        elements.scrollDateBadge.innerText = visibleDate;
        
        // Update timeline active badge
        const activeLabel = document.getElementById('timeline-active-label');
        if (activeLabel) {
            activeLabel.innerText = visibleDate;
        }
    }
    
    // Update timeline position
    const timelineBadge = document.getElementById('timeline-active-badge');
    const container = document.getElementById('timeline-scrollbar-container');
    if (timelineBadge && container && viewPanel.scrollHeight > viewPanel.clientHeight) {
        const pct = viewPanel.scrollTop / (viewPanel.scrollHeight - viewPanel.clientHeight);
        const maxTop = container.clientHeight;
        timelineBadge.style.top = `${pct * maxTop}px`;
        
        // Fade in
        container.classList.add('visible');
        
        // Fade out after scrolling stops
        clearTimeout(timelineHideTimeout);
        timelineHideTimeout = setTimeout(() => {
            // Check if user is currently interacting with the timeline
            if (typeof isDraggingTimeline === 'undefined' || !isDraggingTimeline) {
                container.classList.remove('visible');
            }
        }, 1500);
    }
}

function renderLightboxPhoto() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    // Track current photo for editing/scanning operations
    state.currentLightboxPhoto = photo.path;
    
    // Reset metadata editors, drawing state, and zoom Scale
    if (elements.dateEditorContainer) elements.dateEditorContainer.classList.add('hidden');
    if (elements.locationEditorContainer) elements.locationEditorContainer.classList.add('hidden');
    if (elements.dateMismatchAlert) elements.dateMismatchAlert.classList.add('hidden');
    resetDrawingState();
    resetZoom();
    
    // Setup carousel navigation arrows
    elements.lightboxPrev.style.display = (state.lightboxIndex === 0) ? 'none' : 'flex';
    elements.lightboxNext.style.display = (state.lightboxIndex === state.lightboxPhotos.length - 1) ? 'none' : 'flex';
    
    // Blurred background backing
    elements.lightboxBgBlur.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent(photo.path)}")`;
    
    // Check if video file
    const ext = photo.path.split('.').pop().toLowerCase();
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    
    if (isVideo) {
        elements.lightboxImg.classList.add('hidden');
        const wrapper = document.getElementById('custom-video-wrapper');
        if (wrapper) wrapper.classList.remove('hidden');
        
        elements.lightboxVideo.src = `/api/photo/file/${encodeURIComponent(photo.path)}`;
        elements.lightboxVideo.load();
        elements.lightboxVideo.muted = false;
        elements.lightboxVideo.volume = 1.0;
        
        // Fix vertical video: once dimensions are known, constrain the wrapper correctly
        elements.lightboxVideo.onloadedmetadata = function() {
            const vw = elements.lightboxVideo.videoWidth;
            const vh = elements.lightboxVideo.videoHeight;
            if (!vw || !vh) return;
            
            const container = document.getElementById('lightbox-media-container');
            if (!container) return;
            
            const cw = container.clientWidth;
            const ch = container.clientHeight;
            const videoAspect = vw / vh;
            const containerAspect = cw / ch;
            
            let displayW, displayH;
            if (videoAspect < containerAspect) {
                // Video is taller relative to container → constrain by height
                displayH = Math.min(ch * 0.95, ch);
                displayW = displayH * videoAspect;
            } else {
                // Video is wider → constrain by width
                displayW = Math.min(cw * 0.95, cw);
                displayH = displayW / videoAspect;
            }
            
            if (wrapper) {
                wrapper.style.width = displayW + 'px';
                wrapper.style.height = displayH + 'px';
                wrapper.style.maxWidth = '100%';
                wrapper.style.maxHeight = '100%';
            }
            elements.lightboxVideo.style.width = '100%';
            elements.lightboxVideo.style.height = '100%';
            elements.lightboxVideo.style.maxWidth = '';
            elements.lightboxVideo.style.maxHeight = '';
        };
        
        elements.lightboxVideo.play().catch(err => {
            console.log("Autoplay unmuted blocked, trying muted:", err);
            elements.lightboxVideo.muted = true;
            elements.lightboxVideo.play().catch(e => console.log("Autoplay blocked:", e));
        });
        
        // Reset custom controls indicators
        const timeline = document.getElementById('video-timeline');
        const timeCur = document.getElementById('video-time-cur');
        const timeDur = document.getElementById('video-time-dur');
        if (timeline) timeline.value = 0;
        if (timeCur) timeCur.innerText = '0:00';
        if (timeDur) timeDur.innerText = '0:00';
        
        updateVolumeUI();
        
        if (elements.lightboxZoomControls) {
            elements.lightboxZoomControls.classList.add('hidden');
        }
    } else {
        const wrapper = document.getElementById('custom-video-wrapper');
        if (wrapper) {
            wrapper.classList.add('hidden');
            // Reset wrapper sizing for next video
            wrapper.style.width = '';
            wrapper.style.height = '';
        }
        elements.lightboxVideo.src = '';
        elements.lightboxVideo.onloadedmetadata = null;
        elements.lightboxImg.classList.remove('hidden');
        elements.lightboxImg.src = `/api/photo/file/${encodeURIComponent(photo.path)}`;
        if (elements.lightboxZoomControls) {
            elements.lightboxZoomControls.classList.remove('hidden');
        }
    }
    
    // Side Panel Metadata
    if (elements.photoTitle) elements.photoTitle.innerText = photo.filename;
    const fi = document.getElementById('photo-filename-input');
    if (fi) fi.value = photo.filename;
    elements.photoPath.innerText = photo.path;
    
    // Format Date taken
    elements.photoDate.innerText = formatPhotoDate(photo.date_taken);
    
    // Format File Size & Resolution
    const mbSize = (photo.size / (1024 * 1024)).toFixed(2);
    elements.photoSize.innerText = `${mbSize} MB`;
    
    // Calculate megapixels
    let resText = `${photo.width} x ${photo.height}`;
    if (photo.width && photo.height) {
        const mp = (photo.width * photo.height / 1000000).toFixed(1);
        resText = `${mp}MP ${resText}`;
    }
    elements.photoResolution.innerText = resText;
    elements.photoFormat.innerText = photo.file_type;
    
    // Populate Camera Details if they exist
    const cameraSection = document.getElementById('camera-info-section');
    const cameraModel = document.getElementById('camera-model-text');
    const cameraSettings = document.getElementById('camera-settings-text');
    
    if (cameraSection && cameraModel && cameraSettings) {
        const hasCameraInfo = photo.camera_make || photo.camera_model || photo.f_stop || photo.exposure_time || photo.focal_length || photo.iso;
        
        if (hasCameraInfo) {
            cameraSection.classList.remove('hidden');
            let makeModel = [];
            if (photo.camera_make) makeModel.push(photo.camera_make);
            if (photo.camera_model) makeModel.push(photo.camera_model);
            cameraModel.innerText = makeModel.join(' ') || 'Unknown Camera';
            
            let settings = [];
            if (photo.f_stop) settings.push(`ƒ/${photo.f_stop}`);
            if (photo.exposure_time) settings.push(photo.exposure_time);
            if (photo.focal_length) settings.push(`${photo.focal_length}mm`);
            if (photo.iso) settings.push(`ISO${photo.iso}`);
            cameraSettings.innerText = settings.join('  ');
        } else {
            cameraSection.classList.add('hidden');
        }
    }
    
    // Render location map
    renderLightboxMap(photo);
    
    // Fetch and render faces in photo
    renderLightboxFaces(photo.path);
    
    // Render Album mappings for this photo
    renderLightboxAlbums(photo.path);
    
    // Set Archive button label
    if (elements.lightboxArchiveBtn) {
        if (photo.archived_at) {
            elements.lightboxArchiveBtn.innerHTML = '<i data-lucide="archive-restore" style="width:16px; height:16px;"></i> Unarchive Photo';
            elements.lightboxArchiveBtn.title = "Restore from archive to main timeline";
        } else {
            elements.lightboxArchiveBtn.innerHTML = '<i data-lucide="archive" style="width:16px; height:16px;"></i> Archive Photo';
            elements.lightboxArchiveBtn.title = "Hide this photo from main timeline";
        }
        lucide.createIcons();
    }
    
    // Update favorite heart button state
    const favBtn = document.getElementById('lightbox-favorite-btn');
    if (favBtn) {
        if (photo.is_favorite) {
            favBtn.classList.add('favorited');
            favBtn.title = 'Remove from Favorites';
        } else {
            favBtn.classList.remove('favorited');
            favBtn.title = 'Add to Favorites';
        }
    }

    
    // Background metadata refresh & autoscan from disk (debounced 0.7s)
    const activeIndexBeforeFetch = state.lightboxIndex;
    
    if (state.autoscanTimeout) clearTimeout(state.autoscanTimeout);
    
    state.autoscanTimeout = setTimeout(() => {
        fetch('/api/photo/refresh-metadata', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ photo_path: photo.path })
        })
        .then(res => {
            if (!res.ok) throw new Error("Metadata refresh failed");
            return res.json();
        })
        .then(data => {
            if (data.success && data.photo) {
                if (state.lightboxIndex === activeIndexBeforeFetch) {
                    state.lightboxPhotos[state.lightboxIndex] = data.photo;
                    const updated = data.photo;
                    
                    if (elements.photoTitle) elements.photoTitle.innerText = updated.filename;
    const fi = document.getElementById('photo-filename-input');
    if (fi) fi.value = updated.filename;
                    elements.photoPath.innerText = updated.path;
                    elements.photoDate.innerText = formatPhotoDate(updated.date_taken);
                    elements.photoSize.innerText = `${(updated.size / (1024 * 1024)).toFixed(2)} MB`;
                    
                    let resTextFetch = `${updated.width} x ${updated.height}`;
                    if (updated.width && updated.height) {
                        const mpFetch = (updated.width * updated.height / 1000000).toFixed(1);
                        resTextFetch = `${mpFetch}MP ${resTextFetch}`;
                    }
                    elements.photoResolution.innerText = resTextFetch;
                    elements.photoFormat.innerText = updated.file_type;
                    
                    // Populate Camera Details
                    const camSec = document.getElementById('camera-info-section');
                    if (camSec) {
                        const hasCam = updated.camera_make || updated.camera_model || updated.f_stop || updated.exposure_time || updated.focal_length || updated.iso;
                        if (hasCam) {
                            camSec.classList.remove('hidden');
                            let mm = [];
                            if (updated.camera_make) mm.push(updated.camera_make);
                            if (updated.camera_model) mm.push(updated.camera_model);
                            document.getElementById('camera-model-text').innerText = mm.join(' ') || 'Unknown Camera';
                            
                            let s = [];
                            if (updated.f_stop) s.push(`ƒ/${updated.f_stop}`);
                            if (updated.exposure_time) s.push(updated.exposure_time);
                            if (updated.focal_length) s.push(`${updated.focal_length}mm`);
                            if (updated.iso) s.push(`ISO${updated.iso}`);
                            document.getElementById('camera-settings-text').innerText = s.join('  ');
                        } else {
                            camSec.classList.add('hidden');
                        }
                    }
                    
                    renderLightboxMap(updated);
                    renderLightboxFaces(updated.path);
                    
                    // Update Archive button label on background sync
                    if (elements.lightboxArchiveBtn) {
                        if (updated.archived_at) {
                            elements.lightboxArchiveBtn.innerHTML = '<i data-lucide="archive-restore" style="width:16px; height:16px;"></i> Unarchive Photo';
                        } else {
                            elements.lightboxArchiveBtn.innerHTML = '<i data-lucide="archive" style="width:16px; height:16px;"></i> Archive Photo';
                        }
                        lucide.createIcons();
                    }
                    
                    if (elements.dateMismatchAlert && elements.mismatchDetectedDate) {
                        if (data.has_date_mismatch && data.filename_date) {
                            elements.mismatchDetectedDate.innerText = formatPhotoDate(data.filename_date);
                            elements.dateMismatchAlert.classList.remove('hidden');
                        } else {
                            elements.dateMismatchAlert.classList.add('hidden');
                        }
                    }
                }
            }
        })
        .catch(err => console.log("Background metadata sync skipped:", err));
    }, 700);
}

// Lightbox Map Renderer using Leaflet Map
// Render Detected Faces inside Lightbox Info
let currentRetagFaceId = null;
let currentRetagPhotoPath = null;
const retagModal = document.getElementById('retag-face-modal');
const retagInput = document.getElementById('retag-face-input');
const retagDatalist = document.getElementById('retag-people-list');
const btnCancelRetag = document.getElementById('cancel-retag-face-btn');
const btnSaveRetag = document.getElementById('save-retag-face-btn');

function editFaceTagPrompt(faceId, currentName, photoPath) {
    currentRetagFaceId = faceId;
    currentRetagPhotoPath = photoPath;
    
    // Populate datalist with existing people
    fetch('/api/people')
        .then(res => res.json())
        .then(data => {
            if(retagDatalist) {
                retagDatalist.innerHTML = '';
                data.forEach(p => {
                    if (!p.name.startsWith('Person ')) {
                        const opt = document.createElement('option');
                        opt.value = p.name;
                        retagDatalist.appendChild(opt);
                    }
                });
            }
            
            if(retagInput) {
                retagInput.value = currentName.startsWith('Person ') ? '' : currentName;
            }
            if(retagModal) {
                retagModal.classList.remove('hidden');
                setTimeout(() => retagInput && retagInput.focus(), 50);
            }
        });
}

function closeRetagModal() {
    if(retagModal) retagModal.classList.add('hidden');
    if(retagInput) retagInput.value = '';
    currentRetagFaceId = null;
    currentRetagPhotoPath = null;
}

if (btnCancelRetag) btnCancelRetag.addEventListener('click', closeRetagModal);

if (btnSaveRetag) {
    btnSaveRetag.addEventListener('click', () => {
        if (!currentRetagFaceId) return;
        const newName = retagInput ? retagInput.value.trim() : '';
        
        fetch('/api/faces/edit-tag', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_id: currentRetagFaceId, new_name: newName })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert("Failed to retag: " + data.error);
            } else {
                if (typeof loadStaticData === 'function') loadStaticData();
                renderLightboxFaces(currentRetagPhotoPath);
                closeRetagModal();
            }
        })
        .catch(err => {
            alert("Error communicating with server");
            closeRetagModal();
        });
    });
    
    if (retagInput) {
        retagInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                btnSaveRetag.click();
            }
        });
    }
}

function setPersonCoverFace(personId, faceId, photoPath) {
    if (!personId) return;
    fetch('/api/people/set-cover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ person_id: personId, face_id: faceId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert("Failed to set cover: " + data.error);
        } else {
            loadStaticData();
            renderLightboxFaces(photoPath);
        }
    })
    .catch(err => alert("Error setting cover photo"));
}

function renamePersonPrompt(id, currentName) {
    const cleanName = currentName.startsWith('Person ') ? '' : currentName;
    const newName = prompt(`Enter name for this person (currently "${currentName}"):`, cleanName);
    
    if (newName === null) return; // Cancelled
    
    const trimmed = newName.trim();
    if (!trimmed) return;
    
    fetch('/api/people/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, name: trimmed })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert("Failed to rename: " + data.error);
            return;
        }
        // Reload people references & current lightbox faces
        loadStaticData();
        
        // Refresh grid based on current view
        if (state.currentView === 'people') {
            loadPeople();
        }
        
        const photo = state.lightboxPhotos[state.lightboxIndex];
        if (photo) {
            renderLightboxFaces(photo.path);
        }
    })
    .catch(err => alert("Error communicating with server"));
}

// Lightbox Albums Mapping
function removePhotoFromAlbum(albumId, photoPath) {
    fetch('/api/albums/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ album_id: albumId, photos: [photoPath] })
    })
    .then(res => res.json())
    .then(data => {
        loadStaticData();
        renderLightboxAlbums(photoPath);
    });
}

function addPhotoToAlbumFromLightbox() {
    const albumId = elements.lightboxAlbumSelect.value;
    if (!albumId) return;
    
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    fetch('/api/albums/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ album_id: albumId, photos: [photo.path] })
    })
    .then(res => res.json())
    .then(data => {
        elements.lightboxAlbumSelect.value = ''; // Reset select
        loadStaticData();
        renderLightboxAlbums(photo.path);
    });
}

// Modal Album Creation Dialogs
function openCreateAlbumModal() {
    elements.newAlbumNameInput.value = '';
    elements.createAlbumError.classList.add('hidden');
    elements.createAlbumModal.classList.remove('hidden');
    elements.newAlbumNameInput.focus();
}

function closeCreateAlbumModal() {
    elements.createAlbumModal.classList.add('hidden');
}

function createAlbum() {
    const name = elements.newAlbumNameInput.value.trim();
    if (!name) {
        elements.createAlbumError.innerText = 'Album name cannot be empty';
        elements.createAlbumError.classList.remove('hidden');
        return;
    }
    
    fetch('/api/albums/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        closeCreateAlbumModal();
        loadStaticData();
        if (state.currentView === 'albums') {
            loadAlbums();
        }
    })
    .catch(err => {
        elements.createAlbumError.innerText = err.message || 'Failed to create album';
        elements.createAlbumError.classList.remove('hidden');
    });
}

// Add Selected Photos to Album Modal
// Add Selected Photos to Album Modal
function openAddToAlbumModal() {
    if (state.selectedPhotos.size === 0) return;
    
    elements.addToAlbumList.innerHTML = '';
    elements.addToNewAlbumInput.value = '';
    elements.addToAlbumError.classList.add('hidden');
    elements.confirmAddAlbumBtn.disabled = true;
    state.selectedAlbumTarget = null;
    
    if (state.albums.length === 0) {
        elements.addToAlbumList.innerHTML = '<p style="font-size:13px;color:var(--text-muted);padding:10px;">No albums created yet. Select one below or create a new one.</p>';
    } else {
        state.albums.forEach(album => {
            const div = document.createElement('div');
            div.className = 'album-select-item';
            div.dataset.id = album.id;
            
            let text = [];
            if (album.image_count > 0) text.push(`${album.image_count} photo${album.image_count === 1 ? '' : 's'}`);
            if (album.video_count > 0) text.push(`${album.video_count} video${album.video_count === 1 ? '' : 's'}`);
            if (text.length === 0) text.push('0 items');
            
            div.innerText = `${album.name} (${text.join(', ')})`;
            
            div.addEventListener('click', () => {
                document.querySelectorAll('.album-select-item').forEach(el => el.classList.remove('selected'));
                div.classList.add('selected');
                state.selectedAlbumTarget = album.id;
                elements.addToNewAlbumInput.value = ''; // clear input
                elements.confirmAddAlbumBtn.disabled = false;
            });
            
            elements.addToAlbumList.appendChild(div);
        });
    }
    
    // Listen to new album input
    elements.addToNewAlbumInput.oninput = () => {
        if (elements.addToNewAlbumInput.value.trim() !== '') {
            document.querySelectorAll('.album-select-item').forEach(el => el.classList.remove('selected'));
            state.selectedAlbumTarget = null;
            elements.confirmAddAlbumBtn.disabled = false;
            elements.addToAlbumError.classList.add('hidden');
        } else {
            elements.confirmAddAlbumBtn.disabled = true;
        }
    };
    
    elements.addToAlbumModal.classList.remove('hidden');
}

function closeAddToAlbumModal() {
    elements.addToAlbumModal.classList.add('hidden');
    state.selectedAlbumTarget = null;
}

function addSelectedToAlbum() {
    const newAlbumName = elements.addToNewAlbumInput.value.trim();
    const albumId = state.selectedAlbumTarget;
    
    if (!albumId && !newAlbumName) return;
    
    const photosArray = Array.from(state.selectedPhotos);
    elements.confirmAddAlbumBtn.disabled = true;
    elements.confirmAddAlbumBtn.innerText = 'Saving...';
    
    if (newAlbumName) {
        // Create new album first
        fetch('/api/albums/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newAlbumName })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Now add photos to it
                addPhotosToAlbumId(data.album_id, photosArray);
            } else {
                elements.addToAlbumError.innerText = data.error || "Failed to create album";
                elements.addToAlbumError.classList.remove('hidden');
                elements.confirmAddAlbumBtn.disabled = false;
                elements.confirmAddAlbumBtn.innerText = 'Add to Album';
            }
        })
        .catch(err => {
            elements.addToAlbumError.innerText = "Error creating album";
            elements.addToAlbumError.classList.remove('hidden');
            elements.confirmAddAlbumBtn.disabled = false;
            elements.confirmAddAlbumBtn.innerText = 'Add to Album';
        });
    } else {
        // Add to existing album
        addPhotosToAlbumId(albumId, photosArray);
    }
}

function addPhotosToAlbumId(albumId, photosArray) {
    fetch('/api/albums/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ album_id: albumId, photos: photosArray })
    })
    .then(res => res.json())
    .then(data => {
        closeAddToAlbumModal();
        clearSelection();
        loadStaticData(); // Refresh albums list
        if (state.currentView === 'albums') {
            loadAlbums();
        }
        elements.confirmAddAlbumBtn.innerText = 'Add to Album';
    })
    .catch(err => {
        elements.addToAlbumError.innerText = "Error adding photos to album";
        elements.addToAlbumError.classList.remove('hidden');
        elements.confirmAddAlbumBtn.disabled = false;
        elements.confirmAddAlbumBtn.innerText = 'Add to Album';
    });
}

// Load duplicates from API
function trashSelectedPhotos() {
    if (state.selectedPhotos.size === 0) return;
    const pathsArray = Array.from(state.selectedPhotos);
    
    if (!confirm(`Are you sure you want to move the ${pathsArray.length} selected items to the Recycle Bin?`)) {
        return;
    }
    
    fetch('/api/trash/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: pathsArray })
    })
    .then(res => res.json())
    .then(data => {
        clearSelection();
        loadStaticData();
        loadPhotos();
    })
    .catch(err => alert("Failed to move items to Recycle Bin"));
}

async function copyImageToClipboard(photoPath) {
    const response = await fetch(`/api/photo/file/${encodeURIComponent(photoPath)}`);
    if (!response.ok) throw new Error("Failed to fetch image file");
    const blob = await response.blob();
    
    // Convert to standard PNG via Canvas to guarantee maximum compatibility with OS clipboard pasting
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = URL.createObjectURL(blob);
    
    await new Promise((resolve, reject) => {
        img.onload = () => {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob(async (pngBlob) => {
                    try {
                        if (!pngBlob) {
                            reject(new Error("Image conversion failed"));
                            return;
                        }
                        await navigator.clipboard.write([
                            new ClipboardItem({
                                "image/png": pngBlob
                            })
                        ]);
                        URL.revokeObjectURL(img.src);
                        resolve();
                    } catch (clipboardErr) {
                        reject(clipboardErr);
                    }
                }, 'image/png');
            } catch (err) {
                reject(err);
            }
        };
        img.onerror = () => reject(new Error("Failed to render image canvas"));
    });
}

function copySelectedPhotoToClipboard() {
    if (state.selectedPhotos.size === 0) return;
    const pathsArray = Array.from(state.selectedPhotos);
    
    if (pathsArray.length > 1) {
        alert("The clipboard only supports copying a single image at a time. Please select only one photo.");
        return;
    }
    
    const photoPath = pathsArray[0];
    const ext = photoPath.split('.').pop().toLowerCase();
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    if (isVideo) {
        alert("Copying video files to clipboard is not supported by browsers. Only images can be copied.");
        return;
    }
    
    elements.multiCopyBtn.disabled = true;
    elements.multiCopyBtn.innerText = 'Copying...';
    
    copyImageToClipboard(photoPath)
        .then(() => {
            alert("Photo copied to clipboard! You can now paste (Ctrl+V) it in Discord, Slack, or image editors.");
            clearSelection();
        })
        .catch(err => {
            alert("Failed to copy photo to clipboard: " + err.message);
        })
        .finally(() => {
            elements.multiCopyBtn.disabled = false;
            elements.multiCopyBtn.innerHTML = '<i data-lucide="copy"></i> Copy Photo';
            lucide.createIcons();
        });
}


function copyLightboxPhotoToClipboard() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    const ext = photo.path.split('.').pop().toLowerCase();
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    if (isVideo) {
        alert("Copying video files to clipboard is not supported by browsers. Only images can be copied.");
        return;
    }
    
    elements.lightboxCopyBtn.disabled = true;
    elements.lightboxCopyBtn.innerText = 'Copying...';
    
    copyImageToClipboard(photo.path)
        .then(() => {
            alert("Photo copied to clipboard! You can now paste (Ctrl+V) it in Discord, Slack, or image editors.");
        })
        .catch(err => {
            alert("Failed to copy photo to clipboard: " + err.message);
        })
        .finally(() => {
            elements.lightboxCopyBtn.disabled = false;
            elements.lightboxCopyBtn.innerHTML = '<i data-lucide="copy" style="width:16px; height:16px;"></i> Copy Photo';
            lucide.createIcons();
        });
}

// Moves current lightbox photo to trash
function trashCurrentLightboxPhoto() {
    if (state.lightboxIndex === -1 || state.lightboxPhotos.length === 0) return;
    const photo = state.lightboxPhotos[state.lightboxIndex];
    
    if (!confirm(`Are you sure you want to move "${photo.filename}" to the Recycle Bin?`)) {
        return;
    }
    
    fetch('/api/trash/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: [photo.path] })
    })
    .then(res => res.json())
    .then(data => {
        closeLightbox();
        loadStaticData();
        loadPhotos();
    })
    .catch(err => alert("Failed to move item to Recycle Bin"));
}

// Archives or Unarchives the selected photos
function archiveSelectedPhotos() {
    if (state.selectedPhotos.size === 0) return;
    const pathsArray = Array.from(state.selectedPhotos);
    
    const isArchiveView = (state.currentView === 'archive');
    const endpoint = isArchiveView ? '/api/archive/restore' : '/api/archive/move';
    const actionText = isArchiveView ? 'unarchive' : 'archive';
    
    if (!confirm(`Are you sure you want to ${actionText} the ${pathsArray.length} selected items?`)) {
        return;
    }
    
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: pathsArray })
    })
    .then(res => res.json())
    .then(data => {
        clearSelection();
        loadPhotos();
    })
    .catch(err => alert(`Failed to ${actionText} selected items`));
}

// Toggles archive state for the currently previewed photo in Lightbox
function toggleLightboxPhotoArchive() {
    if (state.lightboxIndex === -1 || state.lightboxPhotos.length === 0) return;
    const photo = state.lightboxPhotos[state.lightboxIndex];
    
    const isArchived = !!photo.archived_at;
    const endpoint = isArchived ? '/api/archive/restore' : '/api/archive/move';
    const actionText = isArchived ? 'unarchive' : 'archive';
    
    if (!confirm(`Are you sure you want to ${actionText} "${photo.filename}"?`)) {
        return;
    }
    
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: [photo.path] })
    })
    .then(res => res.json())
    .then(data => {
        closeLightbox();
        loadPhotos();
    })
    .catch(err => alert(`Failed to ${actionText} photo`));
}

function restoreTrashPhotos(photoPaths) {
    fetch('/api/trash/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: photoPaths })
    })
    .then(res => res.json())
    .then(data => {
        loadStaticData();
        loadTrashPhotos();
    })
    .catch(err => alert("Failed to restore items"));
}

function purgeSinglePhoto(photoPath) {
    fetch('/api/trash/purge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: [photoPath] })
    })
    .then(res => res.json())
    .then(data => {
        loadStaticData();
        loadTrashPhotos();
    })
    .catch(err => alert("Failed to purge item"));
}



function restoreAllRecycleBin() {
    if (!state.trashedPhotos || state.trashedPhotos.length === 0) return;
    
    if (!confirm("Are you sure you want to restore all items currently in the Recycle Bin back to their original folders?")) {
        return;
    }
    
    elements.restoreAllTrashBtn.disabled = true;
    elements.restoreAllTrashBtn.innerText = 'Restoring...';
    
    const pathsArray = state.trashedPhotos.map(p => p.path);
    
    fetch('/api/trash/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: pathsArray })
    })
    .then(res => res.json())
    .then(data => {
        alert("All items restored successfully!");
        loadStaticData();
        loadTrashPhotos();
    })
    .catch(err => {
        alert("Failed to restore items");
    })
    .finally(() => {
        elements.restoreAllTrashBtn.disabled = false;
        elements.restoreAllTrashBtn.innerHTML = `<i data-lucide="rotate-ccw" style="width:16px; height:16px; margin-right:6px;"></i> Restore All`;
        lucide.createIcons();
    });
}

// Face Rescan Settings Trigger
function triggerFaceRescan() {
    if (!confirm("Are you sure you want to rescan faces for all photos? This will run in the background. Existing manual annotations will be preserved, but automatic faces will be updated with the improved high-recall model.")) {
        return;
    }
    
    elements.rescanFacesBtn.disabled = true;
    
    fetch('/api/faces/rescan', { method: 'POST' })
    .then(res => {
        if (!res.ok) throw new Error("Failed to start rescan");
        return res.json();
    })
    .then(data => {
        // Show progress box
        elements.scanProgressBox.classList.remove('hidden');
        elements.progressFile.innerText = 'Initializing face rescan...';
        elements.progressPercent.innerText = '0%';
        elements.progressBarFill.style.width = '0%';
        
        // Start polling scanner progress
        state.scanStatus = 'scanning';
        pollScanStatus();
    })
    .catch(err => {
        alert("Failed to start face rescan");
        elements.rescanFacesBtn.disabled = false;
    });
}

// Metadata Inline Editors
function parseDateParts(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/);
    if (match) {
        return {
            year: match[1],
            month: match[2],
            day: match[3],
            hour: match[4],
            minute: match[5]
        };
    }
    return null;
}

function updateRawDateFromParts() {
    const y = elements.editDateYear.value.trim().padStart(4, '0');
    const m = elements.editDateMonth.value.trim().padStart(2, '0');
    const d = elements.editDateDay.value.trim().padStart(2, '0');
    const h = elements.editDateHour.value.trim().padStart(2, '0');
    const min = elements.editDateMinute.value.trim().padStart(2, '0');
    
    // Default seconds to 00
    if (elements.editDateInput) elements.editDateInput.value = `${y}-${m}-${d} ${h}:${min}:00`;
}

function updatePartsFromRawDate() {
    const parts = parseDateParts(elements.editDateInput ? elements.editDateInput.value : '');
    if (parts) {
        elements.editDateYear.value = parts.year;
        elements.editDateMonth.value = parts.month;
        elements.editDateDay.value = parts.day;
        elements.editDateHour.value = parts.hour;
        elements.editDateMinute.value = parts.minute;
    }
}

// Bind sync events (called once during setup)
if (elements.editDateInput) {
    elements.editDateInput.addEventListener('input', updatePartsFromRawDate);
}
['editDateYear', 'editDateMonth', 'editDateDay', 'editDateHour', 'editDateMinute'].forEach(key => {
    if (elements[key]) {
        elements[key].addEventListener('input', updateRawDateFromParts);
    }
});
if (elements.cancelDateBtn) {
    elements.cancelDateBtn.addEventListener('click', toggleDateEditor);
}

function toggleDateEditor() {
    const isHidden = elements.dateEditorContainer.classList.contains('hidden');
    if (isHidden) {
        const photo = state.lightboxPhotos[state.lightboxIndex];
        const dateStr = photo.date_taken || '';
        if (elements.editDateInput) if (elements.editDateInput) elements.editDateInput.value = dateStr;
        updatePartsFromRawDate();
        elements.dateEditorContainer.classList.remove('hidden');
        elements.editDateYear.focus();
    } else {
        elements.dateEditorContainer.classList.add('hidden');
    }
}

function savePhotoDate() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    const newDate = elements.editDateInput ? elements.editDateInput.value.trim() : '';
    
    elements.saveDateBtn.disabled = true;
    elements.saveDateBtn.innerText = 'Saving...';
    
    fetch('/api/photo/edit_metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            photo_path: photo.path,
            date_taken: newDate
        })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        photo.date_taken = newDate;
        elements.photoDate.innerText = formatPhotoDate(newDate);
        elements.dateEditorContainer.classList.add('hidden');
        loadPhotos(); // Refresh grid dates
    })
    .catch(err => {
        alert(err.message || 'Failed to save date');
    })
    .finally(() => {
        elements.saveDateBtn.disabled = false;
        elements.saveDateBtn.innerText = 'Save';
    });
}

function fixPhotoDateFromFilename() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    elements.fixDateMismatchBtn.disabled = true;
    elements.fixDateMismatchBtn.innerText = 'Fixing...';
    
    fetch('/api/photo/fix-date-from-filename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_path: photo.path })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        if (data.success) {
            photo.date_taken = data.date_taken;
            elements.photoDate.innerText = formatPhotoDate(data.date_taken);
            if (elements.dateMismatchAlert) elements.dateMismatchAlert.classList.add('hidden');
            loadPhotos();
            alert("File creation/modification date successfully corrected on disk and database!");
        }
    })
    .catch(err => {
        alert("Failed to fix date: " + err.message);
    })
    .finally(() => {
        elements.fixDateMismatchBtn.disabled = false;
        elements.fixDateMismatchBtn.innerHTML = '<i data-lucide="wrench" style="width: 12px; height: 12px;"></i> Fix Date on Disk & DB';
        lucide.createIcons();
    });
}

function toggleLocationEditor() {
    const isHidden = elements.locationEditorContainer.classList.contains('hidden');
    if (isHidden) {
        const photo = state.lightboxPhotos[state.lightboxIndex];
        elements.editLocationInput.value = photo.place_name || '';
        elements.locationEditorContainer.classList.remove('hidden');
        elements.editLocationInput.focus();
    } else {
        elements.locationEditorContainer.classList.add('hidden');
    }
}

function savePhotoLocation() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    const newLocation = elements.editLocationInput.value.trim();
    
    elements.saveLocationBtn.disabled = true;
    elements.saveLocationBtn.innerText = 'Saving...';
    
    fetch('/api/photo/edit_metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            photo_path: photo.path,
            place_name: newLocation || ""
        })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        photo.place_name = newLocation || null;
        elements.photoLocation.innerText = newLocation || 'No location metadata';
        elements.locationEditorContainer.classList.add('hidden');
        loadPhotos(); // Refresh places filters/grids
    })
    .catch(err => {
        alert(err.message || 'Failed to save location');
    })
    .finally(() => {
        elements.saveLocationBtn.disabled = false;
        elements.saveLocationBtn.innerText = 'Save';
    });
}

// Manual Face Bounding Box Selector
function toggleManualFaceDrawingMode() {
    // If viewing a video, skip drawing mode and open the video-person dropdown instead
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (photo) {
        const ext = photo.path.split('.').pop().toLowerCase();
        if (['mp4', 'mov', 'm4v', 'hevc'].includes(ext)) {
            openVideoPersonModal(photo.path);
            return;
        }
    }

    state.isDrawingMode = !state.isDrawingMode;
    if (state.isDrawingMode) {
        elements.addFaceManualBtn.classList.add('active');
        elements.addFaceManualBtn.style.borderColor = 'var(--primary-color)';
        elements.addFaceManualBtn.style.color = 'var(--primary-color)';
        elements.manualFaceInstructions.classList.remove('hidden');
        elements.lightbox.classList.add('drawing-active');
    } else {
        resetDrawingState();
    }
}

function resetDrawingState() {
    state.isDrawingMode = false;
    state.isDrawing = false;
    state.drawBox = { x: 0, y: 0, w: 0, h: 0 };
    if (elements.addFaceManualBtn) {
        elements.addFaceManualBtn.classList.remove('active');
        elements.addFaceManualBtn.style.borderColor = '';
        elements.addFaceManualBtn.style.color = '';
    }
    if (elements.manualFaceInstructions) {
        elements.manualFaceInstructions.classList.add('hidden');
    }
    if (elements.lightboxDrawingOverlay) {
        elements.lightboxDrawingOverlay.classList.add('hidden');
    }
    if (elements.lightbox) {
        elements.lightbox.classList.remove('drawing-active');
    }
}

// ==========================================
// Video Person Tagging (dropdown, no crop)
// ==========================================
let currentVideoPath = null;
const videoPersonModal = document.getElementById('video-person-modal');
const videoPersonSelect = document.getElementById('video-person-select');
const videoPersonError = document.getElementById('video-person-error');
const cancelVideoPersonBtn = document.getElementById('cancel-video-person-btn');
const confirmVideoPersonBtn = document.getElementById('confirm-video-person-btn');

function openVideoPersonModal(videoPath) {
    currentVideoPath = videoPath;
    if (videoPersonError) videoPersonError.classList.add('hidden');
    if (videoPersonSelect) videoPersonSelect.innerHTML = '<option value="">-- Select a person --</option>';

    // Populate dropdown with only named (non-anonymous) people
    fetch('/api/people')
        .then(res => res.json())
        .then(data => {
            if (videoPersonSelect) {
                data.forEach(p => {
                    if (!p.name.startsWith('Person ')) {
                        const opt = document.createElement('option');
                        opt.value = p.id;
                        opt.innerText = p.name;
                        videoPersonSelect.appendChild(opt);
                    }
                });
            }
            if (videoPersonModal) videoPersonModal.classList.remove('hidden');
        });
}

function closeVideoPersonModal() {
    if (videoPersonModal) videoPersonModal.classList.add('hidden');
    currentVideoPath = null;
}

if (cancelVideoPersonBtn) cancelVideoPersonBtn.addEventListener('click', closeVideoPersonModal);

if (confirmVideoPersonBtn) {
    confirmVideoPersonBtn.addEventListener('click', () => {
        const personId = videoPersonSelect ? videoPersonSelect.value : '';
        if (!personId) {
            if (videoPersonError) {
                videoPersonError.innerText = 'Please select a person.';
                videoPersonError.classList.remove('hidden');
            }
            return;
        }
        if (!currentVideoPath) return;

        fetch('/api/faces/add_to_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_path: currentVideoPath, person_id: parseInt(personId) })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                if (videoPersonError) {
                    videoPersonError.innerText = data.error;
                    videoPersonError.classList.remove('hidden');
                }
            } else {
                closeVideoPersonModal();
                loadStaticData();
                renderLightboxFaces(currentVideoPath || state.currentLightboxPhoto);
            }
        })
        .catch(err => {
            if (videoPersonError) {
                videoPersonError.innerText = 'Error communicating with server.';
                videoPersonError.classList.remove('hidden');
            }
        });
    });
}

function resetZoom() {
    state.zoomScale = 1;
    state.panOffset = { x: 0, y: 0 };
    applyZoomTransform();
}

function applyZoomTransform() {
    const img = elements.lightboxImg;
    if (!img) return;
    img.style.transform = `translate(${state.panOffset.x}px, ${state.panOffset.y}px) scale(${state.zoomScale})`;
    if (state.zoomScale > 1) {
        img.style.cursor = state.isPanning ? 'grabbing' : 'grab';
    } else {
        img.style.cursor = '';
    }
}

function handleDrawStart(e) {
    const isVideo = elements.lightboxImg.classList.contains('hidden');
    const media = isVideo ? elements.lightboxVideo : elements.lightboxImg;
    if (!media) return;

    if (state.isDrawingMode) {
        const rect = media.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        // Ensure click is inside image bounds
        if (clickX < 0 || clickX > rect.width || clickY < 0 || clickY > rect.height) return;
        
        state.isDrawing = true;
        state.drawStart = { x: clickX, y: clickY };
        state.drawBox = { x: clickX, y: clickY, w: 0, h: 0 };
        
        elements.lightboxDrawingOverlay.classList.remove('hidden');
        updateDrawingOverlay(clickX, clickY, 0, 0, rect);
    } else {
        // Panning Mode (only if zoomed in)
        if (state.zoomScale <= 1) return;
        e.preventDefault();
        state.isPanning = true;
        state.panStart = { x: e.clientX - state.panOffset.x, y: e.clientY - state.panOffset.y };
        media.style.transition = 'none'; // latency-free tracking
        applyZoomTransform();
    }
}

function handleDrawing(e) {
    const isVideo = elements.lightboxImg.classList.contains('hidden');
    const media = isVideo ? elements.lightboxVideo : elements.lightboxImg;
    if (!media) return;

    if (state.isDrawingMode) {
        if (!state.isDrawing) return;
        const rect = media.getBoundingClientRect();
        
        let currentX = e.clientX - rect.left;
        let currentY = e.clientY - rect.top;
        
        // Constrain inside image boundaries
        currentX = Math.max(0, Math.min(rect.width, currentX));
        currentY = Math.max(0, Math.min(rect.height, currentY));
        
        const x = Math.min(state.drawStart.x, currentX);
        const y = Math.min(state.drawStart.y, currentY);
        const w = Math.abs(state.drawStart.x - currentX);
        const h = Math.abs(state.drawStart.y - currentY);
        
        state.drawBox = { x, y, w, h };
        updateDrawingOverlay(x, y, w, h, rect);
    } else {
        // Panning mode tracking
        if (!state.isPanning) return;
        state.panOffset.x = e.clientX - state.panStart.x;
        state.panOffset.y = e.clientY - state.panStart.y;
        applyZoomTransform();
    }
}

function updateDrawingOverlay(x, y, w, h, rect) {
    const containerRect = elements.lightboxMediaContainer.getBoundingClientRect();
    const offsetLeft = rect.left - containerRect.left;
    const offsetTop = rect.top - containerRect.top;
    
    elements.lightboxDrawingOverlay.style.left = `${offsetLeft + x}px`;
    elements.lightboxDrawingOverlay.style.top = `${offsetTop + y}px`;
    elements.lightboxDrawingOverlay.style.width = `${w}px`;
    elements.lightboxDrawingOverlay.style.height = `${h}px`;
}

function handleDrawEnd(e) {
    if (state.isDrawingMode) {
        if (!state.isDrawing) return;
        state.isDrawing = false;
        
        const isVideo = elements.lightboxImg.classList.contains('hidden');
        const media = isVideo ? elements.lightboxVideo : elements.lightboxImg;
        if (!media) return;
        
        const rect = media.getBoundingClientRect();
        
        if (state.drawBox.w < 10 || state.drawBox.h < 10) {
            elements.lightboxDrawingOverlay.classList.add('hidden');
            return;
        }
        
        // Convert to percentages relative to the displayed image area
        const pctX = state.drawBox.x / rect.width;
        const pctY = state.drawBox.y / rect.height;
        const pctW = state.drawBox.w / rect.width;
        const pctH = state.drawBox.h / rect.height;
        
        // Always use the browser's actual rendered dimensions (respects EXIF rotation)
        // NOT photo.width/height from DB which may be pre-rotation raw sensor values
        const natWidth = isVideo ? media.videoWidth : media.naturalWidth;
        const natHeight = isVideo ? media.videoHeight : media.naturalHeight;
        
        // Scale up relative to original (transposed) image coordinates
        let bx = Math.round(pctX * natWidth);
        let by = Math.round(pctY * natHeight);
        let bw = Math.round(pctW * natWidth);
        let bh = Math.round(pctH * natHeight);
        
        // Add 20% padding on each side so the crop is slightly zoomed out from selection
        const padX = Math.round(bw * 0.20);
        const padY = Math.round(bh * 0.20);
        bx = Math.max(0, bx - padX);
        by = Math.max(0, by - padY);
        bw = Math.min(natWidth - bx, bw + padX * 2);
        bh = Math.min(natHeight - by, bh + padY * 2);
        
        state.pendingFaceBox = { x: bx, y: by, w: bw, h: bh };
        
        openManualFaceModal();
    } else {
        if (state.isPanning) {
            state.isPanning = false;
            const isVideo = elements.lightboxImg.classList.contains('hidden');
            const media = isVideo ? elements.lightboxVideo : elements.lightboxImg;
            if (media) {
                media.style.transition = ''; // restore smooth transition
            }
            applyZoomTransform();
        }
    }
}

function openManualFaceModal() {
    elements.manualFaceNameInput.value = '';
    elements.manualFaceSelectExisting.value = '';
    elements.manualFaceError.classList.add('hidden');
    
    // Populate existing people options
    elements.manualFaceSelectExisting.innerHTML = '<option value="">-- Or select existing person --</option>';
    state.people.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.innerText = p.name;
        elements.manualFaceSelectExisting.appendChild(opt);
    });
    
    elements.manualFaceModal.classList.remove('hidden');
    elements.manualFaceNameInput.focus();
}

function submitManualFaceLabel() {
    const name = elements.manualFaceNameInput.value.trim();
    const existingId = elements.manualFaceSelectExisting.value;
    
    if (!name && !existingId) {
        elements.manualFaceError.innerText = 'Please specify a name or select an existing person';
        elements.manualFaceError.classList.remove('hidden');
        return;
    }
    
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    const payload = {
        photo_path: photo.path,
        x: state.pendingFaceBox.x,
        y: state.pendingFaceBox.y,
        w: state.pendingFaceBox.w,
        h: state.pendingFaceBox.h,
        person_id: existingId ? parseInt(existingId) : null,
        person_name: name || null
    };
    
    fetch('/api/faces/add_manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to add manual face label");
        return res.json();
    })
    .then(data => {
        elements.manualFaceModal.classList.add('hidden');
        resetDrawingState();
        loadStaticData();
        renderLightboxFaces(photo.path);
    })
    .catch(err => {
        elements.manualFaceError.innerText = err.message || 'Error saving face label';
        elements.manualFaceError.classList.remove('hidden');
    });
}

function deleteFaceLabel(faceId, photoPath) {
    fetch('/api/faces/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ face_id: faceId })
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to delete face label");
        return res.json();
    })
    .then(data => {
        loadStaticData();
        renderLightboxFaces(photoPath);
    })
    .catch(err => alert("Error deleting face label: " + err.message));
}

function unnamePerson(id) {
    fetch('/api/people/unname', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    })
    .then(res => res.json())
    .then(data => {
        loadStaticData();
        loadPeople();
    })
    .catch(err => alert("Failed to unname person"));
}

function deletePerson(id) {
    fetch('/api/people/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    })
    .then(res => res.json())
    .then(data => {
        loadStaticData();
        loadPeople();
    })
    .catch(err => alert("Failed to delete person"));
}


// ==========================================
// NEW FEATURES WIRING (Scans, Cover Photo, AI Train)
// ==========================================

// Manual Scan Buttons
const btnScanDir = document.getElementById('scan-directory-btn');
const btnRescanMeta = document.getElementById('rescan-metadata-btn');
const btnRefreshPlaces = document.getElementById('refresh-places-btn');
const btnForceCluster = document.getElementById('force-cluster-btn');

if (btnScanDir) {
    btnScanDir.addEventListener('click', () => {
        fetch('/api/scan_directory', { method: 'POST' }).then(() => {
            alert('Scan for new files started in the background!');
        });
    });
}

if (btnRescanMeta) {
    btnRescanMeta.addEventListener('click', () => {
        fetch('/api/metadata/rescan', { method: 'POST' }).then(() => {
            alert('Metadata rescan & missing files track started!');
        });
    });
}

const btnRebuildCache = document.getElementById('rebuild-cache-btn');
if (btnRebuildCache) {
    btnRebuildCache.addEventListener('click', () => {
        if(confirm("This will permanently delete all physical cache files (thumbnails and face crops) and rebuild the database file mapping. Albums and Face identities will NOT be lost. This might take a while on next load. Continue?")) {
            fetch('/api/cache/rebuild', { method: 'POST' }).then(() => {
                alert('Cache rebuild and missing files track started! Check the top notification bar for progress.');
            });
        }
    });
}

if (btnRefreshPlaces) {
    btnRefreshPlaces.addEventListener('click', () => {
        fetch('/api/metadata/refresh_places', { method: 'POST' }).then(() => {
            alert('Places geocoding refresh started!');
        });
    });
}

if (btnForceCluster) {
    btnForceCluster.addEventListener('click', () => {
        fetch('/api/faces/force_cluster', { method: 'POST' }).then(() => {
            alert('Forced AI Face Clustering started!');
        });
    });
}

// Override Safe Rescan Faces
const rescanBtn = document.getElementById('rescan-faces-btn');
if (rescanBtn) {
    // Remove old listeners if any (simple way is clone/replace)
    const newBtn = rescanBtn.cloneNode(true);
    rescanBtn.parentNode.replaceChild(newBtn, rescanBtn);
    newBtn.addEventListener('click', () => {
        if (confirm("Are you sure you want to run a safe rescan? This will detect faces on photos that were missed, but WILL NOT delete your named groups!")) {
            fetch('/api/faces/safe_rescan', { method: 'POST' }).then(() => {
                alert('Safe Face Rescan started in background!');
            });
        }
    });
}

const reevaluateBtn = document.getElementById('reevaluate-faces-btn');
if (reevaluateBtn) {
    reevaluateBtn.addEventListener('click', () => {
        reevaluateBtn.disabled = true;
        const originalText = reevaluateBtn.innerHTML;
        reevaluateBtn.innerHTML = '<i class="lucide-refresh-cw animate-spin"></i> Processing...';
        
        fetch('/api/scan/reevaluate_faces', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                reevaluateBtn.disabled = false;
                reevaluateBtn.innerHTML = originalText;
                if (data.success) {
                    alert(`Re-evaluation complete! Moved ${data.reassigned} faces to better matching people, and unassigned ${data.unassigned} faces that no longer matched.`);
                    if (state.currentView === 'people') {
                        loadPeople();
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                reevaluateBtn.disabled = false;
                reevaluateBtn.innerHTML = originalText;
                alert('Failed to re-evaluate faces.');
            });
    });
}

// ==========================================
// Cover Photo Popup Override
// ==========================================
let coverPhotoPersonId = null;

// The old Set Cover Photo button in People Grid is inside `renderPeopleList`
// We need to attach event delegation for it.
document.addEventListener('DOMContentLoaded', () => {
    const pg = document.getElementById('people-grid-root');
    if (pg) {
        pg.addEventListener('click', (e) => {
            const btn = e.target.closest('.person-action-btn');
            if (btn && btn.innerHTML.includes('Make Cover')) {
                e.stopPropagation();
        const personCard = btn.closest('.person-card');
        if (personCard) {
            coverPhotoPersonId = personCard.dataset.id;
            openCoverPhotoModal(coverPhotoPersonId);
        }
    }
        });
    }
});

function openCoverPhotoModal(personId) {
    const modal = document.getElementById('cover-photo-modal');
    const grid = document.getElementById('cover-photo-grid');
    grid.innerHTML = '<p>Loading faces...</p>';
    modal.classList.remove('hidden');
    
    fetch(`/api/people/${personId}/faces`)
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = '';
            if (!data.faces || data.faces.length === 0) {
                grid.innerHTML = '<p>No faces available for this person.</p>';
                return;
            }
            
            data.faces.forEach(face => {
                const img = document.createElement('img');
                img.src = `/api/photo/crop/${face.id}`;
                img.style.width = '100%';
                img.style.height = '100px';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '8px';
                img.style.cursor = 'pointer';
                img.style.border = '2px solid transparent';
                
                img.addEventListener('click', () => {
                    // Set cover
                    fetch('/api/people/set-cover', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ person_id: personId, face_id: face.id })
                    }).then(() => {
                        modal.classList.add('hidden');
                        renderPeopleList();
                    });
                });
                
                grid.appendChild(img);
            });
        });
}

function openRenameAlbumModal(albumId, currentName) {
    const modal = document.getElementById('rename-album-modal');
    const input = document.getElementById('rename-album-input');
    input.value = currentName;
    modal.classList.remove('hidden');
    input.focus();
    
    const saveBtn = document.getElementById('save-rename-album-btn');
    const cancelBtn = document.getElementById('cancel-rename-album-btn');
    
    // Clear previous listeners by cloning
    const newSaveBtn = saveBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    newCancelBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });
    
    newSaveBtn.addEventListener('click', () => {
        const newName = input.value.trim();
        if (!newName || newName === currentName) {
            modal.classList.add('hidden');
            return;
        }
        
        fetch('/api/albums/rename', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ album_id: albumId, new_name: newName })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                modal.classList.add('hidden');
                loadAlbums(); // refresh albums view
            } else {
                alert(data.error || 'Failed to rename album');
            }
        });
    });
}

function openAlbumCoverModal(albumId) {
    const modal = document.getElementById('cover-photo-modal');
    const grid = document.getElementById('cover-photo-grid');
    grid.innerHTML = '<div style="width: 100%; text-align: center; padding: 20px; color: var(--text-color);">Loading photos...</div>';
    modal.classList.remove('hidden');
    
    const cancelBtn = document.getElementById('cancel-cover-photo-btn');
    const newCancelBtn = cancelBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    newCancelBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });
    
    // Fetch photos for this album
    fetch(`/api/photos?albums=${albumId}`)
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = '';
            if (!data || data.length === 0) {
                grid.innerHTML = '<div style="width: 100%; text-align: center; padding: 20px; color: var(--text-color);">No photos available in this album.</div>';
                return;
            }
            
            data.forEach(photo => {
                const img = document.createElement('img');
                img.src = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}`;
                img.style.width = '100%';
                img.style.height = '120px';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '12px';
                img.style.cursor = 'pointer';
                img.style.transition = 'transform 0.2s, box-shadow 0.2s';
                img.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                
                img.addEventListener('mouseenter', () => {
                    img.style.transform = 'scale(1.05)';
                    img.style.boxShadow = '0 8px 15px rgba(0,0,0,0.2)';
                });
                
                img.addEventListener('mouseleave', () => {
                    img.style.transform = 'scale(1)';
                    img.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                });
                
                img.addEventListener('click', () => {
                    fetch('/api/albums/set-cover', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ album_id: albumId, photo_path: photo.path })
                    }).then(() => {
                        modal.classList.add('hidden');
                        loadAlbums(); // refresh albums view
                    });
                });
                
                grid.appendChild(img);
            });
        });
}

// ==========================================
// AI Training / Merge Logic
// ==========================================
let trainingPairs = [];
let currentPairIndex = 0;

// Add a button dynamically to the People header
const peopleHeader = document.querySelector('.people-header');
if (peopleHeader) {
    const trainBtn = document.createElement('button');
    trainBtn.className = 'btn btn-primary';
    trainBtn.innerHTML = '<i data-lucide="brain-circuit" style="width:16px; height:16px;"></i> Improve AI';
    trainBtn.addEventListener('click', startAiTraining);
    peopleHeader.appendChild(trainBtn);
}

function startAiTraining() {
    const modal = document.getElementById('ai-training-modal');
    modal.classList.remove('hidden');
    document.getElementById('ai-train-name-1').innerText = "Loading...";
    
    fetch('/api/faces/training_pairs')
        .then(res => res.json())
        .then(data => {
            trainingPairs = data.pairs || [];
            currentPairIndex = 0;
            showNextTrainingPair();
        });
}

function showNextTrainingPair() {
    if (currentPairIndex >= trainingPairs.length) {
        document.getElementById('ai-training-modal').classList.add('hidden');
        alert("No more faces to train right now. Great job!");
        renderPeopleList();
        return;
    }
    
    const pair = trainingPairs[currentPairIndex];
    document.getElementById('ai-train-name-1').innerText = pair.person_name;
    document.getElementById('ai-train-img-1').src = `/api/photo/crop/${pair.named_face_id}`;
    document.getElementById('ai-train-img-2').src = `/api/photo/crop/${pair.unknown_face_id}`;
}

document.getElementById('ai-train-yes-btn')?.addEventListener('click', () => {
    const pair = trainingPairs[currentPairIndex];
    fetch('/api/people/merge', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            person_id: pair.person_id,
            unknown_face_id: pair.unknown_face_id
        })
    }).then(() => {
        currentPairIndex++;
        showNextTrainingPair();
    });
});

document.getElementById('ai-train-no-btn')?.addEventListener('click', () => {
    currentPairIndex++;
    showNextTrainingPair();
});

document.getElementById('ai-train-skip-text')?.addEventListener('click', () => {
    currentPairIndex++;
    showNextTrainingPair();
});




// ==========================================
// Lightbox Refresh Button Wiring
// ==========================================
const btnRefreshPhoto = document.getElementById('lightbox-refresh-btn');
if (btnRefreshPhoto) {
    btnRefreshPhoto.addEventListener('click', () => {
        if (!state.currentLightboxPhoto) return;
        
        // Spin the icon
        const icon = btnRefreshPhoto.querySelector('i');
        if (icon) {
            icon.style.transition = 'transform 1s linear';
            icon.style.transform = 'rotate(360deg)';
        }
        
        fetch('/api/photo/refresh', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: state.currentLightboxPhoto })
        })
        .then(res => {
            if (res.status === 404) {
                return res.json().then(data => {
                    if (data.error === "file_missing") {
                        handleMissingPhoto(state.currentLightboxPhoto);
                        return null; // Stop propagation
                    }
                    throw new Error("File not found");
                });
            }
            return res.json();
        })
        .then(data => {
            if (!data) return; // Handled missing
            
            if (icon) {
                icon.style.transform = '';
            }
            if (data.success) {
                if (icon) {
                    const originalLucide = icon.getAttribute('data-lucide');
                    icon.setAttribute('data-lucide', 'check');
                    icon.style.color = '#10b981';
                    lucide.createIcons();
                    setTimeout(() => {
                        icon.setAttribute('data-lucide', originalLucide);
                        icon.style.color = '';
                        lucide.createIcons();
                        const path = state.currentLightboxPhoto;
                        closeLightbox();
                        setTimeout(() => openLightbox(path), 300);
                    }, 1500);
                } else {
                    const path = state.currentLightboxPhoto;
                    closeLightbox();
                    setTimeout(() => openLightbox(path), 300);
                }
            } else {
                alert("Failed to refresh photo: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            if (icon) icon.style.transform = '';
            alert("Error refreshing photo.");
        });
    });
}

function handleMissingPhoto(photoPath) {
    // Show a loading throbber/bar at the bottom of the screen
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'missing-file-loader';
    loadingDiv.style.position = 'fixed';
    loadingDiv.style.bottom = '20px';
    loadingDiv.style.left = '50%';
    loadingDiv.style.transform = 'translateX(-50%)';
    loadingDiv.style.background = 'var(--bg-card)';
    loadingDiv.style.padding = '10px 20px';
    loadingDiv.style.borderRadius = '8px';
    loadingDiv.style.boxShadow = '0 4px 12px rgba(0,0,0,0.5)';
    loadingDiv.style.zIndex = '9999';
    loadingDiv.style.display = 'flex';
    loadingDiv.style.alignItems = 'center';
    loadingDiv.style.gap = '10px';
    loadingDiv.style.fontSize = '14px';
    loadingDiv.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Looking for missing file...`;
    document.body.appendChild(loadingDiv);
    lucide.createIcons();
    
    fetch('/api/photo/find_missing', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ path: photoPath })
    })
    .then(res => res.json())
    .then(data => {
        document.body.removeChild(loadingDiv);
        if (data.success && data.new_path) {
            alert("File was found at a new location! Updating gallery link and reloading...");
            closeLightbox();
            loadStaticData();
            setTimeout(() => openLightbox(data.new_path), 500);
        } else {
            // Show Retarget Modal
            const modalHTML = `
                <div id="retarget-modal-overlay" class="retarget-modal-overlay visible">
                    <div class="retarget-modal-content">
                        <div class="retarget-modal-header">
                            <i data-lucide="file-question" style="color: var(--accent-color);"></i>
                            File Not Found
                        </div>
                        <div class="retarget-modal-body">
                            The file could not be found at its original location or inside any tracked directories.
                        </div>
                        <div class="retarget-input-group">
                            <label>Retarget File (Absolute Folder Path)</label>
                            <input type="text" id="retarget-dir-input" placeholder="e.g. D:\\My New Folder">
                        </div>
                        <div class="retarget-modal-actions">
                            <button class="btn-cancel-retarget" id="retarget-cancel-btn">Cancel</button>
                            <button class="btn-delete-record" id="retarget-delete-btn">
                                <i data-lucide="trash-2" style="width:14px; height:14px;"></i> Remove from Gallery
                            </button>
                            <button class="btn-retarget" id="retarget-search-btn">
                                <i data-lucide="search" style="width:14px; height:14px;"></i> Search Directory
                            </button>
                        </div>
                    </div>
                </div>
            `;
            const wrapper = document.createElement('div');
            wrapper.innerHTML = modalHTML;
            const overlay = wrapper.firstElementChild;
            document.body.appendChild(overlay);
            lucide.createIcons();
            
            const cleanupModal = () => {
                overlay.classList.remove('visible');
                setTimeout(() => { if (document.body.contains(overlay)) document.body.removeChild(overlay); }, 300);
            };
            
            document.getElementById('retarget-cancel-btn').onclick = cleanupModal;
            
            document.getElementById('retarget-delete-btn').onclick = () => {
                cleanupModal();
                fetch('/api/photo/delete_record', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path: photoPath })
                }).then(() => {
                    closeLightbox();
                    loadPhotos(); // reload grid
                });
            };
            
            document.getElementById('retarget-search-btn').onclick = () => {
                const searchDir = document.getElementById('retarget-dir-input').value.trim();
                if (!searchDir) {
                    alert('Please enter a directory path to search.');
                    return;
                }
                
                const btn = document.getElementById('retarget-search-btn');
                btn.disabled = true;
                btn.innerHTML = `<i data-lucide="loader-2" class="spin" style="width:14px; height:14px;"></i> Searching...`;
                lucide.createIcons();
                
                fetch('/api/photo/find_missing', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path: photoPath, search_dir: searchDir })
                })
                .then(r => r.json())
                .then(rData => {
                    cleanupModal();
                    if (rData.success && rData.new_path) {
                        alert("File found! Updating gallery...");
                        closeLightbox();
                        loadStaticData();
                        setTimeout(() => openLightbox(rData.new_path), 500);
                    } else {
                        alert("File was not found in that directory.");
                    }
                })
                .catch(() => {
                    alert("Error searching directory.");
                    cleanupModal();
                });
            };
        }
    })
    .catch(err => {
        document.body.removeChild(loadingDiv);
        alert("Error while searching for missing file.");
    });
}

// ==========================================


// ==========================================
// File Path Editor (Retargeting)
// ==========================================
const btnEditPath = document.getElementById('edit-path-btn');
const pathEditorContainer = document.getElementById('path-editor-container');
const editPathInput = document.getElementById('edit-path-input');
const btnSavePath = document.getElementById('save-path-btn');
const btnCancelPath = document.getElementById('cancel-path-btn');

if (btnEditPath) {
    btnEditPath.addEventListener('click', () => {
        if (!state.currentLightboxPhoto) return;
        pathEditorContainer.classList.remove('hidden');
        editPathInput.value = state.currentLightboxPhoto;
        editPathInput.focus();
    });
}

if (btnCancelPath) {
    btnCancelPath.addEventListener('click', () => {
        pathEditorContainer.classList.add('hidden');
    });
}

if (btnSavePath) {
    btnSavePath.addEventListener('click', () => {
        const newPath = editPathInput.value.trim();
        if (!newPath) return;
        if (newPath === state.currentLightboxPhoto) {
            pathEditorContainer.classList.add('hidden');
            return;
        }
        
        btnSavePath.disabled = true;
        btnSavePath.innerText = 'Saving...';
        
        fetch('/api/photo/find_missing', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: state.currentLightboxPhoto, search_dir: newPath })
        })
        .then(res => res.json())
        .then(data => {
            btnSavePath.disabled = false;
            btnSavePath.innerText = 'Retarget';
            
            if (data.success && data.new_path) {
                pathEditorContainer.classList.add('hidden');
                alert("File retargeted successfully! Updating gallery...");
                closeLightbox();
                loadStaticData();
                setTimeout(() => openLightbox(data.new_path), 500);
            } else {
                alert("Could not find or verify the file at that exact path.");
            }
        })
        .catch(err => {
            btnSavePath.disabled = false;
            btnSavePath.innerText = 'Retarget';
            alert("Error while retargeting file.");
        });
    });
}


// ==========================================
// Sidebar Albums Toggle & Navigation
// ==========================================
// (Logic moved inline to index.html to handle Lucide re-renders)

// ==========================================
// Statistics View Logic
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    const memBtn = document.getElementById('nav-memories');
    if (memBtn) memBtn.addEventListener('click', (e) => { e.preventDefault(); switchView('memories'); });
});


// --- NEW LOGIC: Statistics Heatmap ---
function initStatsHeatmap() {
    const originalRenderChart = window.renderChart || renderChart;
    window.renderChart = function(yearlyData, targetYear) {
        originalRenderChart(yearlyData, targetYear);
        
        document.getElementById('stats-heatmap-container').classList.add('hidden');
        
        setTimeout(() => {
            const root = document.getElementById('custom-chart-root');
            if(!root) return;
            // FIX: use .chart-col
            const bars = root.querySelectorAll('.chart-col');
            bars.forEach((bar, idx) => {
                bar.style.cursor = 'pointer';
                bar.addEventListener('click', () => {
                    const month = (idx + 1).toString().padStart(2, '0');
                    loadStatsHeatmap(targetYear, month);
                });
            });
        }, 100);
    };
}

function loadStatsHeatmap(year, month) {
    const container = document.getElementById('stats-heatmap-container');
    container.classList.remove('hidden');
    container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading daily activity...</p></div>`;
    
    fetch(`/api/stats/heatmap?year=${year}&month=${month}`)
        .then(res => res.json())
        .then(data => {
            const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            const monthName = monthNames[parseInt(month) - 1];
            
            const daysInMonth = new Date(parseInt(year), parseInt(month), 0).getDate();
            
            let maxCount = 0;
            for (let i = 1; i <= daysInMonth; i++) {
                const day = i.toString().padStart(2, '0');
                if (data[day] > maxCount) maxCount = data[day];
            }
            if (maxCount === 0) maxCount = 1;
            
            let gridHTML = `<div class="heatmap-header" style="margin-bottom: 24px;">${monthName} ${year}</div><div class="heatmap-grid">`;
            
            for (let i = 1; i <= daysInMonth; i++) {
                const dayStr = i.toString().padStart(2, '0');
                const count = data[dayStr] || 0;
                
                let opacity = 0;
                if (count > 0) {
                    opacity = 0.2 + (0.8 * (count / maxCount)); 
                }
                
                const style = count > 0 ? `background-color: rgba(99, 102, 241, ${opacity});` : '';
                gridHTML += `<div class="heatmap-cell" data-count="${count}" style="${style}">
                                <div class="heatmap-tooltip">${monthName} ${i}: ${count} media</div>
                             </div>`;
            }
            gridHTML += '</div>';
            container.innerHTML = gridHTML;
        });
}
document.addEventListener('DOMContentLoaded', initStatsHeatmap);

// Filename renaming logic
const filenameInput = document.getElementById('photo-filename-input');
if (filenameInput) {
    const handleRename = async () => {
        if (!state.currentLightboxPhoto) return;
        const oldPath = state.currentLightboxPhoto.file_path;
        const newName = filenameInput.value.trim();
        
        if (!newName || oldPath.endsWith(newName)) return; // No change
        
        try {
            const res = await fetch('/api/photo/rename', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    photo_path: oldPath,
                    new_filename: newName
                })
            });
            const data = await res.json();
            if (data.success) {
                // Update frontend state
                state.currentLightboxPhoto.file_path = data.new_path;
                state.currentLightboxPhoto.filename = data.new_filename;
                elements.photoPath.textContent = data.new_path;
                
                // Update photo in global arrays
                const gridPhoto = state.photos.find(p => p.file_path === oldPath);
                if (gridPhoto) {
                    gridPhoto.file_path = data.new_path;
                    gridPhoto.filename = data.new_filename;
                }
            } else {
                alert(data.error || 'Failed to rename file');
                filenameInput.value = state.currentLightboxPhoto.filename; // Revert
            }
        } catch (e) {
            console.error(e);
            alert('Error renaming file');
            filenameInput.value = state.currentLightboxPhoto.filename; // Revert
        }
    };
    
    filenameInput.addEventListener('blur', handleRename);
    filenameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            filenameInput.blur();
        }
    });
}


// --- SCROLL WHEEL PICKER LOGIC ---
const wheelData = {
    day: Array.from({length: 31}, (_, i) => String(i+1).padStart(2, '0')),
    month: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
    year: Array.from({length: 40}, (_, i) => String(new Date().getFullYear() - 20 + i)),
    hour: Array.from({length: 12}, (_, i) => String(i === 0 ? 12 : i).padStart(2, '0')),
    minute: Array.from({length: 60}, (_, i) => String(i).padStart(2, '0')),
    ampm: ['AM', 'PM']
};

function initScrollPicker(id, items) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = '';
    // Pad top and bottom to allow scrolling to first/last
    el.innerHTML += `<div style="height: 43px;"></div>`;
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'scroll-picker-item';
        div.dataset.value = item;
        div.textContent = item;
        el.appendChild(div);
    });
    el.innerHTML += `<div style="height: 43px;"></div>`;

    let scrollTimeout;
    el.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            updateActiveScrollItem(el);
            syncWheelsToRaw();
        }, 100);
    });
    
    // Click to select
    el.addEventListener('click', (e) => {
        if (e.target.classList.contains('scroll-picker-item')) {
            setScrollPickerValue(el, e.target.dataset.value);
        }
    });
}

function updateActiveScrollItem(el) {
    const items = el.querySelectorAll('.scroll-picker-item');
    const centerPosition = el.scrollTop + (el.clientHeight / 2);
    let closestItem = null;
    let minDiff = Infinity;
    
    items.forEach(item => {
        item.classList.remove('active');
        const itemCenter = item.offsetTop + (item.offsetHeight / 2) - el.offsetTop;
        const diff = Math.abs(itemCenter - centerPosition);
        if (diff < minDiff) {
            minDiff = diff;
            closestItem = item;
        }
    });
    if (closestItem) closestItem.classList.add('active');
}

function setScrollPickerValue(el, val) {
    if (!el || !val) return;
    const items = el.querySelectorAll('.scroll-picker-item');
    for (let item of items) {
        if (item.dataset.value === val) {
            el.scrollTo({
                top: item.offsetTop - el.offsetTop - (el.clientHeight / 2) + (item.offsetHeight / 2),
                behavior: 'smooth'
            });
            setTimeout(() => updateActiveScrollItem(el), 300);
            return;
        }
    }
}

function syncWheelsToRaw() {
    const rawInput = document.getElementById('edit-date-raw');
    if (!rawInput) return;
    
    const getVal = (id) => {
        const el = document.getElementById(id);
        if(!el) return '00';
        const active = el.querySelector('.active');
        if (active) return active.dataset.value;
        const items = el.querySelectorAll('.scroll-picker-item');
        if (items.length > 0) return items[0].dataset.value;
        return '00';
    };
    
    const y = getVal('picker-year');
    const m = getVal('picker-month');
    const d = getVal('picker-day');
    
    let hStr = getVal('picker-hour');
    const mi = getVal('picker-minute');
    const ap = getVal('picker-ampm');
    
    let h = parseInt(hStr, 10);
    if (ap === 'PM' && h !== 12) h += 12;
    if (ap === 'AM' && h === 12) h = 0;
    
    const h24 = String(h).padStart(2, '0');
    
    if (y && m && d) {
        rawInput.value = `${y}-${m}-${d} ${h24}:${mi}:00`;
    }
}

function syncRawToWheels() {
    const rawInput = document.getElementById('edit-date-raw');
    if (!rawInput) return;
    const val = rawInput.value.trim();
    if (!val) return;
    
    // Parse YYYY-MM-DD HH:MM:SS
    const parts = val.split(/[^\d]+/);
    if (parts.length >= 3) {
        setScrollPickerValue(document.getElementById('picker-year'), parts[0]);
        setScrollPickerValue(document.getElementById('picker-month'), parts[1]);
        setScrollPickerValue(document.getElementById('picker-day'), parts[2]);
    }
    if (parts.length >= 5) {
        let h = parseInt(parts[3], 10);
        const m = parts[4];
        let ap = 'AM';
        if (h >= 12) {
            ap = 'PM';
            if (h > 12) h -= 12;
        }
        if (h === 0) h = 12;
        
        setScrollPickerValue(document.getElementById('picker-hour'), String(h).padStart(2, '0'));
        setScrollPickerValue(document.getElementById('picker-minute'), m);
        setScrollPickerValue(document.getElementById('picker-ampm'), ap);
    }
}

// Initialize pickers
if (document.getElementById('picker-day')) {
    initScrollPicker('picker-day', wheelData.day);
    initScrollPicker('picker-month', wheelData.month);
    initScrollPicker('picker-year', wheelData.year);
    initScrollPicker('picker-hour', wheelData.hour);
    initScrollPicker('picker-minute', wheelData.minute);
    initScrollPicker('picker-ampm', wheelData.ampm);
    
    const rawInput = document.getElementById('edit-date-raw');
    if (rawInput) {
        rawInput.addEventListener('change', syncRawToWheels);
        rawInput.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') syncRawToWheels();
        });
    }
}

// Override toggleDateEditor to sync raw to wheels upon opening
const originalToggleDateEditor = toggleDateEditor;
window.toggleDateEditor = function() {
    originalToggleDateEditor();
    const isHidden = elements.dateEditorContainer.classList.contains('hidden');
    if (!isHidden) {
        setTimeout(syncRawToWheels, 50); // Small delay to ensure display:flex is rendered so offsetTop works
    }
};
