html_path = 'app/templates/partials/views/view-stats.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

bad = 'Projected growth based on your current upload rate'
good = 'Historical total storage growth over time'

html = html.replace(bad, good)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
