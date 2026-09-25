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

let isRecapLoading = false;

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
            
            // Render Person Fan Photos
            const personFan = document.getElementById('person-photos-fan');
            if (personFan) {
                personFan.innerHTML = '';
                
                let pPhotos = data.top_person_photos || [];
                const feat = data.top_person_feature;
                
                // Add feature photo to the center (if available)
                let fanPhotos = [];
                if (feat) {
                    fanPhotos.push(feat);
                }
                // Fill the rest up to 5 total photos
                for (let i = 0; i < pPhotos.length; i++) {
                    if (fanPhotos.length >= 5) break;
                    if (pPhotos[i] !== feat) {
                        fanPhotos.push(pPhotos[i]);
                    }
                }
                
                if (fanPhotos.length > 0) {
                    // Create polaroid style fan
                    const angles = fanPhotos.length === 5 ? [-20, -10, 0, 10, 20] :
                                   fanPhotos.length === 4 ? [-15, -5, 5, 15] :
                                   fanPhotos.length === 3 ? [-12, 0, 12] :
                                   fanPhotos.length === 2 ? [-8, 8] : [0];
                    
                    fanPhotos.forEach((p, idx) => {
                        const div = document.createElement('div');
                        // Make the feature photo (index 0) stand out more if we have multiple
                        const isFeature = (feat && p === feat);
                        div.className = isFeature ? 'person-fan-photo feature-photo' : 'person-fan-photo';
                        
                        // Feature photo stays on top
                        const z = isFeature ? 10 : (5 - Math.abs(angles[idx]));
                        
                        // Push outer photos down slightly to create an arc
                        const dropY = Math.abs(angles[idx] || 0) * 1.5;
                        
                        div.style.zIndex = z;
                        div.style.transform = `rotate(${angles[idx] || 0}deg) translateY(${dropY}px)`;
                        div.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(p)}" />`;
                        personFan.appendChild(div);
                    });
                }
            }

            
            if (data.iconic_place) {
                document.getElementById('recap-stat-place').innerText = data.iconic_place;
                
                const fan = document.getElementById('place-photos-fan');
                fan.innerHTML = '';
                if (data.iconic_place_photos && data.iconic_place_photos.length > 0) {
                    const photos = data.iconic_place_photos;
                    // Distribute fan angles based on number of photos
                    const angles = photos.length === 3 ? [-12, 0, 12] : photos.length === 2 ? [-8, 8] : [0];
                    const zIndices = [1, 3, 2]; // Keep center on top usually
                    
                    photos.forEach((p, idx) => {
                        const div = document.createElement('div');
                        div.className = 'place-fan-photo';
                        div.style.zIndex = zIndices[idx] || 1;
                        div.style.transform = `rotate(${angles[idx] || 0}deg) translateY(${Math.abs(angles[idx] || 0) * 1.5}px)`;
                        div.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(p)}" />`;
                        fan.appendChild(div);
                    });
                }
            } else {
                document.getElementById('slide-place').style.display = 'none'; // skip
            }
            
            // Skiper 30 Parallax Gallery - Massive Scatter
            const gallery = document.getElementById('recap-parallax-gallery');
            gallery.innerHTML = '';
            
            // Clean up any previously injected dynamic styles
            document.querySelectorAll('.dynamic-float-style').forEach(el => el.remove());
            
            if (data.gallery_photos && data.gallery_photos.length > 0) {
                // Prevent repeating: cap the pool strictly to unique photos, max 24.
                let pool = [...new Set(data.gallery_photos)]; // Unique only
                pool.sort(() => 0.5 - Math.random());
                
                let renderList = pool.slice(0, 24);
                const count = renderList.length;
                
                // We have a 6x4 grid (24 slots). Pick 'count' random unique slots.
                let slots = [];
                for (let i = 0; i < 24; i++) slots.push(i);
                slots.sort(() => 0.5 - Math.random());
                slots = slots.slice(0, count);
                
                renderList.forEach((photoPath, i) => {
                    const slot = slots[i];
                    const col = slot % 6;
                    const row = Math.floor(slot / 6);
                    
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item`;
                    
                    // Decrease size significantly to prevent overlapping (80px to 220px)
                    const size = 80 + Math.random() * 140; 
                    
                    // Container is 140% oversized. Visible area is ~15% to 85%.
                    // 6 cols spanning 70% = 11.6% width each.
                    // 4 rows spanning 70% = 17.5% height each.
                    const cellX = 15 + (col * 11.6); 
                    const cellY = 15 + (row * 17.5);
                    
                    // Mild jitter to keep them safely inside their cells
                    const posX = cellX + (Math.random() * 4 - 2); 
                    const posY = cellY + (Math.random() * 4 - 2); 
                    
                    const delay = Math.random() * -30; 
                    const duration = 25 + Math.random() * 20; 
                    const rot = (Math.random() - 0.5) * 40; 
                    
                    img.style.position = 'absolute';
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*40 - 20)}px`;
                    img.style.left = `${posX}%`;
                    img.style.top = `${posY}%`;
                    img.style.opacity = '0.35';
                    img.style.zIndex = Math.floor(Math.random() * 10);
                    
                    const animName = `customFloat${i}_${Date.now()}`;
                    const style = document.createElement('style');
                    style.className = 'dynamic-float-style';
                    
                    // Reduce animation drift distance to prevent them floating into each other's spaces
                    style.innerHTML = `
                        @keyframes ${animName} {
                            0% { transform: translateY(0px) rotate(${rot}deg); }
                            100% { transform: translateY(${Math.random()*80 - 40}px) rotate(${rot + (Math.random()*16-8)}deg); }
                        }
                    `;
                    document.head.appendChild(style);
                    
                    img.style.animation = `${animName} ${duration}s infinite alternate ease-in-out`;
                    img.style.animationDelay = `${delay}s`;
                    
                    gallery.appendChild(img);
                });
            }

            // Set backdrop (Parallax)
            const backdropImg = data.memorable_moment || (clone.querySelector('img') ? clone.querySelector('img').src : '');
            if (backdropImg) {
                document.getElementById('recap-backdrop').style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(backdropImg)}')`;
                            }
            
            // Generate dynamic yearly background theme
            generateYearlyTheme(fetchYear);
            
            // Finish loader
            
            
            setTimeout(() => {
                // Slide up preloader (Skiper 15)
                preloader.classList.add('slide-up');
                
                // Show slides
                document.getElementById('recap-slides-container').classList.remove('hidden');
                
                // Remove clone
                clone.remove();
                element.style.opacity = '1';
                
                // Init sequence
                recapCurrentSlide = 0;
                recapSlides = Array.from(document.querySelectorAll('.recap-slide')).filter(s => s.style.display !== 'none');
                showRecapSlide(0);
                
                isRecapLoading = false;
            }, 600);
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
                        const polaroid = document.createElement('div');
                        polaroid.className = 'montage-polaroid';
                        polaroid.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(photoPath)}" />`;
                        container.appendChild(polaroid);
                        
                        // Stagger entrance
                        setTimeout(() => {
                            // Calculate random rotation between -15 and 15 degrees
                            const rotation = (Math.random() * 30 - 15).toFixed(1);
                            polaroid.style.transform = `scale(1) translateY(0) rotate(${rotation}deg)`;
                            polaroid.style.zIndex = idx + 10;
                            polaroid.classList.add('in');
                            
                            // If this is the last polaroid, trigger the exit and next slide
                            if (idx === photos.length - 1) {
                                setTimeout(() => {
                                    // Scatter out
                                    const allPolaroids = container.querySelectorAll('.montage-polaroid');
                                    allPolaroids.forEach(p => p.classList.add('out'));
                                    
                                    // Auto-advance to intro text slide
                                    setTimeout(() => {
                                        nextRecapSlide();
                                    }, 600); // Wait for scatter animation
                                }, 1500); // Hold the final stacked montage for 1.5s
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
        
    const types = photos.length >= 3 ? ['skiper-32', 'skiper-30'] : ['blur'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    if (type === 'skiper-32') {
        // Skiper 32 Scroll Images Reveal
        const grid = document.createElement('div');
        grid.className = 'skiper-32-grid';
        
        const randomValues = [
            {rotateXStart:-45,translateZStart:-450,translateYStart:2150},
            {rotateXStart:-67,translateZStart:-720,translateYStart:1720},
            {rotateXStart:-38,translateZStart:-380,translateYStart:1380},
            {rotateXStart:-82,translateZStart:-890,translateYStart:1890},
            {rotateXStart:-53,translateZStart:-540,translateYStart:2540},
            {rotateXStart:-71,translateZStart:-760,translateYStart:1760},
            {rotateXStart:-42,translateZStart:-420,translateYStart:1420},
            {rotateXStart:-89,translateZStart:-950,translateYStart:1950},
            {rotateXStart:-48,translateZStart:-480,translateYStart:1480},
            {rotateXStart:-75,translateZStart:-800,translateYStart:1800},
            {rotateXStart:-35,translateZStart:-350,translateYStart:1350},
            {rotateXStart:-85,translateZStart:-920,translateYStart:1920},
            {rotateXStart:-58,translateZStart:-580,translateYStart:1580},
            {rotateXStart:-69,translateZStart:-740,translateYStart:1740},
            {rotateXStart:-44,translateZStart:-440,translateYStart:1440},
            {rotateXStart:-78,translateZStart:-830,translateYStart:1830},
            {rotateXStart:-51,translateZStart:-510,translateYStart:1510},
            {rotateXStart:-87,translateZStart:-940,translateYStart:1940},
            {rotateXStart:-39,translateZStart:-390,translateYStart:1390},
            {rotateXStart:-73,translateZStart:-780,translateYStart:1780}
        ];
        
        const items = [];
        for(let i=0; i<20; i++) {
            const img = document.createElement('img');
            img.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[i % photos.length]);
            img.className = 'skiper-32-item';
            
            const rv = randomValues[i];
            img.style.transform = `translateY(${rv.translateYStart}px) translateZ(${rv.translateZStart}px) rotateX(${rv.rotateXStart}deg)`;
            img.style.opacity = '0';
            img.style.transition = 'none';
            grid.appendChild(img);
            items.push(img);
        }
        
        layer.appendChild(grid);
        
        // Force reflow
        void grid.offsetWidth;
        
        // Animate In
        items.forEach((img, i) => {
            img.style.transition = 'transform 0.8s cubic-bezier(0.2, 0, 0.2, 1), opacity 0.8s ease';
            img.style.transform = 'translateY(0px) translateZ(0px) rotateX(0deg)';
            img.style.opacity = '1';
        });
        
        setTimeout(() => {
            callback();
            
            // Animate Out (zoom through camera)
            items.forEach((img, i) => {
                const rv = randomValues[i];
                // reverse them but zoom past camera (positive Z)
                img.style.transition = 'transform 0.6s cubic-bezier(0.8, 0, 0.2, 1), opacity 0.5s ease 0.1s';
                img.style.transform = `translateY(${-rv.translateYStart}px) translateZ(200px) rotateX(${-rv.rotateXStart}deg)`;
                img.style.opacity = '0';
            });
            
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 600);
            
        }, 850);
        
    } else if (type === 'skiper-30') {
        // Skiper 30 Parallax Blur Transition
        // Takes a random image, scales it up massively with heavy blur, hiding the slide change inside the blur.
        const img = document.createElement('img');
        img.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.opacity = '0';
        img.style.transform = 'scale(1)';
        img.style.filter = 'blur(0px)';
        img.style.transition = 'all 0.6s cubic-bezier(0.8, 0, 0.2, 1)';
        
        layer.appendChild(img);
        
        // Force reflow
        void img.offsetWidth;
        
        // Animate in: rapid zoom and heavy blur
        img.style.opacity = '1';
        img.style.transform = 'scale(1.5)';
        img.style.filter = 'blur(30px)';
        
        setTimeout(() => {
            callback(); // Swap slides while completely blurred
            
            // Animate out: continue zooming, fade out opacity
            img.style.transition = 'all 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)';
            img.style.transform = 'scale(2)';
            img.style.opacity = '0';
            
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 600);
        }, 600);
        
    } else {
        // Fallback blur
        layer.style.backdropFilter = 'blur(0px)';
        layer.style.transition = 'backdrop-filter 0.3s ease';
        requestAnimationFrame(() => layer.style.backdropFilter = 'blur(30px)');
        setTimeout(() => {
            callback();
            layer.style.backdropFilter = 'blur(0px)';
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 300);
        }, 300);
    }
}

function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        playSlideTransition(() => {
            recapCurrentSlide++;
            showRecapSlide(recapCurrentSlide);
        });
    } else {
        closeRecapPlayer();
    }
}

function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        playSlideTransition(() => {
            recapCurrentSlide--;
            showRecapSlide(recapCurrentSlide);
        });
    }
}

function closeRecapPlayer() {
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


function generateYearlyTheme(year) {
    const container = document.getElementById('theme-canvas');
    if (container) container.innerHTML = '';
}
