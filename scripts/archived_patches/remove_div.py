html = open('app/templates/partials/lightbox-modal.html').read()
lines = html.split('\n')
# Line 70 is index 69
if lines[69].strip() == '</div>':
    print("Found it, deleting")
    del lines[69]
else:
    print("Not exactly </div> at line 70, let's find it")
    for i in range(65, 75):
        if lines[i].strip() == '</div>' and lines[i+1].strip() == '':
            del lines[i]
            break

open('app/templates/partials/lightbox-modal.html', 'w').write('\n'.join(lines))
