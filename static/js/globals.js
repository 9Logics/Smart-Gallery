
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
    lightboxImg: document.getElementById('lightbox-img-active'),
    lightboxImgBuffer: document.getElementById('lightbox-img-buffer'),
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
    cancelScanBtn: document.getElementById('cancel-scan-btn'),
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
    squareGridLayout: document.getElementById('square-grid-layout'),
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
