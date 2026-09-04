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
            appAlert("Failed to set cover: " + data.error);
        } else {
            loadStaticData();
            renderLightboxFaces(photoPath);
        }
    })
    .catch(err => appAlert("Error setting cover photo"));
}

function renamePersonPrompt(id, currentName) {
    const cleanName = currentName.startsWith('Person ') ? '' : currentName;
    const newName = prompt(`Enter name for this person (currently "${currentName}"):`, cleanName);
    
    if (newName === null) return; // Cancelled
    
    const trimmed = newName.trim();
    if (!trimmed) return;
    
    API.renamePerson(id, trimmed)
    .then(data => {
        if (data.error) {
            appAlert("Failed to rename: " + data.error);
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
    .catch(err => appAlert("Error communicating with server"));
}

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
    .catch(err => appAlert("Error deleting face label: " + err.message));
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
    .catch(err => appAlert("Failed to unname person"));
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
    .catch(err => appAlert("Failed to delete person"));
}

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
        
        API.renameAlbum(albumId, newName ).then(data => {
            if (data.success) {
                modal.classList.add('hidden');
                loadAlbums(); // refresh albums view
            } else {
                appAlert(data.error || 'Failed to rename album');
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
                    API.setAlbumCover(albumId, photo.path).then(() => {
                        modal.classList.add('hidden');
                        loadAlbums(); // refresh albums view
                    });
                });
                
                grid.appendChild(img);
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
            appAlert("File was found at a new location! Updating gallery link and reloading...");
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
                    appAlert('Please enter a directory path to search.');
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
                        appAlert("File found! Updating gallery...");
                        closeLightbox();
                        loadStaticData();
                        setTimeout(() => openLightbox(rData.new_path), 500);
                    } else {
                        appAlert("File was not found in that directory.");
                    }
                })
                .catch(() => {
                    appAlert("Error searching directory.");
                    cleanupModal();
                });
            };
        }
    })
    .catch(err => {
        document.body.removeChild(loadingDiv);
        appAlert("Error while searching for missing file.");
    });
}

function showDataModal(title, desc) {
    if(!dataOpModal) return;
    dataOpTitle.textContent = title;
    dataOpDesc.textContent = desc;
    dataOpModal.classList.remove('hidden');
    setTimeout(() => dataOpModal.classList.add('visible'), 10);
}

function hideDataModal() {
    if(!dataOpModal) return;
    dataOpModal.classList.remove('visible');
    setTimeout(() => dataOpModal.classList.add('hidden'), 300);
}
window.openPersonCoverModal = function(personId) {
    const modal = document.getElementById('person-cover-photo-modal');
    const grid = document.getElementById('person-cover-photo-grid');
    grid.innerHTML = '<div style="width: 100%; text-align: center; padding: 20px; color: var(--text-color);">Loading faces...</div>';
    modal.classList.remove('hidden');
    
    const cancelBtn = document.getElementById('cancel-person-cover-btn');
    const newCancelBtn = cancelBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    newCancelBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });
    
    fetch(`/api/people/${personId}/faces`)
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = '';
            if (!data.faces || data.faces.length === 0) {
                grid.innerHTML = '<div style="width: 100%; text-align: center; padding: 20px; color: var(--text-color);">No faces available.</div>';
                return;
            }
            
            data.faces.forEach(face => {
                const faceDiv = document.createElement('div');
                faceDiv.style.aspectRatio = '1';
                faceDiv.style.borderRadius = '50%';
                faceDiv.style.overflow = 'hidden';
                faceDiv.style.cursor = 'pointer';
                faceDiv.style.border = '2px solid transparent';
                faceDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
                
                faceDiv.innerHTML = `<img src="/api/photo/crop/${face.id}" style="width: 100%; height: 100%; object-fit: cover;" loading="lazy">`;
                
                faceDiv.addEventListener('mouseover', () => faceDiv.style.borderColor = 'var(--accent-color)');
                faceDiv.addEventListener('mouseout', () => faceDiv.style.borderColor = 'transparent');
                
                faceDiv.addEventListener('click', () => {
                    fetch('/api/people/set-cover', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ person_id: personId, face_id: face.id })
                    })
                    .then(r => r.json())
                    .then(res => {
                        modal.classList.add('hidden');
                        if (window.loadStaticData) window.loadStaticData(); // Refresh sidebar
                        
                        // Update the hero avatar dynamically
                        const heroAvatar = document.getElementById('person-hero-avatar');
                        if (heroAvatar) {
                            heroAvatar.src = `/api/photo/crop/${face.id}?_t=${Date.now()}`;
                        }
                    })
                    .catch(e => console.error(e));
                });
                
                grid.appendChild(faceDiv);
            });
        })
        .catch(err => {
            grid.innerHTML = '<div style="width: 100%; text-align: center; padding: 20px; color: red;">Failed to load.</div>';
        });
};
