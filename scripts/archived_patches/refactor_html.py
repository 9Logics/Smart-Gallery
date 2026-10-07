html_path = 'app/templates/partials/views/view-stats.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the old storage-prediction-card and replace it with a cleaner grid of 3 stats
old_prediction_card = '''                        <div class="chart-card storage-prediction-card" style="margin-bottom: 24px;">
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

new_prediction_grid = '''                        <div class="stats-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 24px;">
                            <div class="stat-card">
                                <h3>Upload Rate</h3>
                                <div class="stat-value" style="font-size: 20px;"><span id="stat-growth-rate">0 MB</span> <span style="font-size: 14px; font-weight: normal; color: var(--text-secondary);">/ mo</span></div>
                            </div>
                            <div class="stat-card">
                                <h3>Current Storage</h3>
                                <div class="stat-value" id="stat-current-total" style="font-size: 20px;">0 GB</div>
                            </div>
                            <div class="stat-card">
                                <h3>End of Year (Est.)</h3>
                                <div class="stat-value" id="stat-predicted-total" style="font-size: 20px; color: var(--chart-photos);">0 GB</div>
                            </div>
                        </div>'''

if old_prediction_card in html:
    html = html.replace(old_prediction_card, new_prediction_grid)
    print("Replaced forecast card.")
else:
    print("Could not find old forecast card.")

# 2. Add the SVG trend graph under Storage Analysis
# Look for the end of the Storage Analysis card
storage_analysis_end = '''                                <div><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:var(--chart-videos); margin-right:6px;"></span>Videos: <span id="stat-storage-videos" style="color:var(--text-primary); font-weight:600;">-</span></div>
                                <div style="margin-left: auto;">Total: <span id="stat-storage-total" style="color:var(--text-primary); font-weight:600;">-</span></div>
                            </div>
                        </div>'''

new_trend_graph = '''                                <div><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:var(--chart-videos); margin-right:6px;"></span>Videos: <span id="stat-storage-videos" style="color:var(--text-primary); font-weight:600;">-</span></div>
                                <div style="margin-left: auto;">Total: <span id="stat-storage-total" style="color:var(--text-primary); font-weight:600;">-</span></div>
                            </div>
                        </div>

                        <div class="chart-card storage-trend-card" style="margin-bottom: 24px;">
                            <div class="chart-header" style="margin-bottom: 24px;">
                                <h3 style="margin-top: 0; margin-bottom: 4px; font-size: 16px; color: #ffffff; font-weight: 500;">Storage Trend</h3>
                                <span style="font-size: 13px; color: var(--text-secondary);">Projected growth based on your current upload rate</span>
                            </div>
                            
                            <!-- SVG Chart Container -->
                            <div id="forecast-svg-container" style="width: 100%; height: 160px; position: relative;">
                            </div>
                        </div>'''

if storage_analysis_end in html:
    html = html.replace(storage_analysis_end, new_trend_graph)
    print("Added SVG graph under Storage Analysis.")
else:
    print("Could not find Storage Analysis card.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
