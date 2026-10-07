import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

target = '''                </div>
            </div>

          </div>
      </div>
        
        <div class="recap-nav-left" onclick="prevRecapSlide()"></div>
        <div class="recap-nav-right" onclick="nextRecapSlide()"></div>
        <div class="recap-close" onclick="closeRecapPlayer()">✕</div>
    </div>'''

replacement = '''                </div>
            </div>
        </div>
        
        <div class="recap-nav-left" onclick="prevRecapSlide()"></div>
        <div class="recap-nav-right" onclick="nextRecapSlide()"></div>
        <div class="recap-close" onclick="closeRecapPlayer()">✕</div>
    </div>'''

html = html.replace(target, replacement)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed div structure")
