
// Welcome Hero Slideshow
let heroInterval = null;
const initWelcomeHero = async () => {
    try {
        const res = await fetch('/api/memories/welcome');
        const data = await res.json();
        const photos = data.photos;
        if (!photos || photos.length === 0) return;
        
        const bgsContainer = document.getElementById('welcome-hero-bgs');
        if (!bgsContainer) return;
        
        bgsContainer.innerHTML = ''; // clear
        
        // Create img divs
        const imgDivs = [];
        photos.forEach((photo, i) => {
            const div = document.createElement('div');
            div.className = 'hero-bg-img';
            if (i === 0) {
                div.style.backgroundImage = `url('${photo.url}')`;
                div.classList.add('active');
            } else {
                setTimeout(() => {
                    div.style.backgroundImage = `url('${photo.url}')`;
                }, 1500 + (i * 100)); 
            }
            bgsContainer.appendChild(div);
            imgDivs.push(div);
        });

        const updateHeroMetadata = (photo) => {
            const hr = new Date().getHours();
            let greeting = 'Good Evening';
            if (hr < 12) greeting = 'Good Morning';
            else if (hr < 17) greeting = 'Good Afternoon';
            
            const elGreeting = document.getElementById('hero-greeting');
            if(elGreeting) elGreeting.innerText = greeting;

            const quotes = [
                "Enjoy your memories.",
                "Moments to remember.",
                "A beautifully captured moment.",
                "Take a trip down memory lane."
            ];
            let quote = quotes[Math.floor(Math.random() * quotes.length)];
            if (photo.location) quote = `Looking back at ${photo.location.split(',')[0]}`;
            
            const elQuote = document.getElementById('hero-quote');
            if(elQuote) elQuote.innerText = quote;
            
            const elLoc = document.getElementById('hero-location');
            if(elLoc) elLoc.innerText = photo.location || 'Unknown Location';
            
            let dateStr = 'Unknown Date';
            if (photo.date) {
                const d = new Date(photo.date);
                if (!isNaN(d.getTime())) {
                    dateStr = d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
                }
            }
            const elDate = document.getElementById('hero-date');
            if(elDate) elDate.innerText = dateStr;

            const btn = document.getElementById('hero-lightbox-btn');
            if(btn) {
                btn.onclick = () => {
                    if (typeof openLightbox === 'function') openLightbox(photo.path);
                };
            }
        };

        if (photos.length > 0) updateHeroMetadata(photos[0]);

        if (heroInterval) clearInterval(heroInterval);
        if (imgDivs.length > 1) {
            let curr = 0;
            heroInterval = setInterval(() => {
                imgDivs[curr].classList.remove('active');
                curr = (curr + 1) % imgDivs.length;
                imgDivs[curr].classList.add('active');
                updateHeroMetadata(photos[curr]);
            }, 10000);
        }
    } catch (e) {
        console.error("Failed to init welcome hero", e);
    }
};

