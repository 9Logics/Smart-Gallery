css = """
/* Lightbox Filmstrip */
#lightbox-filmstrip-container {
    width: calc(100% - 48px);
    height: 85px;
    margin: 0 auto 24px auto;
    background: rgba(15, 22, 38, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    overflow-x: auto;
    flex-shrink: 0;
    box-sizing: border-box;
    scroll-behavior: smooth;
    z-index: 50;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

#lightbox-filmstrip-container.hidden {
    opacity: 0;
    height: 0;
    margin-bottom: 0;
    padding-top: 0;
    padding-bottom: 0;
    border-width: 0;
    transform: translateY(20px) scale(0.95);
    pointer-events: none;
    overflow: hidden !important;
}

#lightbox-filmstrip-container::-webkit-scrollbar {
    height: 6px;
}
#lightbox-filmstrip-container::-webkit-scrollbar-track {
    background: transparent;
}
#lightbox-filmstrip-container::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
}
"""

with open('app/static/style.css', 'a', encoding='utf-8') as f:
    f.write(css)
