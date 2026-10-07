import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target_progress = """.story-progress-container {
    display: flex;
    gap: 4px;
    padding: 24px 24px 16px;
    width: 100%;
    background: linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 100%);
}"""

replacement_progress = """.story-playback-bar {
    position: absolute;
    bottom: 24px;
    left: 24px;
    right: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    z-index: 100;
    pointer-events: auto;
}
.story-playback-bar .btn-icon {
    backdrop-filter: none !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: white;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0.8;
    transition: opacity 0.2s, transform 0.2s;
}
.story-playback-bar .btn-icon:hover {
    opacity: 1;
    transform: scale(1.1);
}
.story-playback-bar .btn-icon i {
    width: 20px;
    height: 20px;
}
.story-progress-container {
    display: flex;
    gap: 4px;
    flex: 1;
}"""

if target_progress in css:
    css = css.replace(target_progress, replacement_progress)
    print("CSS updated!")
else:
    print("Failed to update CSS")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