function loadMemories() {
    const container = document.getElementById('memories-container');
    const peopleContainer = document.getElementById('people-spotlight-container');
    
    container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Finding memories...</p></div>`;
    if (peopleContainer) peopleContainer.innerHTML = '';
    
    Promise.all([
        fetch('/api/memories/on_this_day').then(res => res.json()),
        fetch('/api/memories/curated').then(res => res.json())
    ]).then(([onThisDayData, curatedData]) => {
        container.innerHTML = '';
        // Init the welcome hero
        initWelcomeHero();

        if (peopleContainer) {
            peopleContainer.innerHTML = '';
            // Force remove old cached header if user hasn't hard refreshed
            const prevSibling = peopleContainer.previousElementSibling;
            if (prevSibling && prevSibling.classList.contains('section-header') && prevSibling.innerHTML.includes('People Spotlight')) {
                prevSibling.remove();
            }
        }
        
        const carouselContainer = document.createElement('div');
        carouselContainer.className = 'memories-carousel-container';
        
        const track = document.createElement('div');
        track.className = 'memories-track';
        
        const btnLeft = document.createElement('div');
        btnLeft.className = 'carousel-btn carousel-btn-left hidden';
        btnLeft.innerHTML = '<i data-lucide="chevron-left"></i>';
        
        const btnRight = document.createElement('div');
        btnRight.className = 'carousel-btn carousel-btn-right hidden';
        btnRight.innerHTML = '<i data-lucide="chevron-right"></i>';
        
        carouselContainer.appendChild(btnLeft);
        carouselContainer.appendChild(track);
        carouselContainer.appendChild(btnRight);
        
        // Handle pagination scroll
        const scrollAmount = () => carouselContainer.clientWidth * 0.8;
        btnLeft.addEventListener('click', () => {
            track.scrollBy({ left: -scrollAmount(), behavior: 'smooth' });
        });
        btnRight.addEventListener('click', () => {
            track.scrollBy({ left: scrollAmount(), behavior: 'smooth' });
        });
        
        track.addEventListener('scroll', () => {
            if (track.scrollLeft > 20) btnLeft.classList.remove('hidden');
            else btnLeft.classList.add('hidden');
            
            if (track.scrollLeft < track.scrollWidth - track.clientWidth - 20) btnRight.classList.remove('hidden');
            else btnRight.classList.add('hidden');
        });
        
        // Init buttons later after items append
        setTimeout(() => {
            if (track.scrollWidth > track.clientWidth) btnRight.classList.remove('hidden');
        }, 500);

        // --- Helpers ---
        const addCarouselCard = (titleText, items, targetTrack, extraClass='') => {
            if (!items || items.length === 0) return null;
            
            const wrapper = document.createElement('div');
            wrapper.className = 'memory-card-wrapper' + (extraClass ? ' ' + extraClass : '');
            
            const card = document.createElement('div');
            card.className = 'memory-card' + (extraClass ? ' ' + extraClass : '');
            
            const bg1 = document.createElement('div');
            bg1.className = 'memory-card-bg';
            bg1.style.transition = 'opacity 0.6s ease';
            
            const bg2 = document.createElement('div');
            bg2.className = 'memory-card-bg';
            bg2.style.transition = 'opacity 0.6s ease';
            bg2.style.opacity = '0';
            
            let currentBg = bg1;
            let nextBg = bg2;
            
            const overlay = document.createElement('div');
            overlay.className = 'memory-card-overlay';
            
            const title = document.createElement('div');
            title.className = 'memory-card-title';
            title.innerText = titleText;
            
            const subtitle = document.createElement('div');
            subtitle.className = 'memory-card-subtitle';
            
            const progressContainer = document.createElement('div');
            progressContainer.className = 'memory-progress-bar-container';
            const progressBar = document.createElement('div');
            progressBar.className = 'memory-progress-bar';
            progressContainer.appendChild(progressBar);
            
            if (items.length <= 1) {
                progressContainer.style.display = 'none';
            }
            
            overlay.appendChild(title);
            overlay.appendChild(subtitle);
            card.appendChild(bg1);
            card.appendChild(bg2);
            card.appendChild(overlay);
            card.appendChild(progressContainer);
            wrapper.appendChild(card);
            targetTrack.appendChild(wrapper);
            
            bg1.style.zIndex = '1';
            bg2.style.zIndex = '1';
            overlay.style.zIndex = '10';
            progressContainer.style.zIndex = '10';
            
            let currIdx = 0;
            let currentVideoEl = null;
            let currentBadge = null;
            let interval = null;

            let isHovering = false;
            let hoverTimeout = null;
            let isMorphed = false;
            let currentTargetRatio = 4/3; 

            const showSlide = (idx) => {
                const item = items[idx];
                const safePath = item.file_path.replace(/\\/g, '/');
                const isVid = !!safePath.match(/\.(mp4|mov|avi|mkv|webm)$/i);
                const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(safePath)}`;
                
                const performSwap = () => {
                    nextBg.style.backgroundImage = `url('${thumbUrl}')`;
                    nextBg.style.backgroundSize = 'cover';
                    
                    nextBg.style.opacity = '1';
                    currentBg.style.opacity = '0';
                    
                    let temp = currentBg;
                    currentBg = nextBg;
                    nextBg = temp;
                    
                    subtitle.innerText = item.subtitle;
                };

                if (!isVid) {
                    const preloadImg = new Image();
                    preloadImg.onload = () => {
                        if (preloadImg.width) currentTargetRatio = preloadImg.width / preloadImg.height;
                        performSwap();
                    };
                    preloadImg.onerror = performSwap;
                    preloadImg.src = thumbUrl;
                } else {
                    performSwap();
                }
                
                if (currentVideoEl) {
                    currentVideoEl.pause();
                    currentVideoEl.removeAttribute('src');
                    currentVideoEl.load();
                    currentVideoEl.remove();
                    currentVideoEl = null;
                }
                if (window.memoriesCountdownIntervals && window.memoriesCountdownIntervals[wrapper.id]) {
                    clearInterval(window.memoriesCountdownIntervals[wrapper.id]);
                }
                if (currentBadge) { currentBadge.remove(); currentBadge = null; }

                if (isVid) {
                    currentVideoEl = document.createElement('video');
                    currentVideoEl.src = `/api/photo/file/${encodeURIComponent(safePath)}`;
                    currentVideoEl.muted = true;
                    currentVideoEl.loop = true;
                    currentVideoEl.preload = 'metadata';
                    currentVideoEl.style.position = 'absolute';
                    currentVideoEl.style.inset = '0';
                    currentVideoEl.style.width = '100%';
                    currentVideoEl.style.height = '100%';
                    currentVideoEl.style.objectFit = 'cover';
                    currentVideoEl.style.opacity = '1';
                    currentVideoEl.style.zIndex = '2';
                    card.appendChild(currentVideoEl);

                    currentBadge = document.createElement('div');
                    currentBadge.className = 'memory-video-badge';
                    currentBadge.style.zIndex = '10';
                    currentBadge.innerHTML = `<i data-lucide="play" style="width:14px; height:14px;"></i><span class="vid-duration"></span>`;
                    card.appendChild(currentBadge);
                    if (window.lucide) lucide.createIcons();
                    currentVideoEl.play().catch(e=>{});

                    let countdownInterval = null;
                    const updateCountdown = () => {
                        const span = currentBadge.querySelector('.vid-duration');
                        if (span && currentVideoEl.duration) {
                            const remaining = Math.max(0, currentVideoEl.duration - currentVideoEl.currentTime);
                            const mins = Math.floor(remaining / 60);
                            const secs = Math.floor(remaining % 60).toString().padStart(2, '0');
                            span.innerText = `${mins}:${secs}`;
                        }
                    };

                    currentVideoEl.addEventListener('loadedmetadata', () => {
                        updateCountdown();
                        if (currentVideoEl.videoWidth) currentTargetRatio = currentVideoEl.videoWidth / currentVideoEl.videoHeight;
                    });
                    window.memoriesCountdownIntervals = window.memoriesCountdownIntervals || {};
                    wrapper.id = wrapper.id || 'wrapper_' + Math.random().toString(36).substr(2, 9);
                    currentVideoEl.addEventListener('play', () => {
                        if (window.memoriesCountdownIntervals[wrapper.id]) clearInterval(window.memoriesCountdownIntervals[wrapper.id]);
                        window.memoriesCountdownIntervals[wrapper.id] = setInterval(updateCountdown, 500);
                    });
                    currentVideoEl.addEventListener('pause', () => {
                        if (window.memoriesCountdownIntervals[wrapper.id]) clearInterval(window.memoriesCountdownIntervals[wrapper.id]);
                    });
                    
                    if (isMorphed) {
                        currentVideoEl.style.objectFit = 'contain';
                    }
                }

                progressBar.style.animation = 'none';
                progressBar.offsetHeight;
                if (items.length > 1) {
                    progressBar.style.animation = 'memoryProgress 5s linear forwards';
                    if (isHovering) {
                        progressBar.style.animationPlayState = 'paused';
                    }
                }
            };
            
            card.addEventListener('click', () => {
                if (isMorphed) {
                    isMorphed = false;
                    isHovering = false;
                    if (hoverTimeout) clearTimeout(hoverTimeout);
                    card.style.position = '';
                    card.style.top = '';
                    card.style.left = '';
                    card.style.width = '';
                    card.style.height = '';
                    card.style.zIndex = '';
                    wrapper.style.zIndex = '';
                    card.style.boxShadow = '';
                    card.style.transition = '';
                    overlay.style.opacity = '1';
                    progressContainer.style.opacity = '1';
                    if (currentBadge) currentBadge.style.opacity = '1';
                    if (currentVideoEl) {
                        currentVideoEl.muted = true;
                        currentVideoEl.style.objectFit = 'cover';
                    } else {
                        bg1.style.backgroundSize = 'cover';
                        bg2.style.backgroundSize = 'cover';
                        let currentSafePath = items[currIdx].file_path.replace(/\\/g, '/');
                        currentBg.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(currentSafePath)}')`;
                    }
                }
                if (typeof state !== 'undefined') state.lightboxPhotos = items.map(i => ({path: i.file_path, date_taken: i.date_taken, file_type: i.file_type || (i.file_path.match(/\.(mp4|mov|avi|mkv|webm)$/i) ? 'MP4' : 'JPG')}));
                openLightbox(items[currIdx].file_path);
            });
            
            wrapper.addEventListener('mouseenter', () => {
                isHovering = true;
                if (interval) { clearInterval(interval); interval = null; }
                progressBar.style.animationPlayState = 'paused';
                
                let currentSafePath = items[currIdx].file_path.replace(/\\/g, '/');
                let isVid = !!currentSafePath.match(/\.(mp4|mov|avi|mkv|webm)$/i);
                let highResSrc = '';
                let thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(currentSafePath)}`;
                if (!isVid) {
                    highResSrc = `/api/photo/file/${encodeURIComponent(currentSafePath)}`;
                    let preloadImg = new Image();
                    preloadImg.src = highResSrc;
                }
                
                overlay.style.opacity = '0';
                progressContainer.style.opacity = '0';
                if (currentBadge) currentBadge.style.opacity = '0';
                
                if (currentVideoEl) {
                    currentVideoEl.muted = false;
                    currentVideoEl.play().catch(e=>{});
                }
                
                hoverTimeout = setTimeout(() => {
                    isMorphed = true;
                    document.body.style.overflow = 'hidden';
                    
                    const rect = wrapper.getBoundingClientRect();
                    
                    wrapper.style.zIndex = '9999';
                    card.style.position = 'fixed';
                    card.style.zIndex = '9999';
                    card.style.top = rect.top + 'px';
                    card.style.left = rect.left + 'px';
                    card.style.width = rect.width + 'px';
                    card.style.height = rect.height + 'px';
                    card.style.margin = '0';
                    
                    card.offsetHeight;
                    
                    card.style.transition = 'all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)';
                    
                    let targetRatio = currentTargetRatio || 4/3;
                    
                    // Fixed massive size for pop view
                    let newH = window.innerHeight * 0.70;
                    let newW = newH * targetRatio;
                    
                    if (newW > window.innerWidth * 0.85) {
                        newW = window.innerWidth * 0.85;
                        newH = newW / targetRatio;
                    }
                    if (newH < 350) {
                        newH = Math.min(350, window.innerHeight * 0.9);
                        newW = newH * targetRatio;
                    }
                    
                    let newTop = rect.top - (newH - rect.height) / 2;
                    let newLeft = rect.left - (newW - rect.width) / 2;
                    const margin = 20;
                    if (newLeft < margin) newLeft = margin;
                    else if (newLeft + newW > window.innerWidth - margin) newLeft = window.innerWidth - margin - newW;
                    if (newTop < margin) newTop = margin;
                    else if (newTop + newH > window.innerHeight - margin) newTop = window.innerHeight - margin - newH;
                    
                    card.style.top = newTop + 'px';
                    card.style.left = newLeft + 'px';
                    card.style.width = newW + 'px';
                    card.style.height = newH + 'px';
                    card.style.boxShadow = '0 20px 50px rgba(0,0,0,0.7)';
                    
                    if (currentVideoEl) currentVideoEl.style.objectFit = 'contain';
                    else {
                        bg1.style.backgroundSize = 'contain';
                        bg2.style.backgroundSize = 'contain';
                        if (highResSrc) {
                            currentBg.style.backgroundImage = `url('${highResSrc}'), url('${thumbUrl}')`;
                        }
                    }
                    
                }, 2000);
            });
            
            wrapper.addEventListener('mouseleave', () => {
                isHovering = false;
                if (hoverTimeout) clearTimeout(hoverTimeout);
                
                if (isMorphed) {
                    isMorphed = false;
                    const rect = wrapper.getBoundingClientRect();
                    card.style.top = rect.top + 'px';
                    card.style.left = rect.left + 'px';
                    card.style.width = rect.width + 'px';
                    card.style.height = rect.height + 'px';
                    card.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
                    
                    if (currentVideoEl) {
                        currentVideoEl.muted = true;
                        currentVideoEl.style.objectFit = 'cover';
                    }
                    else {
                        bg1.style.backgroundSize = 'cover';
                        bg2.style.backgroundSize = 'cover';
                        let currentSafePath = items[currIdx].file_path.replace(/\\/g, '/');
                        let thumbUrlRestored = `/api/photo/thumbnail/${encodeURIComponent(currentSafePath)}`;
                        currentBg.style.backgroundImage = `url('${thumbUrlRestored}')`;
                    }

                    setTimeout(() => {
                        if (isHovering) return;
                        card.style.position = '';
                        card.style.top = '';
                        card.style.left = '';
                        card.style.width = '';
                        card.style.height = '';
                        card.style.zIndex = '';
                        wrapper.style.zIndex = '';
                        card.style.boxShadow = '';
                        card.style.transition = '';
                        
                        overlay.style.opacity = '1';
                        progressContainer.style.opacity = '1';
                        if (currentBadge) currentBadge.style.opacity = '1';
                    }, 400);
                } else {
                    overlay.style.opacity = '1';
                    progressContainer.style.opacity = '1';
                    if (currentBadge) currentBadge.style.opacity = '1';
                    if (currentVideoEl) currentVideoEl.muted = true;
                }
                
                progressBar.style.animationPlayState = 'running';
                if (items.length > 1 && !interval) {
                    interval = setInterval(() => {
                        currIdx = (currIdx + 1) % items.length;
                        showSlide(currIdx);
                    }, 5000);
                }
            });
            
            showSlide(0);
            
            if (items.length > 1) {
                interval = setInterval(() => {
                    currIdx = (currIdx + 1) % items.length;
                    showSlide(currIdx);
                }, 5000);
            }
            return interval;
        };

        const addStaticCard = (titleText, subtitleText, photoPath, sizeClass='panel-square') => {
            return addCarouselCard(titleText, [{ subtitle: subtitleText, file_path: photoPath, date_taken: new Date().toISOString() }], track, sizeClass);
        };

        window.memoriesIntervals = window.memoriesIntervals || [];
        window.memoriesIntervals.forEach(int => clearInterval(int));
        window.memoriesIntervals = [];
        
        window.memoriesCountdownIntervals = window.memoriesCountdownIntervals || {};
        for (let key in window.memoriesCountdownIntervals) {
            clearInterval(window.memoriesCountdownIntervals[key]);
        }
        window.memoriesCountdownIntervals = {};
        
        // --- 1. On This Day ---
        if (!onThisDayData.error && onThisDayData.success !== false) {
            const years = Object.keys(onThisDayData).sort((a,b) => b - a);
            let items = [];
            years.forEach(year => {
                if (onThisDayData[year] && onThisDayData[year].length > 0) {
                    onThisDayData[year].forEach(p => {
                        items.push({ subtitle: year, file_path: p.file_path, date_taken: p.date_taken });
                    });
                }
            });
            items.sort((a,b) => parseInt(a.subtitle) - parseInt(b.subtitle));
            if (items.length > 0) {
                const int = addCarouselCard('On this day', items, track, 'panel-rect-v');
                if (int) window.memoriesIntervals.push(int);
            }
        }

        // --- 2. Curated Blocks ---
        if (curatedData && curatedData.success && curatedData.curated) {
            const c = curatedData.curated;
            
            if (c.spotlight_day && c.spotlight_day.length > 0) {
                const items = c.spotlight_day.map(p => {
                    const d = new Date(p.date_taken);
                    return { subtitle: d.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'}), file_path: p.file_path, date_taken: p.date_taken };
                });
                const int = addCarouselCard('Spotlight on a Day', items, track, 'panel-hero');
                if (int) window.memoriesIntervals.push(int);
            }

            if (c.featured_moment) {
                const dateObj = new Date(c.featured_moment.date_taken);
                const dateStr = dateObj.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'});
                addStaticCard('Featured Moment', dateStr, c.featured_moment.file_path, 'panel-rect-h');
            }
            if (c.album_pick) {
                addStaticCard('From your Album', c.album_pick.name, c.album_pick.cover_photo_path, 'panel-rect-h');
            }
            if (c.featured_video) {
                const dateObj = new Date(c.featured_video.date_taken);
                const dateStr = dateObj.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'});
                addStaticCard('Video Spotlight', dateStr, c.featured_video.file_path, 'panel-hero');
            }
            
            // --- 3. People Spotlight ---
            if (c.people_spotlight && peopleContainer) {
                const ps = c.people_spotlight;
                
                const header = document.createElement('div');
                header.className = 'section-header';
                header.innerHTML = `
                    <div>
                        <h2>People Spotlight</h2>
                        <span class="section-subtitle">Rediscover moments with ${ps.person.name}</span>
                    </div>
                `;
                peopleContainer.appendChild(header);
                
                const psRow = document.createElement('div');
                psRow.className = 'people-spotlight-row';
                
                // Profile Tile
                const profileTile = document.createElement('div');
                profileTile.className = 'people-profile-tile';
                profileTile.innerHTML = `
                    <img src="/api/photo/crop/${ps.person.cover_face_id}" class="people-profile-img" alt="${ps.person.name}">
                    <div class="people-profile-name">${ps.person.name}</div>
                `;
                profileTile.addEventListener('click', () => {
                    if (typeof state !== 'undefined') {
                        state.filters.people = [ps.person.id.toString()];
                        if (typeof switchTab === 'function') switchTab('photos-tab');
                        if (typeof applyFilters === 'function') applyFilters();
                    }
                });
                psRow.appendChild(profileTile);
                
                // Stats Tile
                const statsTile = document.createElement('div');
                statsTile.className = 'people-stats-tile';
                statsTile.innerHTML = `
                    <div class="stat-box">
                        <div class="stat-num">${ps.person.total_count}</div>
                        <div class="stat-label">Total Photos</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num">${ps.person.shared_count}</div>
                        <div class="stat-label">Photos Together</div>
                    </div>
                `;
                psRow.appendChild(statsTile);
                
                // Person Photos Carousel
                if (ps.person_photos && ps.person_photos.length > 0) {
                    const items = ps.person_photos.map(p => {
                        const d = new Date(p.date_taken);
                        return { subtitle: d.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'}), file_path: p.file_path, date_taken: p.date_taken };
                    });
                    const int = addCarouselCard('Spotlight', items, psRow, 'wide-card');
                    if (int) window.memoriesIntervals.push(int);
                }
                
                // Photos Together Carousel
                if (ps.shared_photos && ps.shared_photos.length > 0) {
                    const items = ps.shared_photos.map(p => {
                        const d = new Date(p.date_taken);
                        return { subtitle: d.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'}), file_path: p.file_path, date_taken: p.date_taken };
                    });
                    const int = addCarouselCard('Photos Together', items, psRow, 'wide-card');
                    if (int) window.memoriesIntervals.push(int);
                } else {
                    const quoteTile = document.createElement('div');
                    quoteTile.className = 'shared-quote';
                    quoteTile.innerHTML = `
                        <i data-lucide="camera" style="width:32px; height:32px; opacity:0.8;"></i>
                        <p>"A picture is a poem without words.<br>Take more photos with ${ps.person.name}!"</p>
                    `;
                    psRow.appendChild(quoteTile);
                }
                
                peopleContainer.appendChild(psRow);
            }
        }
        
        if (track.children.length === 0 && (!c || !c.people_spotlight)) {
            container.innerHTML = `<div class="memory-empty" style="display:flex; flex-direction:column; align-items:center; gap:16px;"><i data-lucide="image-off" style="width:48px; height:48px; opacity:0.5;"></i>Nothing found for memories today.</div>`; 
        } else {
            if (track.children.length > 0) {
                container.appendChild(carouselContainer);
            } else {
                container.innerHTML = ''; // Clear loading state
            }
            window.lucide.createIcons();
        }
        
        if (window.lucide) lucide.createIcons();

    }).catch(e => {
        console.error(e);
        container.innerHTML = `<div class="memory-empty">Error loading memories.</div>`;
    });
}
