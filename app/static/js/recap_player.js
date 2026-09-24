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


// Skiper29 Siena Parallax Depth Hover
document.addEventListener('mousemove', (e) => {
    const slides = document.querySelectorAll('.recap-slide.active');
    if(slides.length === 0) return;
    
    const slide = slides[0];
    const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
    
    // Tilt the slide container
    slide.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    
    // Move individual layers based on depth
    const layers = slide.querySelectorAll('.siena-layer');
    layers.forEach(layer => {
        const depth = layer.getAttribute('data-depth') || 20;
        const xOffset = (window.innerWidth / 2 - e.pageX) * (depth / 1000);
        const yOffset = (window.innerHeight / 2 - e.pageY) * (depth / 1000);
        layer.style.transform = `translateZ(${depth}px) translate(${xOffset}px, ${yOffset}px)`;
    });
});

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

function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        recapCurrentSlide++;
        showRecapSlide(recapCurrentSlide);
    } else {
        closeRecapPlayer();
    }
}

function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        recapCurrentSlide--;
        showRecapSlide(recapCurrentSlide);
    }
}

function closeRecapPlayer() {
    document.getElementById('recap-player-overlay').classList.add('hidden');
    const clone = document.querySelector('.recap-transition-clone');
    if (clone) clone.remove();
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
    
    const palettes = [
        ['#FF0A54', '#FF477E', '#FF7096', '#FF85A1', '#FBB1BD'], // Pink Goo
        ['#00F5D4', '#00BBF9', '#FEE440', '#F15BB5', '#9B5DE5'], // Retro Pop
        ['#FF9A9E', '#FECFEF', '#A1C4FD', '#C2E9FB', '#D4FC79'], // Dreamy Pastel
        ['#FA709A', '#FEE140', '#F3A183', '#556270', '#FF3CAC'], // Sunset Paint
        ['#8EC5FC', '#E0C3FC', '#4FACFE', '#00F2FE', '#38F9D7'], // Frosty Fluid
        ['#ff0055', '#0033ff', '#00ff99', '#ffff00', '#ff00ff']  // Cyber Neon
    ];
    
    const palette = palettes[Math.floor(myRand() * palettes.length)];
    const styleType = Math.floor(myRand() * 3); // 0 = Gooey, 1 = Soft Orbs, 2 = Sharp Confetti
    
    if (styleType === 0) {
        // Gooey Mixing Paint
        container.style.filter = "url('#recap-goo')";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<8; i++) {
            const blob = document.createElement('div');
            blob.className = 'theme-blob';
            blob.style.background = palette[i % palette.length];
            blob.style.left = (myRand() * 80) + 'vw';
            blob.style.top = (myRand() * 80) + 'vh';
            blob.style.animationDuration = (12 + myRand() * 10) + 's';
            blob.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(blob);
        }
    } else if (styleType === 1) {
        // Soft Gradient Orbs
        container.style.filter = "blur(80px)";
        container.style.mixBlendMode = "screen";
        for(let i=0; i<6; i++) {
            const orb = document.createElement('div');
            orb.className = 'theme-orb';
            orb.style.background = palette[i % palette.length];
            orb.style.left = (myRand() * 60 - 10) + 'vw';
            orb.style.top = (myRand() * 60 - 10) + 'vh';
            orb.style.animationDuration = (15 + myRand() * 15) + 's';
            orb.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(orb);
        }
    } else {
        // Sharp Geometric Confetti
        container.style.filter = "none";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<40; i++) {
            const shape = document.createElement('div');
            shape.className = 'theme-sharp';
            shape.style.background = palette[i % palette.length];
            shape.style.left = (myRand() * 100) + 'vw';
            shape.style.top = (myRand() * 100) - 20 + 'vh';
            shape.style.animationDuration = (4 + myRand() * 8) + 's';
            shape.style.animationDelay = '-' + (myRand() * 10) + 's';
            
            // Randomly pick triangle, square, or line
            const r = myRand();
            if (r < 0.33) {
                shape.style.clipPath = 'polygon(50% 0%, 0% 100%, 100% 100%)';
                shape.style.width = (30 + myRand() * 60) + 'px';
                shape.style.height = (30 + myRand() * 60) + 'px';
            } else if (r < 0.66) {
                shape.style.borderRadius = (myRand() * 20) + 'px'; // rounded rect
                shape.style.width = (20 + myRand() * 50) + 'px';
                shape.style.height = (20 + myRand() * 50) + 'px';
            } else {
                shape.style.borderRadius = '50%';
                shape.style.width = (10 + myRand() * 40) + 'px';
                shape.style.height = shape.style.width;
            }
            
            container.appendChild(shape);
        }
    }
}
