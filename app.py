from app.app_core import *
from app.routes.misc import misc_bp
from app.routes.scan import scan_bp
from app.routes.system import system_bp
from app.routes.photos import photos_bp
from app.routes.faces import faces_bp
from app.routes.places import places_bp
from app.routes.albums import albums_bp
from app.routes.metadata import metadata_bp

app.register_blueprint(misc_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(system_bp)
app.register_blueprint(photos_bp)
app.register_blueprint(faces_bp)
app.register_blueprint(places_bp)
app.register_blueprint(albums_bp)
app.register_blueprint(metadata_bp)

import sys
import threading
import time
import argparse

def find_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

if __name__ == '__main__':
    init_db()
    
    # Pre-load AI models in the background to prevent UI freezing on first search/scan
    def preload_models():
        try:
            print("Pre-loading AI models in background...")
            from app.scene_classifier import load_clip
            load_clip()
            print("AI models pre-loaded successfully!")
        except Exception as e:
            print(f"Failed to pre-load AI models: {e}")
            
    threading.Thread(target=preload_models, daemon=True).start()

    parser = argparse.ArgumentParser()
    parser.add_argument('--dev', action='store_true', help='Run in development mode (Terminal + Web Browser)')
    parser.add_argument('--bridge', action='store_true', help='Run as a native desktop window using pywebview')
    args = parser.parse_args()
    
    if getattr(sys, 'frozen', False):
        args.bridge = True
        
        # Create a desktop shortcut automatically if running as EXE
        import os
        import subprocess
        try:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            shortcut_path = os.path.join(desktop, 'Project Gallery One.lnk')
            if not os.path.exists(shortcut_path):
                target = sys.executable
                icon = target
                working_dir = os.path.dirname(target)
                ps_script = f"""
                $WshShell = New-Object -comObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{target}"
                $Shortcut.IconLocation = "{icon}"
                $Shortcut.WorkingDirectory = "{working_dir}"
                $Shortcut.Save()
                """
                subprocess.run(["powershell", "-Command", ps_script], creationflags=0x08000000)
        except Exception as e:
            print(f"Failed to create desktop shortcut: {e}")
    
    import socket
    import subprocess
    import sys
    
    PORT = 5000
    URL = f"http://127.0.0.1:{PORT}"
    
    def open_pwa(delay=1.5):
        if delay > 0:
            time.sleep(delay)
        print("Launching in true default system browser...")
        import webbrowser
        webbrowser.open(URL)
            
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    if args.bridge:
        print("Starting Native Bridge Mode...")
        import webview
        import json
        import os
        from app.bridge_api import GalleryApi
        from app.app_core import CACHE_DIR
        
        state_file = os.path.join(CACHE_DIR, 'window_state.json')
        w, h = 1400, 900
        x, y = None, None
        is_max = False
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    st = json.load(f)
                w = st.get('width', 1400)
                h = st.get('height', 900)
                x = st.get('x', None)
                y = st.get('y', None)
                is_max = st.get('maximized', False)
            except Exception:
                pass
                
        kwargs = {
            'title': 'Project Gallery One',
            'url': app,
            'js_api': GalleryApi(),
            'width': w,
            'height': h,
            'min_size': (800, 600),
            'maximized': is_max
        }
        if x is not None and y is not None and not is_max:
            kwargs['x'] = x
            kwargs['y'] = y
            
        window = webview.create_window(**kwargs)
        state_tracker = {'maximized': is_max}
        
        def on_max():
            state_tracker['maximized'] = True
            save_state()
            
        def on_restore():
            state_tracker['maximized'] = False
            save_state()
            
        def on_close():
            # Force kill the python process instantly. 
            # This guarantees WebView2 child processes (msedgewebview2.exe) are instantly terminated by the OS.
            import os
            os._exit(0)
            
        window.events.maximized += on_max
        window.events.restored += on_restore
        window.events.closed += on_close
        
        def save_state():
            try:
                with open(state_file, 'w') as f:
                    st = {'maximized': state_tracker['maximized']}
                    if not state_tracker['maximized']:
                        st['width'] = window.width
                        st['height'] = window.height
                        st['x'] = window.x
                        st['y'] = window.y
                    else:
                        st['width'] = w
                        st['height'] = h
                        st['x'] = x
                        st['y'] = y
                    json.dump(st, f)
            except Exception:
                pass
                
        def state_poller():
            import time
            while True:
                time.sleep(5)
                save_state()
                
        import threading
        threading.Thread(target=state_poller, daemon=True).start()
        
        webview.start(debug=args.dev, private_mode=False)
        sys.exit(0)

    import os
    # If we are NOT the child process created by the Werkzeug reloader
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        if is_port_in_use(PORT):
            print(f"Server is already running on port {PORT}. Launching app and exiting...")
            open_pwa(delay=0)
            sys.exit(0)
            
        # Start the browser thread only in the master process so it doesn't launch twice
        threading.Thread(target=open_pwa, daemon=True).start()
    
    if args.dev:
        print(f"Starting DEV server on port {PORT}...")
        app.run(host='127.0.0.1', debug=True, port=PORT)
    else:
        print(f"Starting PROD server on port {PORT}...")
        try:
            from waitress import serve
            serve(app, host='127.0.0.1', port=PORT)
        except ImportError:
            app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)
