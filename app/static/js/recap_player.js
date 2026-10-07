window.recapTimeouts = [];
window.recapSetTimeout = function(fn, ms) {
    let t = window.setTimeout(fn, ms);
    window.recapTimeouts.push(t);
    return t;
};


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
    
    // DUPLICATE PHOTOS IF NOT ENOUGH (fixes the loop breaking / sticking to left bug)
    // Swiper's loop + slidesPerView 'auto' requires enough items to fill the view plus padding.
    const originalDeck = [...deck];
    while (deck.length < 15) {
        deck = deck.concat(originalDeck);
    }
    deck = deck.slice(0, 24);
    
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
        speed: 800,
        autoplay: { delay: 2500, disableOnInteraction: false },
        loopedSlides: deck.length, // Ensures cloning works perfectly
        coverflowEffect: {
            rotate: 45,
            stretch: -20,
            depth: 250,
            modifier: 1,
            slideShadows: false, // Prevents dark ghosting overlay during scroll
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
function handleParallaxMouseMove(e) {}

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
    
    if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') {
        prevRecapSlide();
    } else if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') {
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
    Array.from(clone.children).forEach(c => { c.style.transition='opacity 0.2s'; c.style.opacity='0'; });
    
    // Put clone inside the overlay so it doesn't obscure the preloader
    const overlay = document.getElementById('recap-player-overlay');
    clone.style.zIndex = '10'; // Put it at the bottom of the overlay's stacking context
    overlay.insertBefore(clone, overlay.firstChild);
    
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
    const preloader = document.getElementById('recap-preloader');
    
    
    // Reset state
    overlay.classList.remove('hidden');
    preloader.classList.remove('slide-up');
    document.getElementById('recap-slides-container').classList.add('hidden');
    
    const slideTopPlaces = document.getElementById('slide-top-places');
    if (slideTopPlaces) slideTopPlaces.style.display = '';

    
    // Attach listeners (removed on close)
    
    document.addEventListener('keydown', handleRecapKeyboard);
    


    // M3 Expressive Theming & Shapes based on Year
    let fetchYear = year || new Date().getFullYear();
    
    const m3Themes = [
        { primary: '#D0BCFF', surface: '#4A4458', canvas: 'radial-gradient(circle at 50% 50%, #4A4458 0%, #000 100%)' }, // Purple
        { primary: '#FFB59B', surface: '#5D3C28', canvas: 'radial-gradient(circle at 50% 50%, #5D3C28 0%, #000 100%)' }, // Peach
        { primary: '#82D9AD', surface: '#1E4E36', canvas: 'radial-gradient(circle at 50% 50%, #1E4E36 0%, #000 100%)' }, // Mint
        { primary: '#AEC6FF', surface: '#19376D', canvas: 'radial-gradient(circle at 50% 50%, #19376D 0%, #000 100%)' }, // Azure
        { primary: '#FFB4AB', surface: '#690005', canvas: 'radial-gradient(circle at 50% 50%, #690005 0%, #000 100%)' }, // Rose
        { primary: '#E2E25E', surface: '#494A00', canvas: 'radial-gradient(circle at 50% 50%, #494A00 0%, #000 100%)' }  // Lemon
    ];
    
    // Hash year to a theme
    const themeIndex = parseInt(fetchYear) % m3Themes.length;
    const theme = m3Themes[themeIndex];
    
    // Apply CSS Variables
    overlay.style.setProperty('--m3-primary', theme.primary);
    overlay.style.setProperty('--m3-surface', theme.surface);
    const canvas = document.getElementById('m3-aurora-canvas');
    if (canvas) canvas.style.background = theme.canvas;
    
    // Inject Dynamic Year Title (Watermark)
    let watermark = document.getElementById('recap-year-watermark');
    if (!watermark) {
        watermark = document.createElement('div');
        watermark.id = 'recap-year-watermark';
        watermark.style.position = 'absolute';
        watermark.style.top = '32px';
        watermark.style.left = '48px';
        watermark.style.fontFamily = "'Outfit', sans-serif";
        watermark.style.fontSize = '2.5rem';
        watermark.style.fontWeight = '900';
        watermark.style.opacity = '0.5';
        watermark.style.zIndex = '999';
        watermark.style.transition = 'color 0.5s';
        overlay.appendChild(watermark);
    }
    watermark.style.color = theme.primary;
    watermark.innerText = month ? `${month} ${fetchYear}` : fetchYear;
    
    // Replace abstract shapes with massive SVG M3 Expressive paths
    const shapesContainer = document.querySelector('.m3-expressive-shapes');
    if (shapesContainer) {
                shapesContainer.innerHTML = `
            <!-- First Morpher: Top Right -->
            <svg class="m3-svg-shape shape-scallop" viewBox="0 0 100 100" style="position:absolute; width:120vh; height:120vh; top:-10%; right:-10%; opacity:0.04; fill: ${theme.primary}; animation: m3ShapeFloat1 25s infinite alternate ease-in-out;">
                <path d="M 100.0 50.0 C 100.0 54.0, 84.5 57.0, 83.3 60.8 C 82.1 64.6, 92.8 76.2, 90.5 79.4 C 88.1 82.6, 73.8 76.0, 70.6 78.3 C 67.4 80.7, 69.2 96.3, 65.5 97.6 C 61.7 98.8, 54.0 85.0, 50.0 85.0 C 46.0 85.0, 38.3 98.8, 34.5 97.6 C 30.8 96.3, 32.6 80.7, 29.4 78.3 C 26.2 76.0, 11.9 82.6, 9.5 79.4 C 7.2 76.2, 17.9 64.6, 16.7 60.8 C 15.5 57.0, 0.0 54.0, 0.0 50.0 C -0.0 46.0, 15.5 43.0, 16.7 39.2 C 17.9 35.4, 7.2 23.8, 9.5 20.6 C 11.9 17.4, 26.2 24.0, 29.4 21.7 C 32.6 19.3, 30.8 3.7, 34.5 2.4 C 38.3 1.2, 46.0 15.0, 50.0 15.0 C 54.0 15.0, 61.7 1.2, 65.5 2.4 C 69.2 3.7, 67.4 19.3, 70.6 21.7 C 73.8 24.0, 88.1 17.4, 90.5 20.6 C 92.8 23.8, 82.1 35.4, 83.3 39.2 C 84.5 43.0, 100.0 46.0, 100.0 50.0 Z">
                    <animate attributeName="d" dur="15s" repeatCount="indefinite" values="M 100.0 50.0 C 100.0 54.0, 84.5 57.0, 83.3 60.8 C 82.1 64.6, 92.8 76.2, 90.5 79.4 C 88.1 82.6, 73.8 76.0, 70.6 78.3 C 67.4 80.7, 69.2 96.3, 65.5 97.6 C 61.7 98.8, 54.0 85.0, 50.0 85.0 C 46.0 85.0, 38.3 98.8, 34.5 97.6 C 30.8 96.3, 32.6 80.7, 29.4 78.3 C 26.2 76.0, 11.9 82.6, 9.5 79.4 C 7.2 76.2, 17.9 64.6, 16.7 60.8 C 15.5 57.0, 0.0 54.0, 0.0 50.0 C -0.0 46.0, 15.5 43.0, 16.7 39.2 C 17.9 35.4, 7.2 23.8, 9.5 20.6 C 11.9 17.4, 26.2 24.0, 29.4 21.7 C 32.6 19.3, 30.8 3.7, 34.5 2.4 C 38.3 1.2, 46.0 15.0, 50.0 15.0 C 54.0 15.0, 61.7 1.2, 65.5 2.4 C 69.2 3.7, 67.4 19.3, 70.6 21.7 C 73.8 24.0, 88.1 17.4, 90.5 20.6 C 92.8 23.8, 82.1 35.4, 83.3 39.2 C 84.5 43.0, 100.0 46.0, 100.0 50.0 Z; M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z; M 100.0 50.0 C 100.0 54.7, 99.0 61.0, 97.6 65.5 C 96.1 69.9, 93.2 75.6, 90.5 79.4 C 87.7 83.2, 83.2 87.7, 79.4 90.5 C 75.6 93.2, 69.9 96.1, 65.5 97.6 C 61.0 99.0, 54.7 100.0, 50.0 100.0 C 45.3 100.0, 39.0 99.0, 34.5 97.6 C 30.1 96.1, 24.4 93.2, 20.6 90.5 C 16.8 87.7, 12.3 83.2, 9.5 79.4 C 6.8 75.6, 3.9 69.9, 2.4 65.5 C 1.0 61.0, 0.0 54.7, 0.0 50.0 C -0.0 45.3, 1.0 39.0, 2.4 34.5 C 3.9 30.1, 6.8 24.4, 9.5 20.6 C 12.3 16.8, 16.8 12.3, 20.6 9.5 C 24.4 6.8, 30.1 3.9, 34.5 2.4 C 39.0 1.0, 45.3 0.0, 50.0 0.0 C 54.7 -0.0, 61.0 1.0, 65.5 2.4 C 69.9 3.9, 75.6 6.8, 79.4 9.5 C 83.2 12.3, 87.7 16.8, 90.5 20.6 C 93.2 24.4, 96.1 30.1, 97.6 34.5 C 99.0 39.0, 100.0 45.3, 100.0 50.0 Z; M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z; M 100.0 50.0 C 100.0 54.0, 84.5 57.0, 83.3 60.8 C 82.1 64.6, 92.8 76.2, 90.5 79.4 C 88.1 82.6, 73.8 76.0, 70.6 78.3 C 67.4 80.7, 69.2 96.3, 65.5 97.6 C 61.7 98.8, 54.0 85.0, 50.0 85.0 C 46.0 85.0, 38.3 98.8, 34.5 97.6 C 30.8 96.3, 32.6 80.7, 29.4 78.3 C 26.2 76.0, 11.9 82.6, 9.5 79.4 C 7.2 76.2, 17.9 64.6, 16.7 60.8 C 15.5 57.0, 0.0 54.0, 0.0 50.0 C -0.0 46.0, 15.5 43.0, 16.7 39.2 C 17.9 35.4, 7.2 23.8, 9.5 20.6 C 11.9 17.4, 26.2 24.0, 29.4 21.7 C 32.6 19.3, 30.8 3.7, 34.5 2.4 C 38.3 1.2, 46.0 15.0, 50.0 15.0 C 54.0 15.0, 61.7 1.2, 65.5 2.4 C 69.2 3.7, 67.4 19.3, 70.6 21.7 C 73.8 24.0, 88.1 17.4, 90.5 20.6 C 92.8 23.8, 82.1 35.4, 83.3 39.2 C 84.5 43.0, 100.0 46.0, 100.0 50.0 Z" keyTimes="0; 0.25; 0.5; 0.75; 1" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1" />
                </path>
            </svg>
            
            <!-- Second Morpher: Bottom Left -->
            <svg class="m3-svg-shape shape-star" viewBox="0 0 100 100" style="position:absolute; width:100vh; height:100vh; bottom:-10%; left:-10%; opacity:0.03; fill: ${theme.primary}; animation: m3ShapeFloat2 30s infinite alternate ease-in-out; transform-origin: center;">
                <path d="M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z">
                    <animate attributeName="d" dur="12s" repeatCount="indefinite" values="M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z; M 100.0 50.0 C 100.0 54.0, 84.5 57.0, 83.3 60.8 C 82.1 64.6, 92.8 76.2, 90.5 79.4 C 88.1 82.6, 73.8 76.0, 70.6 78.3 C 67.4 80.7, 69.2 96.3, 65.5 97.6 C 61.7 98.8, 54.0 85.0, 50.0 85.0 C 46.0 85.0, 38.3 98.8, 34.5 97.6 C 30.8 96.3, 32.6 80.7, 29.4 78.3 C 26.2 76.0, 11.9 82.6, 9.5 79.4 C 7.2 76.2, 17.9 64.6, 16.7 60.8 C 15.5 57.0, 0.0 54.0, 0.0 50.0 C -0.0 46.0, 15.5 43.0, 16.7 39.2 C 17.9 35.4, 7.2 23.8, 9.5 20.6 C 11.9 17.4, 26.2 24.0, 29.4 21.7 C 32.6 19.3, 30.8 3.7, 34.5 2.4 C 38.3 1.2, 46.0 15.0, 50.0 15.0 C 54.0 15.0, 61.7 1.2, 65.5 2.4 C 69.2 3.7, 67.4 19.3, 70.6 21.7 C 73.8 24.0, 88.1 17.4, 90.5 20.6 C 92.8 23.8, 82.1 35.4, 83.3 39.2 C 84.5 43.0, 100.0 46.0, 100.0 50.0 Z; M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z; M 100.0 50.0 C 100.0 54.7, 99.0 61.0, 97.6 65.5 C 96.1 69.9, 93.2 75.6, 90.5 79.4 C 87.7 83.2, 83.2 87.7, 79.4 90.5 C 75.6 93.2, 69.9 96.1, 65.5 97.6 C 61.0 99.0, 54.7 100.0, 50.0 100.0 C 45.3 100.0, 39.0 99.0, 34.5 97.6 C 30.1 96.1, 24.4 93.2, 20.6 90.5 C 16.8 87.7, 12.3 83.2, 9.5 79.4 C 6.8 75.6, 3.9 69.9, 2.4 65.5 C 1.0 61.0, 0.0 54.7, 0.0 50.0 C -0.0 45.3, 1.0 39.0, 2.4 34.5 C 3.9 30.1, 6.8 24.4, 9.5 20.6 C 12.3 16.8, 16.8 12.3, 20.6 9.5 C 24.4 6.8, 30.1 3.9, 34.5 2.4 C 39.0 1.0, 45.3 0.0, 50.0 0.0 C 54.7 -0.0, 61.0 1.0, 65.5 2.4 C 69.9 3.9, 75.6 6.8, 79.4 9.5 C 83.2 12.3, 87.7 16.8, 90.5 20.6 C 93.2 24.4, 96.1 30.1, 97.6 34.5 C 99.0 39.0, 100.0 45.3, 100.0 50.0 Z; M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z" keyTimes="0; 0.25; 0.5; 0.75; 1" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1" />
                </path>
            </svg>
        `;
    }

    // Fetch data — include month if provided
    let fetchUrl = `/api/recap/generate/${fetchYear}`;
    if (month) fetchUrl += `/${month}`;

    fetch(fetchUrl)
        .then(res => { if (!res.ok) throw new Error('API Error: ' + res.status); return res.json(); })
        .then(data => {
            if (!isRecapLoading) return;
            recapData = data;
            
            // Populate UI
            document.getElementById('recap-ai-comment').innerText = data.ai_comment;
            
            // We don't populate numbers yet, we animate them on slide load
            
            
            document.getElementById('recap-stat-person').innerText = data.top_person || "Yourself!";
              initSkiper47Carousel('person-photos-fan', data.top_person_photos, data.top_person_feature);

            
            if (data.top_places && data.top_places.length > 0) {
                buildPlacesAccordion(data.top_places);
            } else {
                const s = document.getElementById('slide-top-places');
                if (s) s.style.display = 'none';
            }
            
            // Skiper 30 Parallax Gallery removed per user preference.

            // Set backdrop (Parallax) and Hero image
            const backdropImg = data.memorable_moment || (clone.querySelector('img') ? clone.querySelector('img').src : '');
            if (backdropImg) {
                let imgUrl = backdropImg;
                if (!backdropImg.startsWith('http') && !backdropImg.startsWith('blob:') && !backdropImg.startsWith('data:')) {
                    imgUrl = `/api/photo/thumbnail/${encodeURIComponent(backdropImg)}`;
                }
                document.getElementById('recap-backdrop').style.backgroundImage = `url('${imgUrl}')`;
                
                
            }
            
            // Finish loader
            
            
            window.recapSetTimeout(() => {
                // PRELOADER: Wait for all high-res main images to download
                let preloadUrls = [];
                
                if (data.top_person_photos) preloadUrls = preloadUrls.concat(data.top_person_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
                if (data.top_person_feature) preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.top_person_feature)}`);
                if (data.iconic_place_photos) preloadUrls = preloadUrls.concat(data.iconic_place_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
                if (data.moment_photos) {
                    // Skip full res for marquee
                } else if (data.memorable_moment) {
                    preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.memorable_moment)}`);
                }
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
                let timerPromise = new Promise(resolve => window.recapSetTimeout(resolve, 800));
                loadPromises.push(timerPromise);
                
                let preloaderText = document.querySelector('.preloader-text');
                if(preloaderText) preloaderText.innerText = "Developing high-res photos...";
                
                Promise.all(loadPromises).then(() => {
                    // Slide up preloader (Skiper 15)
                    preloader.classList.add('slide-up');
                        
                    // Show slides
                    document.getElementById('recap-slides-container').classList.remove('hidden');
                    
                    // Remove clone
                    if (clone) { clone.style.opacity = '0'; window.recapSetTimeout(() => clone.remove(), 600); }
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
            console.error("RECAP PLAYER CRASH:", err);
            isRecapLoading = false;
            
            // RED SCREEN OF DEATH
            const errorDiv = document.createElement('div');
            errorDiv.style.position = 'fixed';
            errorDiv.style.top = '0';
            errorDiv.style.left = '0';
            errorDiv.style.width = '100vw';
            errorDiv.style.height = '100vh';
            errorDiv.style.backgroundColor = '#d32f2f';
            errorDiv.style.color = '#fff';
            errorDiv.style.zIndex = '999999';
            errorDiv.style.padding = '40px';
            errorDiv.style.fontFamily = 'monospace';
            errorDiv.style.overflow = 'auto';
            
            errorDiv.innerHTML = `
                <h1 style="font-size:3rem;margin-top:0;">RECAP CRASHED</h1>
                <p style="font-size:1.5rem;"><b>Message:</b> ${err.message || err}</p>
                <p style="font-size:1.2rem;"><b>Location:</b> recap_player.js - openRecapPlayer</p>
                <pre style="background:rgba(0,0,0,0.3);padding:20px;border-radius:8px;margin-top:20px;white-space:pre-wrap;">${err.stack || 'No stack trace'}</pre>
                <button onclick="this.parentElement.remove(); closeRecapPlayer();" style="margin-top:30px;padding:10px 20px;font-size:1.2rem;background:#fff;color:#d32f2f;border:none;border-radius:4px;cursor:pointer;font-weight:bold;">Close Error & Exit Player</button>
            `;
            document.body.appendChild(errorDiv);
        });
}

