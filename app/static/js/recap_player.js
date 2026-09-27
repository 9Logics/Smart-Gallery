

// --- [REGION: CYCLING DECK ENGINE (SKIPER-54)] ---
function initSkiper47Carousel(containerId, photos, featurePhoto) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    let deck = [];
    if (featurePhoto) deck.push(featurePhoto);
    for (let i = 0; i < photos.length; i++) {
        if (deck.length >= 10) break;
        if (photos[i] !== featurePhoto && !deck.includes(photos[i])) deck.push(photos[i]);
    }
    
    let swiperHtml = `<div class="swiper skiper-47-swiper"><div class="swiper-wrapper">`;
    deck.forEach(p => {
        swiperHtml += `<div class="swiper-slide skiper-47-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" /></div>`;
    });
    swiperHtml += `</div><div class="swiper-pagination"></div></div>`;
    
    container.innerHTML = swiperHtml;
    
    new Swiper('.skiper-47-swiper', {
        effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto',
        observer: true,
        observeParents: true,
        loop: true,
        coverflowEffect: {
            rotate: 45,
            stretch: -20,
            depth: 300,
            modifier: 1,
            slideShadows: true,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
}


window.recapDeckIntervals = [];

// Recap Player Logic

let recapCurrentSlide = 0;
let recapSlides = [];
let recapData = null;


// Skiper37 Number Flow Animation
function animateNumberFlow(obj, start, end, duration) {
    obj.innerHTML = '';
    const endStr = String(end);
    
    for (let i = 0; i < endStr.length; i++) {
        const targetDigit = parseInt(endStr[i]);
        const column = document.createElement('div');
        column.className = 'number-flow-digit';
        
        // We will create a strip of numbers 0-9 repeatedly, then stop at the target
        let strip = '';
        // Add 20 digits to scroll through for effect
        for(let j=0; j<20; j++) {
            strip += `<span>${j % 10}</span>`;
        }
        strip += `<span>${targetDigit}</span>`;
        column.innerHTML = strip;
        obj.appendChild(column);
        
        // Trigger animation
        requestAnimationFrame(() => {
            const digitHeight = 100; // matches line-height
            const totalScroll = 20 * digitHeight;
            column.style.transform = `translateY(-${totalScroll}px)`;
            // Stagger columns slightly
            column.style.transitionDelay = `${i * 0.1}s`;
        });
    }
}

// Skiper29 Siena Parallax Depth Hover - Professional rAF Lerp Implementation
let targetX = 0, targetY = 0;
let currentX = 0, currentY = 0;
let isParallaxRunning = false;


// --- [REGION: PARALLAX & MOUSE DEPTH (SIENA/SKIPER-29)] ---
function handleParallaxMouseMove(e) {
    const slides = document.querySelectorAll('.recap-slide.active');
    if(slides.length === 0) return;
    
    targetX = (window.innerWidth / 2 - e.pageX);
    targetY = (window.innerHeight / 2 - e.pageY);
    
    if (!isParallaxRunning) {
        isParallaxRunning = true;
        requestAnimationFrame(updateParallax);
    }
}

function updateParallax() {
    const slides = document.querySelectorAll('.recap-slide.active');
    if(slides.length === 0) {
        isParallaxRunning = false;
        return;
    }
    
    // Lerp towards the target (using a factor of 0.1 for a fluid, spring-like feel)
    currentX += (targetX - currentX) * 0.1;
    currentY += (targetY - currentY) * 0.1;
    
    const slide = slides[0];
    
    // Tilt the slide container (reduced multiplier for subtler, classy tilt)
    slide.style.transform = `rotateY(${currentX / 100}deg) rotateX(${currentY / 100}deg)`;
    
    // Move individual layers based on depth
    const layers = slide.querySelectorAll('.siena-layer');
    layers.forEach(layer => {
        const depth = layer.getAttribute('data-depth') || 20;
        const xOffset = currentX * (depth / 3500);
        const yOffset = currentY * (depth / 3500);
        layer.style.transform = `translateZ(${depth}px) translate(${xOffset}px, ${yOffset}px)`;
    });
    
    // Continue loop if we haven't reached the target
    if (Math.abs(targetX - currentX) > 0.1 || Math.abs(targetY - currentY) > 0.1) {
        requestAnimationFrame(updateParallax);
    } else {
        isParallaxRunning = false;
    }
}


// --- [REGION: EVENT HANDLERS] ---
function handleRecapKeyboard(e) {
    if (document.getElementById('recap-player-overlay').classList.contains('hidden')) return;
    
    if (e.key === 'ArrowLeft') {
        prevRecapSlide();
    } else if (e.key === 'ArrowRight') {
        nextRecapSlide();
    } else if (e.key === 'Escape') {
        closeRecapPlayer();
    }
}

// --- [REGION: STATE VARIABLES] ---
let isRecapLoading = false;


// --- [REGION: OPEN & INIT PLAYER] ---
function openRecapPlayer(element, year, month = null) {
    if (isRecapLoading) return;
    isRecapLoading = true;
    
    // 1. FLIP Animation: Create a clone of the clicked element
    const rect = element.getBoundingClientRect();
    const clone = element.cloneNode(true);
    clone.className = 'recap-transition-clone';
    clone.style.top = rect.top + 'px';
    clone.style.left = rect.left + 'px';
    clone.style.width = rect.width + 'px';
    clone.style.height = rect.height + 'px';
    clone.style.borderRadius = '20px';
    document.body.appendChild(clone);
    
    // Hide original slightly
    element.style.opacity = '0';
    
    // Trigger transition next frame
    requestAnimationFrame(() => {
        clone.style.top = '0px';
        clone.style.left = '0px';
        clone.style.width = '100vw';
        clone.style.height = '100vh';
        clone.style.borderRadius = '0px';
    });
    
    // Start Preloader
    const overlay = document.getElementById('recap-player-overlay');
    const preloader = document.getElementById('recap-preloader');
    
    
    // Reset state
    overlay.classList.remove('hidden');
    preloader.classList.remove('slide-up');
    document.getElementById('recap-slides-container').classList.add('hidden');
    document.getElementById('slide-place').style.display = ''; // H5: Reset in case previous recap hid it
    
    // Attach listeners (removed on close)
    document.addEventListener('mousemove', handleParallaxMouseMove);
    document.addEventListener('keydown', handleRecapKeyboard);
    

    // Fetch data — include month if provided
    let fetchYear = year || new Date().getFullYear();
    let fetchUrl = `/api/recap/generate/${fetchYear}`;
    if (month) fetchUrl += `/${month}`;
    fetch(fetchUrl)
        .then(res => res.json())
        .then(data => {
            recapData = data;
            
            // Populate UI
            document.getElementById('recap-ai-comment').innerText = data.ai_comment;
            
            // We don't populate numbers yet, we animate them on slide load
            
            
            document.getElementById('recap-stat-person').innerText = data.top_person || "Yourself!";
              initSkiper47Carousel('person-photos-fan', data.top_person_photos, data.top_person_feature);

            
            if (data.iconic_place) {
                document.getElementById('recap-stat-place').innerText = data.iconic_place;
                
                initSkiper54Carousel('place-photos-fan', data.iconic_place_photos);
            } else {
                document.getElementById('slide-place').style.display = 'none'; // skip
            }
            
            // Skiper 30 Parallax Gallery - Massive Scatter
            const gallery = document.getElementById('recap-parallax-gallery');
            gallery.innerHTML = '';
            
            // Clean up any previously injected dynamic styles
            document.querySelectorAll('.dynamic-float-style').forEach(el => el.remove());
            
            if (data.gallery_photos && data.gallery_photos.length > 0) {
                let pool = [...new Set(data.gallery_photos)];
                pool.sort(() => 0.5 - Math.random());
                
                // Allow up to 24 photos. If fewer, allow duplication up to 24 to fill space.
                let renderList = [];
                while (renderList.length < 24 && pool.length > 0) {
                    renderList = renderList.concat(pool);
                }
                renderList = renderList.slice(0, 24);
                
                let slots = [];
                for (let i = 0; i < 24; i++) slots.push(i);
                slots.sort(() => 0.5 - Math.random());
                
                renderList.forEach((photoPath, i) => {
                    const slot = slots[i];
                    const col = slot % 6;
                    const row = Math.floor(slot / 6);
                    
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item`;
                    
                    // C1: 3 Size Tiers
                    const sizeTier = Math.random();
                    const size = sizeTier > 0.8 ? (200 + Math.random()*40) : sizeTier > 0.4 ? (140 + Math.random()*40) : (80 + Math.random()*40);
                    
                    const cellX = 15 + (col * 11.6); 
                    const cellY = 15 + (row * 17.5);
                    const posX = cellX + (Math.random() * 4 - 2); 
                    const posY = cellY + (Math.random() * 4 - 2); 
                    
                    const delay = Math.random() * -30; 
                    const duration = 25 + Math.random() * 20; 
                    
                    // C2: Depth-Aware Opacity & Blur
                    const depthTier = Math.random();
                    let opacity = 0.3;
                    let blur = 0;
                    let scale = 1;
                    
                    if (depthTier > 0.6) {
                        opacity = 0.45; scale = 1.1; // Near
                    } else if (depthTier > 0.3) {
                        opacity = 0.30; // Mid
                    } else {
                        opacity = 0.15; blur = 2; // Far
                    }
                    
                    img.style.position = 'absolute';
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*40 - 20)}px`;
                    img.style.left = `${posX}%`;
                    img.style.top = `${posY}%`;
                    img.style.opacity = opacity;
                    img.style.filter = `blur(${blur}px)`;
                    img.style.transform = `scale(${scale})`;
                    img.style.zIndex = Math.floor(Math.random() * 5);
                    
                    
                    // C3: GSAP Physics Float (Skiper 30 / 32 Engine)
                    gallery.appendChild(img);
                    
                    const rotBase = (Math.random() - 0.5) * 40;
                    const driftY = 40 + Math.random() * 40;
                    const driftX = 20 + Math.random() * 20;
                    
                    // Initial state
                    gsap.set(img, {
                        x: 0,
                        y: 0,
                        rotation: rotBase,
                        scale: scale
                    });
                    
                    // Complex elliptical float
                    gsap.to(img, {
                        x: driftX,
                        y: driftY,
                        rotation: rotBase + 5,
                        duration: duration / 2,
                        ease: "sine.inOut",
                        yoyo: true,
                        repeat: -1,
                        delay: delay
                    });
                    
                    gsap.to(img, {
                        x: -driftX * 0.5,
                        rotation: rotBase - 3,
                        duration: duration * 0.8,
                        ease: "sine.inOut",
                        yoyo: true,
                        repeat: -1,
                        delay: delay * 1.5
                    });
                    
gallery.appendChild(img);
                });
            }

            // Set backdrop (Parallax) and Hero image
            const backdropImg = data.memorable_moment || (clone.querySelector('img') ? clone.querySelector('img').src : '');
            if (backdropImg) {
                let imgUrl = backdropImg;
                if (!backdropImg.startsWith('http') && !backdropImg.startsWith('blob:') && !backdropImg.startsWith('data:')) {
                    imgUrl = `/api/photo/thumbnail/${encodeURIComponent(backdropImg)}`;
                }
                document.getElementById('recap-backdrop').style.backgroundImage = `url('${imgUrl}')`;
                
                const heroImg = document.getElementById('hero-moment-img');
                if (heroImg) {
                    heroImg.src = imgUrl;
                }
            }
            
            // Generate dynamic yearly background theme
            generateYearlyTheme(fetchYear);
            
            // Finish loader
            
            
            setTimeout(() => {
                // PRELOADER: Wait for all high-res main images to download
                let preloadUrls = [];
                
                if (data.top_person_photos) preloadUrls = preloadUrls.concat(data.top_person_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
                if (data.top_person_feature) preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.top_person_feature)}`);
                if (data.iconic_place_photos) preloadUrls = preloadUrls.concat(data.iconic_place_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
                if (data.memorable_moment) preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.memorable_moment)}`);
                if (data.gallery_photos) preloadUrls = preloadUrls.concat(data.gallery_photos.slice(0,8).map(p => `/api/photo/file/${encodeURIComponent(p)}`));
                
                // Deduplicate
                preloadUrls = [...new Set(preloadUrls)];
                
                let loadPromises = preloadUrls.map(url => {
                    return new Promise((resolve) => {
                        const img = new Image();
                        img.onload = resolve;
                        img.onerror = resolve; // Continue even if one fails
                        img.src = url;
                    });
                });
                
                // Ensure preloader runs for at least 800ms for visual FLIP transition to settle
                let timerPromise = new Promise(resolve => setTimeout(resolve, 800));
                loadPromises.push(timerPromise);
                
                let preloaderText = document.querySelector('.preloader-text');
                if(preloaderText) preloaderText.innerText = "Developing high-res photos...";
                
                Promise.all(loadPromises).then(() => {
                    // Slide up preloader (Skiper 15)
                    preloader.classList.add('slide-up');
                        
                    // Show slides
                    document.getElementById('recap-slides-container').classList.remove('hidden');
                    
                    // Remove clone
                    if (clone) clone.remove();
                    element.style.opacity = '1';
                    
                    // Init sequence
                    recapCurrentSlide = 0; if(document.getElementById('slide-montage')) document.getElementById('slide-montage').style.display = 'none';
                    recapSlides = Array.from(document.querySelectorAll('.recap-slide')).filter(s => s.style.display !== 'none');
                    showRecapSlide(0);
                    
                    isRecapLoading = false;
                });
            }, 100);
        })
        .catch(err => {
            console.error(err);
            isRecapLoading = false;
            closeRecapPlayer();
        });
}

