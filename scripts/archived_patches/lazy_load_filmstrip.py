import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_idx = js.find('function populateFilmstrip() {')
end_idx = js.find('function updateVolumeUI() {', start_idx)

new_func = """function populateFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container || container.classList.contains('hidden')) return;
    
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
        wrapper.onmouseout = () => { if (index !== state.lightboxIndex) wrapper.style.opacity = '0.5'; };
        
        wrapper.addEventListener('click', () => {
            state.lightboxIndex = index;
            renderLightboxPhoto();
            // Re-render filmstrip to update active borders
            populateFilmstrip();
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
    
    // Scroll selected to view without animation so it instantly centers if re-rendered
    setTimeout(() => {
        const selected = container.children[state.lightboxIndex];
        if (selected) {
            // Use auto so re-renders don't cause sliding spasms
            selected.scrollIntoView({ behavior: 'auto', inline: 'center', block: 'nearest' });
        }
    }, 10);
}

"""

js = js[:start_idx] + new_func + js[end_idx:]

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
