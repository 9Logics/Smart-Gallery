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
    
    const isSimpleSlide = localStorage.getItem('simpleSlideMode') === 'true';
    const simpleSlideToggle = document.getElementById('simple-slide-mode');
    if (simpleSlideToggle) simpleSlideToggle.checked = isSimpleSlide;
    
    const isNoLightboxAnim = localStorage.getItem('disableLightboxAnim') === 'true';
    const noLightboxAnimToggle = document.getElementById('disable-lightbox-anim');
    if (noLightboxAnimToggle) noLightboxAnimToggle.checked = isNoLightboxAnim;

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
    
    const squareGridToggle = document.getElementById('square-grid-layout');
    if (squareGridToggle) {
        const isSquare = localStorage.getItem('square-grid-mode') === 'true';
        squareGridToggle.checked = isSquare;
        if (isSquare) {
            document.body.classList.add('square-grid-mode');
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
    
    const simpleSlideToggle = document.getElementById('simple-slide-mode');
    if (simpleSlideToggle) {
        simpleSlideToggle.addEventListener('change', (e) => {
            localStorage.setItem('simpleSlideMode', e.target.checked);
        });
    }

    const noLightboxAnimToggle = document.getElementById('disable-lightbox-anim');
    if (noLightboxAnimToggle) {
        noLightboxAnimToggle.addEventListener('change', (e) => {
            localStorage.setItem('disableLightboxAnim', e.target.checked);
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
    if (elements.cancelScanBtn) {
        elements.cancelScanBtn.addEventListener('click', cancelScan);
    }
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
    const squareGridToggle = document.getElementById('square-grid-layout');
    if (squareGridToggle) {
        squareGridToggle.addEventListener('change', () => {
            const isSquare = squareGridToggle.checked;
            if (isSquare) {
                document.body.classList.add('square-grid-mode');
            } else {
                document.body.classList.remove('square-grid-mode');
            }
            localStorage.setItem('square-grid-mode', isSquare ? 'true' : 'false');
            
            // Re-render photos if needed
            if (state.currentView === 'photos' && typeof loadPhotos === 'function') {
                loadPhotos();
            }
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
            showPrevPhoto();
        } else if (e.key === 'ArrowRight') {
            showNextPhoto();
        } else if (e.key === ' ' || e.key === 'Spacebar') {
            if (isVideoActive) {
                if (video.paused) video.play().catch(err => console.log(err));
                else video.pause();
                e.preventDefault();
            }
        } else if (e.key === 'ArrowUp') {
            if (isVideoActive) {
                video.volume = Math.min(1.0, video.volume + 0.1);
                if (video.volume > 0) state.lastUnmutedVolume = video.volume;
                video.muted = false;
                updateVolumeUI();
                e.preventDefault();
            }
        } else if (e.key === 'ArrowDown') {
            if (isVideoActive) {
                video.volume = Math.max(0.0, video.volume - 0.1);
                if (video.volume > 0) state.lastUnmutedVolume = video.volume;
                video.muted = (video.volume === 0);
                updateVolumeUI();
                e.preventDefault();
            }
        } else if (e.key.toLowerCase() === 'm') {
            if (isVideoActive) {
                if (video.muted || video.volume === 0) {
                    video.muted = false;
                    video.volume = (state.lastUnmutedVolume && state.lastUnmutedVolume > 0) ? state.lastUnmutedVolume : 1.0;
                } else {
                    state.lastUnmutedVolume = video.volume;
                    video.muted = true;
                }
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
        
        // Mute Toggle Button & Volume Slider
        if (muteBtn) {
            muteBtn.addEventListener('click', () => {
                if (video.muted || video.volume === 0) {
                    video.muted = false;
                    video.volume = (state.lastUnmutedVolume && state.lastUnmutedVolume > 0) ? state.lastUnmutedVolume : 1.0;
                } else {
                    state.lastUnmutedVolume = video.volume;
                    video.muted = true;
                }
                updateVolumeUI();
            });
        }
        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                video.volume = e.target.value;
                video.muted = (video.volume == 0);
                if (video.volume > 0) {
                    state.lastUnmutedVolume = video.volume;
                }
                updateVolumeUI();
            });
        }
        
        video.addEventListener('volumechange', () => {
            if (typeof updateVolumeUI === 'function') updateVolumeUI();
        });
        
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
    
    // Stop any memory hover videos from continuing to fetch/play in the background
    if (view !== 'memories' && typeof window.unloadMemories === 'function') {
        window.unloadMemories();
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

function updateBasicSidePanelUI(photo) {
    if (elements.photoTitle) elements.photoTitle.innerText = photo.filename;
    const fi = document.getElementById('photo-filename-input');
    if (fi) fi.value = photo.filename;
    elements.photoPath.innerText = photo.path;
    
    // Format Date taken
    elements.photoDate.innerText = formatPhotoDate(photo.date_taken);
    
    // Format File Size & Resolution
    const kbSize = photo.size < 1024 * 1024;
    const sizeFormatted = kbSize ? `${Math.round(photo.size / 1024)} KB` : `${(photo.size / (1024 * 1024)).toFixed(2)} MB`;
    
    let resText = `${photo.width || 0}x${photo.height || 0}`;
    let mpText = '';
    if (photo.width && photo.height) {
        mpText = `${Math.round(photo.width * photo.height / 1000000)}MP`;
    }
    const techDetailsStr = [sizeFormatted, resText, mpText].filter(Boolean).join(' | ');
    
    const techDetailsEl = document.getElementById('photo-tech-details');
    if (techDetailsEl) techDetailsEl.innerText = techDetailsStr;
    
    // Populate Camera Details if they exist
    const cameraSection = document.getElementById('camera-tech-section');
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
            if (photo.iso) settings.push(`ISO ${photo.iso}`);
            if (photo.focal_length) settings.push(`${photo.focal_length}mm`);
            // if we had exposure bias, we'd add it here.
            if (photo.f_stop) settings.push(`F${photo.f_stop}`);
            if (photo.exposure_time) settings.push(photo.exposure_time);
            cameraSettings.innerText = settings.join(' | ');
        } else {
            cameraSection.classList.add('hidden');
        }
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
}

function updateHeavySidePanelUI(photo) {
    // Render heavy components
    renderLightboxFaces(photo.path);
    renderLightboxAlbums(photo.path);
}

function updateMorphFrameBounds(photo) {
    const frame = document.getElementById('lightbox-morph-frame');
    const container = document.getElementById('lightbox-media-container');
    if (!frame || !container) return null;
    
    if (localStorage.getItem('simpleSlideMode') === 'true') {
        frame.style.width = '100%';
        frame.style.height = '100%';
        return { 
            w: container.clientWidth * 0.90, 
            h: container.clientHeight * 0.90 
        };
    }
    
    // Default fallback bounds if metadata is missing (16:9 placeholder)
    let imgW = photo.width || 1920;
    let imgH = photo.height || 1080;
    
    // Allow up to 90% of screen size to leave room for padding
    const maxWidth = container.clientWidth * 0.90;
    const maxHeight = container.clientHeight * 0.90;
    
    const aspect = imgW / imgH;
    const maxAspect = maxWidth / maxHeight;
    
    let targetW, targetH;
    
    if (aspect > maxAspect) {
        // Limited by container width
        targetW = maxWidth;
        targetH = maxWidth / aspect;
    } else {
        // Limited by container height
        targetW = maxHeight * aspect;
        targetH = maxHeight;
    }
    
    // Update frame dimensions for CSS morphing
    frame.style.width = Math.round(targetW) + 'px';
    frame.style.height = Math.round(targetH) + 'px';
    
    return { w: Math.round(targetW), h: Math.round(targetH) };
}

function renderLightboxPhoto(direction = null) {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    // Capture old frame bounds for cropping
    const frame = document.getElementById('lightbox-morph-frame');
    let oldW = '100%';
    let oldH = '100%';
    if (frame) {
        oldW = frame.style.width || '100%';
        oldH = frame.style.height || '100%';
    }
    
    // Update morphing frame size
    const bounds = updateMorphFrameBounds(photo);
    
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
    
    // Check if video file
    const ext = photo.path.split('.').pop().toLowerCase();
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    
    if (isVideo) {
        // Show the thumbnail for quick scrubbing instead of just hiding it!
        const thumbSrc = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}`;
        elements.lightboxImg.src = thumbSrc;
        elements.lightboxImg.style.transition = '';
        elements.lightboxImg.style.opacity = '1';
        elements.lightboxImg.classList.remove('hidden');
        elements.lightboxImgBuffer.classList.add('hidden');
        elements.lightboxImgBuffer.style.opacity = '0';
        
        const wrapper = document.getElementById('custom-video-wrapper');
        if (wrapper) wrapper.classList.remove('hidden');
        
        elements.lightboxVideo.src = `/api/photo/file/${encodeURIComponent(photo.path)}`;
        elements.lightboxVideo.style.opacity = '0'; // Hide video initially
        elements.lightboxVideo.load();
        
        const spinner = document.getElementById('video-loading-spinner');
        const errMsg = document.getElementById('video-error-msg');
        if (spinner) spinner.classList.remove('hidden');
        if (errMsg) errMsg.classList.add('hidden');
        
        if (state.videoLoadTimeout) clearTimeout(state.videoLoadTimeout);
        state.videoLoadTimeout = setTimeout(() => {
            if (spinner) spinner.classList.add('hidden');
            if (errMsg) errMsg.classList.remove('hidden');
        }, 10000);
        
        elements.lightboxVideo.oncanplay = () => {
            if (state.videoLoadTimeout) clearTimeout(state.videoLoadTimeout);
            if (spinner) spinner.classList.add('hidden');
            elements.lightboxVideo.style.opacity = '1';
            
            setTimeout(() => {
                if (elements.lightboxVideo.src.endsWith(encodeURIComponent(photo.path))) {
                    elements.lightboxImg.classList.add('hidden');
                }
            }, 50);
        };
        
        elements.lightboxVideo.onerror = () => {
            if (state.videoLoadTimeout) clearTimeout(state.videoLoadTimeout);
            if (spinner) spinner.classList.add('hidden');
            if (errMsg) errMsg.classList.remove('hidden');
        };
        
        // Ensure initial volume state is recorded if not set
        if (state.lastUnmutedVolume === undefined && !elements.lightboxVideo.muted && elements.lightboxVideo.volume > 0) {
            state.lastUnmutedVolume = elements.lightboxVideo.volume;
        }
        
        if (typeof updateVolumeUI === 'function') updateVolumeUI();
        
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
        let wasInterrupted = false;
        if (state.transitionTimeout) {
            clearTimeout(state.transitionTimeout);
            wasInterrupted = true;
        }
        if (state.crossfadeTimeout) {
            clearTimeout(state.crossfadeTimeout);
            wasInterrupted = true;
        }
        
        if (wasInterrupted) state.isScrubbing = true;
        
        if (state.scrubTimeout) clearTimeout(state.scrubTimeout);
        state.scrubTimeout = setTimeout(() => {
            state.isScrubbing = false;
        }, 200);
        
        elements.lightboxImgBuffer.onload = null;
        elements.lightboxImg.style.transition = '';
        elements.lightboxImgBuffer.style.transition = '';
        
        // If we interrupted a crossfade, lightboxImg will have opacity 0.
        // We must swap them early so the visible full-res image is used for the slide-out animation!
        if (elements.lightboxImg.style.opacity === '0' || elements.lightboxImgBuffer.style.opacity === '1') {
            const temp = elements.lightboxImg;
            elements.lightboxImg = elements.lightboxImgBuffer;
            elements.lightboxImgBuffer = temp;
            
            elements.lightboxImg.style.zIndex = '2';
            elements.lightboxImgBuffer.style.zIndex = '1';
        }
        
        // Force reset opacities to expected baseline for slide animation
        elements.lightboxImg.style.opacity = '1';
        elements.lightboxImgBuffer.style.opacity = '0';
        
        elements.lightboxImg.classList.remove('hidden');
        elements.lightboxImgBuffer.classList.remove('hidden');
        
        const wrapper = document.getElementById('custom-video-wrapper');
        const wasVideo = wrapper && !wrapper.classList.contains('hidden');
        if (wrapper) {
            wrapper.classList.add('hidden');
            if (wasVideo && elements.lightboxVideo) {
                elements.lightboxVideo.pause();
                elements.lightboxVideo.removeAttribute('src'); // Stop downloading/playing
                elements.lightboxVideo.load();
            }
        }
        
        const newSrc = `/api/photo/file/${encodeURIComponent(photo.path)}`;
        
        if (direction && !wasVideo && elements.lightboxImg.src && elements.lightboxImg.src !== window.location.href) {
            const thumbSrc = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}`;
            
            if (state.isScrubbing) {
                // Scrubbing: Instant swap, no slide animation
                elements.lightboxImg.src = thumbSrc;
                elements.lightboxImg.style.animation = '';
                elements.lightboxImg.style.opacity = '1';
                elements.lightboxImgBuffer.style.opacity = '0';
                
                // Delay full-res load until scrub stops
                if (state.scrubFullResTimeout) clearTimeout(state.scrubFullResTimeout);
                state.scrubFullResTimeout = setTimeout(() => {
                    if (state.lightboxPhotos[state.lightboxIndex].path !== photo.path) return;
                    
                    const handleFullResLoad = () => {
                        elements.lightboxImgBuffer.onload = null;
                        
                        elements.lightboxImgBuffer.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
                        elements.lightboxImg.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
                        
                        elements.lightboxImgBuffer.style.opacity = '1';
                        elements.lightboxImg.style.opacity = '0';
                        
                        state.crossfadeTimeout = setTimeout(() => {
                            elements.lightboxImgBuffer.style.transition = '';
                            elements.lightboxImg.style.transition = '';
                            
                            const t2 = elements.lightboxImg;
                            elements.lightboxImg = elements.lightboxImgBuffer;
                            elements.lightboxImgBuffer = t2;
                            
                            elements.lightboxImg.style.zIndex = '2';
                            elements.lightboxImgBuffer.style.zIndex = '1';
                            state.crossfadeTimeout = null;
                        }, 250);
                    };
                    
                    elements.lightboxImgBuffer.onload = handleFullResLoad;
                    if (elements.lightboxImgBuffer.src.endsWith(newSrc)) elements.lightboxImgBuffer.src = '';
                    elements.lightboxImgBuffer.src = newSrc;
                    if (elements.lightboxImgBuffer.complete) handleFullResLoad();
                }, 250);
            } else {
            elements.lightboxImgBuffer.onload = () => {
                // Animate old image out
                elements.lightboxImg.style.animation = direction === 'next' 
                    ? 'slideOutLeft 0.2s cubic-bezier(0.4, 0, 0.2, 1) forwards' 
                    : 'slideOutRight 0.2s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                
                // Animate new image in
                elements.lightboxImgBuffer.style.opacity = '1';
                elements.lightboxImgBuffer.style.animation = direction === 'next'
                    ? 'slideInRight 0.2s cubic-bezier(0.4, 0, 0.2, 1) both' 
                    : 'slideInLeft 0.2s cubic-bezier(0.4, 0, 0.2, 1) both';

                // Cleanup and swap roles after transition, then load full-res
                if (state.transitionTimeout) clearTimeout(state.transitionTimeout);
                state.transitionTimeout = setTimeout(() => {
                    elements.lightboxImg.style.animation = ''; 
                    elements.lightboxImg.style.opacity = '0';
                    elements.lightboxImgBuffer.style.animation = '';
                    
                    // Swap identities
                    const temp = elements.lightboxImg;
                    elements.lightboxImg = elements.lightboxImgBuffer;
                    elements.lightboxImgBuffer = temp;
                    
                    elements.lightboxImg.style.zIndex = '2';
                    elements.lightboxImgBuffer.style.zIndex = '1';
                    state.transitionTimeout = null;
                    
                    // Now silently load full-res into the hidden buffer and crossfade
                    const handleFullResLoad = () => {
                        elements.lightboxImgBuffer.onload = null;
                        
                        elements.lightboxImgBuffer.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
                        elements.lightboxImg.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
                        
                        elements.lightboxImgBuffer.style.opacity = '1';
                        elements.lightboxImg.style.opacity = '0';
                        
                        // Swap again after crossfade settles
                        state.crossfadeTimeout = setTimeout(() => {
                            elements.lightboxImgBuffer.style.transition = '';
                            elements.lightboxImg.style.transition = '';
                            
                            const t2 = elements.lightboxImg;
                            elements.lightboxImg = elements.lightboxImgBuffer;
                            elements.lightboxImgBuffer = t2;
                            
                            elements.lightboxImg.style.zIndex = '2';
                            elements.lightboxImgBuffer.style.zIndex = '1';
                            state.crossfadeTimeout = null;
                        }, 250);
                    };
                    
                    elements.lightboxImgBuffer.onload = handleFullResLoad;
                    // Reset src to force a refresh if it happens to be the same URL from a previous view
                    if (elements.lightboxImgBuffer.src.endsWith(newSrc)) elements.lightboxImgBuffer.src = '';
                    elements.lightboxImgBuffer.src = newSrc;
                    
                    if (elements.lightboxImgBuffer.complete) handleFullResLoad();
                }, 200);
            };
            
            // Load thumbnail into buffer (instant since it's already cached)
            if (!state.isScrubbing) elements.lightboxImgBuffer.src = thumbSrc;
            }
        } else {
            const handleInstantLoad = () => {
                elements.lightboxImgBuffer.onload = null;
                // Bring buffer to front so it renders above the thumbnail
                elements.lightboxImgBuffer.style.zIndex = '3';
                elements.lightboxImgBuffer.style.opacity = '0';
                
                // Force reflow before starting transition
                void elements.lightboxImgBuffer.offsetWidth;
                
                // Crossfade new high-res image over the thumbnail
                elements.lightboxImgBuffer.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
                elements.lightboxImgBuffer.style.opacity = '1';
                
                if (state.transitionTimeout) clearTimeout(state.transitionTimeout);
                state.transitionTimeout = setTimeout(() => {
                    elements.lightboxImgBuffer.style.transition = '';
                    
                    // Swap identities: buffer becomes active
                    const temp = elements.lightboxImg;
                    elements.lightboxImg = elements.lightboxImgBuffer;
                    elements.lightboxImgBuffer = temp;
                    
                    elements.lightboxImg.style.zIndex = '2';
                    elements.lightboxImg.style.opacity = '1';
                    elements.lightboxImgBuffer.style.zIndex = '1';
                    elements.lightboxImgBuffer.style.opacity = '0';
                    state.transitionTimeout = null;
                }, 250);
            };
            
            elements.lightboxImgBuffer.onload = handleInstantLoad;
            if (elements.lightboxImgBuffer.src.endsWith(newSrc)) elements.lightboxImgBuffer.src = '';
            elements.lightboxImgBuffer.src = newSrc;
            
            if (elements.lightboxImgBuffer.complete) handleInstantLoad();
        }
        
        if (elements.lightboxZoomControls) {
            elements.lightboxZoomControls.classList.remove('hidden');
        }
    }
    
    updateBasicSidePanelUI(photo);
    
    // Add loading transition ONLY to heavy sections
    const facesSection = document.getElementById('lightbox-people-heading')?.parentNode;
    const mapContainer = document.getElementById('photo-map');
    const albumSection = document.getElementById('lightbox-albums-list')?.parentNode;
    
    if (mapContainer) mapContainer.classList.add('loading-transition');
    
    // Clear heavy side panel contents immediately
    const mapSection = document.getElementById('photo-map');
    if (mapSection && mapSection.parentNode) {
        const hasCoords = photo.latitude !== null && photo.longitude !== null && !isNaN(photo.latitude) && !isNaN(photo.longitude) && !(photo.latitude === 0 && photo.longitude === 0);
        mapSection.parentNode.style.display = 'block';
        mapSection.style.display = hasCoords ? 'block' : 'none';
        
        const locAddressEl = document.getElementById('photo-location-address');
        if (elements.photoLocation && locAddressEl) {
            if (hasCoords || photo.place_name) {
                locAddressEl.innerHTML = `<div class="skeleton-card" style="width: 80%; height: 14px; border-radius: 4px; margin-bottom: 2px;"></div>`;
                elements.photoLocation.innerHTML = `<div class="skeleton-card" style="width: 50%; height: 14px; border-radius: 4px;"></div>`;
            } else {
                locAddressEl.innerText = 'No location metadata';
                elements.photoLocation.innerText = 'Unknown';
            }
        }
    }
    if (elements.lightboxFacesList) {
        const facesParent = elements.lightboxFacesList.closest('.sidebar-section');
        if (facesParent) facesParent.style.display = 'block';
        elements.lightboxFacesList.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; gap:6px; padding:6px; width:100%;">
                <div class="skeleton-card" style="width: 56px; height: 56px; border-radius: 50%;"></div>
                <div class="skeleton-card" style="width: 48px; height: 12px; border-radius: 4px;"></div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:center; gap:6px; padding:6px; width:100%;">
                <div class="skeleton-card" style="width: 56px; height: 56px; border-radius: 50%;"></div>
                <div class="skeleton-card" style="width: 48px; height: 12px; border-radius: 4px;"></div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:center; gap:6px; padding:6px; width:100%;">
                <div class="skeleton-card" style="width: 56px; height: 56px; border-radius: 50%;"></div>
                <div class="skeleton-card" style="width: 48px; height: 12px; border-radius: 4px;"></div>
            </div>
        `;
    }
    if (elements.lightboxAlbumsList) {
        elements.lightboxAlbumsList.innerHTML = `
            <div class="skeleton-grid" style="display: flex; gap: 8px; padding: 4px 0;">
                <div class="skeleton-card" style="width: 80px; height: 26px; border-radius: 12px;"></div>
                <div class="skeleton-card" style="width: 110px; height: 26px; border-radius: 12px;"></div>
            </div>
        `;
    }
    
    // Defer heavy side panel UI updates to hide transition lag and let frame finish morphing
    const delay = direction ? 350 : 0;
    if (state.sidePanelDebounceTimeout) clearTimeout(state.sidePanelDebounceTimeout);
    state.sidePanelDebounceTimeout = setTimeout(() => {
        updateHeavySidePanelUI(photo);
    }, delay);
    
    // Map is heavily delayed for performance
    if (state.mapDebounceTimeout) clearTimeout(state.mapDebounceTimeout);
    state.mapDebounceTimeout = setTimeout(() => {
        const currentPhoto = state.lightboxPhotos[state.lightboxIndex];
        if (currentPhoto && currentPhoto.path === photo.path) {
            renderLightboxMap(currentPhoto);
            if (mapContainer) mapContainer.classList.remove('loading-transition');
        }
    }, 3000);

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
                    const kbSizeFetch = updated.size < 1024 * 1024;
                    const sizeFormattedFetch = kbSizeFetch ? `${Math.round(updated.size / 1024)} KB` : `${(updated.size / (1024 * 1024)).toFixed(2)} MB`;
                    
                    let resTextFetch = `${updated.width || 0}x${updated.height || 0}`;
                    let mpTextFetch = '';
                    if (updated.width && updated.height) {
                        mpTextFetch = `${Math.round(updated.width * updated.height / 1000000)}MP`;
                    }
                    const techDetailsStrFetch = [sizeFormattedFetch, resTextFetch, mpTextFetch].filter(Boolean).join(' | ');
                    
                    const techDetailsEl = document.getElementById('photo-tech-details');
                    if (techDetailsEl) techDetailsEl.innerText = techDetailsStrFetch;
                    
                    // Populate Camera Details
                    const camSec = document.getElementById('camera-tech-section');
                    if (camSec) {
                        const hasCam = updated.camera_make || updated.camera_model || updated.f_stop || updated.exposure_time || updated.focal_length || updated.iso;
                        if (hasCam) {
                            camSec.classList.remove('hidden');
                            let mm = [];
                            if (updated.camera_make) mm.push(updated.camera_make);
                            if (updated.camera_model) mm.push(updated.camera_model);
                            document.getElementById('camera-model-text').innerText = mm.join(' ') || 'Unknown Camera';
                            
                            let s = [];
                            if (updated.iso) s.push(`ISO ${updated.iso}`);
                            if (updated.focal_length) s.push(`${updated.focal_length}mm`);
                            if (updated.f_stop) s.push(`F${updated.f_stop}`);
                            if (updated.exposure_time) s.push(updated.exposure_time);
                            document.getElementById('camera-settings-text').innerText = s.join(' | ');
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

    // Background Image Prefetching (Next 2, Prev 1)
    setTimeout(() => {
        const prefetchOffsets = [1, 2, -1];
        prefetchOffsets.forEach(offset => {
            const prefetchIdx = state.lightboxIndex + offset;
            if (prefetchIdx >= 0 && prefetchIdx < state.lightboxPhotos.length) {
                const prefetchPhoto = state.lightboxPhotos[prefetchIdx];
                if (prefetchPhoto) {
                    const ext = prefetchPhoto.path.split('.').pop().toLowerCase();
                    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
                    if (!isVideo) {
                        const img = new Image();
                        img.src = `/api/photo/file/${encodeURIComponent(prefetchPhoto.path)}`;
                    }
                }
            }
        });
    }, 50);
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
    
    const frame = document.getElementById('lightbox-morph-frame');
    
    if (state.zoomScale > 1) {
        img.style.cursor = state.isPanning ? 'grabbing' : 'grab';
        if (frame) frame.classList.add('zoomed');
    } else {
        img.style.cursor = '';
        if (frame) frame.classList.remove('zoomed');
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

const btnScanHeroAI = document.getElementById('scan-hero-ai-btn');
if (btnScanHeroAI) {
    btnScanHeroAI.addEventListener('click', () => {
        fetch('/api/scan/hero-ai', { method: 'POST' }).then(() => {
            alert('Hero AI aesthetic scan started! Check the top notification bar for progress.');
        });
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