function showRecapSlide(index) {
    recapSlides.forEach((s, i) => {
        if (i === index) {
            s.classList.add('active');
            
            // Montage Transition Buffer Slide
            if (s.id === 'slide-montage' && recapData) {
                const container = document.getElementById('montage-container');
                container.innerHTML = '';
                
                if (recapData.gallery_photos && recapData.gallery_photos.length > 0) {
                    const photos = recapData.gallery_photos.slice(0, 5); // Max 5 polaroids
                    
                    photos.forEach((photoPath, idx) => {
                        const burst = document.createElement('div');
                        burst.className = 'montage-burst-photo';
                        burst.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(photoPath)}" />`;
                        container.appendChild(burst);
                        
                        // Stagger entrance
                        setTimeout(() => {
                            const tx = (Math.random() - 0.5) * 40 + 'vw';
                            const ty = (Math.random() - 0.5) * 40 + 'vh';
                            const rot = (Math.random() - 0.5) * 40 + 'deg';
                            
                            burst.style.setProperty('--target-x', tx);
                            burst.style.setProperty('--target-y', ty);
                            burst.style.setProperty('--target-rot', rot);
                            
                            burst.style.animation = `throwOn 0.6s forwards cubic-bezier(0.175, 0.885, 0.32, 1.275)`;
                            burst.style.zIndex = idx + 10;
                            
                            // If this is the last photo, trigger the exit and next slide
                            if (idx === photos.length - 1) {
                                setTimeout(() => {
                                    // Scatter out
                                    const allBurst = container.querySelectorAll('.montage-burst-photo');
                                    allBurst.forEach(p => {
                                        p.style.transition = 'transform 0.5s ease-in, opacity 0.5s ease-in';
                                        p.style.transform = `scale(0.1) translate(0,0) rotate(-45deg)`;
                                        p.style.opacity = '0';
                                    });
                                    
                                    // Auto-advance to intro text slide
                                    setTimeout(() => {
                                        nextRecapSlide();
                                    }, 600); // Wait for scatter animation
                                }, 1500); // Hold the final burst for 1.5s
                            }
                        }, idx * 180); // 180ms delay between drops
                    });
                } else {
                    // Skip montage if no photos
                    setTimeout(nextRecapSlide, 50);
                }
            }
            
            // If it's the stats slide, trigger number animation (Skiper 37)
            if (s.id === 'slide-stats' && recapData) {
                const p = document.getElementById('recap-stat-photos');
                const v = document.getElementById('recap-stat-videos');
                p.innerHTML = '0';
                v.innerHTML = '0';
                setTimeout(() => {
                    animateNumberFlow(p, 0, recapData.total_photos, 2000);
                    animateNumberFlow(v, 0, recapData.total_videos, 2000);
                }, 300);
            }
            
        } else {
            s.classList.remove('active');
        }
    });
}

