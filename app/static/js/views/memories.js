
// Welcome Hero Slideshow
window.memoriesCleanups = window.memoriesCleanups || [];
let heroInterval = null;
const initWelcomeHero = async () => {
    const bgsContainer = document.getElementById('welcome-hero-bgs');
    if (!bgsContainer) return;
    
    // Animate presets while waiting for API
    let presetDivs = Array.from(bgsContainer.querySelectorAll('.hero-bg-img'));
    if (presetDivs.length > 0) {
        let presetCurr = Math.floor(Math.random() * presetDivs.length);
        presetDivs.forEach(div => div.classList.remove('active'));
        presetDivs[presetCurr].classList.add('active');
        
        if (heroInterval) clearInterval(heroInterval);
        heroInterval = setInterval(() => {
            presetDivs[presetCurr].classList.remove('active');
            presetCurr = (presetCurr + 1) % presetDivs.length;
            presetDivs[presetCurr].classList.add('active');
        }, 5000);
    }

    try {
        const res = await fetch('/api/memories/welcome');
        const data = await res.json();
        const photos = data.photos;
        if (!photos || photos.length === 0) return;
        
        // Shuffle the AI photos so it varies across dashboard visits even with API caching
        photos.sort(() => Math.random() - 0.5);
        
        if (heroInterval) clearInterval(heroInterval);
        bgsContainer.innerHTML = ''; // clear presets
        
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
            
            const locStr = photo.location ? photo.location.split(',')[0] : null;
            let subjectStr = null;
            
            const tagsToUse = photo.ai_tags || photo.tags || [];
            
            if (tagsToUse && Array.isArray(tagsToUse) && tagsToUse.length > 0) {
                const skipTags = ['indoor', 'outdoor', 'day', 'night', 'nature', 'landscape', 'portrait', 'macro', 'close up', 'blur', 'bokeh', 'black and white', 'vintage', 'retro', 'color', 'colorful', 'bright', 'vibrant', 'dark', 'light', 'shadow'];
                const subjects = tagsToUse.filter(t => typeof t === 'string' && !skipTags.includes(t.toLowerCase()));
                if (subjects.length > 0) {
                    subjectStr = subjects[0].charAt(0).toUpperCase() + subjects[0].slice(1);
                }
            }
            
            if (subjectStr && locStr) {
                const lowerSubject = subjectStr.toLowerCase();
                const smartQuotes = [
                    `A beautiful memory of a ${lowerSubject} in ${locStr}.`,
                    `Capturing the essence of a ${lowerSubject} at ${locStr}.`,
                    `Looking back at this ${lowerSubject} from ${locStr}.`,
                    `Unforgettable moments: ${subjectStr} in ${locStr}.`,
                    `Exploring ${locStr}: A perfect ${lowerSubject} shot.`,
                    `${subjectStr} captured beautifully in ${locStr}.`,
                    `A nostalgic look back at a ${lowerSubject} in ${locStr}.`
                ];
                quote = smartQuotes[Math.floor(Math.random() * smartQuotes.length)];
            } else if (subjectStr) {
                const lowerSubject = subjectStr.toLowerCase();
                const smartQuotes = [
                    `A beautifully captured ${lowerSubject}.`,
                    `Focusing on the details: ${subjectStr}.`,
                    `The simple beauty of a ${lowerSubject}.`,
                    `A perfect shot of a ${lowerSubject}.`
                ];
                quote = smartQuotes[Math.floor(Math.random() * smartQuotes.length)];
            } else if (locStr) {
                quote = `Looking back at ${locStr}.`;
            }
            
            const elQuote = document.getElementById('hero-quote');
            const elMeta = document.querySelector('.hero-meta');
            
            if (elQuote) elQuote.style.opacity = '0';
            if (elMeta) elMeta.style.opacity = '0';
            
            setTimeout(() => {
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
                
                if (elQuote) elQuote.style.opacity = '';
                if (elMeta) elMeta.style.opacity = '';
            }, 500);

            const btn = document.getElementById('hero-lightbox-btn');
            if (btn) {
                btn.onclick = (e) => {
                    e.stopPropagation();
                    if (typeof state !== 'undefined') {
                        state.lightboxPhotos = photos.map(p => ({
                            path: p.path,
                            date_taken: p.date_taken,
                            file_type: p.file_type || (p.path.match(/\.(mp4|mov|avi|mkv|webm)$/i) ? 'MP4' : 'JPG')
                        }));
                    }
                    if (typeof openLightbox === 'function') openLightbox(photo.path);
                };
            }
        };

        if (photos.length > 0) updateHeroMetadata(photos[0]);

        if (heroInterval) clearInterval(heroInterval);
        if (imgDivs.length > 1) {
            let curr = 0;
            
            const cycleNext = () => {
                imgDivs[curr].classList.remove('active');
                curr = (curr + 1) % imgDivs.length;
                imgDivs[curr].classList.add('active');
                updateHeroMetadata(photos[curr]);
            };
            
            heroInterval = setInterval(cycleNext, 10000);
            
            // Dislike button
            const btnDislike = document.getElementById('hero-dislike-btn');
            if (btnDislike) {
                btnDislike.onclick = (e) => {
                    e.stopPropagation();
                    fetch('/api/memories/hero/blacklist', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({path: photos[curr].path})
                    }).catch(err => console.warn('Failed to blacklist hero:', err));
                    
                    // Remove from arrays so it doesn't show again in this session
                    imgDivs[curr].remove();
                    imgDivs.splice(curr, 1);
                    photos.splice(curr, 1);
                    if(curr >= imgDivs.length) curr = 0;
                    
                    if (imgDivs.length > 0) {
                        imgDivs[curr].classList.add('active');
                        updateHeroMetadata(photos[curr]);
                        clearInterval(heroInterval);
                        heroInterval = setInterval(cycleNext, 10000);
                    }
                };
            }
            
            // Scan more button
            const btnScanMore = document.getElementById('hero-scan-more-btn');
            if (btnScanMore) {
                btnScanMore.onclick = (e) => {
                    e.stopPropagation();
                    const icon = btnScanMore.querySelector('i');
                    if (icon) {
                        icon.style.transition = 'transform 1s linear';
                        icon.style.transform = 'rotate(360deg)';
                        setTimeout(() => { icon.style.transition = ''; icon.style.transform = ''; }, 1000);
                    }
                    fetch('/api/memories/hero/scan_more', { method: 'POST' }).catch(e => console.warn(e));
                    cycleNext();
                    clearInterval(heroInterval);
                    heroInterval = setInterval(cycleNext, 10000);
                };
            }
            
            window.memoriesCleanups.push(() => {
                if (heroInterval) clearInterval(heroInterval);
            });
        }
    } catch (e) {
        console.error("Failed to init welcome hero", e);
    }
};

