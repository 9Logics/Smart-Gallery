let frequencyChart = null;

function loadStats() {
    Promise.all([
        fetch('/api/stats').then(res => res.json()),
        fetch('/api/stats/calendar').then(res => res.json())
    ]).then(([data, calendarData]) => {
        renderCalendarHeatmap(calendarData);

            document.getElementById('stat-total-photos').innerText = data.total_photos.toLocaleString();
            document.getElementById('stat-total-videos').innerText = data.total_videos.toLocaleString();
            
            const pSize = data.total_photo_size || 0;
            const vSize = data.total_video_size || 0;
            const tSize = pSize + vSize;
            
            const formatBytes = (bytes) => {
                if (!+bytes) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
            };
            
            if (tSize > 0) {
                document.getElementById('storage-bar-photos').style.width = `${(pSize / tSize) * 100}%`;
                document.getElementById('storage-bar-videos').style.width = `${(vSize / tSize) * 100}%`;
            } else {
                document.getElementById('storage-bar-photos').style.width = '0%';
                document.getElementById('storage-bar-videos').style.width = '0%';
            }
            
            document.getElementById('stat-storage-photos').innerText = formatBytes(pSize);
            document.getElementById('stat-storage-videos').innerText = formatBytes(vSize);
            document.getElementById('stat-storage-total').innerText = formatBytes(tSize);

            // Calculate Last 3 Months and This Year stats
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1; // 1-12
            
            let tyPhotosCount = 0, tyPhotosSize = 0, tyVideosCount = 0, tyVideosSize = 0;
            let l3mPhotosCount = 0, l3mPhotosSize = 0, l3mVideosCount = 0, l3mVideosSize = 0;
            
            // Loop through data.yearly to aggregate
            Object.keys(data.yearly).forEach(yearStr => {
                const yearNum = parseInt(yearStr);
                const yearObj = data.yearly[yearStr];
                
                if (yearNum === currentYear) {
                    // Aggregate this year
                    Object.keys(yearObj.months).forEach(monthStr => {
                        const mNum = parseInt(monthStr);
                        const mObj = yearObj.months[monthStr];
                        
                        tyPhotosCount += (mObj.photos || 0);
                        tyVideosCount += (mObj.videos || 0);
                        tyPhotosSize += (mObj.storage_photos || 0);
                        tyVideosSize += (mObj.storage_videos || 0);
                        
                        // Check if within last 3 months
                        // (We only look at the current year for simplicity, but a full 3mo wrap can be done)
                        let monthDiff = currentMonth - mNum;
                        if (monthDiff >= 0 && monthDiff < 3) {
                            l3mPhotosCount += (mObj.photos || 0);
                            l3mVideosCount += (mObj.videos || 0);
                            l3mPhotosSize += (mObj.storage_photos || 0);
                            l3mVideosSize += (mObj.storage_videos || 0);
                        }
                    });
                } else if (yearNum === currentYear - 1) {
                    // Wrap around logic for last 3 months
                    Object.keys(yearObj.months).forEach(monthStr => {
                        const mNum = parseInt(monthStr);
                        const mObj = yearObj.months[monthStr];
                        let monthDiff = (currentMonth + 12) - mNum;
                        if (monthDiff > 0 && monthDiff < 3) {
                            l3mPhotosCount += (mObj.photos || 0);
                            l3mVideosCount += (mObj.videos || 0);
                            l3mPhotosSize += (mObj.storage_photos || 0);
                            l3mVideosSize += (mObj.storage_videos || 0);
                        }
                    });
                }
            });

            // Update UI for Recent Stats
            if (document.getElementById('stat-ty-photos')) {
                document.getElementById('stat-ty-photos').innerText = tyPhotosCount.toLocaleString();
                document.getElementById('stat-ty-photos-size').innerText = formatBytes(tyPhotosSize);
                document.getElementById('stat-ty-videos').innerText = tyVideosCount.toLocaleString();
                document.getElementById('stat-ty-videos-size').innerText = formatBytes(tyVideosSize);
                
                document.getElementById('stat-3mo-photos').innerText = l3mPhotosCount.toLocaleString();
                document.getElementById('stat-3mo-photos-size').innerText = formatBytes(l3mPhotosSize);
                document.getElementById('stat-3mo-videos').innerText = l3mVideosCount.toLocaleString();
                document.getElementById('stat-3mo-videos-size').innerText = formatBytes(l3mVideosSize);
            }
            
            // Restore Upload Rate and Current Storage for top cards
            const totalDaysThisYear = 365;
            const startOfYear = new Date(currentYear, 0, 1);
            const daysPassed = Math.max(1, Math.floor((now - startOfYear) / (1000 * 60 * 60 * 24)));
            const tyTotalSize = tyPhotosSize + tyVideosSize;
            const monthsPassed = Math.max(1, daysPassed / 30.44);
            const avgBytesPerMonth = tyTotalSize / monthsPassed;
            
            if (document.getElementById('stat-growth-rate')) {
                document.getElementById('stat-growth-rate').innerText = formatBytes(avgBytesPerMonth);
            }
            if (document.getElementById('stat-current-total')) {
                document.getElementById('stat-current-total').innerText = formatBytes(tSize);
            }
            if (document.getElementById('stat-predicted-total')) {
                const predictedBytes = avgBytesPerMonth * 12;
                const startOfYearSize = Math.max(0, tSize - tyTotalSize);
                const endOfYearSize = startOfYearSize + predictedBytes;
                document.getElementById('stat-predicted-total').innerText = formatBytes(endOfYearSize);
            }
            
            // Build Historical Storage Trend
            const trendContainer = document.getElementById('forecast-svg-container');
            if (trendContainer) {
                let allTrendPoints = [];
                let cumulativeSize = 0;
                
                const sortedYears = Object.keys(data.yearly)
                    .filter(y => parseInt(y) > 1995)
                    .sort((a, b) => a - b);
                    
                sortedYears.forEach(yearStr => {
                    const yearNum = parseInt(yearStr);
                    const yearData = data.yearly[yearStr];
                    const sortedMonths = Object.keys(yearData.months).sort((a, b) => a - b);
                    sortedMonths.forEach(monthStr => {
                        const mObj = yearData.months[monthStr];
                        const mSize = (mObj.storage_photos || 0) + (mObj.storage_videos || 0);
                        cumulativeSize += mSize;
                        allTrendPoints.push({
                            time: new Date(yearNum, parseInt(monthStr) - 1).getTime(),
                            size: cumulativeSize,
                            dateStr: new Date(yearNum, parseInt(monthStr) - 1).toLocaleDateString('en-US', {month: 'short', year: 'numeric'})
                        });
                    });
                });
                
                if (allTrendPoints.length > 0) {
                    const lastPt = allTrendPoints[allTrendPoints.length - 1];
                    if (lastPt.time < now.getTime() - 30*24*60*60*1000) {
                        allTrendPoints.push({
                            time: now.getTime(),
                            size: cumulativeSize,
                            dateStr: "Today"
                        });
                    }
                }
                
                const header = trendContainer.previousElementSibling;
                if (header && !document.getElementById('trend-timeframes')) {
                    header.style.display = 'flex';
                    header.style.alignItems = 'flex-start';
                    
                    const tfDiv = document.createElement('div');
                    tfDiv.id = 'trend-timeframes';
                    tfDiv.style.display = 'flex';
                    tfDiv.style.gap = '16px';
                    tfDiv.style.marginLeft = 'auto';
                    tfDiv.style.fontSize = '13px';
                    tfDiv.innerHTML = "<span class='tf-btn' data-tf='1Y' style='cursor:pointer; color:var(--text-secondary); transition: color 0.2s;'>1Y</span> <span class='tf-btn' data-tf='5Y' style='cursor:pointer; color:var(--text-secondary); transition: color 0.2s;'>5Y</span> <span class='tf-btn active' data-tf='Max' style='cursor:pointer; color:var(--chart-photos); font-weight:600; transition: color 0.2s;'>Max</span>";
                    header.appendChild(tfDiv);
                    
                    tfDiv.querySelectorAll('.tf-btn').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            tfDiv.querySelectorAll('.tf-btn').forEach(b => {
                                b.style.color = 'var(--text-secondary)';
                                b.style.fontWeight = 'normal';
                                b.classList.remove('active');
                            });
                            e.target.style.color = 'var(--chart-photos)';
                            e.target.style.fontWeight = '600';
                            e.target.classList.add('active');
                            renderTrendChart(e.target.dataset.tf);
                        });
                    });
                }
                
                function renderTrendChart(timeframe) {
                    if (allTrendPoints.length === 0) return;
                    
                    let cutoffTime = 0;
                    if (timeframe === '1Y') cutoffTime = now.getTime() - (365 * 24 * 60 * 60 * 1000);
                    if (timeframe === '5Y') cutoffTime = now.getTime() - (5 * 365 * 24 * 60 * 60 * 1000);
                    
                    let trendPoints = allTrendPoints.filter(pt => pt.time >= cutoffTime);
                    
                    if (trendPoints.length < 2 && allTrendPoints.length >= 2) {
                        const firstPt = allTrendPoints.find(pt => pt.time >= cutoffTime) || allTrendPoints[allTrendPoints.length - 1];
                        trendPoints = [firstPt];
                    }
                    if (trendPoints.length === 1 && allTrendPoints.length > 1) {
                        const idx = allTrendPoints.indexOf(trendPoints[0]);
                        if (idx > 0) trendPoints.unshift(allTrendPoints[idx - 1]);
                    }
                    if (trendPoints.length === 0) trendPoints = allTrendPoints;
                    
                    trendContainer.innerHTML = '';
                    trendContainer.style.height = '180px';
                    
                    const minTime = trendPoints[0].time;
                    const maxTime = trendPoints[trendPoints.length - 1].time;
                    const minSize = Math.max(0, trendPoints[0].size * 0.95);
                    const maxSize = trendPoints[trendPoints.length - 1].size * 1.05;
                    
                    const paddingLeft = 45;
                    const paddingBottom = 20;
                    
                    const chartWrapper = document.createElement('div');
                    chartWrapper.style.position = 'relative';
                    chartWrapper.style.width = '100%';
                    chartWrapper.style.height = '100%';
                    
                    const pathData = trendPoints.map((pt, i) => {
                        const x = minTime === maxTime ? 100 : ((pt.time - minTime) / (maxTime - minTime)) * 100;
                        const y = maxSize === minSize ? 100 : 100 - ((pt.size - minSize) / (maxSize - minSize)) * 100;
                        return (i===0 ? 'M' : 'L') + ' ' + x + ' ' + y;
                    }).join(' ');
                    
                    const fillPathData = pathData + ' L 100 100 L 0 100 Z';
                    
                    const svgHTML = '<svg width="calc(100% - ' + paddingLeft + 'px)" height="calc(100% - ' + paddingBottom + 'px)" style="position:absolute; left:' + paddingLeft + 'px; top:0; overflow:visible;" viewBox="0 0 100 100" preserveAspectRatio="none">' +
                        '<defs>' +
                            '<linearGradient id="trendGradient2" x1="0" y1="0" x2="0" y2="1">' +
                                '<stop offset="0%" stop-color="var(--chart-photos)" stop-opacity="0.3" />' +
                                '<stop offset="100%" stop-color="var(--chart-photos)" stop-opacity="0.0" />' +
                            '</linearGradient>' +
                        '</defs>' +
                        '<line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,255,255,0.05)" stroke-width="1" vector-effect="non-scaling-stroke" />' +
                        '<line x1="0" y1="50" x2="100" y2="50" stroke="rgba(255,255,255,0.05)" stroke-width="1" vector-effect="non-scaling-stroke" />' +
                        '<line x1="0" y1="100" x2="100" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="1" vector-effect="non-scaling-stroke" />' +
                        '<path d="' + fillPathData + '" fill="url(#trendGradient2)" />' +
                        '<path d="' + pathData + '" fill="none" stroke="var(--chart-photos)" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linejoin="round" />' +
                    '</svg>';
                    
                    chartWrapper.innerHTML = svgHTML;
                    
                    const yAxis = document.createElement('div');
                    yAxis.style.position = 'absolute';
                    yAxis.style.left = '0';
                    yAxis.style.top = '0';
                    yAxis.style.height = 'calc(100% - ' + paddingBottom + 'px)';
                    yAxis.style.display = 'flex';
                    yAxis.style.flexDirection = 'column';
                    yAxis.style.justifyContent = 'space-between';
                    yAxis.style.fontSize = '11px';
                    yAxis.style.color = 'var(--text-secondary)';
                    
                    const fmtY = (val) => {
                        const gb = val / (1024*1024*1024);
                        if (gb >= 1) return gb.toFixed(0) + 'GB';
                        const mb = val / (1024*1024);
                        return mb.toFixed(0) + 'MB';
                    };
                    
                    yAxis.innerHTML = '<div style="transform: translateY(-50%);">' + fmtY(maxSize) + '</div>' +
                        '<div style="transform: translateY(-50%);">' + fmtY(minSize + (maxSize - minSize)/2) + '</div>' +
                        '<div style="transform: translateY(-50%);">' + fmtY(minSize) + '</div>';
                    chartWrapper.appendChild(yAxis);
                    
                    const xAxis = document.createElement('div');
                    xAxis.style.position = 'absolute';
                    xAxis.style.left = paddingLeft + 'px';
                    xAxis.style.bottom = '0';
                    xAxis.style.width = 'calc(100% - ' + paddingLeft + 'px)';
                    xAxis.style.display = 'flex';
                    xAxis.style.justifyContent = 'space-between';
                    xAxis.style.fontSize = '11px';
                    xAxis.style.color = 'var(--text-secondary)';
                    
                    xAxis.innerHTML = '<div>' + trendPoints[0].dateStr + '</div>' +
                        '<div>' + trendPoints[Math.floor(trendPoints.length/2)].dateStr + '</div>' +
                        '<div>' + trendPoints[trendPoints.length-1].dateStr + '</div>';
                    chartWrapper.appendChild(xAxis);
                    
                    const hoverLine = document.createElement('div');
                    hoverLine.style.position = 'absolute';
                    hoverLine.style.top = '0';
                    hoverLine.style.bottom = paddingBottom + 'px';
                    hoverLine.style.width = '1px';
                    hoverLine.style.background = 'transparent';
                    hoverLine.style.opacity = '0';
                    hoverLine.style.pointerEvents = 'none';
                    hoverLine.style.borderLeft = '1px dashed var(--text-secondary)';
                    
                    const hoverDot = document.createElement('div');
                    hoverDot.style.position = 'absolute';
                    hoverDot.style.width = '10px';
                    hoverDot.style.height = '10px';
                    hoverDot.style.borderRadius = '50%';
                    hoverDot.style.background = 'var(--chart-photos)';
                    hoverDot.style.border = '2px solid var(--bg-deep)';
                    hoverDot.style.transform = 'translate(-50%, -50%)';
                    hoverDot.style.opacity = '0';
                    hoverDot.style.pointerEvents = 'none';
                    
                    const tooltip = document.createElement('div');
                    tooltip.style.position = 'absolute';
                    tooltip.style.background = 'rgba(20,20,25,0.95)';
                    tooltip.style.border = '1px solid rgba(255,255,255,0.1)';
                    tooltip.style.padding = '6px 10px';
                    tooltip.style.borderRadius = '6px';
                    tooltip.style.color = '#fff';
                    tooltip.style.fontSize = '12px';
                    tooltip.style.fontWeight = '500';
                    tooltip.style.pointerEvents = 'none';
                    tooltip.style.opacity = '0';
                    tooltip.style.transform = 'translate(-50%, -100%)';
                    tooltip.style.marginTop = '-10px';
                    tooltip.style.whiteSpace = 'nowrap';
                    tooltip.style.zIndex = '10';
                    tooltip.style.boxShadow = '0 4px 12px rgba(0,0,0,0.5)';
                    
                    chartWrapper.appendChild(hoverLine);
                    chartWrapper.appendChild(hoverDot);
                    chartWrapper.appendChild(tooltip);
                    
                    const overlay = document.createElement('div');
                    overlay.style.position = 'absolute';
                    overlay.style.left = paddingLeft + 'px';
                    overlay.style.top = '0';
                    overlay.style.width = 'calc(100% - ' + paddingLeft + 'px)';
                    overlay.style.height = 'calc(100% - ' + paddingBottom + 'px)';
                    overlay.style.cursor = 'crosshair';
                    
                    overlay.addEventListener('mousemove', (e) => {
                        const rect = overlay.getBoundingClientRect();
                        const pctX = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                        const targetTime = minTime + pctX * (maxTime - minTime);
                        
                        let closest = trendPoints[0];
                        let minDiff = Math.abs(closest.time - targetTime);
                        for (let i = 1; i < trendPoints.length; i++) {
                            const diff = Math.abs(trendPoints[i].time - targetTime);
                            if (diff < minDiff) {
                                minDiff = diff;
                                closest = trendPoints[i];
                            }
                        }
                        
                        const exactPtX = paddingLeft + ((closest.time - minTime) / (maxTime - minTime)) * rect.width;
                        const pointY = ((maxSize - closest.size) / (maxSize - minSize)) * rect.height;
                        
                        hoverLine.style.left = exactPtX + 'px';
                        hoverLine.style.opacity = '1';
                        
                        hoverDot.style.left = exactPtX + 'px';
                        hoverDot.style.top = pointY + 'px';
                        hoverDot.style.opacity = '1';
                        
                        tooltip.innerHTML = '<span style="color:var(--chart-photos)">' + formatBytes(closest.size) + '</span> &middot; <span style="color:var(--text-secondary); font-weight:normal;">' + closest.dateStr + '</span>';
                        tooltip.style.left = exactPtX + 'px';
                        tooltip.style.top = pointY + 'px';
                        tooltip.style.opacity = '1';
                    });
                    
                    overlay.addEventListener('mouseleave', () => {
                        hoverLine.style.opacity = '0';
                        hoverDot.style.opacity = '0';
                        tooltip.style.opacity = '0';
                    });
                    
                    chartWrapper.appendChild(overlay);
                    trendContainer.appendChild(chartWrapper);
                }
                
                renderTrendChart('Max');
            }
            
            const years = Object.keys(data.yearly).sort((a,b) => b - a);
            if (years.length > 0) {
                let currentYearIndex = 0;
                
                const display = document.getElementById('stats-year-display');
                const input = document.getElementById('stats-year-input');
                const btnPrev = document.getElementById('stats-year-prev');
                const btnNext = document.getElementById('stats-year-next');
                const container = document.getElementById('stats-year-display-container');
                
                const updateYear = (index) => {
                    if (index >= 0 && index < years.length) {
                        currentYearIndex = index;
                        const year = years[currentYearIndex];
                        display.innerText = year;
                        input.value = year;
                        renderChart(data.yearly, year);
                        
                        btnNext.style.opacity = currentYearIndex > 0 ? "1" : "0.3";
                        btnNext.style.pointerEvents = currentYearIndex > 0 ? "auto" : "none";
                        
                        btnPrev.style.opacity = currentYearIndex < years.length - 1 ? "1" : "0.3";
                        btnPrev.style.pointerEvents = currentYearIndex < years.length - 1 ? "auto" : "none";
                    }
                };
                
                // Initialize
                updateYear(0);
                
                btnPrev.onclick = () => updateYear(currentYearIndex + 1);
                btnNext.onclick = () => updateYear(currentYearIndex - 1);
                
                container.onclick = () => {
                    display.classList.add('hidden');
                    input.classList.remove('hidden');
                    input.focus();
                    input.select();
                };
                
                const handleInputConfirm = () => {
                    const typedYear = input.value;
                    const index = years.indexOf(typedYear);
                    if (index !== -1) {
                        updateYear(index);
                    } else {
                        // Revert if invalid
                        input.value = years[currentYearIndex];
                    }
                    input.classList.add('hidden');
                    display.classList.remove('hidden');
                };
                
                input.onblur = handleInputConfirm;
                input.onkeydown = (e) => {
                    if (e.key === 'Enter') {
                        handleInputConfirm();
                    }
                };
            }
        })
        .catch(err => console.error("Failed to load stats", err));
}

