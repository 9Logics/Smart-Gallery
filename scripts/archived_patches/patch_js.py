import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

target = """    const tl = gsap.timeline();
    
    runnersUp.forEach((runner, i) => {
        if (!runner.cover_face_id) return;
        
        const face = document.createElement('div');
        face.style.position = 'absolute';
        face.style.width = '140px';
        face.style.height = '140px';
        face.style.borderRadius = '50%';
        face.style.background = `url('/api/photo/crop/${runner.cover_face_id}') center/cover`;
        face.style.boxShadow = '0 20px 40px rgba(0,0,0,0.8)';
        face.style.border = '4px solid rgba(255,255,255,0.1)';
        face.style.opacity = '0';
        face.style.left = '50%';
        face.style.top = '50%';
        face.style.marginLeft = '-70px';
        face.style.marginTop = '-70px';
        burstLayer.appendChild(face);
        
        const angle = (i / runnersUp.length) * Math.PI * 2;"""

replacement = """    const tl = gsap.timeline();
    
    const validRunners = runnersUp.filter(r => r.cover_face_id && r.name && !r.name.startsWith('Unnamed') && !r.name.startsWith('Person '));
    if (validRunners.length < 2) {
        callback();
        isRecapTransitioning = false;
        layer.style.display = 'none';
        return;
    }
    
    validRunners.forEach((runner, i) => {
        const face = document.createElement('div');
        face.style.position = 'absolute';
        face.style.width = '140px';
        face.style.height = '140px';
        face.style.borderRadius = '50%';
        face.style.background = `url('/api/photo/crop/${runner.cover_face_id}') center/cover`;
        face.style.boxShadow = '0 20px 40px rgba(0,0,0,0.8)';
        face.style.border = '4px solid rgba(255,255,255,0.1)';
        face.style.opacity = '0';
        face.style.left = '50%';
        face.style.top = '50%';
        face.style.marginLeft = '-70px';
        face.style.marginTop = '-70px';
        burstLayer.appendChild(face);
        
        const angle = (i / validRunners.length) * Math.PI * 2;"""

js = js.replace(target, replacement)
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated mystery reveal logic")