function showRecapSlide(index) {
    recapSlides.forEach((s, i) => {
        if (i === index) {
            s.classList.add('active');
            
            // Epic Journeys Auto-Sequence
            if (s.id === 'slide-top-places') {
                playPlacesAccordionSequence();
            }

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
                        window.recapSetTimeout(() => {
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
                                window.recapSetTimeout(() => {
                                    // Scatter out
                                    const allBurst = container.querySelectorAll('.montage-burst-photo');
                                    allBurst.forEach(p => {
                                        p.style.transition = 'transform 0.5s ease-in, opacity 0.5s ease-in';
                                        p.style.transform = `scale(0.1) translate(0,0) rotate(-45deg)`;
                                        p.style.opacity = '0';
                                    });
                                    
                                    // Auto-advance to intro text slide
                                    window.recapSetTimeout(() => {
                                        nextRecapSlide();
                                    }, 600); // Wait for scatter animation
                                }, 1500); // Hold the final burst for 1.5s
                            }
                        }, idx * 180); // 180ms delay between drops
                    });
                } else {
                    // Skip montage if no photos
                    window.recapSetTimeout(nextRecapSlide, 50);
                }
            }
            
            // If it's the stats slide, trigger number animation (Skiper 37)
            if (s.id === 'slide-stats' && recapData) {
                const p = document.getElementById('recap-stat-photos');
                const v = document.getElementById('recap-stat-videos');
                p.innerHTML = '0';
                v.innerHTML = '0';
                window.recapSetTimeout(() => {
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
    
    const validRunners = runnersUp.filter(r => r.cover_face_id && r.name && !r.name.startsWith('Unnamed') && !r.name.startsWith('Person '));
    if (validRunners.length < 1) {
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
        
        const angle = (i / validRunners.length) * Math.PI * 2;
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


function playSkiper79Transition(titleText, callback, overridePhotos = null) {
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
    
    const fallbackPhotos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const photos = (overridePhotos && overridePhotos.length > 0) ? overridePhotos : fallbackPhotos;
        
    let imgsToUse = [];
    if (photos.length > 0) {
        let pool = [...photos].sort(() => 0.5 - Math.random());
        // Pick 4 random photos for the collage
        while(pool.length > 0 && imgsToUse.length < 4) {
            imgsToUse.push(pool.pop());
        }
        // If we have fewer than 4 (e.g. only 2 top person photos), duplicate them to fill the collage
        let idx = 0;
        while(imgsToUse.length < 4 && imgsToUse.length > 0) {
            imgsToUse.push(photos[idx % photos.length]);
            idx++;
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
        img.src = '/api/photo/thumbnail/' + encodeURIComponent(p);
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
            layer.innerHTML = '';
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
    layer.style.opacity = '1';
    
    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const types = photos.length > 0 ? ['skiper-32', 'skiper-30', 'skiper-71', 'skiper-33'] : ['blur'];
    const type = types[Math.floor(Math.random() * types.length)]; // Dynamic
    
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
            img.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[i % photos.length]);
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
                layer.innerHTML = '';
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
        // Skiper 30 GSAP "Oliver Parallax" Depth Multi-Layer Blur
        layer.style.background = '#000';
        
        // Background layer (slow, highly blurred)
        const bgImg = document.createElement('img');
        bgImg.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        bgImg.style.position = 'absolute';
        bgImg.style.width = '100vw';
        bgImg.style.height = '100vh';
        bgImg.style.objectFit = 'cover';
        bgImg.style.opacity = '0';
        bgImg.style.filter = 'blur(20px)';
        bgImg.style.transform = 'scale(1.2)';
        layer.appendChild(bgImg);
        
        // Midground layer (medium speed, medium blur, smaller)
        const midImg = document.createElement('img');
        midImg.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        midImg.style.position = 'absolute';
        midImg.style.width = '60vw';
        midImg.style.height = '70vh';
        midImg.style.objectFit = 'cover';
        midImg.style.opacity = '0';
        midImg.style.borderRadius = '24px';
        midImg.style.boxShadow = '0 30px 60px rgba(0,0,0,0.8)';
        midImg.style.filter = 'blur(10px)';
        midImg.style.transform = 'scale(0.8) translateY(100px)';
        layer.appendChild(midImg);

        // Foreground layer (fast, sharp, prominent)
        const fgImg = document.createElement('img');
        fgImg.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        fgImg.style.position = 'absolute';
        fgImg.style.width = '40vw';
        fgImg.style.height = '50vh';
        fgImg.style.objectFit = 'cover';
        fgImg.style.opacity = '0';
        fgImg.style.borderRadius = '16px';
        fgImg.style.boxShadow = '0 50px 100px rgba(0,0,0,0.9)';
        fgImg.style.filter = 'blur(0px)';
        fgImg.style.transform = 'scale(0.5) translateY(200px)';
        layer.appendChild(fgImg);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                layer.innerHTML = '';
                isRecapTransitioning = false;
            }
        });
        
        // Fade in all layers
        tl.to([bgImg, midImg, fgImg], { opacity: 1, duration: 0.4 }, 0);
        
        // Parallax scroll animation
        tl.to(bgImg, { scale: 1.5, filter: 'blur(30px)', duration: 2.0, ease: 'power2.inOut' }, 0);
        tl.to(midImg, { scale: 1.1, translateY: '-150px', filter: 'blur(20px)', duration: 2.0, ease: 'power2.inOut' }, 0);
        tl.to(fgImg, { scale: 1.2, translateY: '-300px', filter: 'blur(10px)', duration: 2.0, ease: 'power2.inOut',
            onUpdate: function() {
                if(this.progress() > 0.6 && callback) {
                    callback();
                    callback = null;
                }
            }
        }, 0);
        
        // Fade out transition layer
        tl.to(layer, { opacity: 0, duration: 0.5, ease: 'power2.in' }, 1.5);
        
} else if (type === 'skiper-71') {
        // Skiper 71 GSAP Image Reveal (Clip Path Wipe)
        const img = document.createElement('img');
        img.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.clipPath = 'polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%)';
        layer.appendChild(img);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                layer.innerHTML = '';
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
            img.src = '/api/photo/thumbnail/' + encodeURIComponent(pool[i]);
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
                layer.innerHTML = '';
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
                        layer.innerHTML = '';
                isRecapTransitioning = false;
                    }
                });
            }
        });
    }
}
function nextRecapSlide() {
    if (window.recapTimeouts) {
        window.recapTimeouts.forEach(clearTimeout);
        window.recapTimeouts = [];
    }
    if (recapCurrentSlide < recapSlides.length - 1) {
        let nextSlideId = recapSlides[recapCurrentSlide + 1].id;
        
        let transitionTitle = null;
        let transitionPhotos = null;
        
        if (nextSlideId === 'slide-person') { 
            playMysteryRevealTransition(recapData?.top_person || "Someone Special", recapData?.runners_up || [], () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });
            return;
        }
        if (nextSlideId === 'slide-top-places') { transitionTitle = "EPIC JOURNEYS"; transitionPhotos = recapData?.top_places?.[0]?.photos || null; }
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            }, transitionPhotos);
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
    if (window.recapTimeouts) {
        window.recapTimeouts.forEach(clearTimeout);
        window.recapTimeouts = [];
    }
    if (recapCurrentSlide > 0) {
        let prevSlideId = recapSlides[recapCurrentSlide - 1].id;
        
        let transitionTitle = null;
        let transitionPhotos = null;
        
        if (prevSlideId === 'slide-person') { 
            playMysteryRevealTransition(recapData?.top_person || "Someone Special", recapData?.runners_up || [], () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
            return;
        }
        if (prevSlideId === 'slide-top-places') { transitionTitle = "EPIC JOURNEYS"; transitionPhotos = recapData?.top_places?.[0]?.photos || null; }
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            }, transitionPhotos);
        } else {
            playSlideTransition(() => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
        }
    }
}



