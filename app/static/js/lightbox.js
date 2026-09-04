// Extracted Lightbox Logic

function openLightbox(path) {
    const index = state.lightboxPhotos.findIndex(p => p.path === path || p.file_path === path);
    if (index === -1) return;
    
    state.lightboxIndex = index;
    
    // Attempt to find the thumbnail in the grid for FLIP animation
    let startRect = null;
    const thumbImg = document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img, .story-grid-item[data-path="${CSS.escape(path)}"]`);
    if (thumbImg) {
        startRect = thumbImg.getBoundingClientRect();
        // Instantly display the thumbnail in the lightbox to prevent popping/flashing during flight
        elements.lightboxImg.src = thumbImg.src;
        elements.lightboxImg.style.opacity = '1';
        elements.lightboxImg.style.objectFit = 'cover';
        elements.lightboxImgBuffer.style.objectFit = 'cover';
    }
    
    elements.lightbox.classList.remove('hidden');
    
    initFilmstrip();

    
// Disable transition temporarily to prevent animate-on-mount bugs
    elements.lightboxSidebar.style.transition = 'none';

    // Sync the info panel class state before any layout bounds are calculated
    if (state.isLightboxInfoOpen) {
        elements.lightbox.classList.add('info-open');
        elements.lightboxSidebar.classList.remove('hidden');
        elements.lightboxSidebar.classList.add('open');
        elements.lightboxInfoToggle.style.backgroundColor = 'var(--accent-color)';
    } else {
        elements.lightbox.classList.remove('info-open');
        elements.lightboxSidebar.classList.add('hidden');
        elements.lightboxSidebar.classList.remove('open');
        elements.lightboxInfoToggle.style.backgroundColor = 'rgba(15, 22, 38, 0.6)';
    }

    void elements.lightboxSidebar.offsetWidth; // Force layout
    requestAnimationFrame(() => requestAnimationFrame(() => elements.lightboxSidebar.style.transition = ''));
    
    // Animate background overlay fade in
    elements.lightbox.style.animation = 'none';
    void elements.lightbox.offsetWidth;
    elements.lightbox.style.animation = 'modalFadeIn 0.25s ease forwards';
    
    const main = document.querySelector('.lightbox-main');
    const frame = document.getElementById('lightbox-morph-frame');
    const container = document.getElementById('lightbox-media-container');
    const sidebar = document.querySelector('.lightbox-sidebar');
    
    const disableAnim = localStorage.getItem('disableLightboxAnim') === 'true';
    
    if (startRect && frame && container && !disableAnim) {
        // --- FLIP Animation Engine ---
        
        // 1. Temporarily disable CSS transitions
        frame.style.transition = 'none';
        if (main) main.style.animation = 'none';
        
        // Ensure we don't start from 0x0
        frame.style.width = Math.max(10, startRect.width) + 'px';
        frame.style.height = Math.max(10, startRect.height) + 'px';
        
        // 3. Calculate translation vector from target center to thumbnail center
        const containerRect = container.getBoundingClientRect();
        const targetX = containerRect.left + containerRect.width / 2;
        const targetY = containerRect.top + containerRect.height / 2;
        
        const startX = startRect.left + startRect.width / 2;
        const startY = startRect.top + startRect.height / 2;
        
        const deltaX = startX - targetX;
        const deltaY = startY - targetY;
        
        // 4. Translate frame to perfectly overlay the thumbnail
        frame.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
        
        // Optional: Animate sidebar separately since main animation is disabled
        if (sidebar && state.isLightboxInfoOpen) {
            sidebar.style.animation = 'none';
            void sidebar.offsetWidth;
            sidebar.style.animation = 'lightboxSlideInRight 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards';
        }
        
        // 5. Force DOM reflow to lock in start state
        void frame.offsetWidth;
        
        // 6. Enable smooth transition for FLIP trajectory
        frame.style.transition = 'width 0.35s cubic-bezier(0.16, 1, 0.3, 1), height 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
        
        // 7. Fire target state in next animation frame to guarantee CSS engine picks up the transition
        requestAnimationFrame(() => {
            frame.style.transform = 'translate(0px, 0px)';
            renderLightboxPhoto();
        });
        
        // 8. Cleanup transitions after animation completes
        setTimeout(() => {
            frame.style.transition = ''; // Restore CSS default
            frame.style.transform = '';
            elements.lightboxImg.style.objectFit = '';
            elements.lightboxImgBuffer.style.objectFit = '';
            if (sidebar && state.isLightboxInfoOpen) sidebar.style.animation = '';
        }, 350);
        
    } else {
        // Fallback to basic spring animation if no thumbnail found (e.g. search result without grid)
        if (main && !disableAnim) {
            main.style.animation = 'none';
            void main.offsetWidth; 
            main.classList.add('lightbox-opening');
            setTimeout(() => main.classList.remove('lightbox-opening'), 350);
        }
        renderLightboxPhoto();
    }
}

function closeLightbox() {
    // Clear video states immediately
    if (state.videoLoadTimeout) clearTimeout(state.videoLoadTimeout);
    const spinner = document.getElementById('video-loading-spinner');
    const errMsg = document.getElementById('video-error-msg');
    if (spinner) spinner.classList.add('hidden');
    if (errMsg) errMsg.classList.add('hidden');
    elements.lightboxVideo.pause();
    const controlsContainer = document.getElementById('custom-video-controls-container');
    if (controlsContainer) controlsContainer.classList.add('hidden');

    const path = state.lightboxPhotos[state.lightboxIndex]?.path;
    const thumbImg = path ? document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img, .story-grid-item[data-path="${CSS.escape(path)}"]`) : null;
    
    if (thumbImg && localStorage.getItem('disableLightboxAnim') !== 'true') {
        const startRect = thumbImg.getBoundingClientRect();
        const frame = document.getElementById('lightbox-morph-frame');
        const container = document.getElementById('lightbox-media-container');
        
        // Ensure thumbnail is visible in viewport, if not, skip animation
        const isVisible = (startRect.top >= 0 && startRect.left >= 0 && startRect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && startRect.right <= (window.innerWidth || document.documentElement.clientWidth));
        
        if (frame && container && isVisible) {
            elements.lightbox.style.animation = 'modalFadeOut 0.3s ease forwards';
            
            const sidebar = document.querySelector('.lightbox-sidebar');
            if (sidebar && elements.lightbox.classList.contains('info-open')) {
                sidebar.style.animation = 'none';
                void sidebar.offsetWidth;
                sidebar.style.animation = 'lightboxSlideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards';
            }
            
            const containerRect = container.getBoundingClientRect();
            // Get current dimensions before mutating
            const currentW = frame.clientWidth;
            const currentH = frame.clientHeight;
            
            // Fix frame size explicitly so it can animate down
            frame.style.width = currentW + 'px';
            frame.style.height = currentH + 'px';
            
            const targetX = containerRect.left + containerRect.width / 2;
            const targetY = containerRect.top + containerRect.height / 2;
            
            const thumbX = startRect.left + startRect.width / 2;
            const thumbY = startRect.top + startRect.height / 2;
            
            const deltaX = thumbX - targetX;
            const deltaY = thumbY - targetY;
            
            elements.lightboxImg.style.objectFit = 'cover';
            elements.lightboxImgBuffer.style.objectFit = 'cover';
            
            // Force reflow
            void frame.offsetWidth;
            
            frame.style.transition = 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1), height 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            frame.style.width = startRect.width + 'px';
            frame.style.height = startRect.height + 'px';
            frame.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
            
            setTimeout(completeClose, 300);
            return;
        }
    }
    
    // Fallback: fade out
    elements.lightbox.style.animation = 'modalFadeOut 0.2s ease forwards';
    const sidebar = document.querySelector('.lightbox-sidebar');
    if (sidebar && elements.lightbox.classList.contains('info-open')) {
        sidebar.style.animation = 'none';
        void sidebar.offsetWidth;
        sidebar.style.animation = 'lightboxSlideOutRight 0.2s cubic-bezier(0.4, 0, 0.2, 1) forwards';
    }
    setTimeout(completeClose, 200);
}

