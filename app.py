from app_core import *
from routes.misc import misc_bp
from routes.scan import scan_bp
from routes.system import system_bp
from routes.photos import photos_bp
from routes.faces import faces_bp
from routes.places import places_bp
from routes.albums import albums_bp
from routes.metadata import metadata_bp

app.register_blueprint(misc_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(system_bp)
app.register_blueprint(photos_bp)
app.register_blueprint(faces_bp)
app.register_blueprint(places_bp)
app.register_blueprint(albums_bp)
app.register_blueprint(metadata_bp)


if __name__ == '__main__':
    init_db()
    def open_as_app():
        import time, ctypes, os, subprocess
        time.sleep(1.0)
        
        user32 = ctypes.windll.user32
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            user32.SetProcessDPIAware()
        
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        
        target_w_ratio = 1808 / 1920
        target_h_ratio = 1000 / 1080
        win_w = int(screen_w * target_w_ratio)
        win_h = int(screen_h * target_h_ratio)
        
        pos_x = (screen_w - win_w) // 2
        pos_y = (screen_h - win_h) // 2

        size_arg = f"--window-size={win_w},{win_h}"
        pos_arg  = f"--window-position={pos_x},{pos_y}"

        edge_path = os.path.join(os.environ.get("ProgramFiles(x86)", "C:\Program Files (x86)"), "Microsoft\Edge\Application\msedge.exe")
        chrome_path = os.path.join(os.environ.get("ProgramFiles", "C:\Program Files"), "Google\Chrome\Application\chrome.exe")
        
        if os.path.exists(edge_path):
            try:
                subprocess.Popen([edge_path, "--app=http://127.0.0.1:5000", size_arg, pos_arg])
                return
            except Exception:
                pass
        elif os.path.exists(chrome_path):
            try:
                subprocess.Popen([chrome_path, "--app=http://127.0.0.1:5000", size_arg, pos_arg])
                return
            except Exception:
                pass
                
        import webbrowser
        webbrowser.open("http://127.0.0.1:5000")
        
    import threading
    threading.Thread(target=open_as_app, daemon=True).start()
    app.run(host='127.0.0.1', debug=False, port=5000)

