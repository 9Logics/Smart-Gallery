function initStatsHeatmap() {
    const originalRenderChart = window.renderChart || renderChart;
    window.renderChart = function(yearlyData, targetYear) {
        originalRenderChart(yearlyData, targetYear);
        
        document.getElementById('stats-heatmap-container').classList.add('hidden');
        
        setTimeout(() => {
            const root = document.getElementById('custom-chart-root');
            if(!root) return;
            // FIX: use .chart-col
            const bars = root.querySelectorAll('.chart-col');
            bars.forEach((bar, idx) => {
                bar.style.cursor = 'pointer';
                bar.addEventListener('click', () => {
                    const month = (idx + 1).toString().padStart(2, '0');
                    loadStatsHeatmap(targetYear, month);
                });
            });
        }, 100);
    };
}

function loadStatsHeatmap(year, month) {
    const container = document.getElementById('stats-heatmap-container');
    container.classList.remove('hidden');
    container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading daily activity...</p></div>`;
    
    fetch(`/api/stats/heatmap?year=${year}&month=${month}`)
        .then(res => res.json())
        .then(data => {
            const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            const monthName = monthNames[parseInt(month) - 1];
            
            const daysInMonth = new Date(parseInt(year), parseInt(month), 0).getDate();
            
            let maxCount = 0;
            for (let i = 1; i <= daysInMonth; i++) {
                const day = i.toString().padStart(2, '0');
                if (data[day] > maxCount) maxCount = data[day];
            }
            if (maxCount === 0) maxCount = 1;
            
            let gridHTML = `<div class="heatmap-header" style="margin-bottom: 24px;">${monthName} ${year}</div><div class="heatmap-grid">`;
            
            for (let i = 1; i <= daysInMonth; i++) {
                const dayStr = i.toString().padStart(2, '0');
                const count = data[dayStr] || 0;
                
                let opacity = 0;
                if (count > 0) {
                    opacity = 0.2 + (0.8 * (count / maxCount)); 
                }
                
                const style = count > 0 ? `background-color: rgba(99, 102, 241, ${opacity});` : '';
                gridHTML += `<div class="heatmap-cell" data-count="${count}" style="${style}">
                                <div class="heatmap-tooltip">${monthName} ${i}: ${count} media</div>
                             </div>`;
            }
            gridHTML += '</div>';
            container.innerHTML = gridHTML;
        });
}