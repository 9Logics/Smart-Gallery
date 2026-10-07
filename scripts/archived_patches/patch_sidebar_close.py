import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """            elements.lightbox.style.animation = 'modalFadeOut 0.3s ease forwards';
            
            const containerRect = container.getBoundingClientRect();"""

replacement = """            elements.lightbox.style.animation = 'modalFadeOut 0.3s ease forwards';
            
            const sidebar = document.querySelector('.lightbox-sidebar');
            if (sidebar && elements.lightbox.classList.contains('info-open')) {
                sidebar.style.animation = 'none';
                void sidebar.offsetWidth;
                sidebar.style.animation = 'lightboxSlideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards';
            }
            
            const containerRect = container.getBoundingClientRect();"""

if target in js:
    js = js.replace(target, replacement)
    print("Patched closeLightbox with sidebar slideout")
else:
    print("Target not found in lightbox.js!")

# Also fix the fallback close!
target2 = """    // Fallback: fade out
    elements.lightbox.style.animation = 'modalFadeOut 0.2s ease forwards';
    setTimeout(completeClose, 200);"""

replacement2 = """    // Fallback: fade out
    elements.lightbox.style.animation = 'modalFadeOut 0.2s ease forwards';
    const sidebar = document.querySelector('.lightbox-sidebar');
    if (sidebar && elements.lightbox.classList.contains('info-open')) {
        sidebar.style.animation = 'none';
        void sidebar.offsetWidth;
        sidebar.style.animation = 'lightboxSlideOutRight 0.2s cubic-bezier(0.4, 0, 0.2, 1) forwards';
    }
    setTimeout(completeClose, 200);"""

if target2 in js:
    js = js.replace(target2, replacement2)
    print("Patched fallback close")
else:
    print("Target2 not found in lightbox.js!")

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