let isRecapTransitioning = false;


// --- [REGION: SLIDE TRANSITION LOGIC] ---

function playSkiper79Transition(titleText, callback) {
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

function playSlideTransition(callback) {
    if (isRecapTransitioning) return;
    isRecapTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'flex';
    layer.style.alignItems = 'center';
    layer.style.justifyContent = 'center';
    layer.style.overflow = 'hidden';
    layer.innerHTML = '';
    layer.style.background = 'transparent';
    
    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const types = photos.length > 0 ? ['skiper-32', 'skiper-30', 'skiper-71', 'skiper-33'] : ['blur'];
    const type = 'skiper-33'; // Forced for review
    
    if (type === 'skiper-32') {
        // Skiper 32 GSAP 3D Grid Reveal
        const grid = document.createElement('div');
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(5, 1fr)';
        grid.style.gap = '10px';
        grid.style.width = '150vw';
        grid.style.height = '150vh';
        grid.style.transform = 'translateZ(-1000px) rotateX(45deg)';
        grid.style.transformStyle = 'preserve-3d';
        grid.style.perspective = '2000px';
        
        for(let i=0; i<20; i++) {
            const img = document.createElement('img');
            img.src = '/api/photo/file/' + encodeURIComponent(photos[i % photos.length]);
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '12px';
            img.style.opacity = '0';
            img.style.transform = `translateZ(${Math.random() * 500 - 250}px)`;
            grid.appendChild(img);
        }
        layer.appendChild(grid);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(grid.children, {
            opacity: 1,
            z: 0,
            duration: 0.8,
            stagger: 0.05,
            ease: "power3.out"
        }, 0);
        
        tl.to(grid, {
            z: 500,
            rotateX: 0,
            duration: 1.5,
            ease: "power3.inOut",
            onUpdate: function() {
                if(this.progress() > 0.5 && callback) {
                    callback();
                    callback = null;
                }
            }
        }, 0);
        
        tl.to(grid.children, {
            opacity: 0,
            z: 500,
            duration: 0.5,
            stagger: 0.02,
            ease: "power2.in"
        }, 1.2);
        
    } else if (type === 'skiper-30') {
        // Skiper 30 GSAP Depth Parallax Blur
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.opacity = '0';
        img.style.transform = 'scale(1)';
        img.style.filter = 'blur(0px)';
        layer.appendChild(img);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(img, {
            opacity: 1,
            scale: 1.5,
            filter: 'blur(30px)',
            duration: 0.8,
            ease: "power3.in",
            onComplete: () => {
                if(callback) { callback(); callback = null; }
            }
        });
        
        tl.to(img, {
            opacity: 0,
            scale: 2,
            duration: 0.8,
            ease: "power3.out"
        });
        
    } else if (type === 'skiper-71') {
        // Skiper 71 GSAP Image Reveal (Clip Path Wipe)
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.clipPath = 'polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%)';
        layer.appendChild(img);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(img, {
            clipPath: 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)',
            duration: 1,
            ease: "expo.inOut",
            onComplete: () => {
                if(callback) { callback(); callback = null; }
            }
        });
        
        tl.to(img, {
            opacity: 0,
            scale: 1.1,
            duration: 0.6,
            ease: "power2.out"
        });
        
    } else if (type === 'skiper-33') {
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
        
    } else {
        // Fallback Blur
        layer.style.background = 'rgba(0,0,0,0.8)';
        layer.style.opacity = '0';
        gsap.to(layer, {
            opacity: 1,
            duration: 0.4,
            onComplete: () => {
                if (callback) callback();
                gsap.to(layer, {
                    opacity: 0,
                    duration: 0.4,
                    onComplete: () => {
                        layer.style.display = 'none';
                        isRecapTransitioning = false;
                    }
                });
            }
        });
    }
}
function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        let nextSlideId = recapSlides[recapCurrentSlide + 1].id;
        
        let transitionTitle = null;
        if (nextSlideId === 'slide-person') transitionTitle = "TOP PERSON";
        if (nextSlideId === 'slide-place') transitionTitle = "ICONIC PLACE";
        if (nextSlideId === 'slide-hero') transitionTitle = "HERO MOMENT";
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });
        } else {
            playSlideTransition(() => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });
        }
    } else {
        closeRecapPlayer();
    }
}