function completeClose() {
    elements.lightbox.classList.add('hidden');
    elements.lightbox.classList.remove('info-open');
    elements.lightbox.style.animation = '';
    state.lightboxIndex = -1;
    resetZoom();
    
    elements.lightboxImg.src = '';
    elements.lightboxImgBuffer.src = '';
    elements.lightboxVideo.src = '';
    const wrapper = document.getElementById('custom-video-wrapper');
    if (wrapper) wrapper.classList.add('hidden');
    const controlsContainer = document.getElementById('custom-video-controls-container');
    if (controlsContainer) controlsContainer.classList.add('hidden');
    
    const frame = document.getElementById('lightbox-morph-frame');
    if (frame) {
        frame.style.transition = '';
        frame.style.transform = '';
        frame.style.width = '';
        frame.style.height = '';
    }
    elements.lightboxImg.style.objectFit = '';
    elements.lightboxImgBuffer.style.objectFit = '';

    const sidebar = document.querySelector('.lightbox-sidebar');
    if (sidebar) {
        sidebar.style.animation = '';
        sidebar.style.transition = '';
    }

}

function showPrevPhoto() {
    if (state.lightboxIndex > 0) {
        state.lightboxIndex--;
        state.lastNavTime = Date.now();
        renderLightboxPhoto('prev');
        updateFilmstripUI();
    }
}

