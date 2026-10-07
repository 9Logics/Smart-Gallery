import os
import re

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'app', 'templates')
    static_dir = os.path.join(base_dir, 'app', 'static')
    
    index_path = os.path.join(templates_dir, 'index.html')
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove Jinja IF tags
    content = re.sub(r'{%\s*if\s+.*?%}', '', content)
    content = re.sub(r'{%\s*endif\s*%}', '', content)
    
    # Replace includes
    def replace_include(match):
        filename = match.group(1).strip("'\"")
        filepath = os.path.join(templates_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as inc_f:
                return inc_f.read()
        return f"<!-- Missing include: {filename} -->"
        
    # Match {% include '...' %}
    content = re.sub(r'{%\s*include\s+([\'"].*?[\'"])\s*%}', replace_include, content)
    
    # The output path
    out_path = os.path.join(static_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Built static UI to {out_path}")

if __name__ == '__main__':
    build()
