import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

# I will replace the entire fetch(`/api/recap/month-counts/${currentYear}`) block
old_block_pattern = r"fetch\(`/api/recap/month-counts/\$\{currentYear\}`\).*?\}\);\s+\}\s+// Fetch Past Years"

new_block = '''fetch(`/api/recap/month-counts/${currentYear}`)
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
            
            // Fetch Past Years'''

html_code = re.sub(old_block_pattern, new_block, html_code, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_code)
print("Fixed syntax errors in index.html caused by the subagent.")