function showNextPhoto() {
    if (state.lightboxIndex < state.lightboxPhotos.length - 1) {
        state.lightboxIndex++;
        state.lastNavTime = Date.now();
        renderLightboxPhoto('next');
        updateFilmstripUI();
    }
}

function toggleLightboxInfo() {
    state.isLightboxInfoOpen = !state.isLightboxInfoOpen;
    if (state.isLightboxInfoOpen) {
        elements.lightboxSidebar.classList.remove('hidden');
        elements.lightbox.classList.add('info-open');
        setTimeout(() => elements.lightboxSidebar.classList.add('open'), 10);
        elements.lightboxInfoToggle.style.backgroundColor = 'var(--accent-color)';
    } else {
        elements.lightboxSidebar.classList.remove('open');
        elements.lightbox.classList.remove('info-open');
        setTimeout(() => elements.lightboxSidebar.classList.add('hidden'), 300);
        elements.lightboxInfoToggle.style.backgroundColor = 'rgba(15, 22, 38, 0.6)';
    }
    
    // Invalidate map size after panel transitions
    setTimeout(() => {
        if (state.map) state.map.invalidateSize();
    }, 200);
}

function updateVolumeUI() {
    const video = elements.lightboxVideo;
    const muteBtn = document.getElementById('video-mute-btn');
    const volumeSlider = document.getElementById('video-volume');
    if (!video || !muteBtn || !volumeSlider) return;
    
    if (document.activeElement !== volumeSlider) {
        volumeSlider.value = video.muted ? 0 : video.volume;
    }

    const pct = (volumeSlider.value / 1) * 100;
    volumeSlider.style.background = `linear-gradient(to right, var(--accent-color) ${pct}%, rgba(255, 255, 255, 0.2) ${pct}%)`;

    let targetIcon = 'volume-2';
    if (video.muted || video.volume == 0) {
        targetIcon = 'volume-x';
    } else if (video.volume < 0.5) {
        targetIcon = 'volume-1';
    }

    if (muteBtn.dataset.currentIcon !== targetIcon) {
        muteBtn.innerHTML = `<i data-lucide="${targetIcon}" style="width:18px; height:18px;"></i>`;
        muteBtn.dataset.currentIcon = targetIcon;
        lucide.createIcons();
    }
}

