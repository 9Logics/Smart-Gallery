d = open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8').read()

filmstrip_html = '''
                    <div id="lightbox-filmstrip-container" class="hidden" style="width: 100%; height: 100px; background: rgba(0, 0, 0, 0.6); padding: 10px; display: flex; align-items: center; gap: 8px; overflow-x: auto; flex-shrink: 0; box-sizing: border-box; scroll-behavior: smooth; border-top: 1px solid rgba(255,255,255,0.05);">
                    </div>
'''

d = d.replace('</div> <!-- End of lightbox-image-wrapper-element -->', filmstrip_html + '            </div> <!-- End of lightbox-image-wrapper-element -->')

open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8').write(d)
