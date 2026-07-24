function loadDuplicates() {
    elements.duplicatesGrid.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Scanning for visual duplicates...</p>
        </div>
    `;
    elements.resolveDuplicatesBtn.classList.add('hidden');
    
    fetch('/api/duplicates')
        .then(res => res.json())
        .then(data => {
            state.duplicateGroups = data.map(g => {
                g.checked = true;
                return g;
            });
            renderDuplicates(state.duplicateGroups);
        })
        .catch(err => {
            elements.duplicatesGrid.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="alert-triangle"></i>
                    <p>Failed to scan for duplicates. Check connection.</p>
                </div>
            `;
            lucide.createIcons();
        });
}

// Render duplicate groups cards side-by-side comparison
function renderDuplicates(groups) {
    if (!groups || groups.length === 0) {
        elements.duplicatesGrid.innerHTML = `
            <div class="empty-state">
                <i data-lucide="smile"></i>
                <p>No duplicates found! Your gallery is clean.</p>
            </div>
        `;
        elements.resolveDuplicatesBtn.classList.add('hidden');
        lucide.createIcons();
        return;
    }
    
    // Read the media type filter dropdown
    const filterType = elements.duplicateTypeSelect ? elements.duplicateTypeSelect.value : 'all';
    
    // Filter groups based on type
    const filteredGroups = groups.filter(group => {
        const ext = group.keep.path.split('.').pop().toLowerCase();
        const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
        
        if (filterType === 'photos') return !isVideo;
        if (filterType === 'videos') return isVideo;
        return true; // 'all'
    });
    
    if (filteredGroups.length === 0) {
        elements.duplicatesGrid.innerHTML = `
            <div class="empty-state">
                <i data-lucide="smile"></i>
                <p>No duplicates found matching this media type filter!</p>
            </div>
        `;
        elements.resolveDuplicatesBtn.classList.add('hidden');
        lucide.createIcons();
        return;
    }
    
    elements.duplicatesGrid.innerHTML = '';
    elements.resolveDuplicatesBtn.classList.remove('hidden');
    
    const initialCheckedCount = filteredGroups.filter(g => g.checked !== false).length;
    elements.resolveDuplicatesBtn.innerHTML = `<i data-lucide="trash-2"></i> Resolve ${initialCheckedCount} checked group(s)`;
    elements.resolveDuplicatesBtn.disabled = (initialCheckedCount === 0);
    
    // Store filtered groups reference
    state.activeFilteredGroups = filteredGroups;
    
    filteredGroups.forEach((group) => {
        const originalIndex = state.duplicateGroups.indexOf(group);
        
        const card = document.createElement('div');
        card.className = 'duplicate-group-card';
        card.dataset.index = originalIndex;
        
        const isKeepVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(group.keep.path.split('.').pop().toLowerCase());
        const isDeleteVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(group.delete[0].path.split('.').pop().toLowerCase());
        
        // Render Group Card
        card.innerHTML = `
            <div class="duplicate-group-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <input type="checkbox" class="group-select-checkbox" ${group.checked !== false ? 'checked' : ''} style="width:16px; height:16px; cursor:pointer; accent-color:var(--primary-color);" title="Include in bulk Resolve All">
                    <span class="duplicate-reason-badge">${group.reason}</span>
                </div>
                <div style="display:flex; gap:10px; align-items:center;">
                    <button class="btn btn-secondary swap-btn" style="padding: 4px 10px; font-size:12px; height:auto; display:flex; align-items:center;" title="Swap Keep and Delete suggested files">
                        <i data-lucide="refresh-cw" style="width:12px; height:12px; margin-right:4px;"></i> Swap Sides
                    </button>
                    <button class="btn btn-secondary delete-both-btn" style="padding: 4px 10px; font-size:12px; height:auto; background-color:rgba(239, 68, 68, 0.1); color:#ef4444; border-color:rgba(239, 68, 68, 0.2); display:flex; align-items:center;" title="Move both files to Recycle Bin">
                        <i data-lucide="trash-2" style="width:12px; height:12px; margin-right:4px;"></i> Delete Both
                    </button>
                    <button class="btn btn-primary resolve-btn" style="padding: 4px 10px; font-size:12px; height:auto; background-color:rgba(239, 68, 68, 0.85); border-color:transparent; display:flex; align-items:center;" title="Resolve this duplicate group only">
                        <i data-lucide="trash-2" style="width:12px; height:12px; margin-right:4px;"></i> Resolve Group
                    </button>
                </div>
            </div>
            
            <div class="duplicate-comparison-grid">
                <!-- Keep Card (Suggested Original) -->
                <div class="duplicate-item-panel keep">
                    <span class="duplicate-item-badge">Keep</span>
                    <div class="duplicate-thumb">
                        <img src="/api/photo/thumbnail/${encodeURIComponent(group.keep.path)}" alt="${group.keep.filename}">
                        ${isKeepVideo ? '<div class="video-badge" style="top:5px; right:5px; padding:4px;"><i data-lucide="play" style="width:10px; height:10px;"></i></div>' : ''}
                    </div>
                    <div class="duplicate-details">
                        <h4 title="${group.keep.filename}">${group.keep.filename}</h4>
                        <div class="duplicate-path" title="${group.keep.path}">${group.keep.path}</div>
                        <div class="duplicate-meta-row">
                            <div class="duplicate-meta-item" title="File Size">
                                <i data-lucide="hard-drive"></i>
                                <span>${(group.keep.size / (1024*1024)).toFixed(2)} MB</span>
                            </div>
                            <div class="duplicate-meta-item" title="Resolution">
                                <i data-lucide="maximize"></i>
                                <span>${group.keep.width}x${group.keep.height}</span>
                            </div>
                            <div class="duplicate-meta-item" title="Date Taken">
                                <i data-lucide="calendar"></i>
                                <span>${group.keep.date_taken ? group.keep.date_taken.split(' ')[0] : 'No date'}</span>
                            </div>
                            ${group.keep.place_name ? `
                            <div class="duplicate-meta-item" title="Location: ${group.keep.place_name}">
                                <i data-lucide="map-pin"></i>
                                <span style="max-width:120px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${group.keep.place_name}</span>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
                
                <!-- Delete Card (Suggested Duplicate) -->
                <div class="duplicate-item-panel delete">
                    <span class="duplicate-item-badge">Delete</span>
                    <div class="duplicate-thumb">
                        <img src="/api/photo/thumbnail/${encodeURIComponent(group.delete[0].path)}" alt="${group.delete[0].filename}">
                        ${isDeleteVideo ? '<div class="video-badge" style="top:5px; right:5px; padding:4px;"><i data-lucide="play" style="width:10px; height:10px;"></i></div>' : ''}
                    </div>
                    <div class="duplicate-details">
                        <h4 title="${group.delete[0].filename}">${group.delete[0].filename}</h4>
                        <div class="duplicate-path" title="${group.delete[0].path}">${group.delete[0].path}</div>
                        <div class="duplicate-meta-row">
                            <div class="duplicate-meta-item" title="File Size">
                                <i data-lucide="hard-drive"></i>
                                <span>${(group.delete[0].size / (1024*1024)).toFixed(2)} MB</span>
                            </div>
                            <div class="duplicate-meta-item" title="Resolution">
                                <i data-lucide="maximize"></i>
                                <span>${group.delete[0].width}x${group.delete[0].height}</span>
                            </div>
                            <div class="duplicate-meta-item" title="Date Taken">
                                <i data-lucide="calendar"></i>
                                <span>${group.delete[0].date_taken ? group.delete[0].date_taken.split(' ')[0] : 'No date'}</span>
                            </div>
                            ${group.delete[0].place_name ? `
                            <div class="duplicate-meta-item" title="Location: ${group.delete[0].place_name}">
                                <i data-lucide="map-pin"></i>
                                <span style="max-width:120px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${group.delete[0].place_name}</span>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add events
        card.querySelector('.swap-btn').addEventListener('click', () => {
            swapDuplicateGroup(originalIndex);
        });
        
        card.querySelector('.delete-both-btn').addEventListener('click', () => {
            deleteBothDuplicates(originalIndex);
        });
        
        card.querySelector('.resolve-btn').addEventListener('click', () => {
            resolveSingleDuplicateGroup(originalIndex);
        });
        
        const checkbox = card.querySelector('.group-select-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                group.checked = e.target.checked;
                
                // Recalculate count and update resolve all button
                const active = state.activeFilteredGroups || state.duplicateGroups;
                const checkedCount = active.filter(g => g.checked !== false).length;
                elements.resolveDuplicatesBtn.innerHTML = `<i data-lucide="trash-2"></i> Resolve ${checkedCount} checked group(s)`;
                elements.resolveDuplicatesBtn.disabled = (checkedCount === 0);
            });
        }
        
        elements.duplicatesGrid.appendChild(card);
    });
    
    lucide.createIcons();
}

// Action resolving all duplicate groups at once
function resolveDuplicates() {
    const activeGroups = (state.activeFilteredGroups || state.duplicateGroups).filter(g => g.checked !== false);
    if (!activeGroups || activeGroups.length === 0) return;
    
    const count = activeGroups.length;
    if (!confirm(`Are you sure you want to resolve and clean up duplicates for the ${count} checked duplicate group(s)? This will permanently delete duplicate files from your disk and rename kept copies to remove copy suffixes where necessary.`)) {
        return;
    }
    
    elements.resolveDuplicatesBtn.disabled = true;
    elements.resolveDuplicatesBtn.innerText = 'Resolving duplicates...';
    
    const resolutions = [];
    activeGroups.forEach(group => {
        group.delete.forEach(delItem => {
            resolutions.push({
                delete_path: delItem.path,
                keep_path: group.keep.path,
                action: group.action
            });
        });
    });
    
    fetch('/api/duplicates/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolutions })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        alert(`Successfully resolved duplicates!\nDeleted: ${data.deleted} files.\nRenamed: ${data.renamed} original files to remove copy suffixes.`);
        loadStaticData();
        loadDuplicates();
    })
    .catch(err => {
        alert(err.message || 'Failed to resolve duplicates');
        elements.resolveDuplicatesBtn.disabled = false;
        elements.resolveDuplicatesBtn.innerHTML = `<i data-lucide="trash-2"></i> Resolve all ${count} groups`;
        lucide.createIcons();
    });
}

function swapDuplicateGroup(gIndex) {
    const group = state.duplicateGroups[gIndex];
    if (!group) return;
    
    const oldKeep = group.keep;
    const oldDelete = group.delete[0];
    
    // Swap keep/delete lists
    group.keep = oldDelete;
    group.delete[0] = oldKeep;
    
    // Recalculate action
    const ext = group.keep.filename.split('.').pop();
    const nameWithoutExt = group.keep.filename.substring(0, group.keep.filename.length - ext.length - 1);
    const pattern = /(\s*\(\d+\)|\s*-\s*Copy(\s*\(\d+\))?)+$/i;
    
    if (pattern.test(nameWithoutExt)) {
        group.action = "KEEP_AND_RENAME";
        group.reason = "Swapped by user: Kept copy will be renamed to clean up the suffix.";
    } else {
        group.action = "KEEP_AS_IS";
        group.reason = "Swapped by user: Kept selected original.";
    }
    
    renderDuplicates(state.duplicateGroups);
}

function resolveSingleDuplicateGroup(gIndex) {
    const group = state.duplicateGroups[gIndex];
    if (!group) return;
    
    if (!confirm(`Are you sure you want to resolve duplicates for this group? This will permanently delete the suggested file for deletion and rename/keep the selected original.`)) {
        return;
    }
    
    const resolutions = [];
    group.delete.forEach(delItem => {
        resolutions.push({
            delete_path: delItem.path,
            keep_path: group.keep.path,
            action: group.action
        });
    });
    
    fetch('/api/duplicates/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolutions })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        alert("Group resolved successfully!");
        state.duplicateGroups.splice(gIndex, 1);
        loadStaticData();
        renderDuplicates(state.duplicateGroups);
    })
    .catch(err => {
        alert(err.message || 'Failed to resolve duplicate group');
    });
}

function deleteBothDuplicates(gIndex) {
    const group = state.duplicateGroups[gIndex];
    if (!group) return;
    
    if (!confirm(`Are you sure you want to move BOTH files to the Recycle Bin?`)) {
        return;
    }
    
    const paths = [group.keep.path];
    group.delete.forEach(d => paths.push(d.path));
    
    fetch('/api/trash/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photos: paths })
    })
    .then(res => res.json())
    .then(data => {
        alert("Both copies moved to Recycle Bin successfully.");
        state.duplicateGroups.splice(gIndex, 1);
        loadStaticData();
        renderDuplicates(state.duplicateGroups);
    })
    .catch(err => {
        alert("Failed to delete both duplicates: " + err.message);
    });
}

// Load Recycle Bin (Trash) Photos