// --- [REGION: TOP PLACES ACCORDION] ---
function buildPlacesAccordion(places) {
    const accordion = document.getElementById('places-accordion');
    if (!accordion) return;
    accordion.innerHTML = '';
    
    if (!places || places.length === 0) {
        document.getElementById('slide-top-places').style.display = 'none';
        return;
    }
    
    places.forEach((place, i) => {
        const item = document.createElement('div');
        item.className = 'place-accordion-item';
        item.id = `place-item-${i}`;
        
        // Thumbnail for collapsed state
        if (place.photos && place.photos.length > 0) {
            item.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(place.photos[0])}')`;
            item.style.backgroundSize = 'cover';
            item.style.backgroundPosition = 'center';
        }
        
        const title = document.createElement('div');
        title.className = 'place-item-title';
        title.innerText = place.name;
        item.appendChild(title);
        
        const wrapper = document.createElement('div');
        wrapper.className = 'place-carousel-wrapper';
        
        let swiperHtml = `<div class="swiper place-swiper-${i}"><div class="swiper-wrapper">`;
        place.photos.slice(0, 15).forEach(p => {
            swiperHtml += `<div class="swiper-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" /></div>`;
        });
        swiperHtml += `</div></div>`;
        wrapper.innerHTML = swiperHtml;
        item.appendChild(wrapper);
        
        item.addEventListener('click', () => {
            if (window.placeAutoAnim) {
                window.placeAutoAnim.kill();
                window.placeAutoAnim = null;
            }
            document.querySelectorAll('.place-accordion-item').forEach(el => el.classList.remove('expanded'));
            item.classList.add('expanded');
        });
        
        accordion.appendChild(item);
        
        new Swiper(`.place-swiper-${i}`, {
            loop: true,
            effect: 'fade',
            fadeEffect: { crossFade: true },
            autoplay: { delay: 1500, disableOnInteraction: false },
            allowTouchMove: false
        });
    });
}

