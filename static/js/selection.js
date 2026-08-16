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

