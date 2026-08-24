import ast
import astor
import collections
import os

with open('app.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

routes = []
other_nodes = []

for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        is_route = False
        url = ""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', '') == 'route':
                is_route = True
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    url = decorator.args[0].value
        
        if is_route:
            routes.append({'url': url, 'node': node})
        else:
            other_nodes.append(node)
    else:
        # Check if it's the `if __name__ == '__main__':` block
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == '__name__':
                continue # Skip it
        other_nodes.append(node)

# Group routes by prefix
prefixes = collections.defaultdict(list)
for r in routes:
    url = r['url']
    if url.startswith('/api/faces'):
        prefixes['faces'].append(r)
    elif url.startswith('/api/albums'):
        prefixes['albums'].append(r)
    elif url.startswith('/api/photos') or url.startswith('/api/photo'):
        prefixes['photos'].append(r)
    elif url.startswith('/api/places'):
        prefixes['places'].append(r)
    elif url.startswith('/api/metadata') or url.startswith('/api/archive') or url.startswith('/api/favorites') or url.startswith('/api/trash'):
        prefixes['metadata'].append(r)
    elif url.startswith('/api/data') or url.startswith('/api/settings') or url.startswith('/api/stats'):
        prefixes['system'].append(r)
    elif url.startswith('/api/scan'):
        prefixes['scan'].append(r)
    else:
        prefixes['misc'].append(r)

if not os.path.exists('routes'):
    os.makedirs('routes')

# Write blueprints
blueprints = []
for prefix, items in prefixes.items():
    bp_name = f"{prefix}_bp"
    blueprints.append((prefix, bp_name))
    
    code = f"from flask import Blueprint, request, jsonify, send_file, Response, redirect, url_for, render_template\n"
    code += f"import os, json, sqlite3, time, datetime, shutil\n"
    code += f"from app_core import *\n\n"
    code += f"{bp_name} = Blueprint('{prefix}', __name__)\n\n"
    
    for item in items:
        node = item['node']
        # replace @app.route with @bp.route
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', '') == 'route':
                decorator.func.value.id = bp_name
        
        code += astor.to_source(node) + "\n"
        
    with open(f"routes/{prefix}.py", "w", encoding='utf-8') as f:
        f.write(code)

# Write app_core.py
app_core_tree = ast.Module(body=other_nodes, type_ignores=[])
with open("app_core.py", "w", encoding='utf-8') as f:
    f.write(astor.to_source(app_core_tree))

# Write new app.py
app_py = "from app_core import *\n"
for prefix, bp_name in blueprints:
    app_py += f"from routes.{prefix} import {bp_name}\n"

app_py += "\n"
for prefix, bp_name in blueprints:
    app_py += f"app.register_blueprint({bp_name})\n"

app_py += """

if __name__ == '__main__':
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    
    db_path = os.path.join(CACHE_DIR, 'gallery.db')
    needs_init = not os.path.exists(db_path)
    
    if needs_init:
        init_db()
        print("Database initialized.")
        
    # Start background tasks
    import threading
    threading.Thread(target=watch_directories_task, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
with open("new_app.py", "w", encoding='utf-8') as f:
    f.write(app_py)

print("AST Refactor complete.")
