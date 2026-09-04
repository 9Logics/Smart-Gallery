/**
 * Story Viewer Logic (Second Lightbox)
 * Handles auto-advancing, segmented progress bars, cross-card navigation, and grid view
 */

window.storyState = {
    isActive: false,
    cards: [],          // Array of { title, subtitle, photos: [] }
    cardIndex: 0,
    mediaIndex: 0,
    isPaused: false,
    timerId: null,
    duration: 6000,     // 6 seconds for images
    idleTimer: null,
    muted: true
};

window.openStoryViewer = function(cards, startCardIndex = 0) {
    if (!cards || cards.length === 0 || !cards[startCardIndex]) return;
    
    window.storyState.cards = cards;
    window.storyState.cardIndex = startCardIndex;
    window.storyState.mediaIndex = 0;
    window.storyState.isActive = true;
    window.storyState.isPaused = false;
    window.storyState.muted = true; // Default mute for stories
    
    const modal = document.getElementById('story-lightbox-modal');
    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.add('active'), 10);
    
    const mainArea = document.getElementById('story-media-container');
    const prevCard = document.getElementById('story-prev-card');
    const nextCard = document.getElementById('story-next-card');
    const activeWrapper = document.getElementById('story-active-card-wrapper');
    if (prevCard && mainArea && prevCard.parentElement !== mainArea) {
        mainArea.insertBefore(prevCard, activeWrapper);
        mainArea.appendChild(nextCard);
    }
    
    document.addEventListener('mousemove', handleStoryMouseMove);
    document.addEventListener('keydown', handleStoryKeyDown);
    
    renderStoryMedia('initial');
};

function closeStoryViewer() {
    window.storyState.isActive = false;
    clearStoryTimer();
    clearTimeout(window.storyState.idleTimer);
    
    const modal = document.getElementById('story-lightbox-modal');
    modal.classList.remove('active');
    
    const video = document.getElementById('story-video');
    video.pause();
    video.src = '';
    
    document.removeEventListener('mousemove', handleStoryMouseMove);
    document.removeEventListener('keydown', handleStoryKeyDown);
    
    setTimeout(() => {
        modal.classList.add('hidden');
        document.getElementById('story-grid-view').classList.remove('active');
    }, 300);
}

function handleStoryMouseMove() {
    const uiLayer = document.querySelector('.story-ui-layer');
    if (uiLayer) uiLayer.classList.remove('idle');
    
    const overlays = document.querySelector('.story-card-overlays');
    if (overlays) overlays.classList.remove('idle');
    
    clearTimeout(window.storyState.idleTimer);
    window.storyState.idleTimer = setTimeout(() => {
        if (!window.storyState.isPaused) {
            if (uiLayer) uiLayer.classList.add('idle');
            if (overlays) overlays.classList.add('idle');
        }
    }, 2000);
}


function toggleStoryPause() {
    const state = window.storyState;
    state.isPaused = !state.isPaused;
    
    const vidEl = document.getElementById('story-video');
    const titleEl = document.querySelector('.story-card-center-title');
    const indicator = document.getElementById('story-play-indicator');
    const icon = state.isPaused ? 'play' : 'pause';
    
    if (indicator) {
        indicator.innerHTML = `<i data-lucide="${icon}"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [indicator] });
        indicator.classList.add('active');
        setTimeout(() => indicator.classList.remove('active'), 600);
    }
    
    const playBtn = document.getElementById('story-play-pause-btn');
    if (playBtn) {
        playBtn.innerHTML = `<i data-lucide="${icon}"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [playBtn] });
    }

    if (state.isPaused) {
        clearStoryTimer();
        if (!vidEl.classList.contains('hidden')) vidEl.pause();
        if (titleEl) titleEl.style.opacity = '1';
        const layer = document.querySelector('.story-ui-layer');
        if (layer) layer.classList.remove('idle');
    } else {
        startStoryTimer();
        if (!vidEl.classList.contains('hidden')) vidEl.play();
        setTimeout(fadeOutTitle, 2000);
        handleStoryMouseMove();
    }
}

function toggleStoryMute() {
    const state = window.storyState;
    state.muted = !state.muted;
    const vidEl = document.getElementById('story-video');
    vidEl.muted = state.muted;
    
    const muteBtn = document.getElementById('story-mute-btn');
    muteBtn.innerHTML = state.muted ? '<i data-lucide="volume-x"></i>' : '<i data-lucide="volume-2"></i>';
    if (window.lucide) window.lucide.createIcons({ nodes: [muteBtn] });
}

