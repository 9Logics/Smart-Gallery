import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """            if (data.success) {
                if (icon) {
                    const originalLucide = icon.getAttribute('data-lucide');
                    icon.setAttribute('data-lucide', 'check');
                    icon.style.color = '#10b981';
                    lucide.createIcons();
                    setTimeout(() => {
                        icon.setAttribute('data-lucide', originalLucide);
                        icon.style.color = '';
                        lucide.createIcons();
                        const path = state.currentLightboxPhoto;
                        closeLightbox();
                        setTimeout(() => openLightbox(path), 300);
                    }, 1500);
                } else {
                    const path = state.currentLightboxPhoto;
                    closeLightbox();
                    setTimeout(() => openLightbox(path), 300);
                }
            }"""

replacement = """            if (data.success) {
                // Update local state with fresh DB data (size, width, height, etc.)
                if (data.photo) {
                    const idx = state.lightboxPhotos.findIndex(p => p.path === state.currentLightboxPhoto);
                    if (idx !== -1) {
                        state.lightboxPhotos[idx] = Object.assign({}, state.lightboxPhotos[idx], data.photo);
                    }
                }
                
                if (icon) {
                    const originalLucide = icon.getAttribute('data-lucide');
                    icon.setAttribute('data-lucide', 'check');
                    icon.style.color = '#10b981';
                    lucide.createIcons();
                    setTimeout(() => {
                        icon.setAttribute('data-lucide', originalLucide);
                        icon.style.color = '';
                        lucide.createIcons();
                        const path = state.currentLightboxPhoto;
                        closeLightbox();
                        setTimeout(() => openLightbox(path), 300);
                    }, 1500);
                } else {
                    const path = state.currentLightboxPhoto;
                    closeLightbox();
                    setTimeout(() => openLightbox(path), 300);
                }
            }"""

if target in js:
    js = js.replace(target, replacement)
    print("Replaced JS successfully")
else:
    print("Target not found in core.js!")

with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
    f.write(js)