function playPlacesAccordionSequence() {
    const items = document.querySelectorAll('.place-accordion-item');
    if (!items || items.length === 0) return;
    
    if (window.placeAutoAnim) window.placeAutoAnim.kill();
    items.forEach(el => el.classList.remove('expanded'));
    
    const tl = gsap.timeline();
    window.placeAutoAnim = tl;
    
    // Animate each one popping open for 3 seconds
    items.forEach((item, i) => {
        tl.call(() => {
            items.forEach(el => el.classList.remove('expanded'));
            item.classList.add('expanded');
        });
        tl.to({}, { duration: 3.5 }); 
    });
    
    // Finally, collapse all and wait for user interaction
    tl.call(() => {
        items.forEach(el => el.classList.remove('expanded'));
    });
}

// --- [REGION: CLOSE PLAYER] ---
function closeRecapPlayer() {
    if (window.recapDeckIntervals) {
        window.recapDeckIntervals.forEach(clearInterval);
        window.recapDeckIntervals = [];
    }
    if (window.recapTimeouts) {
        window.recapTimeouts.forEach(clearTimeout);
        window.recapTimeouts = [];
    }
    if (typeof gsap !== 'undefined') {
        gsap.killTweensOf('.siena-layer img');
    }
    
    document.removeEventListener('keydown', handleRecapKeyboard);
    
    const overlay = document.getElementById('recap-player-overlay');
    
    // Play a smooth GSAP fade out animation before hiding
    if (window.gsap && overlay && !overlay.classList.contains('hidden')) {
        gsap.to(overlay, { 
            opacity: 0, 
            duration: 0.6, 
            ease: "power2.inOut",
            onComplete: () => {
                overlay.classList.add('hidden');
                overlay.style.opacity = '1'; // reset for next open
                isRecapLoading = false;
                
                const clone = document.querySelector('.recap-transition-clone');
                if (clone) clone.remove();
                
                // Restore opacity to all cards that might have been clicked
                document.querySelectorAll('.rewind-hero-card, .rewind-mini-card').forEach(card => {
                    gsap.to(card, { opacity: 1, duration: 0.3 });
                });
            }
        });
    } else {
        overlay.classList.add('hidden');
        isRecapLoading = false;
        
        const clone = document.querySelector('.recap-transition-clone');
        if (clone) clone.remove();
        
        document.querySelectorAll('.rewind-hero-card, .rewind-mini-card').forEach(card => {
            card.style.opacity = '1';
        });
    }
}

