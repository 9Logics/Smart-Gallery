import os
import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the hardcoded past years with a script injection target
old_past_row = '''<div class="rewind-row" id="past-row">
                        <div class="rewind-mini-card year-card" onclick="openRecapPlayer(this, this.innerText.trim())"><img src=""/><div class="mini-overlay">2025</div></div>
                        <div class="rewind-mini-card year-card" onclick="openRecapPlayer(this, this.innerText.trim())"><img src=""/><div class="mini-overlay">2024</div></div>
                        <div class="rewind-mini-card year-card" onclick="openRecapPlayer(this, this.innerText.trim())"><img src=""/><div class="mini-overlay">2023</div></div>
                    </div>'''

new_past_row = '''<div class="rewind-row" id="past-row">
                        <!-- Populated dynamically via JS -->
                    </div>'''

html = html.replace(old_past_row, new_past_row)

# Append a small JS block at the very end before </body>
script_injection = '''
    <script>
        // Fetch dynamic years for recap
        document.addEventListener('DOMContentLoaded', () => {
            fetch('/api/recap/years')
                .then(res => res.json())
                .then(data => {
                    if(data.success && data.years) {
                        const pastRow = document.getElementById('past-row');
                        pastRow.innerHTML = ''; // Clear default
                        
                        const currentYear = new Date().getFullYear();
                        
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
                            
                            card.innerHTML = `<img src=""/><div class="mini-overlay">${year}</div>`;
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
    </script>
'''

if 'fetch(\'/api/recap/years\')' not in html:
    html = html.replace('</body>', script_injection + '</body>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Injected dynamic past years logic!")
