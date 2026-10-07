// --- [REGION: DASHBOARD INIT] ---
// Fetch dynamic years and setup recap UI
        document.addEventListener('DOMContentLoaded', () => {
            const currentYear = new Date().getFullYear();
            
            // Set Hero Card Year
            const heroTitle = document.getElementById('recap-hero-year-title');
            if (heroTitle) heroTitle.innerText = `${currentYear} Recap`;
            const heroCard = document.getElementById('rewind-hero-card');
            if (heroCard) heroCard.onclick = function() { openRecapPlayer(this, currentYear); };
            
            // Generate Monthly Cards dynamically
            const monthlyRow = document.getElementById('monthly-row');
            if (monthlyRow) {
                const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                const currentMonthIndex = new Date().getMonth();
                
                fetch(`/api/recap/month-counts/${currentYear}`)
                    .then(res => res.json())
                    .then(data => {
                        const counts = (data && data.counts) ? data.counts : {};
                        const covers = (data && data.covers) ? data.covers : {};
                        
                        // Set Hero Card Cover if available
                        const heroBg = document.getElementById('hero-bg-container');
                        if (heroBg) {
                            const allCovers = Object.values(covers).filter(c => c);
                            if (allCovers.length > 0) {
                                // Shuffle and take up to 3
                                const shuffled = allCovers.sort(() => 0.5 - Math.random());
                                let selected = shuffled.slice(0, 3);
                                while (selected.length < 3 && selected.length > 0) {
                                    selected.push(selected[0]); // duplicate to fill 3 slots if necessary
                                }
                                
                                heroBg.innerHTML = `
                                    <div class="hero-collage-item hero-collage-1" style="background-image: url('/api/photo/thumbnail/${encodeURIComponent(selected[0])}')"></div>
                                    <div class="hero-collage-item hero-collage-2" style="background-image: url('/api/photo/thumbnail/${encodeURIComponent(selected[1])}')"></div>
                                    <div class="hero-collage-item hero-collage-3" style="background-image: url('/api/photo/thumbnail/${encodeURIComponent(selected[2])}')"></div>
                                `;
                                heroBg.style.backgroundImage = 'none';
                                heroBg.style.opacity = '1';
                            }
                        }

                        const monthGradients = [
                            'linear-gradient(135deg, #2D1A43, #1D192B)', // M3 Purple
                            'linear-gradient(135deg, #102636, #101E28)', // M3 Blue/Cyan
                            'linear-gradient(135deg, #132C20, #112118)', // M3 Green
                            'linear-gradient(135deg, #431720, #2C151A)', // M3 Red
                            'linear-gradient(135deg, #432100, #2D1600)', // M3 Orange
                            'linear-gradient(135deg, #15263A, #0F1D2A)', // M3 Indigo
                            'linear-gradient(135deg, #2D1A43, #1D192B)',
                            'linear-gradient(135deg, #102636, #101E28)',
                            'linear-gradient(135deg, #132C20, #112118)',
                            'linear-gradient(135deg, #431720, #2C151A)',
                            'linear-gradient(135deg, #432100, #2D1600)',
                            'linear-gradient(135deg, #15263A, #0F1D2A)'
                        ];
                        const MIN_MEDIA_THRESHOLD = 5;
                        
                        for (let i = currentMonthIndex; i >= 0; i--) {
                            const monthNumberStr = String(i + 1).padStart(2, '0');
                            const monthName = monthNames[i];
                            const mediaCount = counts[monthNumberStr] || 0;
                            const hasEnoughMedia = mediaCount >= MIN_MEDIA_THRESHOLD;
                            
                            const card = document.createElement('div');
                            card.className = 'rewind-mini-card';
                            
                            if (hasEnoughMedia) {
                                card.onclick = function() { openRecapPlayer(this, currentYear, monthNumberStr); };
                            } else {
                                card.classList.add('insufficient-media');
                            }
                            
                            let badge = '';
                            if (mediaCount > 0) {
                                badge = `<div class="count-badge">${mediaCount} items</div>`;
                            }
                            
                            let imgHtml = '';
                            if (covers[monthNumberStr]) {
                                imgHtml = `<img src="/api/photo/thumbnail/${encodeURIComponent(covers[monthNumberStr])}" style="object-fit: cover; width: 100%; height: 100%;"/>`;
                            } else {
                                card.style.background = monthGradients[i];
                            }
                            
                            let noticeHtml = '';
                            if (!hasEnoughMedia) {
                                noticeHtml = `<div class="insufficient-notice"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><line x1="1" y1="1" x2="23" y2="23"/></svg><span>${mediaCount === 0 ? 'No media' : 'Not enough media'}</span></div>`;
                            }
                            
                            card.innerHTML = `${imgHtml}<div class="mini-overlay">${monthName}</div>${badge}${noticeHtml}`;
                            monthlyRow.appendChild(card);
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        for (let i = currentMonthIndex; i >= 0; i--) {
                            const monthNumberStr = String(i + 1).padStart(2, '0');
                            const monthName = monthNames[i];
                            const card = document.createElement('div');
                            card.className = 'rewind-mini-card';
                            card.onclick = function() { openRecapPlayer(this, currentYear, monthNumberStr); };
                            card.innerHTML = `<img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="/><div class="mini-overlay">${monthName}</div>`;
                            monthlyRow.appendChild(card);
                        }
                    });
            }
            
            // Fetch Past Years
            fetch('/api/recap/years')
                .then(res => res.json())
                .then(data => {
                    if(data.success && data.years) {
                        const pastRow = document.getElementById('past-row');
                        pastRow.innerHTML = ''; // Clear default
                        
                        data.years.forEach(yearObj => {
                            const yearStr = typeof yearObj === 'object' ? yearObj.year : yearObj;
                            const cover = typeof yearObj === 'object' ? yearObj.cover_photo : null;
                            
                            if (yearStr == currentYear) return; // Skip current year
                            
                            const card = document.createElement('div');
                            card.className = 'rewind-mini-card year-card';
                            card.onclick = function() { openRecapPlayer(this, yearStr); };
                            
                            const gradients = [
                                'linear-gradient(135deg, #1f4037, #99f2c8)',
                                'linear-gradient(135deg, #c31432, #240b36)',
                                'linear-gradient(135deg, #f12711, #f5af19)',
                                'linear-gradient(135deg, #654ea3, #eaafc8)',
                                'linear-gradient(135deg, #000428, #004e92)',
                                'linear-gradient(135deg, #ee0979, #ff6a00)'
                            ];
                            
                            let imgSrc = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
                            if (cover) {
                                imgSrc = `/api/photo/thumbnail/${encodeURIComponent(cover)}`;
                                card.style.background = '#000';
                            } else {
                                card.style.background = gradients[yearStr % gradients.length];
                            }
                            
                            card.innerHTML = `<img src="${imgSrc}" style="object-fit: cover; width: 100%; height: 100%; opacity: 0.8;"/><div class="mini-overlay">${yearStr}</div>`;
                            pastRow.appendChild(card);
                        });
                        
                        // Fallback if no past years
                        if (pastRow.children.length === 0) {
                            pastRow.innerHTML = '<div style="color: rgba(255,255,255,0.4); padding: 20px;">Not enough photos in past years yet!</div>';
                        }
                    }
                })
                .catch(err => console.error("Failed to load recap years", err));
        });
// --- [END REGION: DASHBOARD INIT] ---
