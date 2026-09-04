var searchContainer = document.querySelector('.search-container');

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
    document.body.className = document.body.className.replace(/[a-z]+-theme/, '');
    document.body.classList.add(savedTheme + '-theme');
    if (elements.themeSelector) elements.themeSelector.value = savedTheme;
    
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

    if (elements.multiArchiveBtn) {
        elements.multiArchiveBtn.addEventListener('click', archiveSelectedPhotos);
    }
    if (elements.multiTrashBtn) {
        elements.multiTrashBtn.addEventListener('click', trashSelectedPhotos);
    }
    if (elements.lightboxArchiveBtn) {
        elements.lightboxArchiveBtn.addEventListener('click', toggleLightboxPhotoArchive);
    }
    if (elements.lightboxTrashBtn) {
        elements.lightboxTrashBtn.addEventListener('click', trashCurrentLightboxPhoto);
    }
    if (elements.restoreAllTrashBtn) {
        elements.restoreAllTrashBtn.addEventListener('click', restoreAllRecycleBin);
    }
    if (elements.trashSortSelect) {
        elements.trashSortSelect.addEventListener('change', () => {
            state.trashSortBy = elements.trashSortSelect.value;
            loadTrashPhotos();
        });
    }

    elements.multiAlbumBtn.addEventListener('click', openAddToAlbumModal);
    
    // Settings Scan Folder
    elements.startScanBtn.addEventListener('click', startScan);
    if (elements.cancelScanBtn) {
        elements.cancelScanBtn.addEventListener('click', cancelScan);
    }
    elements.resolveDuplicatesBtn.addEventListener('click', resolveDuplicates);
    elements.duplicateTypeSelect.addEventListener('change', () => renderDuplicates(state.duplicateGroups));
    
    // Theme toggler
    if (elements.themeSelector) elements.themeSelector.addEventListener('change', (e) => changeTheme(e.target.value));
    
    // Lightbox actions
    elements.lightboxClose.addEventListener('click', closeLightbox);
    elements.lightboxPrev.addEventListener('click', showPrevPhoto);
    elements.lightboxNext.addEventListener('click', showNextPhoto);
    elements.lightboxInfoToggle.addEventListener('click', toggleLightboxInfo);
    if (elements.closeInfoPanelBtn) elements.closeInfoPanelBtn.addEventListener('click', toggleLightboxInfo);
    elements.lightboxAlbumSelect.addEventListener('change', addPhotoToAlbumFromLightbox);

    if (elements.multiCopyBtn) {
        elements.multiCopyBtn.addEventListener('click', copySelectedPhotoToClipboard);
    }



    if (elements.lightboxCopyBtn) {
        elements.lightboxCopyBtn.addEventListener('click', copyLightboxPhotoToClipboard);
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
    
    const lightboxShareBtn = document.getElementById('lightbox-share-btn');
    if (lightboxShareBtn) {
        lightboxShareBtn.addEventListener('click', async () => {
            const photo = state.lightboxPhotos[state.lightboxIndex];
            if (!photo) return;
            
            const url = `/api/photo/file/${encodeURIComponent(photo.path)}?s=${photo.size}`;
            let filename = photo.filename || 'media_file';
            
            try {
                lightboxShareBtn.style.opacity = '0.5';
                lightboxShareBtn.style.pointerEvents = 'none';
                
                const response = await fetch(url);
                const blob = await response.blob();
                
                // Browsers strictly validate file extensions for navigator.share()
                if (blob.type === 'image/jpeg' && !filename.toLowerCase().endsWith('.jpg') && !filename.toLowerCase().endsWith('.jpeg')) {
                    filename = filename.replace(/\.[^/.]+$/, "") + ".jpg";
                }
                
                const file = new File([blob], filename, { type: blob.type });
                
                if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    await navigator.share({
                        files: [file],
                        title: filename
                    });
                } else {
                    alert("Native sharing is not supported on this device/browser.");
                }
            } catch (err) {
                if (err.name !== 'AbortError') {
                    console.error("Share failed", err);
                    
                    // Fallback to downloading the file
                    try {
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    } catch (dlErr) {
                        alert("Failed to share or download file.");
                    }
                }
            } finally {
                lightboxShareBtn.style.opacity = '1';
                lightboxShareBtn.style.pointerEvents = 'auto';
            }
        });
    }








    
    // Zoom and Ratio event listeners
    function updateVisualZoom(size) {
        document.documentElement.style.setProperty('--thumbnail-size', `${size}px`);
        if (elements.settingsZoomSlider && elements.settingsZoomSlider.value != size) {
            elements.settingsZoomSlider.value = size;
        }
        if (elements.gridZoomSlider && elements.gridZoomSlider.value != size) {
            elements.gridZoomSlider.value = size;
        }
    }
    
    function applyFinalZoom(size) {
        localStorage.setItem('grid-thumbnail-size', size);
        if (typeof applyJustifiedLayout === 'function' && !document.body.classList.contains('square-grid-mode')) {
            const containerWidth = document.getElementById('photos-grid-root') ? document.getElementById('photos-grid-root').clientWidth : window.innerWidth;
            const grids = document.querySelectorAll('.photos-grid');
            grids.forEach(grid => {
                const dateKey = grid.dataset.dateKey;
                if (dateKey && typeof calculateGridHeight === 'function' && typeof state !== 'undefined' && state.renderGroups && state.renderGroups[dateKey]) {
                    const expectedHeight = calculateGridHeight(state.renderGroups[dateKey], containerWidth, parseInt(size));
                    grid.style.minHeight = expectedHeight + 'px';
                }
                
                if (grid.children.length > 0) {
                    applyJustifiedLayout(grid, size);
                }
            });
        }
    }

    function stepZoom(amount) {
        const currentSize = parseInt(localStorage.getItem('grid-thumbnail-size')) || 180;
        let newSize = currentSize + amount;
        if (newSize < 120) newSize = 120;
        if (newSize > 320) newSize = 320;
        updateVisualZoom(newSize);
        applyFinalZoom(newSize);
    }

    if (elements.gridZoomSlider) {
        elements.gridZoomSlider.addEventListener('input', (e) => updateVisualZoom(e.target.value));
        elements.gridZoomSlider.addEventListener('change', (e) => applyFinalZoom(e.target.value));
    }
    if (elements.settingsZoomSlider) {
        elements.settingsZoomSlider.addEventListener('input', (e) => updateVisualZoom(e.target.value));
        elements.settingsZoomSlider.addEventListener('change', (e) => applyFinalZoom(e.target.value));
    }

    // Zoom Icons Click Handlers
    const gridZoomOut = document.getElementById('grid-zoom-out-icon');
    const gridZoomIn = document.getElementById('grid-zoom-in-icon');
    const settingsZoomOut = document.getElementById('settings-zoom-out-icon');
    const settingsZoomIn = document.getElementById('settings-zoom-in-icon');

    if (gridZoomOut) gridZoomOut.addEventListener('click', () => stepZoom(-20));
    if (gridZoomIn) gridZoomIn.addEventListener('click', () => stepZoom(20));
    if (settingsZoomOut) settingsZoomOut.addEventListener('click', () => stepZoom(-20));
    if (settingsZoomIn) settingsZoomIn.addEventListener('click', () => stepZoom(20));
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
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
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
            let isScrubbing = false;
            
            const startScrub = () => {
                isScrubbing = true;
                video.pause();
                if (playBtn) {
                    playBtn.innerHTML = '<i data-lucide="play"></i>';
                    if (window.lucide) window.lucide.createIcons();
                }
            };
            const stopScrub = () => { isScrubbing = false; };
            
            timeline.addEventListener('mousedown', startScrub);
            timeline.addEventListener('touchstart', startScrub, {passive: true});
            timeline.addEventListener('mouseup', stopScrub);
            timeline.addEventListener('touchend', stopScrub);

            video.addEventListener('timeupdate', () => {
                if (video.duration && !isScrubbing) {
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
                    timeCur.innerText = formatVideoTime(video.currentTime);
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

    if (elements.multiArchiveBtn) {
        if (view === 'archive') {
            elements.multiArchiveBtn.innerHTML = '<i data-lucide="archive-restore"></i> Unarchive';
            elements.multiArchiveBtn.title = "Unarchive selected photos";
        } else {
            elements.multiArchiveBtn.innerHTML = '<i data-lucide="archive"></i> Archive';
            elements.multiArchiveBtn.title = "Archive selected photos";
        }
    }

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










    
    // Hide sorting widget and filter widget on non-photo sections
    const sortingContainer = document.getElementById('sorting-container');
    const filterContainer = document.getElementById('filter-container');
    if (view === 'photos' || view === 'archive' || view === 'favorites') {
        if (sortingContainer) sortingContainer.classList.remove('hidden');
        if (filterContainer) filterContainer.classList.remove('hidden');
    } else {
        if (sortingContainer) sortingContainer.classList.add('hidden');
        if (filterContainer) filterContainer.classList.add('hidden');
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
window.changeTheme = function(themeName) {
    document.body.className = document.body.className.replace(/[a-z]+-theme/, '');
    document.body.classList.add(themeName + '-theme');
    localStorage.setItem('theme', themeName);
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
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
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
    let sizeFormatted = "";
    if (photo.size) {
        const kbSize = photo.size < 1024 * 1024;
        sizeFormatted = kbSize ? `${Math.round(photo.size / 1024)} KB` : `${(photo.size / (1024 * 1024)).toFixed(2)} MB`;
    }
    
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
        const isVideo = ['mp4', 'mov', 'm4v', 'hevc', 'avi', 'mkv', 'webm'].includes((photo.file_type || '').toLowerCase());
        const hasCameraInfo = isVideo ? (photo.duration || photo.video_codec || photo.fps || photo.camera_make || photo.camera_model) : (photo.camera_make || photo.camera_model || photo.f_stop || photo.exposure_time || photo.focal_length || photo.iso);
        
        if (hasCameraInfo) {
            cameraSection.classList.remove('hidden');
            let makeModel = [];
            if (photo.camera_make) makeModel.push(photo.camera_make);
            if (photo.camera_model) makeModel.push(photo.camera_model);
            cameraModel.innerText = makeModel.join(' ') || (isVideo ? 'Unknown Source' : 'Unknown Camera');
            
            let settings = [];
            if (isVideo) {
                if (photo.duration) {
                    const mins = Math.floor(photo.duration / 60);
                    const secs = Math.floor(photo.duration % 60);
                    settings.push(`${mins}:${secs.toString().padStart(2, '0')}`);
                }
                if (photo.video_codec) settings.push(photo.video_codec);
                settings.push("AAC"); // Generic fallback audio codec
                if (photo.fps) settings.push(`${photo.fps}fps`);
            } else {
                if (photo.iso) settings.push(`ISO ${photo.iso}`);
                if (photo.focal_length) settings.push(`${photo.focal_length}mm`);
                if (photo.f_stop) settings.push(`F${photo.f_stop}`);
                if (photo.exposure_time) {
                    let expStr = String(photo.exposure_time);
                    let expNum = parseFloat(expStr);
                    if (!expStr.includes('/') && !isNaN(expNum) && expNum > 0 && expNum < 1) {
                        settings.push(`1/${Math.round(1/expNum)} s`);
                    } else {
                        settings.push(expStr + (expStr.includes('s') ? '' : ' s'));
                    }
                }
            }
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
    
    // We intentionally don't return if photo.size is missing, 
    // because minimal photo objects from Home views won't have it yet.
    
    // Background cache-busting check
    fetch('/api/photo/refresh_if_changed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: photo.path, expected_size: photo.size })
    }).then(r => r.json()).then(data => {
        if (data.changed && data.photo) {
            // Update state with new metadata
            Object.assign(photo, data.photo);
            if (typeof updateBasicSidePanelUI === 'function') updateBasicSidePanelUI(photo);
            if (typeof updateHeavySidePanelUI === 'function') updateHeavySidePanelUI(photo);
            
            // Reload visual media if we are still viewing this photo
            if (state.lightboxPhotos[state.lightboxIndex].path === photo.path) {
                renderLightboxPhoto(null); // Re-trigger render statically to get new image/video source
            }
        }
    }).catch(e => console.error("Error checking modification:", e));
    
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
        const thumbSrc = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}?s=${photo.size}`;
        elements.lightboxImg.src = thumbSrc;
        elements.lightboxImg.style.transition = '';
        elements.lightboxImg.style.opacity = '1';
        elements.lightboxImg.classList.remove('hidden');
        elements.lightboxImgBuffer.classList.add('hidden');
        elements.lightboxImgBuffer.style.opacity = '0';
        
        const wrapper = document.getElementById('custom-video-wrapper');
        if (wrapper) wrapper.classList.remove('hidden');
        
        elements.lightboxVideo.src = `/api/photo/file/${encodeURIComponent(photo.path)}?s=${photo.size}`;
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
                if (elements.lightboxVideo.src.includes(encodeURIComponent(photo.path))) {
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
            if (wrapper) {
                // The wrapper is inside the morph frame, which is already sized to the correct aspect ratio.
                // We just need to fill it so the video perfectly overlays the thumbnail.
                wrapper.style.width = '100%';
                wrapper.style.height = '100%';
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
        
        const newSrc = `/api/photo/file/${encodeURIComponent(photo.path)}?s=${photo.size}`;
        
        if (direction && !wasVideo && elements.lightboxImg.src && elements.lightboxImg.src !== window.location.href) {
            const thumbSrc = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}?s=${photo.size}`;
            
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
                        const isVideo = ['mp4', 'mov', 'm4v', 'hevc', 'avi', 'mkv', 'webm'].includes((updated.file_type || '').toLowerCase());
                        const hasCam = isVideo ? (updated.duration || updated.video_codec || updated.fps || updated.camera_make || updated.camera_model) : (updated.camera_make || updated.camera_model || updated.f_stop || updated.exposure_time || updated.focal_length || updated.iso);
                        
                        if (hasCam) {
                            camSec.classList.remove('hidden');
                            let mm = [];
                            if (updated.camera_make) mm.push(updated.camera_make);
                            if (updated.camera_model) mm.push(updated.camera_model);
                            document.getElementById('camera-model-text').innerText = mm.join(' ') || (isVideo ? 'Unknown Source' : 'Unknown Camera');
                            
                            let s = [];
                            if (isVideo) {
                                if (updated.duration) {
                                    const mins = Math.floor(updated.duration / 60);
                                    const secs = Math.floor(updated.duration % 60);
                                    s.push(`${mins}:${secs.toString().padStart(2, '0')}`);
                                }
                                if (updated.video_codec) s.push(updated.video_codec);
                                s.push("AAC");
                                if (updated.fps) s.push(`${updated.fps}fps`);
                            } else {
                                if (updated.iso) s.push(`ISO ${updated.iso}`);
                                if (updated.focal_length) s.push(`${updated.focal_length}mm`);
                                if (updated.f_stop) s.push(`F${updated.f_stop}`);
                                if (updated.exposure_time) {
                                    let expStr = String(updated.exposure_time);
                                    let expNum = parseFloat(expStr);
                                    if (!expStr.includes('/') && !isNaN(expNum) && expNum > 0 && expNum < 1) {
                                        s.push(`1/${Math.round(1/expNum)} s`);
                                    } else {
                                        s.push(expStr + (expStr.includes('s') ? '' : ' s'));
                                    }
                                }
                            }
                            document.getElementById('camera-settings-text').innerText = s.join(' | ');
                        } else {
                            camSec.classList.add('hidden');
                        }
                    }
                    
                    updateBasicSidePanelUI(updated);
                    updateHeavySidePanelUI(updated);
                    updateMorphFrameBounds(updated); // Update frame now that we have width/height
                    renderLightboxMap(updated);
                    renderLightboxFaces(updated.path);
                    
                    // Update Archive button label on background sync








                    
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





// Lightbox Albums Mapping






// ==========================================
// Video Person Tagging (dropdown, no crop)
// ==========================================
let currentVideoPath = null;
const videoPersonModal = document.getElementById('video-person-modal');
const videoPersonSelect = document.getElementById('video-person-select');
const videoPersonError = document.getElementById('video-person-error');
const cancelVideoPersonBtn = document.getElementById('cancel-video-person-btn');
const confirmVideoPersonBtn = document.getElementById('confirm-video-person-btn');





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
        if(confirm("Are you sure you want to scan the directory for new files?")) {
            fetch('/api/scan_directory', { method: 'POST' }).then(() => {
                alert('Scan for new files started in the background!');
            });
        }
    });
}

