import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Define createCyclingDeck at the top
if 'window.recapDeckIntervals' not in js:
    js = "window.recapDeckIntervals = [];\n\n" + js

deck_logic = '''
function createCyclingDeck(containerId, photos, featurePhoto) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    
    if (!photos || photos.length === 0) return;
    
    let deck = [];
    if (featurePhoto) deck.push(featurePhoto);
    for (let i = 0; i < photos.length; i++) {
        if (deck.length >= 7) break;
        if (photos[i] !== featurePhoto && !deck.includes(photos[i])) {
            deck.push(photos[i]);
        }
    }
    
    deck.forEach((p, idx) => {
        const div = document.createElement('div');
        div.className = containerId === 'person-photos-fan' ? 'person-fan-photo' : 'place-fan-photo';
        if (featurePhoto && p === featurePhoto && deck.length > 1) {
            div.classList.add('feature-photo');
        }
        
        // Stack them
        let initialZ = (idx === 0) ? deck.length - 1 : (deck.length - 1 - idx);
        const r = (Math.random() - 0.5) * 16; // Random rotation
        
        div.style.zIndex = initialZ;
        div.dataset.rot = r;
        div.style.transform = `translate(0px, 0px) rotate(${r}deg)`;
        
        div.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(p)}" />`;
        container.appendChild(div);
    });
    
    if (deck.length > 1) {
        let interval = setInterval(() => {
            let cards = Array.from(container.children);
            let topCard = cards.find(c => parseInt(c.style.zIndex) === cards.length - 1);
            if (!topCard) return;
            
            let origRot = parseFloat(topCard.dataset.rot || 0);
            
            // 1. Swipe out right
            topCard.style.transform = `translate(180px, -30px) rotate(${origRot + 25}deg)`;
            
            // 2. Slip behind after visually clearing the stack
            setTimeout(() => {
                cards.forEach(c => {
                    let z = parseInt(c.style.zIndex);
                    if (z === cards.length - 1) {
                        c.style.zIndex = 0;
                    } else {
                        c.style.zIndex = z + 1;
                    }
                });
                topCard.style.transform = `translate(0px, 0px) rotate(${origRot}deg)`;
            }, 350); 
            
        }, 2200); // specific intervals
        
        window.recapDeckIntervals.push(interval);
    }
}
'''

# Check if createCyclingDeck is already defined to prevent duplicates
if 'function createCyclingDeck' not in js:
    js = deck_logic + "\n" + js

# 2. Replace Person and Place generation inside fetch
old_person_pattern = r"document\.getElementById\('recap-stat-person'\)\.innerText = data\.top_person \|\| \"Yourself!\";.*?// Render Person Fan Photos.*?if \(fanPhotos\.length > 0\) \{.*?\n\s+\}\n\s+\}"
new_person = r"document.getElementById('recap-stat-person').innerText = data.top_person || \"Yourself!\";\n              createCyclingDeck('person-photos-fan', data.top_person_photos, data.top_person_feature);"
js = re.sub(old_person_pattern, new_person, js, flags=re.DOTALL)

old_place_pattern = r"const fan = document\.getElementById\('place-photos-fan'\);.*?fan\.innerHTML = '';.*?if \(data\.iconic_place_photos && data\.iconic_place_photos\.length > 0\) \{.*?photos\.forEach.*?fan\.appendChild\(div\);\n\s+\}\);\n\s+\}"
new_place = r"createCyclingDeck('place-photos-fan', data.iconic_place_photos, null);"
js = re.sub(old_place_pattern, new_place, js, flags=re.DOTALL)


# 3. Clear intervals in closeRecapPlayer
old_close = r"function closeRecapPlayer\(\) \{"
new_close = r'''function closeRecapPlayer() {
    if (window.recapDeckIntervals) {
        window.recapDeckIntervals.forEach(clearInterval);
        window.recapDeckIntervals = [];
    }'''
if 'window.recapDeckIntervals.forEach(clearInterval);' not in js:
    js = js.replace(old_close, new_close)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Implemented Skiper54 cycling deck animation for recap slides.")
