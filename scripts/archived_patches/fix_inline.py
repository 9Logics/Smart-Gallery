d = open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8').read()
d = d.replace('style="position: relative; display: flex; flex-direction: column;"', 'style="position: relative; display: flex; flex-direction: column; width: 100%; height: 100%;"')
open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8').write(d)
