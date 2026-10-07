import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_idx = js.find('function populateFilmstrip() {')
end_idx = js.find('function updateVolumeUI() {', start_idx)

new_func = """function populateFilmstrip() {
    const container = document.getElementById('lightbox-filmstrip-container');
    if (!container || container.classList.contains('hidden')) return;
    
    container.innerHTML = '';
    
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
            populateFilmstrip();
        });
        
        const thumb = document.createElement('img');
        thumb.src = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}?s=${photo.size || 0}`;
        thumb.style.height = '100%';
        thumb.style.width = 'auto'; // natural aspect ratio
        thumb.style.objectFit = 'cover';
        thumb.style.display = 'block';
        
        wrapper.appendChild(thumb);
        
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
    
    // Scroll selected to view
    setTimeout(() => {
        const selected = container.children[state.lightboxIndex];
        if (selected) {
            selected.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
    }, 50);
}

"""

js = js[:start_idx] + new_func + js[end_idx:]

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
