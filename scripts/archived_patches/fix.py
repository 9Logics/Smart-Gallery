import re
path = 'D:/DevelopmentAppTest Folder/Project Gallery One/app/templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'(?s)document\.querySelectorAll\(''\.rewind-mini-card''\)\.forEach\(\(card, idx\) => \{.*?\n                                \}\);',
    r'''document.querySelectorAll('.rewind-mini-card').forEach((card, idx) => {
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
                                                let img = card.querySelector('img');
                                                img.onload = () => {
                                                    img.classList.add('loaded');
                                                    img.style.animationDelay = `${idx * 0.05}s`;
                                                };
                                                img.src = '/api/photo/thumbnail/' + encodeURIComponent(randomPhoto.path);
                                            }
                                        }).catch(err => console.log('Rewind API fetch failed:', err));
                                });''',
    content
)

# And fix the fetch logic for month-counts which might also be broken
content = re.sub(
    r'(?s)const monthlyRow = document\.getElementById\(''monthly-row''\);\s*if \(monthlyRow\) \{.*?\n            \}\s*// Fetch Past Years',
    r'''const monthlyRow = document.getElementById('monthly-row');
            if (monthlyRow) {
                const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                const currentMonthIndex = new Date().getMonth();
                
                fetch(`/api/recap/month-counts/${currentYear}`)
                    .then(res => res.json())
                    .then(data => {
                        const counts = (data && data.counts) ? data.counts : {};
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
                            
                            card.innerHTML = `<img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="/><div class="mini-overlay">${monthName}</div>${badge}`;
                            monthlyRow.appendChild(card);
                        }
                    })
                    .catch(err => {
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
            
            // Fetch Past Years''',
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
