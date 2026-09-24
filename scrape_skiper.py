import urllib.request
import re
import json

urls = ['https://skiper-ui.com/v1/skiper11', 'https://skiper-ui.com/v1/skiper27']
for url in urls:
    print(f"Fetching {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    
    # Try to find string literals that contain component code
    # Usually Next.js payload contains the raw code blocks in a JS string with escaped newlines
    matches = re.findall(r'\\"(.*?use client.*?)\\"', html)
    if matches:
        print(f"Found code in {url}")
        code = matches[0].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        print(code[:800])
        print('...\n')
    else:
        print(f"No code found in {url} using that regex. Let's try another.")
        matches = re.findall(r'"([^"]*?framer-motion[^"]*?)"', html)
        for m in matches:
            if 'export default function' in m or 'const' in m:
                code = m.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                print(code[:800])
                print('...\n')
                break
