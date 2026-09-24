import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace generateYearlyTheme body
old_pattern = r"(function generateYearlyTheme\(year\) \{)(.*?)(?=\nfunction closeRecapPlayer)"

new_body = '''
    const container = document.getElementById('theme-canvas');
    if (!container) return;
    container.innerHTML = '';
    
    // Seeded random based on year string
    let seedStr = String(year);
    let seed = 0;
    for (let i = 0; i < seedStr.length; i++) {
        seed += seedStr.charCodeAt(i) * (i + 1);
    }
    
    const myRand = () => {
        let x = Math.sin(seed++) * 10000;
        return x - Math.floor(x);
    };
    
    // Pick ONE solid theme color for the entire year
    const themeColors = [
        '#FF0A54', '#00BBF9', '#FEE440', '#00F5D4', '#9B5DE5', '#FA709A', '#8AC926', '#1982C4', '#FF595E'
    ];
    const themeColor = themeColors[Math.floor(myRand() * themeColors.length)];
    
    // Remove filters
    container.style.filter = "none";
    container.style.mixBlendMode = "normal";
    
    const svgShapes = [
        '<circle cx="12" cy="12" r="12" fill="currentColor"/>',
        '<rect x="0" y="0" width="24" height="24" fill="currentColor" transform="rotate(45 12 12)"/>',
        '<polygon points="12,0 24,24 0,24" fill="currentColor"/>',
        '<path d="M10 0h4v10h10v4H14v10h-4V14H0v-4h10z" fill="currentColor"/>', // Cross
        '<polygon points="12,0 15,9 24,9 17,14 19,23 12,18 5,23 7,14 0,9 9,9" fill="currentColor"/>' // Star
    ];
    
    // Create 30 confetti pieces
    for(let i=0; i<30; i++) {
        const svgWrapper = document.createElement('div');
        svgWrapper.className = 'confetti-piece';
        
        // Randomize shape
        const shape = svgShapes[Math.floor(myRand() * svgShapes.length)];
        
        // Build SVG
        svgWrapper.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" style="color: ${themeColor}; width: 100%; height: 100%;">${shape}</svg>`;
        
        // Randomize size, position, duration, and delay
        const size = (15 + myRand() * 25) + 'px';
        svgWrapper.style.width = size;
        svgWrapper.style.height = size;
        svgWrapper.style.left = (myRand() * 100) + 'vw';
        
        // Fall duration between 4s and 12s
        svgWrapper.style.animationDuration = (4 + myRand() * 8) + 's';
        
        // Negative delay so they start already on screen instead of waiting
        svgWrapper.style.animationDelay = '-' + (myRand() * 10) + 's';
        
        container.appendChild(svgWrapper);
    }
}
'''

js = re.sub(old_pattern, r"\1" + new_body, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Replaced generateYearlyTheme with SVG confetti!")
