import re

html_path = 'app/templates/partials/views/view-stats.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the HTML block for the forecast graph
old_html = '''                                <div style="margin-top: 8px;">
                                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">
                                        <span>Jan 1</span>
                                        <span style="color: var(--text-primary); font-weight: 500;">Today</span>
                                        <span>Dec 31</span>
                                    </div>
                                    
                                    <div style="position: relative; width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                                        <!-- Current Usage Line -->
                                        <div id="forecast-current-bar" style="position: absolute; left: 0; top: 0; height: 100%; background: var(--text-secondary); border-radius: 4px; width: 50%;"></div>
                                        <!-- Predicted Usage Line -->
                                        <div id="forecast-predicted-bar" style="position: absolute; left: 50%; top: 0; height: 100%; background: repeating-linear-gradient(45deg, rgba(255,255,255,0.2), rgba(255,255,255,0.2) 4px, transparent 4px, transparent 8px); border-radius: 0 4px 4px 0; width: 25%;"></div>
                                        
                                        <!-- Milestone Marker -->
                                        <div id="forecast-milestone-marker" style="position: absolute; top: -6px; height: 20px; width: 2px; background: var(--chart-videos); display: none;">
                                            <div style="position: absolute; top: -20px; left: -50%; transform: translateX(-50%); font-size: 10px; color: var(--chart-videos); white-space: nowrap; font-weight: bold;" id="forecast-milestone-label"></div>
                                        </div>
                                    </div>
                                </div>'''

new_html = '''                                <div style="margin-top: 24px; position: relative;">
                                    <!-- Date Axis Labels -->
                                    <div style="position: relative; height: 16px; width: 100%; font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">
                                        <span style="position: absolute; left: 0; bottom: 0;">Jan 1</span>
                                        <span id="forecast-today-label" style="position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); color: var(--text-primary); font-weight: 500;">Today</span>
                                        <span style="position: absolute; right: 0; bottom: 0;">Dec 31</span>
                                    </div>
                                    
                                    <div style="position: relative; width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                                        <!-- Current Usage Line (Solid) -->
                                        <div id="forecast-current-bar" style="position: absolute; left: 0; top: 0; height: 100%; background: var(--text-secondary); border-radius: 4px 0 0 4px; width: 50%;"></div>
                                        
                                        <!-- Predicted Usage Line (Striped) -->
                                        <div id="forecast-predicted-bar" style="position: absolute; left: 50%; top: 0; height: 100%; background: repeating-linear-gradient(45deg, rgba(255,255,255,0.2), rgba(255,255,255,0.2) 4px, transparent 4px, transparent 8px); border-radius: 0 4px 4px 0; width: 25%;"></div>
                                        
                                        <!-- Milestone Marker -->
                                        <div id="forecast-milestone-marker" style="position: absolute; top: -10px; height: 28px; width: 2px; background: var(--chart-videos); display: none; z-index: 5;">
                                            <div style="position: absolute; top: -20px; left: -50%; transform: translateX(-50%); font-size: 11px; color: var(--chart-videos); white-space: nowrap; font-weight: bold; background: #09090b; padding: 0 4px; border-radius: 4px; border: 1px solid var(--chart-videos);" id="forecast-milestone-label"></div>
                                        </div>
                                    </div>
                                </div>'''

if old_html in html:
    html = html.replace(old_html, new_html)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('HTML updated')
else:
    print('HTML NOT FOUND')

js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_js = '''                // Bar positioning
                const currentPct = Math.min(100, Math.max(5, (tyTotalSize / predictedBytes) * 100));
                document.getElementById('forecast-current-bar').style.width = currentPct + '%';
                document.getElementById('forecast-predicted-bar').style.left = currentPct + '%';
                document.getElementById('forecast-predicted-bar').style.width = (100 - currentPct) + '%';
                
                // Milestone marker logic: e.g. next round GB milestone
                const currentTotalGb = tSize / (1024*1024*1024);
                const predictedTotalGb = (tSize + (predictedBytes - tyTotalSize)) / (1024*1024*1024);
                
                let milestoneGb = Math.ceil(currentTotalGb);
                if (milestoneGb <= currentTotalGb) milestoneGb += 1; // ensure it's next
                
                if (milestoneGb < predictedTotalGb) {
                    const extraGbNeeded = milestoneGb - currentTotalGb;
                    const predictedExtraGb = predictedTotalGb - currentTotalGb;
                    const pctOfRemaining = (extraGbNeeded / predictedExtraGb) * (100 - currentPct);
                    
                    const marker = document.getElementById('forecast-milestone-marker');
                    if (marker) {
                        marker.style.display = 'block';
                        marker.style.left = (currentPct + pctOfRemaining) + '%';
                        document.getElementById('forecast-milestone-label').innerText = milestoneGb + ' GB';
                    }
                }'''

new_js = '''                // Bar positioning
                const currentPct = Math.min(100, Math.max(5, (daysPassed / 365) * 100));
                document.getElementById('forecast-current-bar').style.width = currentPct + '%';
                
                document.getElementById('forecast-predicted-bar').style.left = currentPct + '%';
                document.getElementById('forecast-predicted-bar').style.width = (100 - currentPct) + '%';
                
                if (document.getElementById('forecast-today-label')) {
                    document.getElementById('forecast-today-label').style.left = currentPct + '%';
                }
                
                // Milestone marker logic: e.g. next round GB milestone
                const currentTotalGb = tSize / (1024*1024*1024);
                const predictedTotalGb = (tSize + (predictedBytes - tyTotalSize)) / (1024*1024*1024);
                
                let milestoneGb = Math.ceil(currentTotalGb);
                if (milestoneGb <= currentTotalGb) milestoneGb += 1; // ensure it's next
                
                if (milestoneGb <= predictedTotalGb) {
                    const extraGbNeeded = milestoneGb - currentTotalGb;
                    const predictedExtraGb = predictedTotalGb - currentTotalGb;
                    const pctOfRemaining = (extraGbNeeded / predictedExtraGb) * (100 - currentPct);
                    
                    const marker = document.getElementById('forecast-milestone-marker');
                    if (marker) {
                        marker.style.display = 'block';
                        marker.style.left = (currentPct + pctOfRemaining) + '%';
                        document.getElementById('forecast-milestone-label').innerText = 'Cross ' + milestoneGb + ' GB';
                    }
                } else {
                    const marker = document.getElementById('forecast-milestone-marker');
                    if (marker) marker.style.display = 'none';
                }'''

if old_js in js:
    js = js.replace(old_js, new_js)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print('JS updated')
else:
    print('JS NOT FOUND')
