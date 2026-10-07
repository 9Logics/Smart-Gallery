import sys

js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

start_str = "// Build Historical Storage Trend"
end_str = "const years = Object.keys(data.yearly).sort((a,b) => b - a);"

new_block = """// Build Historical Storage Trend
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
            """

if start_str in js and end_str in js:
    parts1 = js.split(start_str)
    parts2 = parts1[1].split(end_str)
    
    final_js = parts1[0] + new_block + '\n            ' + end_str + parts2[1]
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(final_js)
    print("INJECTED")
else:
    print("NOT FOUND")
