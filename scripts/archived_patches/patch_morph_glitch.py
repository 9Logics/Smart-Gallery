import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Start of openLightbox
target1 = """        elements.lightboxImg.src = thumbImg.src;
        elements.lightboxImg.style.opacity = '1';
        elements.lightboxImg.style.objectFit = 'cover';"""
replacement1 = """        elements.lightboxImg.src = thumbImg.src;
        elements.lightboxImg.style.opacity = '1';
        elements.lightboxImg.style.objectFit = 'cover';
        elements.lightboxImgBuffer.style.objectFit = 'cover';"""

# 2. Inside close FLIP animation fallback? 
# Wait, let's just do a global replace for objectFit assignments in lightbox.js
# There are specific blocks. Let's be precise.

target2 = """            elements.lightboxImg.style.objectFit = 'cover';
            
            // Force reflow"""
replacement2 = """            elements.lightboxImg.style.objectFit = 'cover';
            elements.lightboxImgBuffer.style.objectFit = 'cover';
            
            // Force reflow"""

target3 = """            elements.lightboxImg.style.objectFit = '';
            if (sidebar) sidebar.style.animation = '';"""
replacement3 = """            elements.lightboxImg.style.objectFit = '';
            elements.lightboxImgBuffer.style.objectFit = '';
            if (sidebar) sidebar.style.animation = '';"""

target4 = """    }
    elements.lightboxImg.style.objectFit = '';
}

function showPrevPhoto()"""
replacement4 = """    }
    elements.lightboxImg.style.objectFit = '';
    elements.lightboxImgBuffer.style.objectFit = '';
}

function showPrevPhoto()"""

js = js.replace(target1, replacement1)
js = js.replace(target2, replacement2)
js = js.replace(target3, replacement3)
js = js.replace(target4, replacement4)

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated lightbox.js")
