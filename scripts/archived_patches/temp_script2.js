
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
                
                for (let i = currentMonthIndex; i >= 0; i--) {
                    const monthNumberStr = String(i + 1).padStart(2, '0');
                    const monthName = monthNames[i];
                    
                    const card = document.createElement('div');
                    card.className = 'rewind-mini-card';
                    card.onclick = function() { openRecapPlayer(this, currentYear, monthNumberStr); };
                    card.innerHTML = `<img src="/static/images/placeholder.png"/><div class="mini-overlay">${monthName}</div>`;
                    monthlyRow.appendChild(card);
                }
            }
            
            // Fetch Past Years
            fetch('/api/recap/years')
                .then(res => res.json())
                .then(data => {
                    if(data.success && data.years) {
                        const pastRow = document.getElementById('past-row');
                        pastRow.innerHTML = ''; // Clear default
                        
                        data.years.forEach(year => {
                            if (year == currentYear) return; // Skip current year (it's in the Hero card)
                            
                            const card = document.createElement('div');
                            card.className = 'rewind-mini-card year-card';
                            card.onclick = function() { openRecapPlayer(this, year); };
                            
                            // Add a random gradient background or try to fetch a thumbnail
                            const gradients = [
                                'linear-gradient(135deg, #1f4037, #99f2c8)',
                                'linear-gradient(135deg, #c31432, #240b36)',
                                'linear-gradient(135deg, #f12711, #f5af19)',
                                'linear-gradient(135deg, #654ea3, #eaafc8)',
                                'linear-gradient(135deg, #000428, #004e92)',
                                'linear-gradient(135deg, #ee0979, #ff6a00)'
                            ];
                            const bg = gradients[year % gradients.length];
                            card.style.background = bg;
                            
                            card.innerHTML = `<img src="/static/images/placeholder.png"/><div class="mini-overlay">${year}</div>`;
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
    
