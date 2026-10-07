js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

bad = '''                    const pathData = trendPoints.map((pt, i) => {
                        const x = trendPoints.length === 1 ? 100 : (i / (trendPoints.length - 1)) * 100;
                        const y = maxSize === 0 ? 100 : 100 - (pt.size / maxSize) * 100;
                        return \\ \ \\;
                    }).join(' ');'''

good = '''                    // Calculate min and max time for linear X axis mapping
                    const minTime = trendPoints[0].time;
                    const maxTime = trendPoints[trendPoints.length - 1].time;
                    
                    const pathData = trendPoints.map((pt, i) => {
                        const x = minTime === maxTime ? 100 : ((pt.time - minTime) / (maxTime - minTime)) * 100;
                        const y = maxSize === 0 ? 100 : 100 - (pt.size / maxSize) * 100;
                        return \\ \ \\;
                    }).join(' ');'''

if bad in js:
    js = js.replace(bad, good)
    print("MAPPING X REPLACED")
else:
    print("MAPPING X NOT FOUND")

bad_push = '''                        trendPoints.push({
                            size: cumulativeSize
                        });'''

good_push = '''                        trendPoints.push({
                            time: new Date(yearNum, parseInt(monthStr) - 1).getTime(),
                            size: cumulativeSize
                        });'''

if bad_push in js:
    js = js.replace(bad_push, good_push)
    print("PUSH REPLACED")
else:
    print("PUSH NOT FOUND")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
