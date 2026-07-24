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
    
    track.innerHTML = '';
    
    // Only show if content is scrollable
    if (viewPanel.scrollHeight <= viewPanel.clientHeight + 100) {
        container.classList.remove('visible');
        return;
    }
    
    // Visibility is now controlled dynamically on scroll via updateScrollingDateLabel
    
    const groups = Array.from(document.querySelectorAll('.date-group'));
    if (groups.length === 0) return;
    
    const scrollableHeight = viewPanel.scrollHeight - viewPanel.clientHeight;
    
    // Find first group of each year
    const yearGroups = new Map();
    groups.forEach(group => {
        const year = group.dataset.year;
        if (year && year !== 'Undated' && !yearGroups.has(year)) {
            yearGroups.set(year, group);
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
        
        // Add a few dots below it for visual padding (unless it's the last one)
        for (let i = 1; i <= 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'timeline-dot';
            dot.style.top = `calc(${pct * 100}% + ${i * 15}px)`;
            track.appendChild(dot);
        }
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
    
    // Group by year
    const dataByYear = {};
    for (const [dateStr, count] of Object.entries(calendarData)) {
        const year = dateStr.substring(0, 4);
        if (!dataByYear[year]) dataByYear[year] = {};
        dataByYear[year][dateStr] = count;
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
    
    years.forEach(year => {
        const yearInt = parseInt(year);
        const yearData = dataByYear[year];
        
        let maxYearly = 0;
        for (const d of Object.values(yearData)) {
            if (d > maxYearly) maxYearly = d;
        }
        
        const getColorScale = (count) => {
            if (count === 0) return 0;
            if (count <= Math.ceil(maxYearly * 0.25)) return 1;
            if (count <= Math.ceil(maxYearly * 0.50)) return 2;
            if (count <= Math.ceil(maxYearly * 0.75)) return 3;
            return 4;
        };
        
        const yearBlock = document.createElement('div');
        yearBlock.className = 'calendar-year-block';
        
        const yearLabel = document.createElement('div');
        yearLabel.className = 'calendar-year-label';
        yearLabel.innerText = year;
        
        const gridWrapper = document.createElement('div');
        gridWrapper.className = 'calendar-grid-wrapper';
        
        const monthsDiv = document.createElement('div');
        monthsDiv.className = 'calendar-months';
        
        const gridDiv = document.createElement('div');
        gridDiv.className = 'calendar-grid';
        
        const isLeapYear = (yearInt % 4 === 0 && yearInt % 100 !== 0) || (yearInt % 400 === 0);
        const daysInYear = isLeapYear ? 366 : 365;
        
        const startDate = new Date(yearInt, 0, 1);
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
            const d = new Date(yearInt, 0, day + 1);
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
            
            const dateStr = `${year}-${String(m+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
            const count = yearData[dateStr] || 0;
            const scale = getColorScale(count);
            
            const cell = document.createElement('div');
            cell.className = `calendar-cell color-scale-${scale}`;
            
            cell.addEventListener('mouseenter', (e) => {
                const monthName = monthNames[m];
                tooltip.innerText = `${count} photo${count === 1 ? '' : 's'} on ${monthName} ${d.getDate()}, ${year}`;
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
    });
}