const btnTrackMoved = document.getElementById('track-moved-btn');

if (btnRescanMeta) {
    btnRescanMeta.addEventListener('click', () => {
        if(confirm("Are you sure you want to re-extract all EXIF metadata? This may take a while.")) {
            fetch('/api/metadata/rescan', { method: 'POST' }).then(() => {
                alert('Metadata rescan started! Check the top notification bar for progress.');
            });
        }
    });
}

if (btnTrackMoved) {
    btnTrackMoved.addEventListener('click', () => {
        if(confirm("Are you sure you want to track moved/missing files? This scans the entire directory.")) {
            fetch('/api/scan/track_moved', { method: 'POST' }).then(() => {
                alert('Missing files tracking started! Check the top notification bar for progress.');
            });
        }
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


const btnScanObjectAI = document.getElementById('scan-object-ai-btn');
if (btnScanObjectAI) {
    btnScanObjectAI.addEventListener('click', () => {
        if(confirm("Are you sure you want to run the Object AI scan? This will process all unscanned images using the CLIP model.")) {
            fetch('/api/scan/object-ai', { method: 'POST' }).then(() => {
                alert('Object AI scan started! Check the top notification bar for progress.');
            });
        }
    });
}

// Skiper UI Cmd+K / Ctrl+K Command Palette Shortcut
window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

const btnScanHeroAI = document.getElementById('scan-hero-ai-btn');
if (btnScanHeroAI) {
    btnScanHeroAI.addEventListener('click', () => {
        if(confirm("Are you sure you want to run the Hero AI Aesthetic scan? This will process all images.")) {
            fetch('/api/scan/hero-ai', { method: 'POST' }).then(() => {
                alert('Hero AI aesthetic scan started! Check the top notification bar for progress.');
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
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
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
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
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
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
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






// Data & Storage Management
const btnExportCache = document.getElementById('btn-export-cache');
const btnImportCache = document.getElementById('btn-import-cache');
const importCacheInput = document.getElementById('import-cache-input');
const btnDeleteDatabase = document.getElementById('btn-delete-database');


const dataOpModal = document.getElementById('data-op-modal');
const dataOpTitle = document.getElementById('data-op-title');
const dataOpDesc = document.getElementById('data-op-desc');





if (btnExportCache) {
    btnExportCache.addEventListener('click', () => {
        const m = document.getElementById('export-options-modal');
        m.classList.remove('hidden');
        setTimeout(() => m.classList.add('visible'), 10);
    });
}

const confirmExportBtn = document.getElementById('confirm-export-btn');
if (confirmExportBtn) {
    confirmExportBtn.addEventListener('click', async () => {
        document.getElementById('export-options-modal').classList.remove('visible'); setTimeout(()=>document.getElementById('export-options-modal').classList.add('hidden'), 300);
        showDataModal("Exporting Data...", "Gathering selected data and compiling backup. This might take a few minutes.");
        
        const params = new URLSearchParams({
            photos: document.getElementById('exp-photos').checked,
            albums: document.getElementById('exp-albums').checked,
            faces: document.getElementById('exp-faces').checked,
            face_imgs: document.getElementById('exp-face-imgs').checked,
            thumbs: document.getElementById('exp-thumbs').checked,
            ai: document.getElementById('exp-ai').checked
        });
        
        try {
            const response = await fetch('/api/data/export?' + params.toString(), { method: 'GET' });
            if (!response.ok) throw new Error('Network response was not ok');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            const now = new Date();
            const dateStr = now.getFullYear() + '-' + 
                            String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(now.getDate()).padStart(2, '0') + ' ' + 
                            String(now.getHours()).padStart(2, '0') + '-' + 
                            String(now.getMinutes()).padStart(2, '0');
            a.download = `gallery backup ${dateStr}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            hideDataModal();
        } catch (err) {
            hideDataModal();
            alert('Export failed: ' + err.message);
        }
    });
}

if (btnImportCache) {
    btnImportCache.addEventListener('click', () => {
        importCacheInput.click();
    });
}

let pendingImportFile = null;

if (importCacheInput) {
    importCacheInput.addEventListener('change', (e) => {
        if (!e.target.files.length) return;
        pendingImportFile = e.target.files[0];
        document.getElementById('import-options-modal').classList.remove('hidden'); setTimeout(()=>document.getElementById('import-options-modal').classList.add('visible'), 10);
    });
}

const confirmImportBtn = document.getElementById('confirm-import-btn');
if (confirmImportBtn) {
    confirmImportBtn.addEventListener('click', async () => {
        document.getElementById('import-options-modal').classList.remove('visible'); setTimeout(()=>document.getElementById('import-options-modal').classList.add('hidden'), 300);
        if (!pendingImportFile) return;
        
        showDataModal("Importing Backup...", "Uploading and merging selected data. Do not close the window!");
        
        const formData = new FormData();
        formData.append('file', pendingImportFile);
        formData.append('photos', document.getElementById('imp-photos').checked);
        formData.append('albums', document.getElementById('imp-albums').checked);
        formData.append('faces', document.getElementById('imp-faces').checked);
        formData.append('face_imgs', document.getElementById('imp-face-imgs').checked);
        formData.append('thumbs', document.getElementById('imp-thumbs').checked);
        formData.append('ai', document.getElementById('imp-ai').checked);
        
        try {
            const response = await fetch('/api/data/import', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
                dataOpTitle.textContent = "Success!";
                dataOpDesc.textContent = "Data imported successfully. Reloading app...";
                setTimeout(() => window.location.reload(), 1000);
            } else {
                hideDataModal();
                alert('Import failed: ' + data.error);
            }
        } catch (err) {
            hideDataModal();
            alert('Import failed: ' + err);
        }
        
        importCacheInput.value = '';
        pendingImportFile = null;
    });
}


if (btnDeleteDatabase) {
    btnDeleteDatabase.addEventListener('click', async () => {
        if(confirm("WARNING: Are you ABSOLUTELY sure you want to delete ALL database data, mapped faces, and cache? This cannot be undone!")) {
            if(confirm("FINAL CONFIRMATION: Click OK to proceed, or Cancel to abort.")) {
                showDataModal("Erasing Data...", "Permanently deleting all database files, caches, and models. Please wait.");
                
                try {
                    const res = await fetch('/api/data/delete_all', { method: 'POST' });
                    const data = await res.json();
                    
                    if (data.success) {
                if (data.width && data.height) {
                    const cards = document.querySelectorAll('.photo-card');
                    for (const card of cards) {
                        if (card.dataset.path === state.currentLightboxPhoto) {
                            card.dataset.ar = (data.width / data.height).toFixed(3);
                            if (window.applyJustifiedLayout && card.parentElement && !document.body.classList.contains('square-grid-mode')) {
                                window.applyJustifiedLayout(card.parentElement, parseInt(localStorage.getItem('grid-thumbnail-size')) || 180);
                            }
                        }
                    }
                }
                        dataOpTitle.textContent = "Deleted!";
                        dataOpDesc.textContent = "All data has been successfully deleted. Rebooting...";
                        setTimeout(() => window.location.reload(), 1000);
                    } else {
                        hideDataModal();
                        alert('Deletion failed: ' + data.error);
                    }
                } catch(err) {
                    hideDataModal();
                    alert('Deletion failed: ' + err);
                }
            }
        }
    });
}



// Skiper90 Gradient Hover Cards global mouse tracker
document.addEventListener('mousemove', (e) => {
    const card = e.target.closest('.album-card, .person-card, .place-card');
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty('--mouse-x', x + 'px');
    card.style.setProperty('--mouse-y', y + 'px');
});



// Skiper97 Video Player Additions
document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('lightbox-video');
    const pipBtn = document.getElementById('video-pip-btn');
    const captionsBtn = document.getElementById('video-captions-btn');
    const bufferBar = document.getElementById('video-buffer-bar');
    const volumeSlider = document.getElementById('video-volume');
    
    if (video) {
        // Picture-in-Picture
        if (pipBtn) {
            pipBtn.addEventListener('click', async () => {
                try {
                    if (document.pictureInPictureElement) {
                        await document.exitPictureInPicture();
                    } else if (document.pictureInPictureEnabled && video.requestPictureInPicture) {
                        await video.requestPictureInPicture();
                    }
                } catch(e) {
                    console.error('PiP failed', e);
                    alert('Picture-in-Picture is not supported in this environment.');
                }
            });
        }
        
        // Captions Toggle (Dummy for now since no VTT)
        if (captionsBtn) {
            captionsBtn.addEventListener('click', () => {
                alert('No subtitles available for this media.');
            });
        }
        
        // Buffer progress
        video.addEventListener('progress', () => {
            if (video.duration > 0 && video.buffered.length > 0) {
                const bufferedEnd = video.buffered.end(video.buffered.length - 1);
                const pct = (bufferedEnd / video.duration) * 100;
                if (bufferBar) {
                    bufferBar.style.width = pct + '%';
                }
            }
        });
        
        // Custom volume slider background update
        if (volumeSlider) {
            const updateVolBg = () => {
                const pct = volumeSlider.value * 100;
                volumeSlider.style.background = 'linear-gradient(to right, #38bdf8 ' + pct + '%, transparent ' + pct + '%)';
            };
            volumeSlider.addEventListener('input', updateVolBg);
            video.addEventListener('volumechange', () => {
                if(volumeSlider) {
                    volumeSlider.value = video.muted ? 0 : video.volume;
                    updateVolBg();
                }
            });
        }
    }
});

