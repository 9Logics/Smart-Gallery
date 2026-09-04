function pollScanStatus() {
    API.getScanStatus()
        .then(data => {
            const wasScanning = (state.scanStatus === 'scanning');
            state.scanStatus = data.status;
            
            if (data.status === 'scanning') {
                elements.scanPill.className = 'scan-pill scanning';
                elements.scanText.innerText = `Scanning: ${data.processed}/${data.total}`;
                
                // Update progress box in Settings
                elements.scanProgressBox.classList.remove('hidden');
                elements.progressFile.innerText = (data.phase ? `${data.phase}: ` : "") + data.current_file;
                
                const pct = data.total > 0 ? Math.round((data.processed / data.total) * 100) : 0;
                elements.progressPercent.innerText = `${data.processed}/${data.total} (${pct}%)`;
                elements.progressBarFill.style.width = `${pct}%`;
                
                // Update circular progress squircle
                const ringEl = document.getElementById('scan-ring-progress');
                if (ringEl) {
                    const circumference = 102.83;
                    const offset = circumference - (circumference * pct / 100);
                    ringEl.setAttribute('stroke-dashoffset', offset);
                }

                // Update percentage text under icon
                const pctEl = document.getElementById('scan-percentage');
                if (pctEl) {
                    pctEl.innerText = `${pct}%`;
                    pctEl.style.opacity = '1';
                }
                
                // --- NEW SLIDEOUT PANEL ---
                const wrapper = document.getElementById('scan-slideout-wrapper');
                if (wrapper) {
                    wrapper.classList.remove('hidden');
                    // Automatically open on new scan if it wasn't scanning before
                    if (!wasScanning && !wrapper.dataset.userToggled) {
                        toggleScanSlideout(true);
                    }
                    
                    document.getElementById('slideout-title-text').childNodes[0].nodeValue = (data.phase ? data.phase + ":" : "Scanning:");
                    document.getElementById('slideout-file-name').innerText = data.current_file;
                    document.getElementById('slideout-count').innerText = `${data.processed}/${data.total}`;
                    document.getElementById('slideout-pct').innerText = `(${pct}%)`;
                    document.getElementById('slideout-bar-fill').style.width = `${pct}%`;
                    
                    const qIndicator = document.getElementById('slideout-queue-indicator');
                    if (qIndicator) {
                        if (data.queue_count > 0) {
                            qIndicator.classList.remove('hidden');
                            document.getElementById('slideout-queue-count').innerText = `${data.queue_count} in queue`;
                        } else {
                            qIndicator.classList.add('hidden');
                        }
                    }
                }

                // Disable all settings scan buttons
                const buttons = [
                    'start-scan-btn', 'scan-directory-btn', 'rescan-metadata-btn', 'track-moved-btn', 
                    'rebuild-cache-btn', 'refresh-places-btn', 'force-cluster-btn', 
                    'rescan-faces-btn', 'reevaluate-faces-btn', 'scan-hero-ai-btn', 'scan-object-ai-btn'
                ];
                buttons.forEach(id => {
                    const btn = document.getElementById(id);
                    if (btn) btn.disabled = true;
                });
            } else {
                elements.scanPill.className = 'scan-pill idle';
                elements.scanText.innerText = 'Gallery Idle';
                
                // Reset progress squircle
                const ringEl = document.getElementById('scan-ring-progress');
                if (ringEl) ringEl.setAttribute('stroke-dashoffset', '102.83');

                // Hide percentage text
                const pctEl = document.getElementById('scan-percentage');
                if (pctEl) pctEl.style.opacity = '0';
                
                elements.scanProgressBox.classList.add('hidden');
                
                // Hide Slideout
                const wrapper = document.getElementById('scan-slideout-wrapper');
                if (wrapper) {
                    wrapper.classList.add('hidden');
                    wrapper.dataset.userToggled = '';
                }
                
                if (elements.cancelScanBtn) {
                    elements.cancelScanBtn.disabled = false;
                    elements.cancelScanBtn.innerText = 'Cancel';
                }
                
                // Re-enable all settings scan buttons
                const buttons = [
                    'start-scan-btn', 'scan-directory-btn', 'rescan-metadata-btn', 'track-moved-btn', 
                    'rebuild-cache-btn', 'refresh-places-btn', 'force-cluster-btn', 
                    'rescan-faces-btn', 'reevaluate-faces-btn', 'scan-hero-ai-btn', 'scan-object-ai-btn'
                ];
                buttons.forEach(id => {
                    const btn = document.getElementById(id);
                    if (btn) btn.disabled = false;
                });
                
                // If scanning just finished, trigger a reload of the current view and references
                if (wasScanning) {
                    loadStaticData();
                    refreshCurrentView();
                    lucide.createIcons();
                }
            }
            // Queue next poll ONLY if scanning or queued
            if (data.status === 'scanning' || data.queue_count > 0) {
                setTimeout(pollScanStatus, 250);
            }
        })
        .catch(err => {
            console.warn("Scan poll failed, retrying in 2s:", err);
            setTimeout(pollScanStatus, 2000);
        });

}

