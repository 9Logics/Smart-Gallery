js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

target = '''    Array.from(clone.children).forEach(c => { c.style.transition='opacity 0.2s'; c.style.opacity='0'; });
    document.body.appendChild(clone);'''

replacement = '''    Array.from(clone.children).forEach(c => { c.style.transition='opacity 0.2s'; c.style.opacity='0'; });
    
    // Put clone inside the overlay so it doesn't obscure the preloader
    const overlay = document.getElementById('recap-player-overlay');
    clone.style.zIndex = '0'; // Put it at the bottom of the overlay's stacking context
    overlay.insertBefore(clone, overlay.firstChild);'''

js = js.replace(target, replacement)
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Moved clone inside overlay")
