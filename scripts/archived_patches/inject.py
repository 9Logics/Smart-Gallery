js_code = """
document.addEventListener('click', function(e) {
    console.log('CLICKED ON:', e.target);
    if (e.target.id === 'recap-close') {
        console.log('RECAP CLOSE CLICKED');
    }
});
setTimeout(() => {
    const rect = document.querySelector('.recap-close').getBoundingClientRect();
    console.log('recap-close 1:', rect);
    const rect2 = document.querySelectorAll('.recap-close')[1].getBoundingClientRect();
    console.log('recap-close 2:', rect2);
}, 2000);
"""
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('</head>', f'<script>{js_code}</script></head>')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Injected debugger")
