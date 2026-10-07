d = open('app/static/js/lightbox.js', 'r', encoding='utf-8').read()

js_addition = '''
// Filmstrip Logic
const filmstripToggleBtn = document.getElementById('lightbox-filmstrip-toggle');
if (filmstripToggleBtn) {
    filmstripToggleBtn.addEventListener('click', toggleFilmstrip);
}

function toggleFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        populateFilmstrip();
    } else {
        container.classList.add('hidden');
    }
}

function populateFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container || container.classList.contains('hidden')) return;
    
    container.innerHTML = '';
    
    state.lightboxPhotos.forEach((photo, index) => {
        const thumb = document.createElement('img');
        // Use thumb size for fast loading
        thumb.src = `/api/photo/file/${encodeURIComponent(photo.path)}?s=thumb`;
        thumb.style.height = '100%';
        thumb.style.aspectRatio = '1 / 1';
        thumb.style.objectFit = 'cover';
        thumb.style.borderRadius = '4px';
        thumb.style.cursor = 'pointer';
        thumb.style.border = index === state.lightboxIndex ? '2px solid var(--accent-color)' : '2px solid transparent';
        thumb.style.opacity = index === state.lightboxIndex ? '1' : '0.6';
        thumb.style.flexShrink = '0';
        thumb.style.transition = 'all 0.2s';
        
        thumb.onmouseover = () => { thumb.style.opacity = '1'; };
        thumb.onmouseout = () => { if (index !== state.lightboxIndex) thumb.style.opacity = '0.6'; };
        
        thumb.addEventListener('click', () => {
            state.lightboxIndex = index;
            renderLightboxPhoto();
            // populateFilmstrip is called by renderLightboxPhoto below if we hook it
        });
        
        container.appendChild(thumb);
    });
    
    // Scroll selected to view
    const selected = container.children[state.lightboxIndex];
    if (selected) {
        selected.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }
}
'''

# Also, we need to call populateFilmstrip() in renderLightboxPhoto so it updates when arrows are used
# Let's find a good place in renderLightboxPhoto
# `updateLocationUI(photo);` is a good anchor
d = d.replace('updateLocationUI(photo);', 'updateLocationUI(photo);\n    if (typeof populateFilmstrip === "function") populateFilmstrip();')

# Append the new logic to the end
d += js_addition

open('app/static/js/lightbox.js', 'w', encoding='utf-8').write(d)
