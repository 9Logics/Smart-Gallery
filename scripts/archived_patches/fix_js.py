import base64

js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

start_str = "// Build SVG"
end_str = "if (container) {"

parts1 = js.split(start_str)
parts2 = parts1[1].split(end_str)

good_block = '''// Build SVG
                const svg = `
                <svg width="100%" height="100%" style="overflow: visible;">
                    <!-- Milestone Line -->
                    <line x1="0%" y1="${yMilestone}%" x2="100%" y2="${yMilestone}%" stroke="var(--chart-videos)" stroke-width="1" stroke-dasharray="4 4" opacity="0.6" />
                    <text x="0%" y="${yMilestone - 8}%" fill="var(--chart-videos)" font-size="11" font-weight="bold">${milestoneGb} GB Milestone</text>
                    
                    <!-- Solid Line (Past) -->
                    <line x1="${x1}%" y1="${y1}%" x2="${x2}%" y2="${y2}%" stroke="var(--text-secondary)" stroke-width="2" />
                    
                    <!-- Dashed Line (Future) -->
                    <line x1="${x2}%" y1="${y2}%" x2="${x3}%" y2="${y3}%" stroke="var(--chart-photos)" stroke-width="2" stroke-dasharray="6 4" />
                    
                    <!-- Points -->
                    <circle cx="${x1}%" cy="${y1}%" r="4" fill="var(--bg-deep)" stroke="var(--text-secondary)" stroke-width="2" />
                    <circle cx="${x2}%" cy="${y2}%" r="5" fill="var(--chart-photos)" stroke="#fff" stroke-width="2" />
                    <circle cx="${x3}%" cy="${y3}%" r="4" fill="var(--bg-deep)" stroke="var(--chart-photos)" stroke-width="2" />
                    
                    <!-- Labels -->
                    <text x="${x1}%" y="${y1 + 18}%" fill="var(--text-secondary)" font-size="11" text-anchor="start">Jan 1</text>
                    <text x="${x2}%" y="${y2 + 20}%" fill="#fff" font-size="12" font-weight="500" text-anchor="middle">Today</text>
                    <text x="${x3}%" y="${y3 + 18}%" fill="var(--text-secondary)" font-size="11" text-anchor="end">Dec 31</text>
                </svg>
                `;
                
                '''

js = parts1[0] + good_block + end_str + parts2[1]

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("FIXED AGAIN")