function formatVideoTime(seconds) {
    if (isNaN(seconds) || seconds === Infinity) return "0:00";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    
    const parts = [];
    if (h > 0) parts.push(h);
    parts.push(h > 0 ? String(m).padStart(2, '0') : m);
    parts.push(String(s).padStart(2, '0'));
    return parts.join(':');
}

function formatPhotoDate(dateStr) {
    if (!dateStr) return 'Unknown date';
    try {
        const date = new Date(dateStr.replace(' ', 'T'));
        if (isNaN(date.getTime())) return dateStr;
        
        // Use device's native region/locale for completely localized date and time!
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        };
        return date.toLocaleString(undefined, options);
    } catch (e) {
        return dateStr;
    }
}

function renderLightboxMap(photo) {
    const mapSection = document.getElementById('photo-map').parentNode;
    
    function formatLocationSplit(placeName) {
        if (!placeName) return { address: 'Unknown Location', poi: 'Unknown' };
        const parts = placeName.split(',').map(p => p.trim());
        if (parts.length <= 1) return { address: placeName, poi: placeName };
        let poi = parts[0];
        if (/^\d+[A-Za-z]?$/.test(parts[0]) && parts.length > 1) {
            poi = parts[1];
        }
        return { address: placeName, poi: poi };
    }

    const topAddress = photo.full_address || photo.place_name || 'Unknown Location';
    const pillsContainer = document.getElementById('photo-location-pills');
    
    function renderPills() {
        const addressContainer = document.getElementById('photo-location-address');
        if (addressContainer) {
            addressContainer.style.display = 'block';
            addressContainer.innerText = topAddress;
        }

        if (!pillsContainer) return;
        pillsContainer.innerHTML = '';
        
        let pillText = photo.place_name || 'Unknown Location';
        if (pillText === 'Coordinates 0,0 error') pillText = 'Unknown Location';
        
        const pill = document.createElement('div');
        pill.style.cssText = 'background: rgba(255,255,255,0.08); padding: 4px 10px; border-radius: 12px; font-size: 12px; color: var(--text-main); cursor: pointer; display: flex; align-items: center; gap: 4px; transition: background 0.2s, transform 0.1s;';
        
        pill.onmouseenter = () => pill.style.background = 'rgba(255,255,255,0.15)';
        pill.onmouseleave = () => pill.style.background = 'rgba(255,255,255,0.08)';
        pill.onmousedown = () => pill.style.transform = 'scale(0.95)';
        pill.onmouseup = () => pill.style.transform = 'scale(1)';
        pill.title = 'Search for "' + pillText + '"';
        
        pill.innerHTML = `<i data-lucide="map-pin" style="width:12px; height:12px; fill:rgba(255,255,255,0.1);"></i> <span>${pillText}</span>`;
        
        if (pillText !== 'Unknown Location') {
            pill.onclick = () => {
                if (typeof state !== 'undefined' && state.filters) {
                    state.filters.search = pillText;
                    const searchInput = document.getElementById('search-input');
                    if (searchInput) {
                        searchInput.value = pillText;
                        const clearBtn = document.getElementById('clear-search-btn');
                        if (clearBtn) clearBtn.classList.remove('hidden');
                    }
                    closeLightbox();
                    if (typeof switchView === 'function') switchView('photos');
                    if (typeof applyFilters === 'function') applyFilters();
                }
            };
        } else {
            pill.style.cursor = 'default';
        }
        
        pillsContainer.appendChild(pill);
        if (typeof lucide !== 'undefined') lucide.createIcons({root: pillsContainer});
    }

    if (typeof L === 'undefined') {
        console.log("[WARNING] Leaflet JS library is not loaded.");
        document.getElementById('photo-map').style.display = 'none';
        renderPills();
        return;
    }
    
    if (photo.latitude !== null && photo.longitude !== null && !isNaN(photo.latitude) && !isNaN(photo.longitude)) {
        if (photo.latitude === 0 && photo.longitude === 0) {
            document.getElementById('photo-map').style.display = 'none';
            renderPills();
            return;
        }

        document.getElementById('photo-map').style.display = 'block';
        renderPills();
        
        // Timeout prevents leaflet sizing issue inside flex panels
        setTimeout(() => {
            try {
                if (!state.map) {
                    state.map = L.map('photo-map', {
                        zoomControl: false,
                        attributionControl: false
                    });
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(state.map);
                }
                
                const coords = [photo.latitude, photo.longitude];
                state.map.setView(coords, 13);
                
                if (state.mapMarker) {
                    state.mapMarker.setLatLng(coords);
                } else {
                    state.mapMarker = L.marker(coords).addTo(state.map);
                }
                
                // Force size recalculation to prevent gray tiles
                state.map.invalidateSize(true);
            } catch (err) {
                console.log("Failed to initialize Leaflet map:", err);
            }
        }, 300);
    } else {
        document.getElementById('photo-map').style.display = 'none';
        renderPills();
    }
}

