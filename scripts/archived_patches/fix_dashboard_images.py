import re

# 1. Update photos.py to return cover photos
py_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\routes\photos.py"
with open(py_path, "r", encoding="utf-8") as f:
    py_code = f.read()

old_month_sql = """cursor.execute(\"\"\"
            SELECT substr(date_taken, 6, 2) as month, COUNT(*) as count 
            FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'mp4', 'mov', 'avi')
            GROUP BY month 
        \"\"\", (date_filter,))"""

new_month_sql = """cursor.execute(\"\"\"
            SELECT 
                substr(date_taken, 6, 2) as month, 
                COUNT(*) as count,
                MAX(file_name) as cover_photo
            FROM photos 
            WHERE date_taken LIKE ? 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY month 
        \"\"\", (date_filter,))"""

old_month_return = """counts = {r[0]: r[1] for r in rows if r[0]}
        return jsonify({'success': True, 'counts': counts})"""

new_month_return = """counts = {r[0]: r[1] for r in rows if r[0]}
        covers = {r[0]: r[2] for r in rows if r[0]}
        return jsonify({'success': True, 'counts': counts, 'covers': covers})"""

if old_month_sql in py_code:
    py_code = py_code.replace(old_month_sql, new_month_sql)
if old_month_return in py_code:
    py_code = py_code.replace(old_month_return, new_month_return)


old_years_sql = """cursor.execute(\"\"\"
            SELECT substr(date_taken, 1, 4) as year, COUNT(*) as count 
            FROM photos 
            WHERE date_taken IS NOT NULL 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp', 'mp4', 'mov', 'avi')
            GROUP BY year 
            HAVING CAST(year AS INTEGER) >= 2000 AND count >= 5
            ORDER BY year DESC
        \"\"\")"""

new_years_sql = """cursor.execute(\"\"\"
            SELECT 
                substr(date_taken, 1, 4) as year, 
                COUNT(*) as count,
                MAX(file_name) as cover_photo
            FROM photos 
            WHERE date_taken IS NOT NULL 
              AND trashed_at IS NULL AND archived_at IS NULL 
              AND LOWER(file_type) IN ('jpg', 'jpeg', 'png', 'heic', 'webp')
            GROUP BY year 
            HAVING CAST(year AS INTEGER) >= 2000 AND count >= 5
            ORDER BY year DESC
        \"\"\")"""

old_years_return = """years = [r[0] for r in rows]
        return jsonify({'success': True, 'years': years})"""

new_years_return = """years = [{'year': r[0], 'cover_photo': r[2]} for r in rows]
        return jsonify({'success': True, 'years': years})"""

if old_years_sql in py_code:
    py_code = py_code.replace(old_years_sql, new_years_sql)
if old_years_return in py_code:
    py_code = py_code.replace(old_years_return, new_years_return)

with open(py_path, "w", encoding="utf-8") as f:
    f.write(py_code)


# 2. Update recap_dashboard.js to consume cover photos
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_dashboard.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Replace Monthly Loop
old_monthly_fetch = """fetch(`/api/recap/month-counts/${currentYear}`)
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
                    })"""

new_monthly_fetch = """fetch(`/api/recap/month-counts/${currentYear}`)
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
                    })"""

if old_monthly_fetch in js_code:
    js_code = js_code.replace(old_monthly_fetch, new_monthly_fetch)
else:
    print("Warning: old_monthly_fetch not found")


# Replace Years Loop
old_years_fetch = """fetch('/api/recap/years')
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
                            
                            card.innerHTML = `<img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="/><div class="mini-overlay">${year}</div>`;
                            pastRow.appendChild(card);
                        });"""

new_years_fetch = """fetch('/api/recap/years')
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
                        });"""

if old_years_fetch in js_code:
    js_code = js_code.replace(old_years_fetch, new_years_fetch)
else:
    print("Warning: old_years_fetch not found")


with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print("Dashboard image fetching patch complete.")
