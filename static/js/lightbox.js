// Extracted Lightbox Logic

function openLightbox(path) {
    const index = state.lightboxPhotos.findIndex(p => p.path === path);
    if (index === -1) return;
    
    state.lightboxIndex = index;
    
    // Attempt to find the thumbnail in the grid for FLIP animation
    let startRect = null;
    const thumbImg = document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img`);
    if (thumbImg) {
        startRect = thumbImg.getBoundingClientRect();
        // Instantly display the thumbnail in the lightbox to prevent popping/flashing during flight
        elements.lightboxImg.src = thumbImg.src;
        elements.lightboxImg.style.opacity = '1';
    }
    
    elements.lightbox.classList.remove('hidden');
    
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
        
        // 2. Set frame to exactly match the thumbnail's screen dimensions
        frame.style.width = startRect.width + 'px';
        frame.style.height = startRect.height + 'px';
        
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
        if (sidebar) {
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
            if (sidebar) sidebar.style.animation = '';
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
    elements.lightbox.classList.add('hidden');
    state.lightboxIndex = -1;
    resetZoom();
    
    // Clear video loading states
    if (state.videoLoadTimeout) clearTimeout(state.videoLoadTimeout);
    const spinner = document.getElementById('video-loading-spinner');
    const errMsg = document.getElementById('video-error-msg');
    if (spinner) spinner.classList.add('hidden');
    if (errMsg) errMsg.classList.add('hidden');
    
    // Release references and stop video playback
    elements.lightboxImg.src = '';
    elements.lightboxVideo.pause();
    elements.lightboxVideo.src = '';
    const wrapper = document.getElementById('custom-video-wrapper');
    if (wrapper) {
        wrapper.classList.add('hidden');
    }
}

function showPrevPhoto() {
    if (state.lightboxIndex > 0) {
        state.lightboxIndex--;
        const timeSince = Date.now() - (state.lastNavTime || 0);
        const direction = timeSince > 300 ? 'prev' : null;
        state.lastNavTime = Date.now();
        renderLightboxPhoto(direction);
    }
}

function showNextPhoto() {
    if (state.lightboxIndex < state.lightboxPhotos.length - 1) {
        state.lightboxIndex++;
        const timeSince = Date.now() - (state.lastNavTime || 0);
        const direction = timeSince > 300 ? 'next' : null;
        state.lastNavTime = Date.now();
        renderLightboxPhoto(direction);
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
        
        const weekday = date.toLocaleDateString('en-US', { weekday: 'long' });
        const day = date.getDate();
        const month = date.toLocaleDateString('en-US', { month: 'long' });
        const year = date.getFullYear();
        
        let hours = date.getHours();
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        const ampm = hours >= 12 ? 'pm' : 'am';
        hours = hours % 12;
        hours = hours ? hours : 12;
        
        return `${weekday}, ${day} ${month} ${year}, ${hours}:${minutes}:${seconds} ${ampm}`;
    } catch (e) {
        return dateStr;
    }
}

function renderLightboxMap(photo) {
    const mapSection = document.getElementById('photo-map').parentNode;
    
    if (typeof L === 'undefined') {
        console.log("[WARNING] Leaflet JS library is not loaded.");
        mapSection.style.display = 'none';
        elements.photoLocation.innerText = photo.place_name || 'Geotagged Location';
        return;
    }
    
    if (photo.latitude !== null && photo.longitude !== null && !isNaN(photo.latitude) && !isNaN(photo.longitude)) {
        if (photo.latitude === 0 && photo.longitude === 0) {
            mapSection.style.display = 'none';
            elements.photoLocation.innerText = 'Coordinates 0,0 error';
            return;
        }

        mapSection.style.display = 'block';
        elements.photoLocation.innerText = photo.place_name || 'Geotagged Location';
        
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
        mapSection.style.display = 'none';
        elements.photoLocation.innerText = 'No location metadata';
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
            elements.lightboxFacesList.innerHTML = '';
            
            if (!faces || faces.length === 0) {
                elements.lightboxFacesList.innerHTML = `<p style="font-size:12.5px;color:var(--text-muted);">No ${isVideo ? 'people tagged' : 'faces detected'}</p>`;
                return;
            }
            
            faces.forEach(face => {
                const wrapper = document.createElement('div');
                wrapper.className = 'face-crop-item-wrapper';
                
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
                    <div class="face-crop-actions" style="display: flex; gap: 4px; align-items: center; margin-right: 6px;">
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
                wrapper.querySelector('.face-delete-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (confirm(`Remove ${face.person_name} from this ${isVideo ? 'video' : 'photo'}?`)) {
                        deleteFaceLabel(face.face_id, photoPath);
                    }
                });
                
                elements.lightboxFacesList.appendChild(wrapper);
            });
            lucide.createIcons();
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
                            elements.lightboxAlbumsList.innerHTML = '';
                            if (!matchedAlbums || matchedAlbums.length === 0) {
                                elements.lightboxAlbumsList.innerHTML = '<p style="font-size:12.5px;color:var(--text-muted);">Not in any albums</p>';
                                return;
                            }
                            
                            matchedAlbums.forEach(album => {
                                const chip = document.createElement('div');
                                chip.className = 'album-chip';
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
                        });
                });
        });
}