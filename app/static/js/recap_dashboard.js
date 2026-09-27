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
                            // Find the first month with a cover from the end of the year
                            for (let i = 12; i >= 1; i--) {
                                const m = String(i).padStart(2, '0');
                                if (covers[m]) {
                                    heroBg.style.backgroundImage = `url('/api/photo/file/${encodeURIComponent(covers[m])}')`;
                                    heroBg.style.backgroundSize = 'cover';
                                    heroBg.style.backgroundPosition = 'center';
                                    heroBg.style.opacity = '0.5';
                                    break;
                                }
                            }
                        }

                        for (let i = currentMonthIndex; i >= 0; i--) {
                            const monthNumberStr = String(i + 1).padStart(2, '0');
                            const monthName = monthNames[i];
                            
                            const card = document.createElement('div');
                            card.className = 'rewind-mini-card';
                            card.onclick = function() { openRecapPlayer(this, currentYear, monthNumberStr); };
                            
                            let badge = '';
                            if (counts[monthNumberStr]) {
                                badge = `<div class="count-badge">${counts[monthNumberStr]} items</div>`;
                            }
                            
                            let imgSrc = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
                            if (covers[monthNumberStr]) {
                                imgSrc = `/api/photo/file/${encodeURIComponent(covers[monthNumberStr])}`;
                            }
                            
                            card.innerHTML = `<img src="${imgSrc}" style="object-fit: cover; width: 100%; height: 100%;"/><div class="mini-overlay">${monthName}</div>${badge}`;
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
                                imgSrc = `/api/photo/file/${encodeURIComponent(cover)}`;
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
