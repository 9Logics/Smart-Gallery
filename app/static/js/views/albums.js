function loadAlbums() {
    elements.albumsGrid.innerHTML = `
        <div class="skeleton-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));">
            ${Array(8).fill('<div style="display: flex; flex-direction: column; gap: 8px;"><div class="skeleton-card" style="aspect-ratio: 1; border-radius: 16px;"></div><div class="skeleton-card" style="height: 16px; width: 70%; border-radius: 4px; margin-top: 4px;"></div><div class="skeleton-card" style="height: 12px; width: 40%; border-radius: 4px;"></div></div>').join('')}
        </div>
    `;
    
    API.getAlbums()
        .then(data => {
            state.albums = data;
            try {
                populateAlbumDropdowns();
                renderAlbums(data);
            } catch (err) {
                elements.albumsGrid.innerHTML = `<p style="color:red">Error rendering: ${err}</p>`;
                console.error("Albums rendering error", err);
            }
        })
        .catch(err => {
            elements.albumsGrid.innerHTML = `<p style="color:red">Fetch error: ${err}</p>`;
            console.error("Albums fetch error", err);
        });
}

function renderAlbums(albums) {
    if (!albums || albums.length === 0) {
        elements.albumsGrid.innerHTML = `
            <div class="empty-state">
                <i data-lucide="folder-open"></i>
                <p>No albums created yet. Click "New Album" to get started.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    elements.albumsGrid.innerHTML = '';
    albums.forEach(album => {
        const card = document.createElement('div');
        card.className = 'album-card';
        
        let coverImgHTML = `<div class="album-cover-placeholder"><i data-lucide="image"></i></div>`;
        if (album.cover_photo_path) {
            coverImgHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(album.cover_photo_path)}" alt="${album.name}">`;
        }
        
        card.style.position = 'relative';
          card.innerHTML = `
            <div class="album-cover">
                ${coverImgHTML}
            </div>
                <div class="album-count-badge" style="position: absolute; top: 12px; left: 12px; z-index: 10; background: rgba(0,0,0,0.6); color: white; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 500; backdrop-filter: blur(4px); pointer-events: none;">
                    ${(function() {
                        let text = [];
                        if (album.image_count > 0) text.push(`${album.image_count} photo${album.image_count === 1 ? '' : 's'}`);
                        if (album.video_count > 0) text.push(`${album.video_count} video${album.video_count === 1 ? '' : 's'}`);
                        if (text.length === 0) text.push('0 items');
                        return text.join(', ');
                    })()}
                </div>
                <div class="album-menu-container" style="position: absolute; top: 12px; right: 12px; z-index: 10;">
                    <button class="btn-icon album-menu-btn" title="Options" data-id="${album.id}" data-name="${album.name}">
                        <i data-lucide="more-vertical"></i>
                    </button>
                    <div class="dropdown-menu hidden" id="album-menu-${album.id}" style="right: 0; left: auto; top: calc(100% + 8px);">
                        <button class="dropdown-item rename-album-btn" data-id="${album.id}" data-name="${album.name}">
                            <i data-lucide="edit-2"></i> Rename Album
                        </button>
                        <button class="dropdown-item set-cover-btn" data-id="${album.id}">
                            <i data-lucide="image"></i> Set Cover Photo
                        </button>
                        <hr style="margin: 4px 0; border: none; border-top: 1px solid var(--border-color);">
                        <button class="dropdown-item delete-album-btn" data-id="${album.id}" style="color: #ef4444;">
                            <i data-lucide="trash-2"></i> Delete Album
                        </button>
                    </div>
                </div>
            <h3 style="margin-bottom: 5px; margin-top: 12px;">${album.name}</h3>
        `;
        
        // Options menu toggling
        const menuBtn = card.querySelector('.album-menu-btn');
        const menu = card.querySelector('.dropdown-menu');
        
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent opening album
            // Hide all other open menus
            document.querySelectorAll('.album-menu-container .dropdown-menu').forEach(m => {
                if (m !== menu) m.classList.add('hidden');
            });
            menu.classList.toggle('hidden');
        });
        
        const renameBtn = card.querySelector('.rename-album-btn');
        renameBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.add('hidden');
            openRenameAlbumModal(album.id, album.name);
        });
        
        const setCoverBtn = card.querySelector('.set-cover-btn');
        setCoverBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.add('hidden');
            openAlbumCoverModal(album.id);
        });
        
        const deleteAlbumBtn = card.querySelector('.delete-album-btn');
        deleteAlbumBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            menu.classList.add('hidden');
            if (await appConfirm(`Are you sure you want to delete the album "${album.name}"? The photos will NOT be deleted.`)) {
                fetch('/api/albums/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ album_id: album.id })
                })
                .then(res => res.json())
                .then(data => {
                    loadStaticData();
                    loadAlbums();
                })
                .catch(err => console.error('Error deleting album:', err));
            }
        });
        
        card.addEventListener('click', (e) => {
            if (e.target.closest('.album-menu-container')) return;
            if (window.openAlbumDetail) window.openAlbumDetail(album);
        });
        
        elements.albumsGrid.appendChild(card);
    });
    
    lucide.createIcons();
}

