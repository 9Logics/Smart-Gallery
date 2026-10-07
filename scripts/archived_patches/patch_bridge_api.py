import re

with open('app/bridge_api.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """        # Fallback for non-JSON returns (like raw text/html)
        try:
            return json.loads(resp.data.decode('utf-8'))
        except json.JSONDecodeError:
            return {'error': 'Response was not JSON', 'text': resp.data.decode('utf-8')}"""

replacement = """        # Fallback for non-JSON returns (like raw text/html)
        try:
            decoded = resp.data.decode('utf-8')
            try:
                return json.loads(decoded)
            except json.JSONDecodeError:
                return {'error': 'Response was not JSON', 'text': decoded}
        except UnicodeDecodeError:
            return {'error': 'Response was binary data and cannot be routed through fetch_internal() bridge'}"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/bridge_api.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched bridge_api.py")
else:
    print("Target not found in bridge_api.py")
