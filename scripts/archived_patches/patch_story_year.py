import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    // Text overlays
    const tTitle = document.getElementById('story-bar-title');
    if (tTitle) tTitle.innerText = card.title || '';
    const tSub = document.getElementById('story-top-subtitle');
    if (tSub) tSub.innerText = card.subtitle || '';
    
    const dDate = new Date(photo.date_taken || photo.created_at);
    const tDate = document.getElementById('story-date-text');
    if (tDate) {
        if (!isNaN(dDate)) {
            tDate.innerText = dDate.toLocaleDateString(undefined, { year: 'numeric', month: '2-digit', day: '2-digit' });
        } else {
            tDate.innerText = '';
        }
    }
    
    const hTitle = document.getElementById('story-title');
    if (hTitle) hTitle.innerText = card.title || '';
    const hSub = document.getElementById('story-subtitle');
    if (hSub) hSub.innerText = card.subtitle || '';"""

replacement = """    // Text overlays
    const tTitle = document.getElementById('story-bar-title');
    if (tTitle) tTitle.innerText = card.title || '';
    
    const dDate = new Date(photo.date_taken || photo.created_at || photo.date);
    
    const tSub = document.getElementById('story-top-subtitle');
    if (tSub) {
        if (!isNaN(dDate)) {
            tSub.innerText = dDate.getFullYear().toString();
        } else {
            tSub.innerText = card.subtitle || '';
        }
    }
    
    const tDate = document.getElementById('story-date-text');
    if (tDate) {
        tDate.innerText = ''; // Clear out the full date
    }
    
    const hTitle = document.getElementById('story-title');
    if (hTitle) hTitle.innerText = card.title || '';
    const hSub = document.getElementById('story-subtitle');
    if (hSub) {
        if (!isNaN(dDate)) {
            hSub.innerText = dDate.getFullYear().toString();
        } else {
            hSub.innerText = card.subtitle || '';
        }
    }"""

if target in js:
    js = js.replace(target, replacement)
    with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched story_viewer.js successfully.")
else:
    print("Target block not found.")
