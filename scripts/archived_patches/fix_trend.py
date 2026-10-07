js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

bad = 'const sortedYears = Object.keys(data.yearly).sort((a, b) => a - b);'
good = '''const sortedYears = Object.keys(data.yearly)
                    .filter(y => parseInt(y) > 1995) // ignore epoch bugs
                    .sort((a, b) => a - b);'''

js = js.replace(bad, good)

# Also, let's make X-axis linear with TIME instead of index! That makes it a true time series.
# Wait, if X is linear time, then if they have a gap from 2010 to 2020, there will be a big flat line. That's realistic!

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