function renderLightboxFaces(photoPath) {
    elements.lightboxFacesList.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;"></div>';
    
    // Determine if current lightbox item is a video
    const ext = photoPath.split('.').pop().toLowerCase();
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    
    // Update heading
    const heading = document.getElementById('lightbox-people-heading');
    if (heading) {
        heading.innerHTML = `<i data-lucide="users"></i> People in this ${isVideo ? 'Video' : 'Photo'}`;
        lucide.createIcons({ nodes: [heading] });
    }
    
    fetch(`/api/photo/faces/${encodeURIComponent(photoPath)}`)
        .then(res => res.json())
        .then(faces => {
            const section = elements.lightboxFacesList.closest('.sidebar-section');
            if (!faces || faces.length === 0) {
                if (section) section.style.display = 'none';
            } else {
                if (section) section.style.display = 'block';
                elements.lightboxFacesList.innerHTML = '';
                faces.forEach((face, index) => {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'face-crop-item-wrapper';
                    wrapper.style.animation = `fadeIn 0.3s ease-out ${index * 0.05}s both`;
                
                // For videos: use the person's cover face photo (their profile pic)
                // For photos: use the individual face crop from this specific photo
                const cropSrc = isVideo && face.cover_face_id
                    ? `/api/photo/crop/${face.cover_face_id}`
                    : `/api/photo/crop/${face.face_id}`;
                
                const isCover = (face.face_id === face.cover_face_id);
                const starStyle = isCover ? 'style="fill: #f59e0b; stroke: #f59e0b;"' : '';
                const starTitle = isCover ? 'Current cover photo' : 'Set as cover photo';
                
                // For videos: hide the star/cover button (not meaningful without a valid crop)
                const coverBtnHtml = isVideo ? '' : `
                        <button class="face-cover-btn btn-icon" ${starStyle} title="${starTitle}" data-face-id="${face.face_id}" data-person-id="${face.person_id}" style="width: 26px; height: 26px; border-radius: 50%; padding: 0; background: transparent;">
                            <i data-lucide="star" style="width: 14px; height: 14px;"></i>
                        </button>`;
                
                wrapper.innerHTML = `
                    <div class="face-crop-item">
                        <div class="face-crop-circle" title="Click to view all ${isVideo ? 'videos' : 'photos'}, double click to retag">
                            <img src="${cropSrc}" alt="Person photo">
                        </div>
                        <span class="face-crop-name" title="Double click to retag">${face.person_name}</span>
                    </div>
                    <div class="face-crop-actions" style="display: flex; gap: 4px; align-items: center;">
                        ${coverBtnHtml}
                        <button class="face-retag-btn btn-icon" title="Retag this person" data-face-id="${face.face_id}" style="width: 26px; height: 26px; border-radius: 50%; padding: 0; background: transparent;">
                            <i data-lucide="user-cog" style="width: 14px; height: 14px;"></i>
                        </button>
                        <button class="face-delete-btn btn-icon" title="Remove person tag" data-face-id="${face.face_id}" style="width: 26px; height: 26px; border-radius: 50%; padding: 0; background: transparent; color: var(--error-color);">
                            <i data-lucide="x" style="width: 14px; height: 14px;"></i>
                        </button>
                    </div>
                `;
                
                // Clicking filters by this person
                wrapper.querySelector('.face-crop-circle').addEventListener('click', (e) => {
                    if (e.detail === 1) {
                        state.clickTimeout = setTimeout(() => {
                            closeLightbox();
                            state.filters.people = [face.person_id];
                            applyFilters();
                        }, 250);
                    }
                });
                
                // Double click triggers individual face retag prompt
                wrapper.querySelector('.face-crop-circle').addEventListener('dblclick', () => {
                    clearTimeout(state.clickTimeout);
                    editFaceTagPrompt(face.face_id, face.person_name, photoPath);
                });
                
                wrapper.querySelector('.face-crop-name').addEventListener('dblclick', () => {
                    editFaceTagPrompt(face.face_id, face.person_name, photoPath);
                });
                
                // Set cover trigger (photos only)
                const coverBtn = wrapper.querySelector('.face-cover-btn');
                if (coverBtn) {
                    coverBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        setPersonCoverFace(face.person_id, face.face_id, photoPath);
                    });
                }
                
                // Retag trigger
                wrapper.querySelector('.face-retag-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    editFaceTagPrompt(face.face_id, face.person_name, photoPath);
                });
                
                // Delete face trigger
                wrapper.querySelector('.face-delete-btn').addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (await appConfirm(`Remove ${face.person_name} from this ${isVideo ? 'video' : 'photo'}?`)) {
                        deleteFaceLabel(face.face_id, photoPath);
                    }
                });
                
                elements.lightboxFacesList.appendChild(wrapper);
                });
                lucide.createIcons();
            }
        })
        .catch(e => {
            elements.lightboxFacesList.innerHTML = `<p style="font-size:12.5px;color:var(--error-color);">Error loading people</p>`;
        });
}

