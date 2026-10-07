import base64

js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

start_str = "// Calculate Storage Forecast"
end_str = "const years = Object.keys(data.yearly).sort((a,b) => b - a);"

if start_str in js and end_str in js:
    parts1 = js.split(start_str)
    parts2 = parts1[1].split(end_str)
    
    new_block = '''// Build Historical Storage Trend
            const container = document.getElementById('forecast-svg-container');
            if (container) {
                let trendPoints = [];
                let cumulativeSize = 0;
                
                const sortedYears = Object.keys(data.yearly).sort((a, b) => a - b);
                sortedYears.forEach(yearStr => {
                    const yearData = data.yearly[yearStr];
                    const sortedMonths = Object.keys(yearData.months).sort((a, b) => a - b);
                    sortedMonths.forEach(monthStr => {
                        const mObj = yearData.months[monthStr];
                        const mSize = (mObj.storage_photos || 0) + (mObj.storage_videos || 0);
                        cumulativeSize += mSize;
                        trendPoints.push({
                            size: cumulativeSize
                        });
                    });
                });
                
                if (trendPoints.length > 0) {
                    const maxSize = cumulativeSize;
                    
                    const pathData = trendPoints.map((pt, i) => {
                        const x = trendPoints.length === 1 ? 100 : (i / (trendPoints.length - 1)) * 100;
                        const y = maxSize === 0 ? 100 : 100 - (pt.size / maxSize) * 100;
                        return `${i===0 ? 'M' : 'L'} ${x} ${y}`;
                    }).join(' ');
                    
                    const fillPathData = pathData + ` L 100 100 L 0 100 Z`;
                    
                    const svg = `
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
                        <path d="${fillPathData}" fill="url(#trendGradient)" />
                        
                        <!-- Line -->
                        <path d="${pathData}" fill="none" stroke="var(--chart-photos)" stroke-width="2.5" vector-effect="non-scaling-stroke" />
                    </svg>
                    <!-- End Dot at Top Right (max value is always the last point) -->
                    <div style="position: absolute; top: -5px; right: -5px; width: 10px; height: 10px; border-radius: 50%; background: var(--chart-photos); border: 2px solid var(--bg-deep);"></div>
                    `;
                    
                    container.innerHTML = svg;
                }
            }
            
            '''
            
    final_js = parts1[0] + new_block + end_str + parts2[1]
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(final_js)
    print("JS UPDATED")
else:
    print("STRINGS NOT FOUND")
