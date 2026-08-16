// Metadata Inline Editors
function parseDateParts(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/);
    if (match) {
        return {
            year: match[1],
            month: match[2],
            day: match[3],
            hour: match[4],
            minute: match[5]
        };
    }
    return null;
}

function updateRawDateFromParts() {
    const y = elements.editDateYear.value.trim().padStart(4, '0');
    const m = elements.editDateMonth.value.trim().padStart(2, '0');
    const d = elements.editDateDay.value.trim().padStart(2, '0');
    const h = elements.editDateHour.value.trim().padStart(2, '0');
    const min = elements.editDateMinute.value.trim().padStart(2, '0');
    
    // Default seconds to 00
    if (elements.editDateInput) elements.editDateInput.value = `${y}-${m}-${d} ${h}:${min}:00`;
}

function updatePartsFromRawDate() {
    const parts = parseDateParts(elements.editDateInput ? elements.editDateInput.value : '');
    if (parts) {
        elements.editDateYear.value = parts.year;
        elements.editDateMonth.value = parts.month;
        elements.editDateDay.value = parts.day;
        elements.editDateHour.value = parts.hour;
        elements.editDateMinute.value = parts.minute;
    }
}

// Bind sync events (called once during setup)
if (elements.editDateInput) {
    elements.editDateInput.addEventListener('input', updatePartsFromRawDate);
}
['editDateYear', 'editDateMonth', 'editDateDay', 'editDateHour', 'editDateMinute'].forEach(key => {
    if (elements[key]) {
        elements[key].addEventListener('input', updateRawDateFromParts);
    }
});
if (elements.cancelDateBtn) {
    elements.cancelDateBtn.addEventListener('click', toggleDateEditor);
}

function toggleDateEditor() {
    const isHidden = elements.dateEditorContainer.classList.contains('hidden');
    if (isHidden) {
        const photo = state.lightboxPhotos[state.lightboxIndex];
        const dateStr = photo.date_taken || '';
        if (elements.editDateInput) if (elements.editDateInput) elements.editDateInput.value = dateStr;
        updatePartsFromRawDate();
        elements.dateEditorContainer.classList.remove('hidden');
        elements.editDateYear.focus();
    } else {
        elements.dateEditorContainer.classList.add('hidden');
    }
}

function savePhotoDate() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    const newDate = elements.editDateInput ? elements.editDateInput.value.trim() : '';
    
    elements.saveDateBtn.disabled = true;
    elements.saveDateBtn.innerText = 'Saving...';
    
    fetch('/api/photo/edit_metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            photo_path: photo.path,
            date_taken: newDate
        })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        photo.date_taken = newDate;
        elements.photoDate.innerText = formatPhotoDate(newDate);
        elements.dateEditorContainer.classList.add('hidden');
        loadPhotos(); // Refresh grid dates
    })
    .catch(err => {
        alert(err.message || 'Failed to save date');
    })
    .finally(() => {
        elements.saveDateBtn.disabled = false;
        elements.saveDateBtn.innerText = 'Save';
    });
}

function fixPhotoDateFromFilename() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    elements.fixDateMismatchBtn.disabled = true;
    elements.fixDateMismatchBtn.innerText = 'Fixing...';
    
    fetch('/api/photo/fix-date-from-filename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_path: photo.path })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        if (data.success) {
            photo.date_taken = data.date_taken;
            elements.photoDate.innerText = formatPhotoDate(data.date_taken);
            if (elements.dateMismatchAlert) elements.dateMismatchAlert.classList.add('hidden');
            loadPhotos();
            alert("File creation/modification date successfully corrected on disk and database!");
        }
    })
    .catch(err => {
        alert("Failed to fix date: " + err.message);
    })
    .finally(() => {
        elements.fixDateMismatchBtn.disabled = false;
        elements.fixDateMismatchBtn.innerHTML = '<i data-lucide="wrench" style="width: 12px; height: 12px;"></i> Fix Date on Disk & DB';
        lucide.createIcons();
    });
}

function toggleLocationEditor() {
    const isHidden = elements.locationEditorContainer.classList.contains('hidden');
    if (isHidden) {
        const photo = state.lightboxPhotos[state.lightboxIndex];
        elements.editLocationInput.value = photo.place_name || '';
        elements.locationEditorContainer.classList.remove('hidden');
        elements.editLocationInput.focus();
    } else {
        elements.locationEditorContainer.classList.add('hidden');
    }
}

function savePhotoLocation() {
    const photo = state.lightboxPhotos[state.lightboxIndex];
    if (!photo) return;
    
    const newLocation = elements.editLocationInput.value.trim();
    
    elements.saveLocationBtn.disabled = true;
    elements.saveLocationBtn.innerText = 'Saving...';
    
    fetch('/api/photo/edit_metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            photo_path: photo.path,
            place_name: newLocation || ""
        })
    })
    .then(res => {
        if (!res.ok) return res.json().then(d => { throw new Error(d.error) });
        return res.json();
    })
    .then(data => {
        photo.place_name = newLocation || null;
        elements.photoLocation.innerText = newLocation || 'No location metadata';
        elements.locationEditorContainer.classList.add('hidden');
        loadPhotos(); // Refresh places filters/grids
    })
    .catch(err => {
        alert(err.message || 'Failed to save location');
    })
    .finally(() => {
        elements.saveLocationBtn.disabled = false;
        elements.saveLocationBtn.innerText = 'Save';
    });
}

