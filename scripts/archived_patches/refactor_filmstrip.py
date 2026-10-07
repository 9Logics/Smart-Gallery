import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Replace populateFilmstrip with initFilmstrip and updateFilmstripUI
start_idx = js.find('function toggleFilmstrip() {')
end_idx = js.find('function updateVolumeUI() {', start_idx)

new_funcs = """function toggleFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        updateFilmstripUI(true); // Jump to center when opened
    } else {
        container.classList.add('hidden');
    }
}

function initFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    // Disconnect previous observer if it exists
    if (window.filmstripObserver) {
        window.filmstripObserver.disconnect();
    }
    
    container.innerHTML = '';
    
    // Create new Intersection Observer for lazy loading
    window.filmstripObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    }, { root: container, rootMargin: '300px 0px' });
    
    state.lightboxPhotos.forEach((photo, index) => {
        const wrapper = document.createElement('div');
        wrapper.dataset.index = index;
        wrapper.style.height = '60px';
        wrapper.style.minWidth = '40px';
        wrapper.style.position = 'relative';
        wrapper.style.cursor = 'pointer';
        wrapper.style.flexShrink = '0';
        wrapper.style.borderRadius = '8px';
        wrapper.style.overflow = 'hidden';
        wrapper.style.border = index === state.lightboxIndex ? '2px solid white' : '2px solid transparent';
        wrapper.style.opacity = index === state.lightboxIndex ? '1' : '0.5';
        wrapper.style.transition = 'all 0.2s';
        
        wrapper.onmouseover = () => { wrapper.style.opacity = '1'; };
        wrapper.onmouseout = () => { if (parseInt(wrapper.dataset.index) !== state.lightboxIndex) wrapper.style.opacity = '0.5'; };
        
        wrapper.addEventListener('click', () => {
            if (state.lightboxIndex === index) return; // ignore if already active
            state.lightboxIndex = index;
            if (typeof renderLightboxPhoto === 'function') renderLightboxPhoto();
            updateFilmstripUI();
        });
        
        const thumb = document.createElement('img');
        // Lazy load the thumbnail image
        thumb.dataset.src = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}?s=${photo.size || 0}`;
        thumb.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; // 1x1 placeholder
        thumb.style.height = '100%';
        thumb.style.width = 'auto'; // natural aspect ratio
        thumb.style.objectFit = 'cover';
        thumb.style.display = 'block';
        
        wrapper.appendChild(thumb);
        window.filmstripObserver.observe(thumb);
        
        if (photo.type === 'video' || photo.path.match(/\\.(mp4|mov|avi|mkv|webm)$/i)) {
            const playIcon = document.createElement('div');
            playIcon.innerHTML = '<i data-lucide="play" style="fill: white; width: 14px; height: 14px; color: white;"></i>';
            playIcon.style.position = 'absolute';
            playIcon.style.top = '50%';
            playIcon.style.left = '50%';
            playIcon.style.transform = 'translate(-50%, -50%)';
            playIcon.style.background = 'rgba(0,0,0,0.5)';
            playIcon.style.borderRadius = '50%';
            playIcon.style.padding = '6px';
            playIcon.style.display = 'flex';
            playIcon.style.justifyContent = 'center';
            playIcon.style.alignItems = 'center';
            playIcon.style.backdropFilter = 'blur(4px)';
            wrapper.appendChild(playIcon);
        }
        
        container.appendChild(wrapper);
    });
    
    if (window.lucide) {
        lucide.createIcons({root: container});
    }
    
    updateFilmstripUI(true);
}

function updateFilmstripUI(instant = false) {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container) return;
    
    const children = container.children;
    for (let i = 0; i < children.length; i++) {
        const wrapper = children[i];
        if (i === state.lightboxIndex) {
            wrapper.style.border = '2px solid white';
            wrapper.style.opacity = '1';
        } else {
            wrapper.style.border = '2px solid transparent';
            wrapper.style.opacity = '0.5';
        }
    }
    
    if (!container.classList.contains('hidden')) {
        const selected = container.children[state.lightboxIndex];
        if (selected) {
            selected.scrollIntoView({ behavior: instant ? 'auto' : 'smooth', inline: 'center', block: 'nearest' });
        }
    }
}

"""

js = js[:start_idx] + new_funcs + js[end_idx:]

# 2. Add initFilmstrip to openLightbox()
# Right before the FLIP animation or after removing hidden from elements.lightbox
inject_point = js.find("elements.lightbox.classList.remove('hidden');")
if inject_point != -1:
    inject_str = "elements.lightbox.classList.remove('hidden');\n    \n    initFilmstrip();\n"
    js = js.replace("elements.lightbox.classList.remove('hidden');", inject_str, 1)

# 3. Add updateFilmstripUI to showPrevPhoto and showNextPhoto
prev_target = "renderLightboxPhoto('prev');"
if prev_target in js:
    js = js.replace(prev_target, prev_target + "\n        updateFilmstripUI();")

next_target = "renderLightboxPhoto('next');"
if next_target in js:
    js = js.replace(next_target, next_target + "\n        updateFilmstripUI();")


with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