function renderChart(yearlyData, targetYear) {
    const root = document.getElementById('custom-chart-root');
    if (!root) return;
    
    const yearStats = yearlyData[targetYear] || {photos: 0, videos: 0, months: {}};
    const months = yearStats.months || {};
    
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    
    // Calculate max value for bar scaling
    let maxCount = 0;
    for (let i = 1; i <= 12; i++) {
        const mKey = i.toString().padStart(2, '0');
        const mData = months[mKey] || {photos: 0, videos: 0};
        const total = mData.photos + mData.videos;
        if (total > maxCount) maxCount = total;
    }
    
    // Ensure maxCount is at least 10 for nice scaling
    if (maxCount < 10) maxCount = 10;
    
    let barsHtml = '';
    for (let i = 1; i <= 12; i++) {
        const mKey = i.toString().padStart(2, '0');
        const mData = months[mKey] || {photos: 0, videos: 0};
        const total = mData.photos + mData.videos;
        
        let pHeight = 0;
        let vHeight = 0;
        if (total > 0) {
            // Calculate absolute percentage of max height for the column
            const colHeightPct = (total / maxCount) * 100;
            // Now calculate relative percentages within the column for stacking
            pHeight = (mData.photos / total) * 100;
            vHeight = (mData.videos / total) * 100;
            
            // To make the heights relative to the max height:
            pHeight = (mData.photos / maxCount) * 100;
            vHeight = (mData.videos / maxCount) * 100;
        }
        
        barsHtml += `
            <div class="chart-col">
                <div class="chart-tooltip">${monthNames[i-1]}: ${mData.photos} Photos, ${mData.videos} Videos</div>
                <div class="chart-bar-container">
                    <div class="chart-bar videos" style="height: ${vHeight}%"></div>
                    <div class="chart-bar photos" style="height: ${pHeight}%"></div>
                </div>
                <span class="chart-label">${monthNames[i-1]}</span>
            </div>
        `;
    }
    
    // Calculate Count Pie Chart percentages
    const totalMedia = yearStats.photos + yearStats.videos;
    let piePhotosPct = 0;
    if (totalMedia > 0) {
        piePhotosPct = Math.round((yearStats.photos / totalMedia) * 100);
    }
    const pieVideosPct = 100 - piePhotosPct;
    const conicGradient = `conic-gradient(#3b82f6 0% ${piePhotosPct}%, #ef4444 ${piePhotosPct}% 100%)`;
    
    // Calculate Storage Pie Chart percentages
    const storagePhotos = yearStats.storage_photos || 0;
    const storageVideos = yearStats.storage_videos || 0;
    const totalStorage = storagePhotos + storageVideos;
    let storagePhotosPct = 0;
    if (totalStorage > 0) {
        storagePhotosPct = Math.round((storagePhotos / totalStorage) * 100);
    }
    const storageVideosPct = 100 - storagePhotosPct;
    // We can use a different color scheme for storage, e.g., purple/yellow, or stick to blue/red
    // Let's use blue/red to keep it consistent
    const storageConicGradient = `conic-gradient(#3b82f6 0% ${storagePhotosPct}%, #ef4444 ${storagePhotosPct}% 100%)`;
    
    // Helper to format bytes
    const formatBytes = (bytes) => {
        if (!+bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    };

    root.innerHTML = `
        <div class="custom-chart-wrapper">
            <div class="custom-bar-chart">
                <div class="chart-y-axis">
                    <span>${maxCount}</span>
                    <span>${Math.round(maxCount/2)}</span>
                    <span>0</span>
                </div>
                ${barsHtml}
            </div>
            
            <div id="stats-heatmap-container" class="hidden" style="margin-top: 24px; margin-bottom: 24px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px;">
                <!-- JS injected calendar block grid -->
            </div>
            
            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                <div class="custom-pie-container" style="flex: 1; min-width: 300px; flex-direction: column; text-align: center; gap: 20px;">
                    <h4 style="margin:0; font-size: 16px; color: #fff;">Items Breakdown</h4>
                    <div class="custom-pie-chart" style="background: ${conicGradient}; margin: 0 auto;"></div>
                    <div class="pie-legend" style="align-items: center;">
                        <div class="pie-legend-item">
                            <div class="legend-dot photos"></div>
                            <span>Photos (${piePhotosPct}%) - ${yearStats.photos}</span>
                        </div>
                        <div class="pie-legend-item">
                            <div class="legend-dot videos"></div>
                            <span>Videos (${pieVideosPct}%) - ${yearStats.videos}</span>
                        </div>
                    </div>
                </div>
                
                <div class="custom-pie-container" style="flex: 1; min-width: 300px; flex-direction: column; text-align: center; gap: 20px;">
                    <h4 style="margin:0; font-size: 16px; color: #fff;">Storage Consumption</h4>
                    <div class="custom-pie-chart" style="background: ${storageConicGradient}; margin: 0 auto;"></div>
                    <div class="pie-legend" style="align-items: center;">
                        <div class="pie-legend-item">
                            <div class="legend-dot photos"></div>
                            <span>Photos (${storagePhotosPct}%) - ${formatBytes(storagePhotos)}</span>
                        </div>
                        <div class="pie-legend-item">
                            <div class="legend-dot videos"></div>
                            <span>Videos (${storageVideosPct}%) - ${formatBytes(storageVideos)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        const hc = document.getElementById('stats-heatmap-container');
        if(hc) hc.classList.add('hidden');
        
        const root = document.getElementById('custom-chart-root');
        if(!root) return;
        const bars = root.querySelectorAll('.chart-col');
        bars.forEach((bar, idx) => {
            bar.style.cursor = 'pointer';
            bar.addEventListener('click', () => {
                const month = (idx + 1).toString().padStart(2, '0');
                if (typeof loadStatsHeatmap === 'function') {
                    loadStatsHeatmap(targetYear, month);
                }
            });
        });
    }, 100);
}


// ==========================================
// TIMELINE SCROLLBAR LOGIC
// ==========================================

function generateTimelineItems() {
    const track = document.getElementById('timeline-track');
    const container = document.getElementById('timeline-scrollbar-container');
    const viewPanel = elements.viewPanel;
    if (!track || !container || !viewPanel) return;

    // Only query date groups that are inside the ACTIVE view section
    const groups = Array.from(document.querySelectorAll('.view-section.active .date-group'));
    
    if (groups.length === 0 || (typeof state !== 'undefined' && state.currentView === 'memories')) {
        container.classList.remove('visible');
        container.style.display = 'none';
        track.innerHTML = '';
        return;
    }

    container.style.display = 'block';
    track.innerHTML = '';

    // Only show if content is scrollable
    if (viewPanel.scrollHeight <= viewPanel.clientHeight + 100) {
        container.classList.remove('visible');
        container.style.display = 'none';
        return;
    }

    const scrollableHeight = viewPanel.scrollHeight - viewPanel.clientHeight;

    const yearGroups = new Map();
    const monthGroups = new Map();

    groups.forEach(group => {
        const year = group.dataset.year;
        const month = group.dataset.month;
        if (year && year !== 'Undated') {
            if (!yearGroups.has(year)) {
                yearGroups.set(year, group);
            } else if (month && !monthGroups.has(`${year}-${month}`)) {
                monthGroups.set(`${year}-${month}`, group);
            }
        }
    });

    // Generate markers
    yearGroups.forEach((group, year) => {
        const offsetTop = group.offsetTop - viewPanel.offsetTop;
        let pct = offsetTop / scrollableHeight;
        if (pct < 0) pct = 0;
        if (pct > 1) pct = 1;

        const marker = document.createElement('div');
        marker.className = 'timeline-marker';
        marker.innerText = year;
        marker.style.top = `${pct * 100}%`;
        track.appendChild(marker);
    });

    // Generate Month dots
    monthGroups.forEach((group, yearMonth) => {
        const offsetTop = group.offsetTop - viewPanel.offsetTop;
        let pct = offsetTop / scrollableHeight;
        if (pct < 0) pct = 0;
        if (pct > 1) pct = 1;

        const dot = document.createElement('div');
        dot.className = 'timeline-dot';
        dot.style.top = `${pct * 100}%`;
        track.appendChild(dot);
    });
}

// Timeline Drag/Click Logic
const timelineTrack = document.getElementById('timeline-track');
if (timelineTrack) {
    let isDraggingTimeline = false;
    
    function scrollToTimelineY(clientY) {
        const viewPanel = elements.viewPanel;
        if (!viewPanel) return;
        
        const rect = timelineTrack.getBoundingClientRect();
        let y = clientY - rect.top;
        if (y < 0) y = 0;
        if (y > rect.height) y = rect.height;
        
        const pct = y / rect.height;
        const scrollableHeight = viewPanel.scrollHeight - viewPanel.clientHeight;
        viewPanel.scrollTop = pct * scrollableHeight;
    }

    timelineTrack.addEventListener('mousedown', (e) => {
        isDraggingTimeline = true;
        scrollToTimelineY(e.clientY);
        document.body.style.userSelect = 'none'; // Prevent text selection while dragging
    });
    
    window.addEventListener('mousemove', (e) => {
        if (!isDraggingTimeline) return;
        scrollToTimelineY(e.clientY);
    });
    
    window.addEventListener('mouseup', () => {
        if (isDraggingTimeline) {
            isDraggingTimeline = false;
            document.body.style.userSelect = '';
        }
    });
    
    // Hide default scroll badge if timeline is visible
    if (elements.scrollDateBadge) {
        elements.scrollDateBadge.style.opacity = '0'; // Hide the old center badge visually, but keep DOM
    }
}

// --- NEW LOGIC: Memories On This Day ---


function renderCalendarHeatmap(calendarData) {
    const root = document.getElementById('stats-calendar-root');
    if (!root) return;
    root.innerHTML = '';
    
    // Group by year and also build "All Time"
    const dataByYear = {};
    const allTimeData = {};
    
    for (const [dateStr, count] of Object.entries(calendarData)) {
        const year = dateStr.substring(0, 4);
        const mmdd = dateStr.substring(5);
        
        if (!dataByYear[year]) dataByYear[year] = {};
        dataByYear[year][mmdd] = count;
        
        if (!allTimeData[mmdd]) allTimeData[mmdd] = 0;
        allTimeData[mmdd] += count;
    }
    
    // Default empty tooltip div
    let tooltip = document.getElementById('calendar-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'calendar-tooltip';
        tooltip.className = 'calendar-tooltip';
        document.body.appendChild(tooltip);
    }
    
    const years = Object.keys(dataByYear).sort((a,b) => b - a);
    if (years.length === 0) {
        root.innerHTML = '<div style="color:var(--text-secondary); font-size: 14px;">No activity data available.</div>';
        return;
    }
    
    function createHeatmapBlock(labelStr, yearData, layoutYear) {
        let maxYearly = 0;
        for (const d of Object.values(yearData)) {
            if (d > maxYearly) maxYearly = d;
        }
        
        const getColorScale = (count) => {
            if (count === 0) return 0;
            const ratio = count / maxYearly;
            let scale = Math.ceil(ratio * 9);
            if (scale < 1) scale = 1;
            if (scale > 9) scale = 9;
            return scale;
        };
        
        const yearBlock = document.createElement('div');
        yearBlock.className = 'calendar-year-block';
        
        const yearLabel = document.createElement('div');
        yearLabel.className = 'calendar-year-label';
        yearLabel.innerText = labelStr;
        
        const gridWrapper = document.createElement('div');
        gridWrapper.className = 'calendar-grid-wrapper';
        
        const monthsDiv = document.createElement('div');
        monthsDiv.className = 'calendar-months';
        
        const gridDiv = document.createElement('div');
        gridDiv.className = 'calendar-grid';
        
        const isLeapYear = (layoutYear % 4 === 0 && layoutYear % 100 !== 0) || (layoutYear % 400 === 0);
        const daysInYear = isLeapYear ? 366 : 365;
        
        const startDate = new Date(layoutYear, 0, 1);
        const startDayOfWeek = startDate.getDay(); 
        
        let currentCol = document.createElement('div');
        currentCol.className = 'calendar-col';
        
        for (let i = 0; i < startDayOfWeek; i++) {
            const padCell = document.createElement('div');
            padCell.className = 'calendar-cell';
            padCell.style.backgroundColor = 'transparent';
            currentCol.appendChild(padCell);
        }
        
        const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        let currentMonth = -1;
        
        for (let day = 0; day < daysInYear; day++) {
            const d = new Date(layoutYear, 0, day + 1);
            const m = d.getMonth();
            
            if (m !== currentMonth) {
                const colIndex = gridDiv.childElementCount;
                const mLabel = document.createElement('div');
                mLabel.className = 'calendar-month-label';
                mLabel.innerText = monthNames[m];
                mLabel.style.left = (colIndex * 15) + 'px'; 
                monthsDiv.appendChild(mLabel);
                currentMonth = m;
            }
            
            const mmdd = `${String(m+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
            const count = yearData[mmdd] || 0;
            const scale = getColorScale(count);
            
            const cell = document.createElement('div');
            cell.className = `calendar-cell color-scale-${scale}`;
            
            if (count > 0) {
                cell.style.cursor = 'pointer';
                cell.addEventListener('click', () => {
                    const monthName = monthNames[m];
                    let query;
                    if (labelStr === "All Time") {
                        query = `${monthName} ${d.getDate()}`;
                    } else {
                        query = `${labelStr}-${String(m+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
                    }
                    
                    if (window.state && window.state.filters) {
                        window.state.filters.date_query = [query];
                    }
                    
                    if (typeof applyFilters === 'function') {
                        applyFilters();
                    }
                });
            }
            
            cell.addEventListener('mouseenter', (e) => {
                const monthName = monthNames[m];
                let displayYear = labelStr === "All Time" ? "" : `, ${labelStr}`;
                tooltip.innerText = `${count} photo${count === 1 ? '' : 's'} on ${monthName} ${d.getDate()}${displayYear}`;
                tooltip.style.opacity = '1';
                
                const rect = cell.getBoundingClientRect();
                tooltip.style.left = (rect.left + rect.width / 2) + 'px';
                tooltip.style.top = rect.top + 'px';
            });
            cell.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
            });
            
            currentCol.appendChild(cell);
            
            if (currentCol.childElementCount === 7 || day === daysInYear - 1) {
                gridDiv.appendChild(currentCol);
                currentCol = document.createElement('div');
                currentCol.className = 'calendar-col';
            }
        }
        
        gridWrapper.appendChild(monthsDiv);
        gridWrapper.appendChild(gridDiv);
        
        yearBlock.appendChild(yearLabel);
        yearBlock.appendChild(gridWrapper);
        
        root.appendChild(yearBlock);
    }
    
    // 1. Render All Time (use a leap year like 2024 for layout so Feb 29 fits)
    if (Object.keys(allTimeData).length > 0 && years.length > 1) {
        createHeatmapBlock("All Time", allTimeData, 2024);
    }
    
    // 2. Render Individual Years
    years.forEach(year => {
        createHeatmapBlock(year, dataByYear[year], parseInt(year));
    });
}