function renderLightboxAlbums(photoPath) {
    elements.lightboxAlbumsList.innerHTML = '';
    
    // Query albums mapping for this photo path
    const matchedAlbums = state.albums.filter(album => {
        // Match through photo listings in albums list loaded initially
        // Wait, it is safer to fetch it or check state.albums details
        // To avoid roundtrips, we can fetch all mappings or we can just fetch specifically
        // Actually, we can get list of albums this photo belongs to by comparing path
        // Since state.albums contains photos count, it doesn't list paths. Let's make a quick fetch.
        return false;
    });
    
    // Let's implement a fetch route if we want accurate details, or we can queries from albums list
    // Actually, we can search state.albums since we don't have paths there. Let's fetch!
    fetch(`/api/photos?albums=`) // No, let's fetch list of albums specifically for this photo path:
    // Better: we can check backend albums endpoint.
    // Wait, let's just make it simple: let the backend return the list of albums for this photo.
    // Since we didn't write an endpoint for that, we can simply fetch `/api/albums` and we can
    // query or filter. Wait, a simpler way is to query `/api/albums` and when adding/removing, 
    // we keep track of mappings in a simpler local state if possible, or fetch.
    // Let's call `/api/albums` and list the ones matching this photo.
    // Since we want virtual albums list in lightbox, let's make a call to a small helper in backend:
    // Let's check which albums contain this photo.
    // We can fetch `/api/albums` and then check mapping. Or we can just fetch and render.
    // Let's check: we didn't add a specific endpoint to list albums by photo, but we can do a call:
    // Let's fetch all albums and check.
    // Wait, let's look at the database. In backend, we can query album names for this photo in a query.
    // We don't have a direct endpoint for albums-by-photo, but we can query `/api/albums` and find out.
    // Actually, we can fetch `/api/albums` and then on the backend we can return album listings.
    // Wait! Let's write a small API call in app.py to get albums for a photo, OR we can query `/api/albums` and in our Javascript we can fetch them.
    // Let's check if we can query them:
    fetch('/api/albums')
        .then(res => res.json())
        .then(allAlbums => {
            state.albums = allAlbums;
            populateAlbumDropdowns();
            
            // To find which albums contain this photo:
            // Since we can query `/api/photos` filter by album, that's one way, but it's too slow.
            // A simpler way: let's query the backend with a fetch.
            // Wait, we can fetch `/api/photos?albums=${a.id}` for each, or we can just list them.
            // Let's write a small endpoint in `app.py` or check if we can just fetch `/api/albums` and filter on backend.
            // Actually, in `app.py` we can write a quick endpoint if needed, but since we already created `app.py`, 
            // is there another way? Yes! We can query:
            // Let's see: `album_photos` has `album_id` and `photo_path`.
            // We can just add a quick helper endpoint to fetch albums for a photo.
            // Wait! Did we write an endpoint for that? No. But we can fetch `/api/albums` and check.
            // Wait, let's edit `app.py` to add `@app.route('/api/photo/albums/<path:photo_path>')`
            // Let's do that! That is extremely clean and reliable.
            // But wait, can we do it without changing `app.py`? We can query `/api/albums` and in the backend it lists album info.
            // Let's add the endpoint to `app.py` in a separate edit, or just write the JS fetching.
            // Let's look at how we can edit `app.py` later. For now, in JS, let's request the photo albums:
            fetch(`/api/albums`)
                .then(res => res.json())
                .then(albums => {
                    // Let's query from backend:
                    // Wait, we can query:
                    fetch(`/api/photos?albums=`)
                    // Let's write the fetch to `/api/photo/albums/` which we will add to `app.py` in a moment!
                    // Path formatting:
                    const encodedPath = encodeURIComponent(photoPath);
                    fetch(`/api/photo/albums/${encodedPath}`)
                        .then(res => {
                            if (!res.ok) return [];
                            return res.json();
                        })
                        .then(matchedAlbums => {
                            if (!matchedAlbums || matchedAlbums.length === 0) {
                                elements.lightboxAlbumsList.innerHTML = '<p style="font-size:12.5px;color:var(--text-muted); animation: fadeIn 0.3s ease-out;">Not in any albums</p>';
                            } else {
                                elements.lightboxAlbumsList.innerHTML = '';
                                matchedAlbums.forEach((album, index) => {
                                    const chip = document.createElement('div');
                                    chip.className = 'album-chip';
                                    chip.style.animation = `fadeIn 0.3s ease-out ${index * 0.05}s both`;
                                    chip.innerHTML = `
                                        <span>${album.name}</span>
                                        <button title="Remove from album"><i data-lucide="x"></i></button>
                                    `;
                                
                                chip.querySelector('button').addEventListener('click', () => {
                                    removePhotoFromAlbum(album.id, photoPath);
                                });
                                
                                elements.lightboxAlbumsList.appendChild(chip);
                                });
                                lucide.createIcons();
                            }
                        })
                        .catch(() => {
                            elements.lightboxAlbumsList.innerHTML = '<p style="font-size:12.5px;color:var(--error-color);">Error loading albums</p>';
                        });
                })
                .catch(() => {
                    elements.lightboxAlbumsList.innerHTML = '<p style="font-size:12.5px;color:var(--error-color);">Error loading albums</p>';
                });
        })
        .catch(() => {
            elements.lightboxAlbumsList.innerHTML = '<p style="font-size:12.5px;color:var(--error-color);">Error loading albums</p>';
        });
}
// Filmstrip Logic
const filmstripToggleBtn = document.getElementById('lightbox-filmstrip-toggle');
if (filmstripToggleBtn) {
    filmstripToggleBtn.addEventListener('click', toggleFilmstrip);
}

function toggleFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        updateFilmstripUI(true); // Jump to center when opened
    } else {
        container.classList.add('hidden');
    }
}

function initFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    // Disconnect previous observer if it exists
    if (window.filmstripObserver) {
        window.filmstripObserver.disconnect();
    }
    
    container.innerHTML = '';
    
    // Create new Intersection Observer for lazy loading
    window.filmstripObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    }, { root: container, rootMargin: '300px 0px' });
    
    state.lightboxPhotos.forEach((photo, index) => {
        const wrapper = document.createElement('div');
        wrapper.dataset.index = index;
        wrapper.style.height = '60px';
        wrapper.style.minWidth = '40px';
        wrapper.style.position = 'relative';
        wrapper.style.cursor = 'pointer';
        wrapper.style.flexShrink = '0';
        wrapper.style.borderRadius = '8px';
        wrapper.style.overflow = 'hidden';
        wrapper.style.border = index === state.lightboxIndex ? '2px solid white' : '2px solid transparent';
        wrapper.style.opacity = index === state.lightboxIndex ? '1' : '0.5';
        wrapper.style.transition = 'all 0.2s';
        
        wrapper.onmouseover = () => { wrapper.style.opacity = '1'; };
        wrapper.onmouseout = () => { if (parseInt(wrapper.dataset.index) !== state.lightboxIndex) wrapper.style.opacity = '0.5'; };
        
        wrapper.addEventListener('click', () => {
            if (state.lightboxIndex === index) return; // ignore if already active
            state.lightboxIndex = index;
            if (typeof renderLightboxPhoto === 'function') renderLightboxPhoto();
            updateFilmstripUI();
        });
        
        const thumb = document.createElement('img');
        // Lazy load the thumbnail image
        thumb.dataset.src = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}?s=${photo.size || 0}`;
        thumb.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; // 1x1 placeholder
        thumb.style.height = '100%';
        thumb.style.width = 'auto'; // natural aspect ratio
        thumb.style.objectFit = 'cover';
        thumb.style.display = 'block';
        
        wrapper.appendChild(thumb);
        window.filmstripObserver.observe(thumb);
        
        if (photo.type === 'video' || photo.path.match(/\.(mp4|mov|avi|mkv|webm)$/i)) {
            const playIcon = document.createElement('div');
            playIcon.innerHTML = '<i data-lucide="play" style="fill: white; width: 14px; height: 14px; color: white;"></i>';
            playIcon.style.position = 'absolute';
            playIcon.style.top = '50%';
            playIcon.style.left = '50%';
            playIcon.style.transform = 'translate(-50%, -50%)';
            playIcon.style.background = 'rgba(0,0,0,0.5)';
            playIcon.style.borderRadius = '50%';
            playIcon.style.padding = '6px';
            playIcon.style.display = 'flex';
            playIcon.style.justifyContent = 'center';
            playIcon.style.alignItems = 'center';
            playIcon.style.backdropFilter = 'blur(4px)';
            wrapper.appendChild(playIcon);
        }
        
        container.appendChild(wrapper);
    });
    
    if (window.lucide) {
        lucide.createIcons({root: container});
    }
    
    updateFilmstripUI(true);
}

function updateFilmstripUI(instant = false) {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    const children = container.children;
    for (let i = 0; i < children.length; i++) {
        const wrapper = children[i];
        if (i === state.lightboxIndex) {
            wrapper.style.border = '2px solid white';
            wrapper.style.opacity = '1';
        } else {
            wrapper.style.border = '2px solid transparent';
            wrapper.style.opacity = '0.5';
        }
    }
    
    if (!container.classList.contains('hidden')) {
        const selected = container.children[state.lightboxIndex];
        if (selected) {
            selected.scrollIntoView({ behavior: instant ? 'auto' : 'smooth', inline: 'center', block: 'nearest' });
        }
    }
}


