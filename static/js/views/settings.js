// Settings View Logic

let heroAllPhotosCache = [];
let heroOverridesCache = { whitelist: [], blacklist: [] };
let currentOverrideType = 'whitelist'; // 'whitelist' or 'blacklist'
let selectedOverridePaths = new Set();

// Ensure loadSettings is called to init
function initSettingsView() {
    loadHeroOverrides();
}

// Fetch and render the current overrides
async function loadHeroOverrides() {
    try {
        const res = await fetch('/api/settings/hero_overrides');
        const data = await res.json();
        heroOverridesCache = data;
        
        renderOverrideGrid('hero-whitelist-grid', data.whitelist || [], 'whitelist');
        renderOverrideGrid('hero-blacklist-grid', data.blacklist || [], 'blacklist');
    } catch (e) {
        console.error("Failed to load hero overrides", e);
    }
}

function renderOverrideGrid(containerId, paths, type) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (paths.length === 0) {
        container.innerHTML = `<div style="padding: 16px; color: var(--text-muted); font-size: 13px;">No ${type}ed images.</div>`;
        return;
    }
    
    paths.forEach(path => {
        const div = document.createElement('div');
        div.className = 'photo-item';
        div.style.position = 'relative';
        div.style.width = '100%';
        div.style.paddingBottom = '100%';
        div.style.borderRadius = '6px';
        div.style.overflow = 'hidden';
        
        const img = document.createElement('img');
        img.src = '/api/photo/thumbnail/' + encodeURIComponent(path.replace(/\\/g, '/'));
        img.style.position = 'absolute';
        img.style.top = '0';
        img.style.left = '0';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn-icon remove-override-btn';
        removeBtn.innerHTML = '<i data-lucide="x"></i>';
        removeBtn.style.position = 'absolute';
        removeBtn.style.top = '4px';
        removeBtn.style.right = '4px';
        removeBtn.style.background = 'rgba(0,0,0,0.6)';
        removeBtn.style.color = '#fff';
        removeBtn.style.padding = '4px';
        removeBtn.style.borderRadius = '50%';
        removeBtn.style.display = 'none';
        
        div.addEventListener('mouseenter', () => removeBtn.style.display = 'block');
        div.addEventListener('mouseleave', () => removeBtn.style.display = 'none');
        
        removeBtn.onclick = (e) => {
            e.stopPropagation();
            removeHeroOverride(path, type);
        };
        
        div.appendChild(img);
        div.appendChild(removeBtn);
        container.appendChild(div);
    });
    
    if (window.lucide) lucide.createIcons();
}

async function removeHeroOverride(path, type) {
    try {
        await fetch('/api/settings/hero_override', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: path, status: 'remove' })
        });
        loadHeroOverrides();
    } catch (e) {
        console.error("Failed to remove override", e);
    }
}

// Open the photo picker modal
async function openPhotoPicker(type) {
    currentOverrideType = type;
    selectedOverridePaths.clear();
    
    const modal = document.getElementById('hero-photo-picker-modal');
    const title = document.getElementById('hero-photo-picker-title');
    const grid = document.getElementById('hero-photo-picker-grid');
    
    title.innerText = `Select Photos to ${type === 'whitelist' ? 'Whitelist' : 'Blacklist'}`;
    grid.innerHTML = '<div style="padding: 20px;">Loading photos...</div>';
    
    modal.classList.remove('hidden');
    
    try {
        // Fetch up to 500 photos for picking
        let fetchUrl = '/api/settings/hero_all_photos?per_page=500';
        if (type === 'blacklist') {
            fetchUrl = '/api/settings/hero_scenic_photos?per_page=500';
        }
        const res = await fetch(fetchUrl);
        const data = await res.json();
        const existingOverrides = new Set(heroOverridesCache[type] || []);
        heroAllPhotosCache = (data.photos || []).filter(p => !existingOverrides.has(p.path));
        
        renderPickerGrid();
    } catch (e) {
        grid.innerHTML = '<div style="padding: 20px; color: #ef4444;">Failed to load photos</div>';
    }
}

function closeHeroPhotoPicker() {
    document.getElementById('hero-photo-picker-modal').classList.add('hidden');
}

function renderPickerGrid() {
    const grid = document.getElementById('hero-photo-picker-grid');
    grid.innerHTML = '';
    
    heroAllPhotosCache.forEach(photo => {
        const div = document.createElement('div');
        div.className = 'photo-item';
        div.style.position = 'relative';
        div.style.width = '100%';
        div.style.paddingBottom = '100%';
        div.style.borderRadius = '6px';
        div.style.overflow = 'hidden';
        div.style.cursor = 'pointer';
        
        const img = document.createElement('img');
        img.src = '/api/photo/thumbnail/' + encodeURIComponent(photo.path.replace(/\\/g, '/'));
        img.style.position = 'absolute';
        img.style.top = '0';
        img.style.left = '0';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        
        const checkIcon = document.createElement('div');
        checkIcon.className = 'picker-check-icon';
        checkIcon.innerHTML = '<i data-lucide="check" style="width:14px; height:14px;"></i>';
        checkIcon.style.position = 'absolute';
        checkIcon.style.bottom = '8px';
        checkIcon.style.right = '8px';
        checkIcon.style.background = 'var(--accent-color)';
        checkIcon.style.color = '#fff';
        checkIcon.style.borderRadius = '50%';
        checkIcon.style.padding = '2px';
        checkIcon.style.display = 'none';
        
        div.onclick = () => {
            if (selectedOverridePaths.has(photo.path)) {
                selectedOverridePaths.delete(photo.path);
                div.style.border = 'none';
                checkIcon.style.display = 'none';
            } else {
                selectedOverridePaths.add(photo.path);
                div.style.border = '2px solid var(--accent-color)';
                checkIcon.style.display = 'block';
            }
        };
        
        div.appendChild(img);
        div.appendChild(checkIcon);
        grid.appendChild(div);
    });
    
    if (window.lucide) lucide.createIcons();
}

async function saveHeroOverrides() {
    if (selectedOverridePaths.size === 0) {
        closeHeroPhotoPicker();
        return;
    }
    
    const saveBtn = document.getElementById('save-overrides-btn');
    const originalText = saveBtn.innerText;
    saveBtn.innerText = 'Saving...';
    saveBtn.disabled = true;
    
    try {
        for (const path of selectedOverridePaths) {
            await fetch('/api/settings/hero_override', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ path: path, status: currentOverrideType })
            });
        }
    } catch (e) {
        console.error("Error saving overrides", e);
    }
    
    saveBtn.innerText = originalText;
    saveBtn.disabled = false;
    closeHeroPhotoPicker();
    loadHeroOverrides();
}

// Global exposure
window.initSettingsView = initSettingsView;
window.loadHeroOverrides = loadHeroOverrides;
window.openPhotoPicker = openPhotoPicker;
window.closeHeroPhotoPicker = closeHeroPhotoPicker;
window.removeHeroOverride = removeHeroOverride;
window.saveHeroOverrides = saveHeroOverrides;