// Extracted openAlbumDetail function
window.openAlbumDetail = function(album) {
    if (typeof switchView === 'function') switchView('albums');
    
    // Animate transition
    elements.albumsListContainer.classList.add('hidden');
    elements.albumDetailContainer.classList.remove('hidden');
    
    elements.albumDetailContainer.classList.remove('album-detail-exit');
    elements.albumDetailContainer.classList.add('album-detail-enter');
    setTimeout(() => {
        elements.albumDetailContainer.classList.remove('album-detail-enter');
    }, 500);
    
    // Set title and context
    state.currentAlbumId = album.id;
    
    // Dynamic Font logic based on title
    const fonts = ['Titan One', 'Bebas Neue', 'Pacifico', 'Abril Fatface', 'Righteous', 'Outfit'];
    let hash = 0;
    for (let i = 0; i < album.name.length; i++) hash = album.name.charCodeAt(i) + ((hash << 5) - hash);
    const font = fonts[Math.abs(hash) % fonts.length];
    
    const heroTitle = document.getElementById('album-detail-hero-title');
    if (heroTitle) {
        heroTitle.style.fontFamily = `"${font}", sans-serif`;
        heroTitle.innerText = album.name;
        
        // Re-trigger title animation
        heroTitle.classList.remove('hero-title-enter');
        void heroTitle.offsetWidth; // Reflow
        heroTitle.classList.add('hero-title-enter');
    }
    
    const dateRangeEl = document.getElementById('album-detail-date-range');
    if (dateRangeEl) {
        dateRangeEl.classList.remove('hero-date-enter');
        void dateRangeEl.offsetWidth; // Reflow
        dateRangeEl.classList.add('hero-date-enter');
    }
    
    // Show sorting controls
    const sortingContainer = document.getElementById('sorting-container');
    const filterContainer = document.getElementById('filter-container');
    if (sortingContainer) sortingContainer.classList.remove('hidden');
    if (filterContainer) filterContainer.classList.remove('hidden');
    
    // Show loading state
    elements.albumDetailGrid.innerHTML = `
        <div class="skeleton-grid">
            ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
        </div>
    `;
    
    // We define a global function to allow sort re-fetching
    window.loadCurrentAlbumPhotos = function() {
        if (!state.currentAlbumId) return;
        fetch(`/api/photos?albums=${state.currentAlbumId}&sort=${state.sortBy}`)
            .then(res => res.json())
            .then(data => {
                state.lightboxPhotos = [...data];
                renderPhotosGrid(data, elements.albumDetailGrid);
                
                // Calculate Date Range
                const dateRangeEl = document.getElementById('album-detail-date-range');
                if (dateRangeEl) {
                    let dates = data.map(p => p.date_taken).filter(d => {
                        if (!d) return false;
                        if (d.startsWith('1980') || d.startsWith('1970')) return false;
                        return true;
                    });
                    dates.sort();
                    
                    if (dates.length > 0) {
                        const firstDate = new Date(dates[0]).toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
                        const lastDate = new Date(dates[dates.length - 1]).toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
                        dateRangeEl.innerText = firstDate === lastDate ? firstDate : `${firstDate} - ${lastDate}`;
                    } else {
                        dateRangeEl.innerText = 'No dates available';
                    }
                }
            })
            .catch(err => {
                elements.albumDetailGrid.innerHTML = `
                    <div class="empty-state">
                        <i data-lucide="alert-triangle"></i>
                        <p>Failed to load album photos.</p>
                    </div>
                `;
                if (window.lucide) window.lucide.createIcons();
            });
    };
    
    window.loadCurrentAlbumPhotos();
};

// Load People (Faces)
