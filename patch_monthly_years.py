import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''                                document.querySelectorAll('.rewind-mini-card').forEach(card => {
                                    const overlayText = card.querySelector('.mini-overlay').innerText;
                                    card.querySelector('img').src = getBestImage(overlayText, overlayText);
                                    
                                    // Step 2: Asynchronously fetch true photos for this exact month/year!
                                    fetch('/api/photos?date_query=' + encodeURIComponent(overlayText))'''

new_js = '''                                document.querySelectorAll('.rewind-mini-card').forEach(card => {
                                    const overlayText = card.querySelector('.mini-overlay').innerText;
                                    
                                    // Force monthly rewinds to query specifically for the current year
                                    let queryText = overlayText;
                                    if (!card.classList.contains('year-card')) {
                                        queryText = `${overlayText} ${new Date().getFullYear()}`;
                                    }
                                    
                                    card.querySelector('img').src = getBestImage(queryText, overlayText);
                                    
                                    // Step 2: Asynchronously fetch true photos for this exact month/year!
                                    fetch('/api/photos?date_query=' + encodeURIComponent(queryText))'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=272', 'v=273')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS Date Queries!")
else:
    print("Could not find JS block to replace!")
