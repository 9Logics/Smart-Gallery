html_path = 'app/templates/partials/views/view-stats.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

bad_snippet = '''                            <!-- SVG Chart Container -->
                            <div id="forecast-svg-container" style="width: 100%; height: 160px; position: relative;">
                            </div>
                        </div>
                            </div>
                        </div>

                        <div id="recent-stats-container"'''

good_snippet = '''                            <!-- SVG Chart Container -->
                            <div id="forecast-svg-container" style="width: 100%; height: 160px; position: relative;">
                            </div>
                        </div>

                        <div id="recent-stats-container"'''

if bad_snippet in html:
    html = html.replace(bad_snippet, good_snippet)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML FIXED")
else:
    print("NOT FOUND")