const createDynamicMemoryCard = (col, extraClass = '') => {
    const wrapper = document.createElement('div');
    wrapper.className = 'memory-card-wrapper' + (extraClass ? ' ' + extraClass : '');
    wrapper.id = 'wrapper_' + Math.random().toString(36).substr(2, 9);
    
    const inner = document.createElement('div');
    inner.className = 'memory-card' + (extraClass ? ' ' + extraClass : '');
    
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
    
    const title = document.createElement('h3');
    title.className = 'memory-card-title';
    title.innerText = col.title || '';
    
    const subtitle = document.createElement('p');
    subtitle.className = 'memory-card-subtitle';
    subtitle.innerText = col.subtitle || '';
    
    const progressContainer = document.createElement('div');
    progressContainer.className = 'memory-progress-bar-container';
    
    const items = col.photos || [];
    const segments = [];
    
    const showDivided = items.length <= 15 && items.length > 1;
    if (items.length > 1) {
        const numSegments = showDivided ? items.length : 1;
        for (let i = 0; i < numSegments; i++) {
            const seg = document.createElement('div');
            seg.className = 'memory-progress-segment';
            const fill = document.createElement('div');
            fill.className = 'memory-progress-fill';
            seg.appendChild(fill);
            progressContainer.appendChild(seg);
            segments.push(fill);
        }
    } else {
        progressContainer.style.display = 'none';
    }
    
    overlay.appendChild(title);
    overlay.appendChild(subtitle);
    inner.appendChild(bg1);
    inner.appendChild(bg2);
    inner.appendChild(overlay);
    inner.appendChild(progressContainer);
    wrapper.appendChild(inner);
    
    bg1.style.zIndex = '1';
    bg2.style.zIndex = '1';
    overlay.style.zIndex = '10';
    progressContainer.style.zIndex = '10';
    
    let currIdx = 0;
    let currentVideoEl = null;
    let currentBadge = null;
    let interval = null;
    let isHovering = false;
    let unmuteTimeout = null;
    
    window.memoriesCleanups.push(() => {
        if (interval) clearInterval(interval);
        if (unmuteTimeout) clearTimeout(unmuteTimeout);
        if (currentVideoEl) {
            currentVideoEl.pause();
            currentVideoEl.removeAttribute('src');
            currentVideoEl.load();
            currentVideoEl.remove();
            currentVideoEl = null;
        }
    });
    
    const showSlide = (idx) => {
        if (!items || items.length === 0) return;
        const item = items[idx];
        const safePath = item.file_path ? item.file_path.replace(/\\/g, '/') : '';
        const isVid = !!safePath.match(/\.(mp4|mov|avi|mkv|webm)$/i);
        const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(safePath)}`;
        if (item.date_taken || item.created_at || item.date) {
            const d = new Date(item.date_taken || item.created_at || item.date);
            if (!isNaN(d)) {
                if (col.title && col.title.toLowerCase().includes('on this day')) {
                    subtitle.innerText = d.getFullYear().toString();
                } else {
                    subtitle.innerText = col.subtitle || '';
                }
            } else {
                subtitle.innerText = col.subtitle || '';
            }
        } else {
            subtitle.innerText = col.subtitle || '';
        }
        
        const performSwap = () => {
            nextBg.style.backgroundImage = `url('${thumbUrl}')`;
            nextBg.style.backgroundSize = 'cover';
            nextBg.style.opacity = '1';
            currentBg.style.opacity = '0';
            
            let temp = currentBg;
            currentBg = nextBg;
            nextBg = temp;
        };
        
        performSwap();
        
        if (currentVideoEl) {
            currentVideoEl.pause();
            currentVideoEl.removeAttribute('src');
            currentVideoEl.load();
            currentVideoEl.remove();
            currentVideoEl = null;
        }
        
        if (isVid) {
            currentVideoEl = document.createElement('video');
            currentVideoEl.src = `/api/photo/file/${encodeURIComponent(safePath)}`;
            currentVideoEl.muted = true;
            currentVideoEl.loop = true;
            currentVideoEl.playsInline = true;
            currentVideoEl.preload = 'metadata';
            currentVideoEl.style.position = 'absolute';
            currentVideoEl.style.inset = '0';
            currentVideoEl.style.width = '100%';
            currentVideoEl.style.height = '100%';
            currentVideoEl.style.objectFit = 'cover';
            currentVideoEl.style.opacity = '1';
            currentVideoEl.style.zIndex = '2';
            inner.appendChild(currentVideoEl);
            currentVideoEl.play().catch(e=>{});
        }
        
        if (items.length > 1) {
            segments.forEach((seg, i) => {
                seg.style.animation = 'none';
                seg.style.width = '0%';
                if (showDivided) {
                    if (i < idx) seg.style.width = '100%';
                    else if (i === idx) {
                        seg.offsetHeight; // reflow
                        seg.style.animation = `memoryProgress ${cycleDuration}ms linear forwards`;
                        if (isHovering) seg.style.animationPlayState = 'paused';
                    }
                } else {
                    if (i === 0) {
                        seg.offsetHeight;
                        seg.style.animation = `memoryProgress ${cycleDuration}ms linear forwards`;
                        if (isHovering) seg.style.animationPlayState = 'paused';
                    }
                }
            });
        }
    };
    
    // Randomize duration between 4s and 6.5s so timings are different for each card
    const cycleDuration = items && items.length > 1 ? 4000 + Math.floor(Math.random() * 2500) : 5000;
    
    if (items && items.length > 0) {
        showSlide(currIdx);
        if (items.length > 1) {
            interval = setInterval(() => {
                currIdx = (currIdx + 1) % items.length;
                showSlide(currIdx);
            }, cycleDuration);
        }
    }
    
    wrapper.addEventListener('mouseenter', () => {
        isHovering = true;
        if (interval) { clearInterval(interval); interval = null; }
        segments.forEach(seg => seg.style.animationPlayState = 'paused');
        
        overlay.style.opacity = '0';
        progressContainer.style.opacity = '0';
        
        if (currentVideoEl) {
            currentVideoEl.muted = true;
            currentVideoEl.play().catch(e=>{});
            unmuteTimeout = setTimeout(() => {
                if (currentVideoEl && isHovering) {
                    currentVideoEl.muted = false;
                    currentVideoEl.play().catch(e => {
                        if (currentVideoEl) {
                            currentVideoEl.muted = true;
                            currentVideoEl.play().catch(err => {});
                        }
                    });
                }
            }, 600);
        }
    });

    wrapper.addEventListener('mouseleave', () => {
        isHovering = false;
        if (unmuteTimeout) clearTimeout(unmuteTimeout);
        
        if (currentVideoEl) {
            currentVideoEl.muted = true;
            currentVideoEl.pause();
        }
        
        overlay.style.opacity = '1';
        progressContainer.style.opacity = '1';
        
        if (items.length > 1) {
            interval = setInterval(() => {
                currIdx = (currIdx + 1) % items.length;
                showSlide(currIdx);
            }, cycleDuration);
        }
        segments.forEach(seg => seg.style.animationPlayState = 'running');
    });

    wrapper.addEventListener('click', () => {
        if (window.openStoryViewer) {
            const parent = wrapper.parentElement;
            let storyData = [];
            let clickIndex = 0;
            
            if (parent) {
                const siblings = Array.from(parent.children).filter(el => el.classList.contains('memory-card-wrapper'));
                storyData = siblings.map(el => {
                    return el._storyData || null;
                }).filter(Boolean);
                clickIndex = siblings.indexOf(wrapper);
            }
            
            if (storyData.length === 0) {
                storyData = [{
                    title: col.title,
                    subtitle: col.subtitle,
                    photos: (col.photos || []).map(p => ({ ...p, path: p.file_path || p.path }))
                }];
                clickIndex = 0;
            }
            
            window.openStoryViewer(storyData, Math.max(0, clickIndex));
        }
    });

    wrapper._storyData = {
        title: col.title,
        subtitle: col.subtitle,
        photos: (col.photos || []).map(p => ({ ...p, path: p.file_path || p.path }))
    };

    const observer = new MutationObserver((mutations) => {
        if (!document.body.contains(wrapper)) {
            if (interval) clearInterval(interval);
            if (unmuteTimeout) clearTimeout(unmuteTimeout);
            if (currentVideoEl) {
                currentVideoEl.pause();
                currentVideoEl.removeAttribute('src');
                currentVideoEl.load();
            }
            observer.disconnect();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    return wrapper;
};



window.unloadMemories = function() {
    if (window.memoriesCleanups) {
        window.memoriesCleanups.forEach(fn => fn());
        window.memoriesCleanups = [];
    }
};

function loadMemories() {
    const container = document.getElementById('memories-container');
    const peopleContainer = document.getElementById('people-spotlight-container');

    container.innerHTML = `
        <div class="memories-3x2-grid-wrapper">
            <div class="memories-3x2-grid skeleton-grid" style="padding: 0; min-height: 450px; flex: 1;">
                ${Array(6).fill('<div class="skeleton-card" style="aspect-ratio: auto; height: 100%; border-radius: 12px;"></div>').join('')}
            </div>
        </div>
    `;
    
    const dashboardAlbums = document.getElementById('dashboard-albums-container');
    if (dashboardAlbums) {
        dashboardAlbums.innerHTML = `
            <div class="skeleton-grid" style="display: flex; gap: 16px; padding: 0; overflow: hidden; margin-top: 16px;">
                ${Array(3).fill('<div class="skeleton-card" style="aspect-ratio: 1; border-radius: 12px; flex: 1; min-width: 0;"></div>').join('')}
            </div>
        `;
    }
    
    if (peopleContainer) {
        peopleContainer.innerHTML = `
            <div class="skeleton-grid" style="display: flex; gap: 16px; padding: 0;">
                <div class="skeleton-card" style="width: 250px; height: 160px; border-radius: 12px; flex-shrink: 0;"></div>
                <div class="skeleton-card" style="flex: 1; height: 160px; border-radius: 12px;"></div>
            </div>
        `;
    }

    Promise.all([
        fetch('/api/memories/collections').then(res => res.json()),
        fetch('/api/memories/curated').then(res => res.json()),
        fetch('/api/albums').then(res => res.json()).catch(() => [])
    ]).then(([collectionsData, curatedData, albumsData]) => {
        container.innerHTML = '';
        initWelcomeHero();
        renderDashboardAlbums(albumsData);

        if (peopleContainer) {
            peopleContainer.innerHTML = '';
            const prevSibling = peopleContainer.previousElementSibling;
            if (prevSibling && prevSibling.classList.contains('section-header') && prevSibling.innerHTML.includes('People Spotlight')) {
                prevSibling.remove();
            }
        }

        const collections = collectionsData.collections || [];
        let currentPage = 0;
        const pageSize = 6;
        const totalPages = Math.ceil(collections.length / pageSize);

        if (collections.length === 0) {
            container.innerHTML = `<div class="memory-empty">No memories found.</div>`;
        } else {
            const gridContainer = document.createElement('div');
            gridContainer.className = 'memories-3x2-grid-wrapper';
            
            const gridElement = document.createElement('div');
            gridElement.className = 'memories-3x2-grid';
            
            const pillarBtn = document.createElement('div');
            pillarBtn.className = 'memories-pillar-btn';
            pillarBtn.innerHTML = '<i data-lucide="chevron-right"></i>';
            if (totalPages <= 1) {
                pillarBtn.style.display = 'none';
            }

            gridContainer.appendChild(gridElement);
            gridContainer.appendChild(pillarBtn);
            container.appendChild(gridContainer);

            const renderPage = () => {
                gridElement.innerHTML = '';
                const start = currentPage * pageSize;
                const end = start + pageSize;
                const pageItems = collections.slice(start, end);
                
                pageItems.forEach(col => {
                    gridElement.appendChild(createDynamicMemoryCard(col));
                });
                
                if (window.lucide) window.lucide.createIcons();
            };

            renderPage();

            pillarBtn.addEventListener('click', () => {
                currentPage = (currentPage + 1) % totalPages;
                renderPage();
            });
        }

        // Render People Spotlight using existing curatedData
        if (curatedData.curated && curatedData.curated.people_spotlight) {
            const ps = curatedData.curated.people_spotlight;
            const psHeader = document.createElement('div');
            psHeader.className = 'section-header';
            psHeader.style.marginBottom = '16px';
            psHeader.innerHTML = `
                <div>
                    <h2>People Spotlight</h2>
                    <span class="section-subtitle">Rediscover moments with ${ps.person.name}</span>
                </div>
            `;
            peopleContainer.appendChild(psHeader);

            const psRow = document.createElement('div');
            psRow.className = 'people-spotlight-row';

            const profileTile = document.createElement('div');
            profileTile.className = 'people-profile-tile';
            let coverHtml = `<div class="album-cover-placeholder"><i data-lucide="user" style="width:48px;height:48px;opacity:0.3"></i></div>`;
            if (ps.person.cover_face_id) {
                coverHtml = `<img src="/api/photo/crop/${ps.person.cover_face_id}" class="people-profile-img" alt="${ps.person.name}">`;
            } else {
                coverHtml = `<img src="/static/images/default_avatar.png" class="people-profile-img" alt="${ps.person.name}">`;
            }
            profileTile.innerHTML = `${coverHtml}<div class="people-profile-name">${ps.person.name}</div>`;
            profileTile.addEventListener('click', () => {
                if (window.openPersonDetail) window.lastViewBeforeDetail = 'memories'; window.openPersonDetail(ps.person);
            });
            psRow.appendChild(profileTile);

            const statsTile = document.createElement('div');
            statsTile.className = 'people-stats-tile';
            statsTile.innerHTML = `
                <div class="stat-box">
                    <div class="stat-num">${ps.person.total_count}</div>
                    <div class="stat-label">Total Photos</div>
                </div>
                <div class="stat-box" style="margin-top: 16px;">
                    <div class="stat-num" style="font-size: 20px;">${ps.person.shared_count}</div>
                    <div class="stat-label">Photos Together</div>
                </div>
            `;
            psRow.appendChild(statsTile);

            const addSpotlightCard = (title, items) => {
                if (!items || items.length === 0) return;
                const col = {
                    title: title,
                    subtitle: items.length + ' items',
                    photos: items
                };
                const card = createDynamicMemoryCard(col, 'spotlight-card wide-card');
                psRow.appendChild(card);
            };

            addSpotlightCard('Spotlight', ps.person_photos);
            addSpotlightCard('Photos Together', ps.shared_photos);
            
            peopleContainer.appendChild(psRow);
            if (window.lucide) lucide.createIcons();
        }

    }).catch(e => {
        console.error(e);
        container.innerHTML = `<div class="memory-empty">Error loading memories.</div>`;
    });
}

function renderDashboardAlbums(albums) {
    const container = document.getElementById('dashboard-albums-container');
    if (!container) return;

    if (!albums || albums.length === 0) {
        container.innerHTML = '';
        return;
    }

    const recentAlbums = albums.slice(0, 10);

    const header = document.createElement('div');
    header.className = 'section-header';
    header.style.marginBottom = '16px';
    header.innerHTML = `
        <div>
            <h2>My Albums</h2>
            <span class="section-subtitle">Your collections</span>
        </div>
    `;

    const carouselContainer = document.createElement('div');
    carouselContainer.className = 'memories-carousel-container';

    const track = document.createElement('div');
    track.className = 'memories-track dashboard-albums-track';

    const btnLeft = document.createElement('div');
    btnLeft.className = 'carousel-btn carousel-btn-left hidden';
    btnLeft.innerHTML = '<i data-lucide="chevron-left"></i>';

    const btnRight = document.createElement('div');
    btnRight.className = 'carousel-btn carousel-btn-right hidden';
    btnRight.innerHTML = '<i data-lucide="chevron-right"></i>';

    carouselContainer.appendChild(btnLeft);
    carouselContainer.appendChild(track);
    carouselContainer.appendChild(btnRight);

    recentAlbums.forEach(album => {
        const card = document.createElement('div');
        card.className = 'dashboard-album-card';
        
        let coverImgHTML = `<div class="album-cover-placeholder"><i data-lucide="image"></i></div>`;
        if (album.cover_photo_path) {
            coverImgHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(album.cover_photo_path)}" alt="${album.name}">`;
        }
        
        card.innerHTML = `
            <div class="dashboard-album-cover">${coverImgHTML}</div>
            <div class="dashboard-album-info">
                <h3>${album.name}</h3>
                <p>${album.total_count} items</p>
            </div>
        `;
        
        card.addEventListener('click', () => {
            if (window.openAlbumDetail) window.lastViewBeforeDetail = 'memories'; window.openAlbumDetail(album);
        });
    track.appendChild(card);
});

