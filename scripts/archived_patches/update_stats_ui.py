import os
import re

html_path = 'app/templates/partials/views/view-stats.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add recent stats container
stats_grid_end = '''                            </div>
                        </div>'''

new_html_content = '''                            </div>
                        </div>

                        <div id="recent-stats-container" class="stats-grid" style="margin-top: 16px;">
                            <div class="stat-card" style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255,255,255,0.05);">
                                <h3 style="font-size: 14px; margin-bottom: 12px; color: var(--text-secondary);">LAST 3 MONTHS</h3>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 15px; font-weight: 600;"><i data-lucide="image" style="width:14px;height:14px;margin-right:6px;vertical-align:-2px;color:var(--chart-photos);"></i><span id="stat-3mo-photos">0</span></span>
                                        <span id="stat-3mo-photos-size" style="font-size: 13px; color: var(--text-secondary);">0 MB</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 15px; font-weight: 600;"><i data-lucide="film" style="width:14px;height:14px;margin-right:6px;vertical-align:-2px;color:var(--chart-videos);"></i><span id="stat-3mo-videos">0</span></span>
                                        <span id="stat-3mo-videos-size" style="font-size: 13px; color: var(--text-secondary);">0 MB</span>
                                    </div>
                                </div>
                            </div>
                            <div class="stat-card" style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255,255,255,0.05);">
                                <h3 style="font-size: 14px; margin-bottom: 12px; color: var(--text-secondary);">THIS YEAR</h3>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 15px; font-weight: 600;"><i data-lucide="image" style="width:14px;height:14px;margin-right:6px;vertical-align:-2px;color:var(--chart-photos);"></i><span id="stat-ty-photos">0</span></span>
                                        <span id="stat-ty-photos-size" style="font-size: 13px; color: var(--text-secondary);">0 MB</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 15px; font-weight: 600;"><i data-lucide="film" style="width:14px;height:14px;margin-right:6px;vertical-align:-2px;color:var(--chart-videos);"></i><span id="stat-ty-videos">0</span></span>
                                        <span id="stat-ty-videos-size" style="font-size: 13px; color: var(--text-secondary);">0 MB</span>
                                    </div>
                                </div>
                            </div>
                        </div>'''

html = html.replace(stats_grid_end, new_html_content, 1)

# Add prediction card
storage_analysis_end = '''                            </div>
                        </div>'''

prediction_card_html = '''                            </div>
                        </div>

                        <div class="chart-card storage-prediction-card" style="margin-bottom: 24px;">
                            <div class="chart-header" style="margin-bottom: 16px;">
                                <h3 style="margin-top: 0; margin-bottom: 4px; font-size: 16px; color: #ffffff; font-weight: 500;">Storage Forecast</h3>
                                <span style="font-size: 13px; color: var(--text-secondary);">Based on this year's upload rate</span>
                            </div>
                            
                            <div style="display: flex; flex-direction: column; gap: 16px;">
                                <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                                    <div>
                                        <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">Current Growth Rate</div>
                                        <div style="font-size: 20px; font-weight: 600; color: #fff;"><span id="stat-growth-rate">0 MB</span> / month</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">Predicted by Year End</div>
                                        <div style="font-size: 20px; font-weight: 600; color: var(--chart-photos);"><span id="stat-predicted-total">0 GB</span></div>
                                    </div>
                                </div>
                                
                                <div style="margin-top: 8px;">
                                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">
                                        <span>Jan 1</span>
                                        <span style="color: var(--text-primary); font-weight: 500;">Today</span>
                                        <span>Dec 31</span>
                                    </div>
                                    
                                    <div style="position: relative; width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                                        <!-- Current Usage Line -->
                                        <div id="forecast-current-bar" style="position: absolute; left: 0; top: 0; height: 100%; background: var(--text-secondary); border-radius: 4px; width: 50%;"></div>
                                        <!-- Predicted Usage Line -->
                                        <div id="forecast-predicted-bar" style="position: absolute; left: 50%; top: 0; height: 100%; background: repeating-linear-gradient(45deg, rgba(255,255,255,0.2), rgba(255,255,255,0.2) 4px, transparent 4px, transparent 8px); border-radius: 0 4px 4px 0; width: 25%;"></div>
                                        
                                        <!-- Milestone Marker -->
                                        <div id="forecast-milestone-marker" style="position: absolute; top: -6px; height: 20px; width: 2px; background: var(--chart-videos); display: none;">
                                            <div style="position: absolute; top: -20px; left: -50%; transform: translateX(-50%); font-size: 10px; color: var(--chart-videos); white-space: nowrap; font-weight: bold;" id="forecast-milestone-label"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>'''

html = html.replace(storage_analysis_end, prediction_card_html, 1)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML updated')
