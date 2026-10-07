import os
path = 'app/routes/system.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

import_statement = "import sys, subprocess, urllib.request, json\n"
if "import sys, subprocess" not in content:
    content = content.replace("import os, json, sqlite3, time, datetime, shutil\n", "import os, json, sqlite3, time, datetime, shutil\n" + import_statement)

update_route = """
@system_bp.route('/api/system/update', methods=['POST'])
def update_app():
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        try:
            # 1. Fetch latest release from GitHub
            req = urllib.request.Request("https://api.github.com/repos/9Logics/Smart-Gallery/releases/latest", headers={'User-Agent': 'SmartGallery-Updater'})
            with urllib.request.urlopen(req) as response:
                release_data = json.loads(response.read())
            
            # Find the executable asset
            exe_url = None
            for asset in release_data.get('assets', []):
                if asset['name'].endswith('.exe'):
                    exe_url = asset['browser_download_url']
                    break
            
            if not exe_url:
                return jsonify({'error': 'No compiled executable (.exe) found in the latest GitHub release.'}), 404
                
            # Download the exe to a temporary file
            temp_dir = os.environ.get('TEMP', os.getcwd())
            temp_exe = os.path.join(temp_dir, 'SmartGallery_update.exe')
            
            req = urllib.request.Request(exe_url, headers={'User-Agent': 'SmartGallery-Updater'})
            with urllib.request.urlopen(req) as response, open(temp_exe, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # Create a batch file to replace the current executable
            current_exe = sys.executable
            bat_path = os.path.join(temp_dir, 'update_smart_gallery.bat')
            
            bat_content = f\"\"\"@echo off
timeout /t 2 /nobreak > NUL
move /y "{temp_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
\"\"\"
            with open(bat_path, 'w') as f:
                f.write(bat_content)
                
            # Launch the batch script detached
            subprocess.Popen([bat_path], creationflags=subprocess.CREATE_NEW_CONSOLE | 0x08000000)
            
            return jsonify({'success': True, 'message': 'Update downloaded. Restarting app to apply update...', 'restart_required': True})
            
        except Exception as e:
            return jsonify({'error': f'Failed to update exe: {str(e)}'}), 500
            
    else:
        # Running from source, use git pull
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            result = subprocess.run(['git', 'pull'], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return jsonify({'success': True, 'message': f'Git pull successful. {result.stdout.strip()}'})
            else:
                return jsonify({'error': f'Git pull failed: {result.stderr}'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to run git pull: {str(e)}'}), 500
"""

if "/api/system/update" not in content:
    content += update_route
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added /api/system/update route.")
else:
    print("Route already exists.")
