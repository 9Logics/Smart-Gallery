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

document.addEventListener('mousemove', (e) => {
    const slides = document.querySelectorAll('.recap-slide.active');
    if(slides.length === 0) return;
    
    targetX = (window.innerWidth / 2 - e.pageX);
    targetY = (window.innerHeight / 2 - e.pageY);
    
    if (!isParallaxRunning) {
        isParallaxRunning = true;
        requestAnimationFrame(updateParallax);
    }
});

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

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function openRecapPlayer(element, year, month = null) {
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
    
    
    // Simulate preloader progress while we fetch API
    let prog = 0;
    const interval = setInterval(() => {
        prog += Math.random() * 15;
        if (prog > 90) prog = 90; // Wait for API
        
    }, 200);
    
    // Fetch data
    let fetchYear = year || new Date().getFullYear();
    fetch(`/api/recap/generate/${fetchYear}`)
        .then(res => res.json())
        .then(data => {
            recapData = data;
            
            // Populate UI
            document.getElementById('recap-ai-comment').innerText = data.ai_comment;
            
            // We don't populate numbers yet, we animate them on slide load
            
            document.getElementById('recap-stat-person').innerText = data.top_person || "Yourself!";
            
            if (data.iconic_place) {
                document.getElementById('recap-stat-place').innerText = data.iconic_place;
            } else {
                document.getElementById('slide-place').style.display = 'none'; // skip
            }
            
            
            // Skiper 30 Parallax Gallery
            const gallery = document.getElementById('recap-parallax-gallery');
            gallery.innerHTML = '';
            if (data.gallery_photos && data.gallery_photos.length > 0) {
                data.gallery_photos.forEach((photoPath, i) => {
                    if(i > 4) return; // Limit to 5 background photos
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item p-item-${i+1}`;
                    gallery.appendChild(img);
                });
            }

            // Set backdrop (Parallax)
            const backdropImg = data.memorable_moment || (clone.querySelector('img') ? clone.querySelector('img').src : '');
            if (backdropImg) {
                document.getElementById('recap-backdrop').style.backgroundImage = `url('/api/photo/file/${encodeURIComponent(backdropImg)}')`;
                document.getElementById('recap-stat-place-img').src = `/api/photo/thumbnail/${encodeURIComponent(backdropImg)}`;
            }
            
            // Generate dynamic yearly background theme
            generateYearlyTheme(fetchYear);
            
            // Finish loader
            clearInterval(interval);
            
            
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
                
            }, 600);
        })
        .catch(err => {
            console.error(err);
            clearInterval(interval);
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
                        polaroid.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(photoPath)}" />`;
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
    
    // We need photos for Skiper transitions. If none, fallback to a fast blur.
    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const types = photos.length >= 3 ? ['skiper-34-scrapbook', 'skiper-32-zoom', 'skiper-33-film'] : ['blur'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    // Helper to get random photo
    const getRandImg = () => `/api/photo/file/${encodeURIComponent(photos[Math.floor(Math.random() * photos.length)])}`;
    
    if (type === 'skiper-34-scrapbook') {
        // Drop 2-3 polaroids fast, scatter out
        const num = 2 + Math.floor(Math.random() * 2);
        let completed = 0;
        
        for(let i=0; i<num; i++) {
            const p = document.createElement('div');
            p.className = 'montage-polaroid';
            p.style.position = 'absolute';
            p.style.width = '35vw';
            p.style.maxWidth = '400px';
            p.innerHTML = `<img src="${getRandImg()}" />`;
            layer.appendChild(p);
            
            setTimeout(() => {
                const rot = (Math.random() * 40 - 20).toFixed(1);
                p.style.transform = `scale(1) translateY(0) rotate(${rot}deg)`;
                p.style.zIndex = i + 10;
                p.classList.add('in');
                
                if (i === num - 1) {
                    // Last one dropped, wait a tiny bit, swap slide, then scatter
                    setTimeout(() => {
                        callback();
                        const allP = layer.querySelectorAll('.montage-polaroid');
                        allP.forEach(card => card.classList.add('out'));
                        
                        setTimeout(() => {
                            layer.style.display = 'none';
                            isRecapTransitioning = false;
                        }, 500);
                    }, 400); // Hold stack
                }
            }, i * 120); // Fast drop
        }
    } 
    else if (type === 'skiper-32-zoom') {
        // A single photo expands to fill screen, slide swaps, then it zooms through the camera
        const p = document.createElement('img');
        p.src = getRandImg();
        p.style.position = 'absolute';
        p.style.width = '20vw';
        p.style.height = '20vh';
        p.style.objectFit = 'cover';
        p.style.borderRadius = '20px';
        p.style.boxShadow = '0 30px 60px rgba(0,0,0,0.5)';
        p.style.transform = 'scale(0.5)';
        p.style.opacity = '0';
        p.style.transition = 'all 0.4s cubic-bezier(0.8, 0, 0.2, 1)';
        layer.appendChild(p);
        
        requestAnimationFrame(() => {
            p.style.transform = 'scale(1)';
            p.style.width = '100vw';
            p.style.height = '100vh';
            p.style.borderRadius = '0px';
            p.style.opacity = '1';
        });
        
        setTimeout(() => {
            callback(); // Swap slide while screen is covered
            p.style.transition = 'all 0.5s cubic-bezier(0.8, 0, 0.2, 1)';
            p.style.transform = 'scale(2.5)'; // Zoom through camera
            p.style.opacity = '0';
            
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 500);
        }, 400);
    }
    else if (type === 'skiper-33-film') {
        // Horizontal film strip sliding across
        const strip = document.createElement('div');
        strip.style.position = 'absolute';
        strip.style.display = 'flex';
        strip.style.gap = '20px';
        strip.style.transform = 'translateX(100vw) rotate(-5deg)';
        strip.style.transition = 'transform 0.6s cubic-bezier(0.7, 0, 0.3, 1)';
        
        for(let i=0; i<3; i++) {
            const img = document.createElement('img');
            img.src = getRandImg();
            img.style.width = '60vw';
            img.style.height = '80vh';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '10px';
            img.style.boxShadow = '0 20px 40px rgba(0,0,0,0.6)';
            strip.appendChild(img);
        }
        layer.appendChild(strip);
        
        requestAnimationFrame(() => {
            strip.style.transform = 'translateX(0) rotate(0deg)'; // Center it
        });
        
        setTimeout(() => {
            callback();
            strip.style.transform = 'translateX(-100vw) rotate(5deg)'; // Slide out
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 600);
        }, 450);
    }
    else {
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
    document.getElementById('recap-player-overlay').classList.add('hidden');
    const clone = document.querySelector('.recap-transition-clone');
    if (clone) clone.remove();
    
    // Restore opacity to all cards that might have been clicked
    document.querySelectorAll('.rewind-hero-card, .rewind-mini-card').forEach(card => {
        card.style.opacity = '1';
    });
}


function generateYearlyTheme(year) {
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
    const styleType = Math.floor(myRand() * 3); // 0 = Goopy Circles, 1 = Organic Morphing Blobs, 2 = Large Jagged Shapes
    
    if (styleType === 0) {
        // Goopy Circles (Solid colors melting into each other using a sharp SVG goo filter)
        container.style.filter = "url('#recap-goo')";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<7; i++) {
            const blob = document.createElement('div');
            blob.className = 'theme-blob';
            // Semi-transparent solid colors so they don't overpower images, but no blurred glow
            blob.style.background = themeColor;
            blob.style.opacity = "0.85";
            blob.style.left = (myRand() * 80) + 'vw';
            blob.style.top = (myRand() * 80) + 'vh';
            blob.style.animationDuration = (12 + myRand() * 10) + 's';
            blob.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(blob);
        }
    } else if (styleType === 1) {
        // Organic Morphing Blobs (Solid flat colors with animated complex border-radius)
        container.style.filter = "none";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<5; i++) {
            const orb = document.createElement('div');
            orb.className = 'theme-orb';
            orb.style.background = themeColor;
            orb.style.opacity = "0.85";
            orb.style.left = (myRand() * 60 - 10) + 'vw';
            orb.style.top = (myRand() * 60 - 10) + 'vh';
            orb.style.animationDuration = (15 + myRand() * 15) + 's';
            orb.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(orb);
        }
    } else {
        // Large Jagged Geometric Shapes
        container.style.filter = "none";
        container.style.mixBlendMode = "normal";
        const polygons = [
            'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)', // Pentagon
            'polygon(25% 0%, 100% 0%, 75% 100%, 0% 100%)', // Parallelogram
            'polygon(50% 0%, 0% 100%, 100% 100%)', // Triangle
            'polygon(40% 0%, 100% 20%, 80% 100%, 0% 80%)', // Irregular quad
            'polygon(0% 15%, 15% 15%, 15% 0%, 85% 0%, 85% 15%, 100% 15%, 100% 85%, 85% 85%, 85% 100%, 15% 100%, 15% 85%, 0% 85%)' // Cross
        ];
        
        for(let i=0; i<12; i++) { // Fewer but much larger shapes
            const shape = document.createElement('div');
            shape.className = 'theme-sharp';
            shape.style.background = themeColor;
            shape.style.opacity = "0.85";
            shape.style.left = (myRand() * 80) + 'vw';
            shape.style.top = (myRand() * 80) - 10 + 'vh';
            shape.style.animationDuration = (20 + myRand() * 15) + 's';
            shape.style.animationDelay = '-' + (myRand() * 10) + 's';
            
            shape.style.clipPath = polygons[Math.floor(myRand() * polygons.length)];
            const size = (60 + myRand() * 120) + 'px'; // Huge distinct shapes
            shape.style.width = size;
            shape.style.height = size;
            
            container.appendChild(shape);
        }
    }
}
