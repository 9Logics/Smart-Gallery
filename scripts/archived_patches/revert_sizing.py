with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    d = f.read()

target = 'style="position: relative; display: flex; justify-content: center; align-items: center; z-index: 2; width: 100%; height: 100%; max-width: 100%; max-height: 100%;"'
replacement = 'style="position: relative; display: flex; justify-content: center; align-items: center; z-index: 2; max-width: 100%; max-height: 100%;"'
d = d.replace(target, replacement)

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(d)
