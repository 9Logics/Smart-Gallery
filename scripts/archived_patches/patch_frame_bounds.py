import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    // Allow up to 90% of screen size to leave room for padding
    const maxWidth = container.clientWidth * 0.90;
    const maxHeight = container.clientHeight * 0.90;"""

replacement = """    // Check if it's a video to reserve space for the controls
    const ext = photo.path ? photo.path.split('.').pop().toLowerCase() : '';
    const isVideo = ['mp4', 'mov', 'm4v', 'hevc'].includes(ext);
    
    // Allow up to 90% of screen size to leave room for padding
    const maxWidth = container.clientWidth * 0.90;
    // Reserve an extra 80px for video controls if it's a video
    const maxHeight = (container.clientHeight * 0.90) - (isVideo ? 80 : 0);"""

if target in js:
    js = js.replace(target, replacement)
    print("Replaced updateMorphFrameBounds logic")
else:
    print("Target not found in core.js")

with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
    f.write(js)