function openStoryGrid() {
    const state = window.storyState;
    const card = state.cards[state.cardIndex];
    const gridView = document.getElementById('story-grid-view');
    const content = document.getElementById('story-grid-content');
    
    document.getElementById('story-grid-title').innerText = card.title || 'All Media';
    content.innerHTML = '';
    
    card.photos.forEach((p, idx) => {
        const item = document.createElement('img');
        item.className = 'story-grid-item';
        let path = p.path || p.file_path || '';
        item.dataset.path = path;
        item.src = `/api/photo/thumbnail/${encodeURIComponent(path)}`;
        item.onclick = () => {
            if (typeof state !== 'undefined' && typeof openLightbox === 'function') {
                state.lightboxPhotos = card.photos;
                openLightbox(path);
            } else if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(path);
            }
        };
        content.appendChild(item);
    });
    
    clearStoryTimer();
    
    // Ensure story is paused
    const vidEl = document.getElementById('story-video');
    if (vidEl && !vidEl.paused) vidEl.pause();
    window.storyState.isPaused = true;
    
    const indicator = document.getElementById('story-play-indicator');
    if (indicator) {
        indicator.innerHTML = `<i data-lucide="play"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [indicator] });
    }
    const playBtn = document.getElementById('story-play-pause-btn');
    if (playBtn) {
        playBtn.innerHTML = `<i data-lucide="play"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [playBtn] });
    }
    
    gridView.classList.remove('hidden');
    // slight delay for transition
    setTimeout(() => gridView.classList.add('active'), 10);
}

function closeStoryGrid() {
    const gridView = document.getElementById('story-grid-view');
    gridView.classList.remove('active');
    setTimeout(() => {
        gridView.classList.add('hidden');
        if (!window.storyState.isPaused) startStoryTimer();
    }, 400);
}

function handleStoryKeyDown(e) {
    if (!window.storyState.isActive) return;
    if (document.getElementById('story-grid-view').classList.contains('active')) {
        if (e.key === 'Escape') closeStoryGrid();
        return;
    }
    if (e.key === 'ArrowRight') nextStoryMedia();
    else if (e.key === 'ArrowLeft') prevStoryMedia();
    else if (e.key === 'Escape') closeStoryViewer();
    else if (e.key === ' ') { e.preventDefault(); toggleStoryPause(); }
}

