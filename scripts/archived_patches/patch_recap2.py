js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

mystery_func = '''
function playMysteryRevealTransition(targetName, runnersUp, callback) {
    if (isRecapTransitioning) return;
    isRecapTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'flex';
    layer.style.alignItems = 'center';
    layer.style.justifyContent = 'center';
    layer.style.overflow = 'hidden';
    layer.innerHTML = '';
    layer.style.background = '#050505';
    layer.style.backdropFilter = 'none';
    
    if (!window.gsap || !runnersUp || runnersUp.length < 2) {
        callback();
        isRecapTransitioning = false;
        layer.style.display = 'none';
        return;
    }
    
    const flashText = document.createElement('h1');
    flashText.style.fontSize = '8rem';
    flashText.style.fontWeight = '900';
    flashText.style.color = '#fff';
    flashText.style.textShadow = '0 0 40px rgba(208, 188, 255, 0.8)';
    flashText.style.letterSpacing = '-0.05em';
    flashText.style.fontFamily = "'Outfit', sans-serif";
    flashText.style.position = 'absolute';
    flashText.style.zIndex = '10';
    flashText.style.opacity = '0';
    flashText.style.transform = 'scale(0.8)';
    layer.appendChild(flashText);
    
    const burstLayer = document.createElement('div');
    burstLayer.style.position = 'absolute';
    burstLayer.style.inset = '0';
    layer.appendChild(burstLayer);
    
    const tl = gsap.timeline();
    
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
        
        const angle = (i / runnersUp.length) * Math.PI * 2;
        const dist = 250 + Math.random() * 250;
        const tx = Math.cos(angle) * dist;
        const ty = Math.sin(angle) * dist;
        
        tl.to(face, {
            x: tx, y: ty, scale: 1, opacity: 1, rotation: -20 + Math.random()*40,
            duration: 0.3, ease: "back.out(1.5)"
        }, i * 0.08);
        
        tl.call(() => {
            flashText.innerText = runner.name;
        }, null, i * 0.08);
    });
    
    tl.to(flashText, { opacity: 1, scale: 1, duration: 0.2, ease: "power2.out" }, 0);
    
    tl.to(burstLayer.children, {
        x: 0, y: 0, scale: 0, opacity: 0, rotation: 180,
        duration: 0.5, ease: "power4.in", stagger: 0.015
    }, "+=0.3");
    
    const flashBang = document.createElement('div');
    flashBang.style.position = 'absolute';
    flashBang.style.inset = '0';
    flashBang.style.background = '#fff';
    flashBang.style.opacity = '0';
    flashBang.style.zIndex = '100';
    layer.appendChild(flashBang);
    
    tl.to(flashText, { scale: 1.5, opacity: 0, filter: 'blur(20px)', duration: 0.3, ease: "power3.in" }, "-=0.3");
    tl.to(flashBang, { opacity: 1, duration: 0.15, ease: "none" }, "-=0.15");
    
    tl.call(() => {
        callback();
    });
    
    tl.to(layer, { opacity: 0, duration: 1.0, ease: "power2.out", delay: 0.1 })
      .call(() => {
          layer.style.display = 'none';
          layer.style.opacity = '1';
          layer.innerHTML = '';
          isRecapTransitioning = false;
          
          const revealedName = document.getElementById('recap-stat-person');
          if (revealedName && window.gsap) {
              gsap.fromTo(revealedName, { scale: 1.5, y: -50, opacity: 0, filter: 'blur(10px)' }, { scale: 1, y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.5, ease: "elastic.out(1, 0.5)" });
          }
      });
}

'''

js = js.replace('function playSkiper79Transition', mystery_func + '\nfunction playSkiper79Transition')

target_next = '''if (nextSlideId === 'slide-person') { transitionTitle = "TOP PERSON"; transitionPhotos = recapData?.top_person_photos || null; }
        if (nextSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }'''

rep_next = '''if (nextSlideId === 'slide-person') { 
            playMysteryRevealTransition(recapData?.top_person || "Someone Special", recapData?.runners_up || [], () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });
            return;
        }
        if (nextSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }'''
js = js.replace(target_next, rep_next)


target_prev = '''if (prevSlideId === 'slide-person') { transitionTitle = "TOP PERSON"; transitionPhotos = recapData?.top_person_photos || null; }
        if (prevSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }'''

rep_prev = '''if (prevSlideId === 'slide-person') { 
            playMysteryRevealTransition(recapData?.top_person || "Someone Special", recapData?.runners_up || [], () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
            return;
        }
        if (prevSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }'''
js = js.replace(target_prev, rep_prev)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Injected Mystery Reveal Transition safely")
