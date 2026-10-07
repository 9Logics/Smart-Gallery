py_path = 'app/routes/photos.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

target = '''        if iconic_place:
            comments.append(f"From exploring {iconic_place} to everyday life,")'''

replacement = '''        if top_places and len(top_places) > 0:
            comments.append(f"From exploring {top_places[0]['name']} to everyday life,")'''

py = py.replace(target, replacement)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
print("Patched AI comment for top_places")