// Manual Face Bounding Box Selector


// Wheel Logic
function initScrollPicker(id, items) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = '';
    // Pad top and bottom to allow scrolling to first/last
    el.innerHTML += `<div style="height: 43px;"></div>`;
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'scroll-picker-item';
        div.dataset.value = item;
        div.textContent = item;
        el.appendChild(div);
    });
    el.innerHTML += `<div style="height: 43px;"></div>`;

    let scrollTimeout;
    el.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            updateActiveScrollItem(el);
            syncWheelsToRaw();
        }, 100);
    });
    
    // Click to select
    el.addEventListener('click', (e) => {
        if (e.target.classList.contains('scroll-picker-item')) {
            setScrollPickerValue(el, e.target.dataset.value);
        }
    });
}

function updateActiveScrollItem(el) {
    const items = el.querySelectorAll('.scroll-picker-item');
    const centerPosition = el.scrollTop + (el.clientHeight / 2);
    let closestItem = null;
    let minDiff = Infinity;
    
    items.forEach(item => {
        item.classList.remove('active');
        const itemCenter = item.offsetTop + (item.offsetHeight / 2) - el.offsetTop;
        const diff = Math.abs(itemCenter - centerPosition);
        if (diff < minDiff) {
            minDiff = diff;
            closestItem = item;
        }
    });
    if (closestItem) closestItem.classList.add('active');
}

function setScrollPickerValue(el, val) {
    if (!el || !val) return;
    const items = el.querySelectorAll('.scroll-picker-item');
    for (let item of items) {
        if (item.dataset.value === val) {
            el.scrollTo({
                top: item.offsetTop - el.offsetTop - (el.clientHeight / 2) + (item.offsetHeight / 2),
                behavior: 'smooth'
            });
            setTimeout(() => updateActiveScrollItem(el), 300);
            return;
        }
    }
}

function syncWheelsToRaw() {
    const rawInput = document.getElementById('edit-date-raw');
    if (!rawInput) return;
    
    const getVal = (id) => {
        const el = document.getElementById(id);
        if(!el) return '00';
        const active = el.querySelector('.active');
        if (active) return active.dataset.value;
        const items = el.querySelectorAll('.scroll-picker-item');
        if (items.length > 0) return items[0].dataset.value;
        return '00';
    };
    
    const y = getVal('picker-year');
    const m = getVal('picker-month');
    const d = getVal('picker-day');
    
    let hStr = getVal('picker-hour');
    const mi = getVal('picker-minute');
    const ap = getVal('picker-ampm');
    
    let h = parseInt(hStr, 10);
    if (ap === 'PM' && h !== 12) h += 12;
    if (ap === 'AM' && h === 12) h = 0;
    
    const h24 = String(h).padStart(2, '0');
    
    if (y && m && d) {
        rawInput.value = `${y}-${m}-${d} ${h24}:${mi}:00`;
    }
}

function syncRawToWheels() {
    const rawInput = document.getElementById('edit-date-raw');
    if (!rawInput) return;
    const val = rawInput.value.trim();
    if (!val) return;
    
    // Parse YYYY-MM-DD HH:MM:SS
    const parts = val.split(/[^\d]+/);
    if (parts.length >= 3) {
        setScrollPickerValue(document.getElementById('picker-year'), parts[0]);
        setScrollPickerValue(document.getElementById('picker-month'), parts[1]);
        setScrollPickerValue(document.getElementById('picker-day'), parts[2]);
    }
    if (parts.length >= 5) {
        let h = parseInt(parts[3], 10);
        const m = parts[4];
        let ap = 'AM';
        if (h >= 12) {
            ap = 'PM';
            if (h > 12) h -= 12;
        }
        if (h === 0) h = 12;
        
        setScrollPickerValue(document.getElementById('picker-hour'), String(h).padStart(2, '0'));
        setScrollPickerValue(document.getElementById('picker-minute'), m);
        setScrollPickerValue(document.getElementById('picker-ampm'), ap);
    }
}

// Initialize pickers
if (document.getElementById('picker-day')) {
    initScrollPicker('picker-day', wheelData.day);
    initScrollPicker('picker-month', wheelData.month);
    initScrollPicker('picker-year', wheelData.year);
    initScrollPicker('picker-hour', wheelData.hour);
    initScrollPicker('picker-minute', wheelData.minute);
    initScrollPicker('picker-ampm', wheelData.ampm);
    
    const rawInput = document.getElementById('edit-date-raw');
    if (rawInput) {
        rawInput.addEventListener('change', syncRawToWheels);
        rawInput.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') syncRawToWheels();
        });
    }
}

// Override toggleDateEditor to sync raw to wheels upon opening
const originalToggleDateEditor = toggleDateEditor;
window.toggleDateEditor = function() {
    originalToggleDateEditor();
    const isHidden = elements.dateEditorContainer.classList.contains('hidden');
    if (!isHidden) {
        setTimeout(syncRawToWheels, 50); // Small delay to ensure display:flex is rendered so offsetTop works
    }
};
