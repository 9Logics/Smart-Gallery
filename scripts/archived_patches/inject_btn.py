d = open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8').read()

new_btn = '<button class="lightbox-filmstrip-toggle" id="lightbox-filmstrip-toggle" title="Toggle Filmstrip"><i data-lucide="gallery-horizontal"></i></button>'
d = d.replace('<button class="lightbox-refresh-btn"', new_btn + '\n            <button class="lightbox-refresh-btn"')

open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8').write(d)
