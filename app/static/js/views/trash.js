function loadTrashPhotos() {
    elements.trashGridRoot.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading Recycle Bin...</p>
        </div>
    `;
    elements.restoreAllTrashBtn.classList.add('hidden');
    
    const sortVal = state.trashSortBy || 'date_desc';
    fetch(`/api/photos?trashed=true&sort=${sortVal}`)
        .then(res => res.json())
        .then(data => {
            state.trashedPhotos = data;
            renderTrashGrid(data);
        })
        .catch(err => {
            elements.trashGridRoot.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="alert-triangle"></i>
                    <p>Failed to load Recycle Bin.</p>
                </div>
            `;
            lucide.createIcons();
        });
}

function getDaysLeft(trashedAtStr) {
    if (!trashedAtStr) return 30;
    try {
        const parts = trashedAtStr.split(' ');
        const dateParts = parts[0].split('-');
        const timeParts = parts[1].split(':');
        const trashedDate = new Date(dateParts[0], dateParts[1] - 1, dateParts[2], timeParts[0], timeParts[1], timeParts[2]);
        const diffTime = Math.abs(new Date() - trashedDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const daysLeft = 30 - diffDays;
        return Math.max(0, daysLeft);
    } catch (e) {
        return 30;
    }
}

function renderTrashGrid(photos) {
    if (!photos || photos.length === 0) {
        elements.trashGridRoot.innerHTML = `
            <div class="empty-state">
                <i data-lucide="trash-2" style="width: 48px; height: 48px; stroke-width: 1.5; color: var(--text-muted);"></i>
                <p>Your Recycle Bin is empty.</p>
            </div>
        `;
        elements.restoreAllTrashBtn.classList.add('hidden');
        lucide.createIcons();
        return;
    }
    
    elements.trashGridRoot.innerHTML = '';
    elements.restoreAllTrashBtn.classList.remove('hidden');
    
    photos.forEach(photo => {
        const item = document.createElement('div');
        item.className = 'photo-card';
        item.style.position = 'relative';
        
        const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(photo.file_type.toLowerCase());
        const daysLeft = getDaysLeft(photo.trashed_at);
        
        item.innerHTML = `
            <div class="photo-thumb-container" style="filter: grayscale(0.5) opacity(0.85); position: relative;">
                <img class="photo-thumbnail" src="/api/photo/thumbnail/${encodeURIComponent(photo.path)}" alt="${photo.filename}">
                ${isVideo ? '<div class="video-badge"><i data-lucide="play"></i></div>' : ''}
                
                <!-- Overlay Badges -->
                <div style="position: absolute; top: 8px; left: 8px; background: rgba(15, 22, 38, 0.8); backdrop-filter: blur(4px); color: #fff; font-size: 10px; font-weight: 700; padding: 3px 6px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.15); z-index: 10;">
                    ${(photo.size / (1024*1024)).toFixed(2)} MB
                </div>
                
                <div style="position: absolute; bottom: 8px; left: 8px; background: rgba(239, 68, 68, 0.95); color: #fff; font-size: 10px; font-weight: 600; padding: 3px 6px; border-radius: 4px; z-index: 10; display: flex; align-items: center; gap: 4px;">
                    <i data-lucide="clock" style="width: 10px; height: 10px;"></i> ${daysLeft}d left
                </div>
            </div>
            <div class="photo-info" style="display:flex; flex-direction:column; gap:4px; padding: 10px;">
                <span class="photo-title" title="${photo.filename}" style="font-weight: 500; font-size:13px; max-width:100%; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${photo.filename}</span>
                <span style="font-size:11px; color:var(--text-muted);">${(photo.size / (1024*1024)).toFixed(2)} MB</span>
            </div>
            <!-- Overlay controls -->
            <div style="position: absolute; top: 8px; right: 8px; display: flex; gap: 6px; z-index: 10;">
                <button class="btn btn-secondary restore-single-btn" style="padding: 0; width: 28px; height: 28px; display: flex; align-items:center; justify-content:center; border-radius: 4px; border-color: rgba(255,255,255,0.25);" title="Restore original file">
                    <i data-lucide="rotate-ccw" style="width: 14px; height: 14px;"></i>
                </button>
                <button class="btn btn-primary delete-single-btn" style="padding: 0; width: 28px; height: 28px; display: flex; align-items:center; justify-content:center; border-radius: 4px; background-color: rgba(239, 68, 68, 0.9); border-color:transparent;" title="Delete permanently">
                    <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                </button>
            </div>
        `;
        
        // Restore single event
        item.querySelector('.restore-single-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            restoreTrashPhotos([photo.path]);
        });
        
        // Delete single permanently event
        item.querySelector('.delete-single-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm(`Are you sure you want to move to the Recycle Bin "${photo.filename}" from disk? This action is irreversible.`)) {
                purgeSinglePhoto(photo.path);
            }
        });
        
        elements.trashGridRoot.appendChild(item);
    });
    
    lucide.createIcons();
}

