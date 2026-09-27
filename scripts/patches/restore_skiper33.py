import re

old_js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\old_recap.js"
new_js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"

with open(old_js_path, "r", encoding="utf-8") as f:
    old_code = f.read()

# Extract old playSlideTransition
start_idx = old_code.find("function playSlideTransition(callback) {")
end_idx = old_code.find("function prevRecapSlide() {", start_idx)
playSlideTransition_code = old_code[start_idx:end_idx]

# Rewrite skiper-33 branch inside the extracted code
skiper33_start = playSlideTransition_code.find("} else if (type === 'skiper-33') {")
skiper33_end = playSlideTransition_code.find("} else {", skiper33_start)

new_skiper33 = """} else if (type === 'skiper-33') {
        // Skiper 33: Tilted 2-Column Perspective Grid Scroll
        layer.style.background = '#000';
        layer.style.perspective = '1200px';
        
        const grid = document.createElement('div');
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(2, 1fr)';
        grid.style.gap = '20px';
        grid.style.width = '60vw';
        // Need enough items to scroll
        grid.style.position = 'absolute';
        
        // The distinct Skiper 33 look: 3D rotation leaning back
        grid.style.transformStyle = 'preserve-3d';
        grid.style.transform = 'rotateX(30deg) rotateY(-15deg) rotateZ(10deg)';
        
        // Add a bunch of square images
        let pool = [...photos, ...photos, ...photos, ...photos]; // ensure enough
        pool.sort(() => 0.5 - Math.random());
        
        for(let i=0; i<12; i++) {
            const img = document.createElement('img');
            img.src = '/api/photo/file/' + encodeURIComponent(pool[i]);
            img.style.width = '100%';
            img.style.aspectRatio = '1 / 1';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '16px'; // A bit of radius as per image
            img.style.opacity = '0';
            img.style.boxShadow = '0 10px 40px rgba(0,0,0,0.8)';
            grid.appendChild(img);
        }
        
        layer.appendChild(grid);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        // Initial setup for the scroll animation
        const imgs = grid.querySelectorAll('img');
        gsap.set(grid, { y: '50vh' });
        
        tl.to(layer, { opacity: 1, duration: 0.3 }, 0);
        
        // Fade in images with stagger
        tl.to(imgs, {
            opacity: 0.8,
            duration: 0.5,
            stagger: 0.05
        }, 0);
        
        // Scroll the grid upwards in 3D space
        tl.to(grid, {
            y: '-100vh',
            duration: 2.0,
            ease: "power2.inOut",
            onComplete: () => {
                if(callback) { callback(); callback = null; }
            }
        }, 0);
        
        // Fade out
        tl.to(layer, {
            opacity: 0,
            duration: 0.4,
            ease: "power2.in"
        }, "-=0.4");
        
    """

if skiper33_start != -1 and skiper33_end != -1:
    playSlideTransition_code = playSlideTransition_code[:skiper33_start] + new_skiper33 + playSlideTransition_code[skiper33_end:]

# Now inject it back into the active recap_player.js
with open(new_js_path, "r", encoding="utf-8") as f:
    new_code = f.read()

inject_idx = new_code.find("function prevRecapSlide() {")
if inject_idx != -1:
    new_code = new_code[:inject_idx] + playSlideTransition_code + "\n\n" + new_code[inject_idx:]
    with open(new_js_path, "w", encoding="utf-8") as f:
        f.write(new_code)
    print("Successfully restored playSlideTransition and upgraded Skiper 33")
else:
    print("Could not find insertion point!")