const seeAllCard = document.createElement('div');
seeAllCard.className = 'dashboard-album-card see-all-card';
seeAllCard.style.display = 'flex';
seeAllCard.style.flexDirection = 'column';
seeAllCard.style.justifyContent = 'center';
seeAllCard.style.alignItems = 'center';
seeAllCard.style.background = 'rgba(255,255,255,0.05)';
seeAllCard.style.cursor = 'pointer';
seeAllCard.style.flex = '0 0 160px';
seeAllCard.style.minWidth = '160px';
seeAllCard.style.overflow = 'visible';
seeAllCard.style.marginRight = '16px'; /* Extra padding at end of scroll */
seeAllCard.innerHTML = `
    <div style="background: rgba(255,255,255,0.1); border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
        <i data-lucide="arrow-right" style="width:24px; height:24px;"></i>
    </div>
    <h3 style="margin: 0; font-size: 14px;">See all albums</h3>
`;
seeAllCard.addEventListener('click', () => {
    if (typeof switchView === 'function') switchView('albums');
});
track.appendChild(seeAllCard);

    container.innerHTML = '';
    container.appendChild(header);
    container.appendChild(carouselContainer);

    const scrollAmount = () => carouselContainer.clientWidth * 0.8;
    btnLeft.addEventListener('click', () => track.scrollBy({ left: -scrollAmount(), behavior: 'smooth' }));
    btnRight.addEventListener('click', () => track.scrollBy({ left: scrollAmount(), behavior: 'smooth' }));

    track.addEventListener('scroll', () => {
        if (track.scrollLeft > 20) btnLeft.classList.remove('hidden');
        else btnLeft.classList.add('hidden');

        if (track.scrollLeft < track.scrollWidth - track.clientWidth - 20) btnRight.classList.remove('hidden');
        else btnRight.classList.add('hidden');
    });
    
    setTimeout(() => {
        if (track.scrollWidth > track.clientWidth) btnRight.classList.remove('hidden');
        window.lucide.createIcons();
    }, 500);
}


