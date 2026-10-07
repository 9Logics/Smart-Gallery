js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

import re

# find the pathData map function
pattern = r'const pathData = trendPoints\.map\(\(pt, i\) => \{.*?return \$\{i===0 \? \'M\' : \'L\'\} \$\{x\} \$\{y\};.*?\}\)\.join\(\' \'\);'

good = '''const minTime = trendPoints[0].time;
                    const maxTime = trendPoints[trendPoints.length - 1].time;
                    
                    const pathData = trendPoints.map((pt, i) => {
                        const x = minTime === maxTime ? 100 : ((pt.time - minTime) / (maxTime - minTime)) * 100;
                        const y = maxSize === 0 ? 100 : 100 - (pt.size / maxSize) * 100;
                        return \ \ \;
                    }).join(' ');'''

js = re.sub(pattern, good, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