function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        let prevSlideId = recapSlides[recapCurrentSlide - 1].id;
        
        let transitionTitle = null;
        if (prevSlideId === 'slide-person') transitionTitle = "TOP PERSON";
        if (prevSlideId === 'slide-place') transitionTitle = "ICONIC PLACE";
        if (prevSlideId === 'slide-hero') transitionTitle = "HERO MOMENT";
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
        } else {
            playSlideTransition(() => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
        }
    }
}


// --- [REGION: CLOSE PLAYER] ---
function closeRecapPlayer() {
    if (window.recapDeckIntervals) {
        window.recapDeckIntervals.forEach(clearInterval);
        window.recapDeckIntervals = [];
    }
    isRecapLoading = false;
    document.querySelectorAll('.dynamic-float-style').forEach(el => el.remove());
    document.getElementById('recap-player-overlay').classList.add('hidden');
    const clone = document.querySelector('.recap-transition-clone');
    if (clone) clone.remove();
    
    // Remove listeners
    document.removeEventListener('mousemove', handleParallaxMouseMove);
    document.removeEventListener('keydown', handleRecapKeyboard);
    
    // Restore opacity to all cards that might have been clicked
    document.querySelectorAll('.rewind-hero-card, .rewind-mini-card').forEach(card => {
        card.style.opacity = '1';
    });
}

function initSkiper54Carousel(containerId, photos) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    let deck = photos.slice(0, 15);
    
    let swiperHtml = `<div class="swiper skiper-54-swiper"><div class="swiper-wrapper">`;
    deck.forEach(p => {
        swiperHtml += `<div class="swiper-slide skiper-54-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" class="skiper-54-img" /></div>`;
    });
    swiperHtml += `</div><div class="swiper-pagination"></div></div>`;
    
    container.innerHTML = swiperHtml;
    
    new Swiper('.skiper-54-swiper', {
        slidesPerView: 'auto',
        centeredSlides: true,
        spaceBetween: 40,
        grabCursor: true,
        loop: true,
        observer: true,
        observeParents: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
}

function generateYearlyTheme(year) {
    const container = document.getElementById('theme-canvas');
    if (container) container.innerHTML = '';
}