function initSkiper54Carousel(containerId, photos) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    // Ensure we have enough photos for the 3D loop effect to work properly.
    // If they only have 1 or 2 photos of this place, Swiper will look broken/empty.
    // We duplicate the array until we have at least 5 slides.
    let deck = [...photos];
    while (deck.length < 15) {
        deck = deck.concat(photos);
    }
    deck = deck.slice(0, 24);
    
    let swiperHtml = `<div class="swiper skiper-54-swiper"><div class="swiper-wrapper">`;
    deck.forEach(p => {
        swiperHtml += `<div class="swiper-slide skiper-54-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" class="skiper-54-img" /></div>`;
    });
    swiperHtml += `</div><div class="swiper-pagination"></div></div>`;
    
    container.innerHTML = swiperHtml;
    
    new Swiper('.skiper-54-swiper', {
        effect: 'coverflow',
        slidesPerView: 'auto',
        centeredSlides: true,
        grabCursor: true,
        loop: true,
        speed: 800,
        autoplay: { delay: 2500, disableOnInteraction: false },
        loopedSlides: deck.length, // Ensures cloning works right for auto width
        observer: true,
        observeParents: true,
        coverflowEffect: {
            rotate: 0,
            stretch: -40,
            depth: 250,
            modifier: 1,
            slideShadows: false, // Cleaner, modern flat look requested
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
}