function renderStoryMedia(direction = 'none') {
    const state = window.storyState;
    if (state.cardIndex < 0 || state.cardIndex >= state.cards.length) return closeStoryViewer();
    
    const card = state.cards[state.cardIndex];
    if (state.mediaIndex < 0 || state.mediaIndex >= card.photos.length) {
        state.cardIndex++;
        state.mediaIndex = 0;
        return renderStoryMedia('nextCard');
    }
    
    const wrapper = document.getElementById('story-active-card-wrapper');
    const prevCardEl = document.getElementById('story-prev-card');
    const nextCardEl = document.getElementById('story-next-card');
    
    // Disable transitions for snapping
    if (wrapper) wrapper.classList.add('no-transition');
    if (prevCardEl) prevCardEl.classList.add('no-transition');
    if (nextCardEl) nextCardEl.classList.add('no-transition');
    
    if (wrapper) wrapper.className = 'story-active-card story-card-active no-transition';
    if (prevCardEl) prevCardEl.className = 'story-preview-card story-card-prev no-transition';
    if (nextCardEl) nextCardEl.className = 'story-preview-card story-card-next no-transition';
    
    if (wrapper) wrapper.offsetHeight; // reflow
    
    if (wrapper) wrapper.classList.remove('no-transition');
    if (prevCardEl) prevCardEl.classList.remove('no-transition');
    if (nextCardEl) nextCardEl.classList.remove('no-transition');
    
    const photo = card.photos[state.mediaIndex];
    let path = photo.path || photo.file_path || '';
    path = path.replace(/\\/g, '/');
    const ext = path.split('.').pop().toLowerCase();
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    
    const imgEl = document.getElementById('story-img');
    const vidEl = document.getElementById('story-video');
    
    imgEl.classList.add('hidden');
    vidEl.classList.add('hidden');
    
    const seekContainer = document.getElementById('story-video-seek-container');
    const spacer = document.getElementById('story-spacer');
    const muteBtn = document.getElementById('story-mute-btn');
    if (seekContainer) seekContainer.classList.toggle('hidden', !isVideo);
    if (spacer) spacer.classList.toggle('hidden', isVideo);
    if (muteBtn) {
        muteBtn.classList.toggle('hidden', !isVideo);
        muteBtn.innerHTML = window.storyState.muted ? '<i data-lucide="volume-x"></i>' : '<i data-lucide="volume-2"></i>';
        if (window.lucide) window.lucide.createIcons({ nodes: [muteBtn] });
    }
    
    if (isVideo) {
        vidEl.src = `/api/photo/file/${encodeURIComponent(path)}`;
        vidEl.muted = state.muted;
        vidEl.classList.remove('hidden');
        vidEl.onended = nextStoryMedia;
        vidEl.play().catch(e => {});
        clearStoryTimer(); // video relies on onended
    } else {
        imgEl.src = `/api/photo/file/${encodeURIComponent(path)}`;
        imgEl.classList.remove('hidden');
        if (!state.isPaused) startStoryTimer();
    }
    
    // Progress bars
    const container = document.getElementById('story-progress-container');
    container.innerHTML = '';
    card.photos.forEach((p, i) => {
        const seg = document.createElement('div');
        seg.className = 'story-progress-segment';
        const fill = document.createElement('div');
        fill.className = 'story-progress-fill';
        
        if (i < state.mediaIndex) fill.style.width = '100%';
        else if (i === state.mediaIndex) {
            fill.style.width = '0%';
            if (!isVideo) {
                fill.style.transition = state.isPaused ? 'none' : 'width 6s linear';
                if (!state.isPaused) setTimeout(() => fill.style.width = '100%', 50);
            } else {
                vidEl.ontimeupdate = () => {
                    if (vidEl.duration) {
                        const pct = (vidEl.currentTime / vidEl.duration * 100);
                        fill.style.width = pct + '%';
                        const seekEl = document.getElementById('story-video-seek');
                        if (seekEl && !seekEl.isDragging) seekEl.value = pct;
                    }
                };
            }
        }
        seg.appendChild(fill);
        container.appendChild(seg);
    });
    
    // Text overlays
    const tTitle = document.getElementById('story-bar-title');
    if (tTitle) tTitle.innerText = card.title || '';
    
    const dDate = new Date(photo.date_taken || photo.created_at || photo.date);
    
    const tSub = document.getElementById('story-top-subtitle');
    if (tSub) {
        if (!isNaN(dDate)) {
            tSub.innerText = dDate.getFullYear().toString();
        } else {
            tSub.innerText = card.subtitle || '';
        }
    }
    
    const tDate = document.getElementById('story-date-text');
    if (tDate) {
        tDate.innerText = ''; // Clear out the full date
    }
    
    const hTitle = document.getElementById('story-title');
    if (hTitle) hTitle.innerText = card.title || '';
    const hSub = document.getElementById('story-subtitle');
    if (hSub) {
        if (!isNaN(dDate)) {
            hSub.innerText = dDate.getFullYear().toString();
        } else {
            hSub.innerText = card.subtitle || '';
        }
    }
    
    const centerTitle = document.querySelector('.story-card-center-title');
    if (centerTitle) {
        if (state.mediaIndex === 0) {
            centerTitle.style.display = 'block';
            centerTitle.style.opacity = '1';
            setTimeout(fadeOutTitle, 3000);
        } else {
            centerTitle.style.display = 'none';
        }
    }
    
    // Preview Cards Setup
    
    if (state.cardIndex < state.cards.length - 1) {
        const nextCard = state.cards[state.cardIndex + 1];
        let p = nextCard.photos[0].path || nextCard.photos[0].file_path || '';
        nextCardEl.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent((p || '').replace(/\\\\/g, '/'))}")`;
        const nxTitle = document.getElementById('story-next-title');
        if (nxTitle) nxTitle.innerText = nextCard.title || '';
        nextCardEl.classList.remove('hidden');
    } else {
        if (nextCardEl) nextCardEl.classList.add('hidden');
    }
    
    if (state.cardIndex > 0) {
        const prevCard = state.cards[state.cardIndex - 1];
        let p = prevCard.photos[0].path || prevCard.photos[0].file_path || '';
        prevCardEl.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent((p || '').replace(/\\\\/g, '/'))}")`;
        const prTitle = document.getElementById('story-prev-title');
        if (prTitle) prTitle.innerText = prevCard.title || '';
        prevCardEl.classList.remove('hidden');
    } else {
        if (prevCardEl) prevCardEl.classList.add('hidden');
    }
}

function fadeOutTitle() {
    if (!window.storyState.isPaused && window.storyState.isActive) {
        const el = document.querySelector('.story-card-center-title');
        if (el) el.style.opacity = '0';
    }
}


let isTransitioning = false;

