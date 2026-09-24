import os

js_path = 'app/static/js/views/stats_heatmap.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_js = '''function initStatsHeatmap() {
    const originalRenderChart = window.renderChart || renderChart;
    window.renderChart = function(yearlyData, targetYear) {
        originalRenderChart(yearlyData, targetYear);'''

new_js = '''function initStatsHeatmap() {
    let originalRenderChart = null;
    if (typeof window !== 'undefined' && window.renderChart) {
        originalRenderChart = window.renderChart;
    } else if (typeof renderChart !== 'undefined') {
        originalRenderChart = renderChart;
    }
    
    if (!originalRenderChart) {
        console.warn('renderChart is not defined yet. Delaying initialization...');
        setTimeout(initStatsHeatmap, 500);
        return;
    }

    window.renderChart = function(yearlyData, targetYear) {
        originalRenderChart(yearlyData, targetYear);'''

if old_js in js:
    js = js.replace(old_js, new_js)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Fixed stats_heatmap.js ReferenceError!")
else:
    print("Could not find js block!")

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=273', 'v=274')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
