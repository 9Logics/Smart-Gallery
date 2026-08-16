import sys

def modify_app():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    targets = [
        "for idx, path in enumerate(new_files):",
        "for i, p in enumerate(all_paths):",
        "for p in unscanned:",
        "for idx, path in enumerate(photos):",
        "for i, (old_path, fname, fsize) in enumerate(missing_photos):"
    ]
    
    cancel_check = \"\"\"
{indent}with scan_lock:
{indent}    if scan_status.get("cancel_requested"):
{indent}        break
\"\"\"
    
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        for t in targets:
            if t in line:
                indent = line[:len(line) - len(line.lstrip())] + "    "
                check_str = cancel_check.format(indent=indent)
                if check_str not in "".join(lines[i:i+5]):
                    new_lines.append(check_str)
                    print(f"Injected cancel check at line {i+1}")
                break
                
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
if __name__ == '__main__':
    modify_app()
