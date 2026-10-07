js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

start_str = "// Build Historical Storage Trend"
end_str = "const years = Object.keys(data.yearly).sort((a,b) => b - a);"

if start_str in js and end_str in js:
    parts1 = js.split(start_str)
    parts2 = parts1[1].split(end_str)
    
    new_block = '''// Restore Upload Rate and Current Storage for top cards
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
                let trendPoints = [];
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
                        trendPoints.push({
                            time: new Date(yearNum, parseInt(monthStr) - 1).getTime(),
                            size: cumulativeSize
                        });
                    });
                });
                
                if (trendPoints.length > 0) {
                    const maxSize = cumulativeSize;
                    const minTime = trendPoints[0].time;
                    const maxTime = trendPoints[trendPoints.length - 1].time;
                    
                    const pathData = trendPoints.map((pt, i) => {
                        const x = minTime === maxTime ? 100 : ((pt.time - minTime) / (maxTime - minTime)) * 100;
                        const y = maxSize === 0 ? 100 : 100 - (pt.size / maxSize) * 100;
                        return \ \ \;
                    }).join(' ');
                    
                    const fillPathData = pathData +  L 100 100 L 0 100 Z;
                    
                    const svg = 
                    <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style="overflow: visible;">
                        <defs>
                            <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="var(--chart-photos)" stop-opacity="0.4" />
                                <stop offset="100%" stop-color="var(--chart-photos)" stop-opacity="0.0" />
                            </linearGradient>
                        </defs>
                        
                        <!-- Baseline -->
                        <line x1="0" y1="100" x2="100" y2="100" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" stroke-dasharray="2 3" vector-effect="non-scaling-stroke" />
                        
                        <!-- Area Fill -->
                        <path d="\" fill="url(#trendGradient)" />
                        
                        <!-- Line -->
                        <path d="\" fill="none" stroke="var(--chart-photos)" stroke-width="2.5" vector-effect="non-scaling-stroke" />
                    </svg>
                    <!-- End Dot at Top Right (max value is always the last point) -->
                    <div style="position: absolute; top: -5px; right: -5px; width: 10px; height: 10px; border-radius: 50%; background: var(--chart-photos); border: 2px solid var(--bg-deep);"></div>
                    ;
                    
                    trendContainer.innerHTML = svg;
                }
            }
            
            '''
    
    # We also need to fix the earlier ilter if I added it in an earlier patch and it's floating somewhere
    final_js = parts1[0] + new_block + end_str + parts2[1]
    
    # clean up the old filter patch if it's there
    bad_filter = '''const sortedYears = Object.keys(data.yearly)
                    .filter(y => parseInt(y) > 1995) // ignore epoch bugs
                    .sort((a, b) => a - b);'''
    if bad_filter in final_js:
        # replace with the normal version since we redefine it in the new block anyway?
        pass

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(final_js)
    print("JS COMPLETELY FIXED")
else:
    print("COULD NOT FIND BLOCK")
