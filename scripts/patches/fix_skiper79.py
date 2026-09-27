import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

start_idx = js_code.find("function playSkiper79Transition(titleText, callback) {")
end_idx = js_code.find("function prevRecapSlide() {", start_idx)

new_fn = '''function playSkiper79Transition(titleText, callback) {
    if (isRecapTransitioning) return;
    isRecapTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'flex';
    layer.style.alignItems = 'center';
    layer.style.justifyContent = 'center';
    layer.style.overflow = 'hidden';
    layer.innerHTML = '';
    
    // Skiper 79 aesthetic: Stark black background, B&W staggered images, massive solid typography
    layer.style.background = '#0a0a0a';
    layer.style.backdropFilter = 'none';
    
    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    let imgsToUse = [];
    if (photos.length > 0) {
        let pool = [...photos].sort(() => 0.5 - Math.random());
        // Pick 4 random photos for the collage
        while(pool.length > 0 && imgsToUse.length < 4) {
            imgsToUse.push(pool.pop());
        }
    }
    
    const positions = [
        { top: '-5%', left: '-5%', width: '35vw', height: '45vh', zIndex: '2' },
        { top: '0%', right: '5%', width: '25vw', height: '35vh', zIndex: '1' },
        { bottom: '-10%', left: '10%', width: '20vw', height: '35vh', zIndex: '3' },
        { bottom: '5%', right: '-5%', width: '35vw', height: '45vh', zIndex: '2' }
    ];
    
    let imgElements = [];
    imgsToUse.forEach((p, i) => {
        let pos = positions[i % positions.length];
        let img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(p);
        img.style.position = 'absolute';
        img.style.objectFit = 'cover';
        img.style.filter = 'grayscale(100%) contrast(120%)';
        img.style.opacity = '0';
        img.style.zIndex = pos.zIndex;
        
        if (pos.top) img.style.top = pos.top;
        if (pos.bottom) img.style.bottom = pos.bottom;
        if (pos.left) img.style.left = pos.left;
        if (pos.right) img.style.right = pos.right;
        img.style.width = pos.width;
        img.style.height = pos.height;
        
        layer.appendChild(img);
        imgElements.push(img);
    });
    
    // Center Text Container
    const textContainer = document.createElement('div');
    textContainer.style.position = 'relative';
    textContainer.style.zIndex = '10';
    textContainer.style.textAlign = 'center';
    
    const h1 = document.createElement('h1');
    // Title case the text to match Skiper 79 "Speakers"
    let formattedText = titleText.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
    h1.innerText = formattedText;
    h1.style.fontFamily = "'Outfit', sans-serif";
    h1.style.fontWeight = '800';
    h1.style.fontSize = '14vw';
    h1.style.color = '#ffffff';
    h1.style.letterSpacing = '-0.04em';
    h1.style.lineHeight = '1';
    h1.style.margin = '0';
    
    const subText = document.createElement('p');
    subText.innerText = "PROJECT GALLERY REWIND";
    subText.style.fontFamily = "'Outfit', sans-serif";
    subText.style.fontWeight = '600';
    subText.style.fontSize = '1vw';
    subText.style.letterSpacing = '0.2em';
    subText.style.color = 'rgba(255,255,255,0.5)';
    subText.style.marginTop = '10px';
    
    textContainer.appendChild(h1);
    textContainer.appendChild(subText);
    
    // Initial animation state
    gsap.set(textContainer, { opacity: 0, scale: 0.8 });
    gsap.set(imgElements, { scale: 1.1 });
    gsap.set(layer, { opacity: 1 });
    layer.appendChild(textContainer);
    
    let tl = gsap.timeline();
    
    // Reveal images with staggered fade and slight scale down
    tl.to(imgElements, {
        opacity: 0.7,
        scale: 1,
        duration: 1.2,
        stagger: 0.1,
        ease: "power3.out"
    }, 0);
    
    // Reveal text aggressively
    tl.to(textContainer, {
        opacity: 1,
        scale: 1,
        duration: 1,
        ease: "back.out(1.2)"
    }, 0.2);
    
    // Hold frame for the swap
    tl.add(() => {
        if (callback) callback();
    }, "+=1.0");
    
    // Fly out
    tl.to(textContainer, {
        scale: 1.1,
        opacity: 0,
        duration: 0.5,
        ease: "power2.in"
    }, "+=0.2");
    
    tl.to(imgElements, {
        scale: 1.05,
        opacity: 0,
        duration: 0.4,
        stagger: 0.05,
        ease: "power2.in"
    }, "<0.1");
    
    tl.to(layer, {
        opacity: 0,
        duration: 0.3,
        onComplete: () => {
            layer.style.display = 'none';
            isRecapTransitioning = false;
        }
    });
}

'''

js_code = js_code[:start_idx] + new_fn + js_code[end_idx:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Rebuilt Skiper 79 transition with perfect aesthetic match.")
