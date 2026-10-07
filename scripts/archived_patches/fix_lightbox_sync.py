import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    d = f.read()

target = """    elements.lightbox.classList.remove('hidden');
    
    // Animate background overlay fade in"""

replacement = """    elements.lightbox.classList.remove('hidden');
    
    // Sync the info panel class state before any layout bounds are calculated
    if (state.isLightboxInfoOpen) {
        elements.lightbox.classList.add('info-open');
        elements.lightboxSidebar.classList.remove('hidden');
        elements.lightboxSidebar.classList.add('open');
        elements.lightboxInfoToggle.style.backgroundColor = 'var(--accent-color)';
    } else {
        elements.lightbox.classList.remove('info-open');
        elements.lightboxSidebar.classList.add('hidden');
        elements.lightboxSidebar.classList.remove('open');
        elements.lightboxInfoToggle.style.backgroundColor = 'rgba(15, 22, 38, 0.6)';
    }
    
    // Animate background overlay fade in"""

if target in d:
    d = d.replace(target, replacement)
    print("Successfully patched openLightbox")
else:
    print("WARNING: target not found")

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(d)
