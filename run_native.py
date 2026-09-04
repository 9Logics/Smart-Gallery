import os
import sys
import subprocess

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, 'app.py')
    
    executable = sys.executable.replace('python.exe', 'pythonw.exe')
    if not os.path.exists(executable):
        executable = sys.executable
        
    # Launch natively without keeping a terminal window open
    subprocess.Popen([executable, app_path, '--bridge'], 
                     cwd=script_dir,
                     creationflags=0x08000000) # CREATE_NO_WINDOW
