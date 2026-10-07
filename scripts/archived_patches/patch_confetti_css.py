import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Add confetti animation
confetti_css = '''
@keyframes confettiFall {
    0% {
        transform: translateY(-10vh) rotate(0deg);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(110vh) rotate(720deg);
        opacity: 0;
    }
}

.confetti-piece {
    position: absolute;
    top: -10vh;
    animation: confettiFall linear infinite;
    will-change: transform;
    opacity: 0;
}
'''

if 'confettiFall' not in css:
    css += confetti_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added confetti CSS!")
