import re

js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# I will replace the whole block starting from // Calculate Storage Forecast down to the end of the if block.
old_block_pattern = r'// Calculate Storage Forecast.*?if \(milestoneGb <= predictedTotalGb\) \{.*?\}\s*\}'

new_block = '''// Calculate Storage Forecast
            if (document.getElementById('stat-growth-rate')) {
                const totalDaysThisYear = 365; // simplify leap year
                const startOfYear = new Date(currentYear, 0, 1);
                const daysPassed = Math.max(1, Math.floor((now - startOfYear) / (1000 * 60 * 60 * 24)));
                
                const tyTotalSize = tyPhotosSize + tyVideosSize;
                
                // Growth rate per month (average this year)
                const monthsPassed = Math.max(1, daysPassed / 30.44);
                const avgBytesPerMonth = tyTotalSize / monthsPassed;
                
                document.getElementById('stat-growth-rate').innerText = formatBytes(avgBytesPerMonth);
                
                // Current total and End of Year predictions
                const predictedBytes = avgBytesPerMonth * 12;
                document.getElementById('stat-current-total').innerText = formatBytes(tSize);
                
                const startOfYearSize = Math.max(0, tSize - tyTotalSize);
                const endOfYearSize = startOfYearSize + predictedBytes;
                
                document.getElementById('stat-predicted-total').innerText = formatBytes(endOfYearSize);
                
                // Milestone marker logic
                const currentTotalGb = tSize / (1024*1024*1024);
                let milestoneGb = Math.ceil(currentTotalGb);
                if (milestoneGb <= currentTotalGb) milestoneGb += 1;
                const milestoneBytes = milestoneGb * 1024 * 1024 * 1024;
                
                // Graph bounds
                const minY = startOfYearSize * 0.98; // 2% padding bottom
                const maxY = Math.max(endOfYearSize, milestoneBytes) * 1.02; // 2% padding top
                
                const getYPct = (val) => 100 - ((val - minY) / (maxY - minY)) * 100;
                
                const x1 = 0;
                const y1 = getYPct(startOfYearSize);
                
                const x2 = (daysPassed / 365) * 100;
                const y2 = getYPct(tSize);
                
                const x3 = 100;
                const y3 = getYPct(endOfYearSize);
                
                const yMilestone = getYPct(milestoneBytes);
                
                // Build SVG
                const svg = \\
                <svg width="100%" height="100%" style="overflow: visible;">
                    <!-- Milestone Line -->
                    <line x1="0%" y1="\\%" x2="100%" y2="\\%" stroke="var(--chart-videos)" stroke-width="1" stroke-dasharray="4 4" opacity="0.6" />
                    <text x="0%" y="\\%" fill="var(--chart-videos)" font-size="11" font-weight="bold">\\ GB Milestone</text>
                    
                    <!-- Solid Line (Past) -->
                    <line x1="\\%" y1="\\%" x2="\\%" y2="\\%" stroke="var(--text-secondary)" stroke-width="2" />
                    
                    <!-- Dashed Line (Future) -->
                    <line x1="\\%" y1="\\%" x2="\\%" y2="\\%" stroke="var(--chart-photos)" stroke-width="2" stroke-dasharray="6 4" />
                    
                    <!-- Points -->
                    <circle cx="\\%" cy="\\%" r="4" fill="var(--bg-deep)" stroke="var(--text-secondary)" stroke-width="2" />
                    <circle cx="\\%" cy="\\%" r="5" fill="var(--chart-photos)" stroke="#fff" stroke-width="2" />
                    <circle cx="\\%" cy="\\%" r="4" fill="var(--bg-deep)" stroke="var(--chart-photos)" stroke-width="2" />
                    
                    <!-- Labels -->
                    <text x="\\%" y="\\%" fill="var(--text-secondary)" font-size="11" text-anchor="start">Jan 1</text>
                    <text x="\\%" y="\\%" fill="#fff" font-size="12" font-weight="500" text-anchor="middle">Today</text>
                    <text x="\\%" y="\\%" fill="var(--text-secondary)" font-size="11" text-anchor="end">Dec 31</text>
                </svg>
                \\;
                
                const container = document.getElementById('forecast-svg-container');
                if (container) {
                    container.innerHTML = svg;
                }
            }'''

# Since regex dotall might match too much, let's just do a string split/replace if possible
# Let's find exactly the block to replace.
import sys

# The exact end of the block in the old JS is:
#                     const marker = document.getElementById('forecast-milestone-marker');
#                     if (marker) marker.style.display = 'none';
#                 }
#             }

js_parts = js.split('// Calculate Storage Forecast')
if len(js_parts) < 2:
    print('Block not found!')
    sys.exit(1)

pre_js = js_parts[0]
post_js_block = js_parts[1]

# find the end of the if (document.getElementById('stat-growth-rate')) { ... } block
# by counting braces or simply splitting by if (marker) marker.style.display = 'none';\n                }\n            }
end_str = "if (marker) marker.style.display = 'none';\n                }\n            }"
if end_str in post_js_block:
    post_js = post_js_block.split(end_str)[1]
    final_js = pre_js + new_block + post_js
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(final_js)
    print("JS successfully replaced")
else:
    print("Could not find end string")
