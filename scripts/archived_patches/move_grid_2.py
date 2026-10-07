with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
div_count = 0
in_grid = False

for i, line in enumerate(lines):
    if '<!-- Story Grid View -->' in line:
        start_idx = i
        in_grid = True
    
    if in_grid:
        div_count += line.count('<div')
        div_count -= line.count('</div')
        
        if div_count == 0 and start_idx != -1 and i > start_idx:
            end_idx = i
            break

if start_idx != -1 and end_idx != -1:
    grid_lines = lines[start_idx:end_idx+1]
    
    # Remove from original location
    del lines[start_idx:end_idx+1]
    
    # Insert right before </body>
    body_close_idx = -1
    for i, line in enumerate(lines):
        if '</body>' in line:
            body_close_idx = i
            break
            
    if body_close_idx != -1:
        lines = lines[:body_close_idx] + grid_lines + lines[body_close_idx:]
        
        with open('app/templates/index.html', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Moved story-grid-view outside story-lightbox-modal successfully!")
    else:
        print("</body> not found")
else:
    print("story-grid-view not found or parsing failed")
