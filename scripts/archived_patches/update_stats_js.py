import os

js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

injection_target = '''            document.getElementById('stat-storage-photos').innerText = formatBytes(pSize);
            document.getElementById('stat-storage-videos').innerText = formatBytes(vSize);
            document.getElementById('stat-storage-total').innerText = formatBytes(tSize);'''

new_js = '''            document.getElementById('stat-storage-photos').innerText = formatBytes(pSize);
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
            
            // Calculate Storage Forecast
            if (document.getElementById('stat-growth-rate')) {
                const totalDaysThisYear = 365; // simplify leap year
                // days passed in current year
                const startOfYear = new Date(currentYear, 0, 1);
                const daysPassed = Math.max(1, Math.floor((now - startOfYear) / (1000 * 60 * 60 * 24)));
                
                const tyTotalSize = tyPhotosSize + tyVideosSize;
                
                // Growth rate per month (average this year)
                const monthsPassed = Math.max(1, daysPassed / 30.44);
                const avgBytesPerMonth = tyTotalSize / monthsPassed;
                
                document.getElementById('stat-growth-rate').innerText = formatBytes(avgBytesPerMonth);
                
                // Predicted total added by end of year
                const predictedBytes = avgBytesPerMonth * 12;
                document.getElementById('stat-predicted-total').innerText = '+' + formatBytes(predictedBytes);
                
                // Bar positioning
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
                }
            }'''

if injection_target in js:
    js = js.replace(injection_target, new_js)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("JS updated successfully")
else:
    print("Injection target not found")
