import os
import shutil

root_dir = os.getcwd()
archive_dir = os.path.join(root_dir, 'scripts', 'archived_patches')
os.makedirs(archive_dir, exist_ok=True)

keep_files = {
    'app.py', 'run_native.py', 'setup.bat', 'Start Project Gallery One.bat',
    'requirements.txt', 'README.md', 'handover.md', 'gallery.db', 'project_gallery.db',
    'Project Gallery One.spec', 'LICENSE'
}
keep_extensions = {'.db'}

moved_count = 0

for filename in os.listdir(root_dir):
    file_path = os.path.join(root_dir, filename)
    if os.path.isfile(file_path):
        if filename in keep_files or any(filename.endswith(ext) for ext in keep_extensions):
            continue
            
        # specifically look for .py, .js, .html scripts that are not main ones
        if filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.html') or filename.endswith('.md'):
            # It's likely a patch file
            if filename.startswith('patch_') or filename.startswith('fix_') or filename.startswith('test_') or \
               filename.startswith('update_') or filename.startswith('gen') or filename.startswith('scratch') or \
               filename.startswith('refactor_') or filename in ['export_logo.py', 'find_browser.py', 'find_photo.py', 'get_img_css.py', 'get_svg.py', 'inject.py', 'make_sparkline.py', 'remove_debug.py', 'restore_webview.py', 'simple_injector.py', 'write_html.js', 'temp_script.js', 'temp_script2.js', 'debug_indent.py', 'migration.py']:
                
                target_path = os.path.join(archive_dir, filename)
                # If file already exists in archive, remove it or rename
                if os.path.exists(target_path):
                    os.remove(target_path)
                shutil.move(file_path, target_path)
                moved_count += 1

print(f"Moved {moved_count} patch scripts to scripts/archived_patches/")
