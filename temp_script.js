
        function toggleRecap() {
            const body = document.body;
            body.classList.toggle('recap-active');
            
            if (body.classList.contains('recap-active')) {
                // Set up Skiper11 Pixel Grid Preloader
                const preloader = document.getElementById('pixel-preloader');
                const counter = document.getElementById('pixel-counter');
                const grid = document.getElementById('pixel-grid');
                preloader.style.display = 'flex';
                counter.style.opacity = '1';
                grid.innerHTML = '';
                
                // Grab images from the page to use as mosaic thumbnails
                const availableImages = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                
                // Calculate perfect responsive grid to cover the screen
                const blockSize = 80;
                const cols = Math.ceil(window.innerWidth / blockSize);
                const rows = Math.ceil(window.innerHeight / blockSize);
                const totalBlocks = cols * rows;
                
                grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
                grid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
                
                for (let i = 0; i < totalBlocks; i++) {
                    const block = document.createElement('div');
                    block.className = 'pixel-block';
                    
                    // 40% chance to put a thumbnail in the block
                    if (Math.random() < 0.4 && availableImages.length > 0) {
                        const randomImg = availableImages[Math.floor(Math.random() * availableImages.length)];
                        block.style.backgroundImage = `url(${randomImg})`;
                    }
                    
                    grid.appendChild(block);
                }

                // Set up Skiper27 Rolling Text
                const title = document.getElementById('recap-title');
                title.innerHTML = '';
                title.classList.remove('revealed');
                
                const text = "Your Rewinds"; // We rely on font-display without uppercase now
                text.split('').forEach((char, i) => {
                    const wrapper = document.createElement('span');
                    wrapper.className = 'roll-char-wrap';
                    
                    const inner = document.createElement('span');
                    inner.className = 'roll-char';
                    inner.innerText = char === ' ' ? '\u00A0' : char;
                    // Custom speed: 0.05 delay between letters
                    inner.style.transitionDelay = (i * 0.05) + 's';
                    
                    wrapper.appendChild(inner);
                    title.appendChild(wrapper);
                });

                // Simulate Loading for Pixel Preloader
                let count = 0;
                const interval = setInterval(() => {
                    count += Math.floor(Math.random() * 10) + 5;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        
                        // Pixel Wipe Animation (slef.me style)
                        counter.style.opacity = '0';
                        const blocks = Array.from(grid.children);
                        // Shuffle array for random pixel disappearance
                        blocks.sort(() => Math.random() - 0.5);
                        
                        // Start text reveal underneath the pixels!
                        title.classList.add('revealed');

                        const totalDuration = 800; // Wipe finishes in 0.8s total
                        const staggerDelay = totalDuration / blocks.length;

                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * staggerDelay);
                        });
                        
                        setTimeout(() => {
                            preloader.style.opacity = '0'; // Smooth fade out
                            setTimeout(() => {
                                preloader.style.display = 'none';
                            }, 800);
                            
                            // 1.5 seconds after reveal, morph to options
                            setTimeout(() => {
                                document.getElementById('recap-container').classList.add('options-active');
                                document.getElementById('rewind-dashboard').classList.add('active');
                                // Bulletproof Smart Thumbnail Assignment
                                const getBestImage = (keyword, seed) => {
                                    return `/static/images/placeholder.png`; // M6: Local fallback instead of picsum
                                };
                                
                                const heroContainer = document.getElementById('hero-bg-container');
                                heroContainer.innerHTML = '';
                                
                                // Step 1: Set instant synchronous fallbacks
                                let heroImages = [];
                                let attempts = 0;
                                while(heroImages.length < 3 && attempts < 20) {
                                    heroImages.push(`/static/images/placeholder.png`);
                                    attempts++;
                                }
                                
                                heroImages.forEach((src, idx) => {
                                    let div = document.createElement('div');
                                    div.className = `hero-collage-item hero-collage-${idx+1}`;
                                    div.style.backgroundImage = `url('${src}')`;
                                    heroContainer.appendChild(div);
                                });
                                
                                document.querySelectorAll('.rewind-mini-card').forEach(card => {
                                    const overlayText = card.querySelector('.mini-overlay').innerText;
                                    
                                    // Force monthly rewinds to query specifically for the current year
                                    let queryText = overlayText;
                                    if (!card.classList.contains('year-card')) {
                                        queryText = `${overlayText} ${new Date().getFullYear()}`;
                                    }
                                    
                                    // Step 2: Asynchronously fetch true photos for this exact month/year!
                                    fetch('/api/photos?date_query=' + encodeURIComponent(queryText))
                                        .then(res => res.json())
                                        .then(photos => {
                                            if (photos && photos.length > 0) {
                                                let randomPhoto = photos[Math.floor(Math.random() * photos.length)];
                                                card.querySelector('img').src = '/api/photo/thumbnail/' + encodeURIComponent(randomPhoto.path);
                                            }
                                        }).catch(err => console.log('Rewind API fetch failed:', err));
                                });
                                
                                // Fetch true photos for the Hero Collage (Current Year Recap)
                                const currentYearStr = String(new Date().getFullYear());
                                fetch('/api/photos?date_query=' + currentYearStr)
                                    .then(res => res.json())
                                    .then(photos => {
                                        if (photos && photos.length >= 3) {
                                            // Shuffle array
                                            photos.sort(() => 0.5 - Math.random());
                                            document.querySelectorAll('.hero-collage-item').forEach((div, idx) => {
                                                // We use /thumbnail/ to load fast, or /file/ for high-res. 
                                                // The hero is large, so let's use the file API but let it load naturally
                                                div.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(photos[idx].path)}')`;
                                            });
                                        }
                                    }).catch(err => console.log('Hero API fetch failed:', err));

                                // Enable Mouse Drag to Scroll
                                document.querySelectorAll('.rewind-row').forEach(row => {
                                    let isDown = false;
                                    let startX;
                                    let scrollLeft;
                                    row.addEventListener('mousedown', (e) => {
                                        isDown = true;
                                        row.style.cursor = 'grabbing';
                                        startX = e.pageX - row.offsetLeft;
                                        scrollLeft = row.scrollLeft;
                                    });
                                    row.addEventListener('mouseleave', () => { isDown = false; row.style.cursor = 'grab'; });
                                    row.addEventListener('mouseup', () => { isDown = false; row.style.cursor = 'grab'; });
                                    row.addEventListener('mousemove', (e) => {
                                        if(!isDown) return;
                                        e.preventDefault();
                                        const x = e.pageX - row.offsetLeft;
                                        const walk = (x - startX) * 2;
                                        row.scrollLeft = scrollLeft - walk;
                                    });
                                });
                            }, 1500);
                        }, totalDuration + 100);
                    }
                    counter.innerText = count + '%';
                }, 100);
            }
        }
    
