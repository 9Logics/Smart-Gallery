import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace open_pwa logic
new_open_pwa = """    def open_pwa(delay=1.5):
        if delay > 0:
            time.sleep(delay)
        
        chrome_paths = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"),
            r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        ]
        
        chrome_exe = None
        for p in chrome_paths:
            if os.path.exists(p):
                chrome_exe = p
                break
                
        try:
            if chrome_exe:
                print(f"Launching Chrome App mode: {chrome_exe}")
                subprocess.Popen([chrome_exe, f'--app={URL}'])
            else:
                # Fallback to default browser
                print("Chrome not found, launching default browser.")
                import webbrowser
                webbrowser.open(URL)
        except Exception as e:
            print(f"Failed to launch PWA: {e}")
            import webbrowser
            webbrowser.open(URL)"""

code = re.sub(r'    def open_pwa\(delay=1\.5\):.*?webbrowser\.open\(URL\)', new_open_pwa, code, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated open_pwa")