function nextStoryMedia() {
    if (isTransitioning) return;
    const state = window.storyState;
    
    if (state.mediaIndex >= state.cards[state.cardIndex].photos.length - 1) {
        if (state.cardIndex >= state.cards.length - 1) return closeStoryViewer();
        
        isTransitioning = true;
        const active = document.getElementById('story-active-card-wrapper');
        const nextCard = document.getElementById('story-next-card');
        const prevCard = document.getElementById('story-prev-card');
        
        active.className = 'story-active-card story-card-prev';
        if (nextCard) nextCard.className = 'story-preview-card story-card-active';
        if (prevCard) prevCard.style.opacity = '0';
        
        const overlays = document.querySelector('.story-card-overlays');
        if (overlays) overlays.style.opacity = '0';
        
        setTimeout(() => {
            state.cardIndex++;
            state.mediaIndex = 0;
            renderStoryMedia('nextCard');
            if (prevCard) prevCard.style.opacity = '';
            if (overlays) overlays.style.opacity = '1';
            isTransitioning = false;
        }, 600);
    } else {
        state.mediaIndex++;
        renderStoryMedia('nextPhoto');
    }
}

function prevStoryMedia() {
    if (isTransitioning) return;
    const state = window.storyState;
    
    if (state.mediaIndex <= 0) {
        if (state.cardIndex <= 0) return closeStoryViewer();
        
        isTransitioning = true;
        const active = document.getElementById('story-active-card-wrapper');
        const prevCard = document.getElementById('story-prev-card');
        const nextCard = document.getElementById('story-next-card');
        
        active.className = 'story-active-card story-card-next';
        if (prevCard) prevCard.className = 'story-preview-card story-card-active';
        if (nextCard) nextCard.style.opacity = '0';
        
        const overlays = document.querySelector('.story-card-overlays');
        if (overlays) overlays.style.opacity = '0';
        
        setTimeout(() => {
            state.cardIndex--;
            state.mediaIndex = state.cards[state.cardIndex].photos.length - 1;
            renderStoryMedia('prevCard');
            if (nextCard) nextCard.style.opacity = '';
            if (overlays) overlays.style.opacity = '1';
            isTransitioning = false;
        }, 600);
    } else {
        state.mediaIndex--;
        renderStoryMedia('prevPhoto');
    }
}

function startStoryTimer() {
    clearStoryTimer();
    window.storyState.timer = setTimeout(nextStoryMedia, 6000);
}

function clearStoryTimer() {
    clearTimeout(window.storyState.timer);
}


function initStoryViewer() {
    document.getElementById('story-close-btn')?.addEventListener('click', closeStoryViewer);
    document.getElementById('story-mute-btn')?.addEventListener('click', toggleStoryMute);
    document.getElementById('story-play-pause-btn')?.addEventListener('click', (e) => { e.stopPropagation(); toggleStoryPause(); });
    
    const seekEl = document.getElementById('story-video-seek');
    if (seekEl) {
        seekEl.addEventListener('mousedown', () => seekEl.isDragging = true);
        seekEl.addEventListener('mouseup', () => seekEl.isDragging = false);
        seekEl.addEventListener('input', (e) => {
            const vidEl = document.getElementById('story-video');
            if (vidEl && vidEl.duration) {
                vidEl.currentTime = (e.target.value / 100) * vidEl.duration;
            }
        });
    }
    
    const wrapper = document.getElementById('story-active-card-wrapper');
    const prevCardEl = document.getElementById('story-prev-card');
    const nextCardEl = document.getElementById('story-next-card');
    if (wrapper) {
        wrapper.addEventListener('click', (e) => {
            if (e.target.closest('button') || e.target.closest('.story-playback-bar')) return;
            toggleStoryPause();
        });
    }
    
    document.getElementById('story-nav-left')?.addEventListener('click', (e) => { e.stopPropagation(); prevStoryMedia(); });
    document.getElementById('story-nav-right')?.addEventListener('click', (e) => { e.stopPropagation(); nextStoryMedia(); });
    document.getElementById('story-nav-prev-arrow')?.addEventListener('click', prevStoryMedia);
    document.getElementById('story-nav-next-arrow')?.addEventListener('click', nextStoryMedia);
    
    document.getElementById('story-next-card')?.addEventListener('click', () => {
        if (isTransitioning) return;
        window.storyState.mediaIndex = window.storyState.cards[window.storyState.cardIndex].photos.length - 1;
        nextStoryMedia();
    });
    
    document.getElementById('story-prev-card')?.addEventListener('click', () => {
        if (isTransitioning) return;
        window.storyState.mediaIndex = 0;
        prevStoryMedia();
    });
    
    document.getElementById('story-grid-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        openStoryGrid();
    });
    document.getElementById('story-grid-back-btn')?.addEventListener('click', closeStoryGrid);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStoryViewer);
} else {
    initStoryViewer();
}


