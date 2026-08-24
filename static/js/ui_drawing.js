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

