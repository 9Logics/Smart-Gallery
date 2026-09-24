import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix closeRecapPlayer to restore opacity
old_close = '''function closeRecapPlayer() {
    document.getElementById('recap-player-overlay').classList.add('hidden');
    const clone = document.querySelector('.recap-transition-clone');
    if (clone) clone.remove();
}'''

new_close = '''function closeRecapPlayer() {
    document.getElementById('recap-player-overlay').classList.add('hidden');
    const clone = document.querySelector('.recap-transition-clone');
    if (clone) clone.remove();
    
    // Restore opacity to all cards that might have been clicked
    document.querySelectorAll('.rewind-hero-card, .rewind-mini-card').forEach(card => {
        card.style.opacity = '1';
    });
}'''

js = js.replace(old_close, new_close)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Fixed closeRecapPlayer to restore opacity!")