// ==========================================
// Dashboard Idle Hero Scanner
// ==========================================
let heroIdleTimer = null;
let heroIdleActive = false;

function resetHeroIdleTimer() {
    if (heroIdleTimer) clearTimeout(heroIdleTimer);
    
    // Only run idle scanning if we are on the memories view
    if (document.getElementById('memories-view') && !document.getElementById('memories-view').classList.contains('hidden')) {
        heroIdleTimer = setTimeout(() => {
            heroIdleActive = true;
            // Silent background scan when user is idle for 30 seconds
            fetch('/api/memories/hero/scan_more', { method: 'POST' }).catch(e => console.warn(e));
            
            // Re-trigger every 30s of deep idle
            heroIdleTimer = setInterval(() => {
                fetch('/api/memories/hero/scan_more', { method: 'POST' }).catch(e => console.warn(e));
            }, 30000);
            
        }, 30000);
    }
}

function handleDashboardActivity() {
    if (heroIdleActive) {
        heroIdleActive = false;
        if (heroIdleTimer) clearInterval(heroIdleTimer);
    }
    resetHeroIdleTimer();
}

window.addEventListener('mousemove', handleDashboardActivity, {passive: true});
window.addEventListener('keydown', handleDashboardActivity, {passive: true});
window.addEventListener('scroll', handleDashboardActivity, {passive: true});
