import os

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

target = """    if args.bridge:
        print("Native Bridge Mode was requested, but user requested no Edge/WebView2. Falling back to Chrome App Mode...")
        pass"""

replacement = """    if args.bridge:
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
        sys.exit(0)"""

code = code.replace(target, replacement)
with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Restored pywebview with aggressive force-kill on close")
