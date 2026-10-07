import re

html_path = 'app/templates/partials/views/view-stats.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the old storage-prediction-card
old_card_pattern = r'<div class="chart-card storage-prediction-card".*?</div>\s*</div>\s*</div>\s*</div>'
new_card = '''<div class="chart-card storage-prediction-card" style="margin-bottom: 24px;">
                            <div class="chart-header" style="margin-bottom: 16px;">
                                <h3 style="margin-top: 0; margin-bottom: 4px; font-size: 16px; color: #ffffff; font-weight: 500;">Storage Trend & Forecast</h3>
                                <span style="font-size: 13px; color: var(--text-secondary);">Projected total storage by year end based on current upload rate</span>
                            </div>
                            
                            <div style="display: flex; gap: 32px; margin-bottom: 24px;">
                                <div>
                                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 4px;">Upload Rate</div>
                                    <div style="font-size: 18px; font-weight: 600; color: #fff;"><span id="stat-growth-rate">0 MB</span> <span style="font-size: 13px; color: var(--text-secondary); font-weight: normal;">/ mo</span></div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 4px;">Current Storage</div>
                                    <div style="font-size: 18px; font-weight: 600; color: #fff;"><span id="stat-current-total">0 GB</span></div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 4px;">End of Year (Est.)</div>
                                    <div style="font-size: 18px; font-weight: 600; color: var(--chart-photos);"><span id="stat-predicted-total">0 GB</span></div>
                                </div>
                            </div>
                            
                            <!-- SVG Chart Container -->
                            <div id="forecast-svg-container" style="width: 100%; height: 160px; position: relative;">
                            </div>
                        </div>'''

html = re.sub(old_card_pattern, new_card, html, flags=re.DOTALL)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML updated')