function refreshCurrentView() {
    if (state.currentView === 'photos') loadPhotos();
    else if (state.currentView === 'albums') loadAlbums();
    else if (state.currentView === 'people') loadPeople();
    else if (state.currentView === 'places') loadPlaces();
}

// Fetch Settings
function fetchSettings() {
    fetch('/api/settings')
        .then(res => res.json())
        .then(data => {
            state.scanFolder = data.scan_folder || '';
            elements.scanFolderInput.value = data.scan_folder || '';
            
            // If scanning directory is not configured, redirect to settings
            if (!data.scan_folder) {
                switchView('settings');
            } else {
                loadPhotos();
            }
        });
}

// Trigger Scan
function startScan() {
    const folder = elements.scanFolderInput.value.trim();
    if (!folder) {
        showScanError("Please specify a directory path");
        return;
    }
    
    elements.scanErrorMsg.classList.add('hidden');
    elements.startScanBtn.disabled = true;
    
    fetch('/api/settings/scan-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        state.scanFolder = folder;
        showScanSuccess();
        pollScanStatus();
    })
    .catch(err => {
        console.error("Scan start error:", err);
        elements.startScanBtn.disabled = false;
        showScanError("Failed to communicate with server");
    });
}

function cancelScan() {
    if (elements.cancelScanBtn) {
        elements.cancelScanBtn.disabled = true;
        elements.cancelScanBtn.innerText = 'Cancelling...';
    }
    
    fetch('/api/scan/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            console.error("Cancel failed:", data.message);
            if (elements.cancelScanBtn) {
                elements.cancelScanBtn.disabled = false;
                elements.cancelScanBtn.innerText = 'Cancel';
            }
        }
    })
    .catch(err => {
        console.error("Error cancelling scan:", err);
        if (elements.cancelScanBtn) {
            elements.cancelScanBtn.disabled = false;
            elements.cancelScanBtn.innerText = 'Cancel';
        }
    });
}

function showScanError(msg) {
    elements.scanErrorMsg.innerText = msg;
    elements.scanErrorMsg.classList.remove('hidden');
}

function showScanSuccess() {
    elements.scanErrorMsg.className = 'error-text hidden';
}



// Slideout toggle
function toggleScanSlideout(open) {
    const wrapper = document.getElementById('scan-slideout-wrapper');
    const panel = document.getElementById('scan-slideout-panel');
    const toggleBtn = document.getElementById('scan-slideout-toggle');
    
    if (wrapper) wrapper.dataset.userToggled = 'true';
    
    if (open) {
        panel.classList.remove('collapsed');
        toggleBtn.classList.add('hidden');
    } else {
        panel.classList.add('collapsed');
        toggleBtn.classList.remove('hidden');
    }
}
