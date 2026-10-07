html = open('app/templates/partials/lightbox-modal.html').read()
lines = html.split('\n')
open_c = 0
close_c = 0
for i, l in enumerate(lines):
    open_c += l.count('<div')
    close_c += l.count('</div')
    if '<aside' in l or '</aside' in l or 'lightbox-sidebar' in l:
        print(f'Line {i+1}: open={open_c}, close={close_c} -> {l.strip()}')
