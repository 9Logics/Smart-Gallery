html = open('app/templates/partials/lightbox-modal.html').read()
lines = html.split('\n')
open_c = 0
close_c = 0
for i, l in enumerate(lines):
    open_c += l.count('<div')
    close_c += l.count('</div')
    if close_c > open_c:
        print(f'Extra </div> found at line {i+1}: {l}')
        break
