css = """

/* Video Controls Hover Animations */
.video-volume-container {
    cursor: pointer;
}

.video-volume-container:hover {
    background: rgba(255, 255, 255, 0.08);
}

.video-volume-slider {
    width: 0px;
    opacity: 0;
    margin-left: 0px;
    cursor: pointer;
    accent-color: var(--accent-color);
    height: 6px;
    border-radius: 4px;
    outline: none;
    -webkit-appearance: none;
    background: rgba(255,255,255,0.2);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    pointer-events: none;
}

.video-volume-container:hover .video-volume-slider {
    width: 80px;
    opacity: 1;
    margin-left: 8px;
    pointer-events: auto;
}
"""

with open('app/static/style.css', 'a', encoding='utf-8') as f:
    f.write(css)
