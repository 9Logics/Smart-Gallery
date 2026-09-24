import urllib.request
import re

url = 'https://skiper-ui.com/v1/skiper86'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Find the title
match_title = re.search(r'<title>(.*?) \| Skiper UI', html)
if match_title:
    print(f"TITLE: {match_title.group(1)}")

# Find the meta description
match_desc = re.search(r'name="description"\s+content="(.*?)"', html)
if match_desc:
    print(f"DESC: {match_desc.group(1)}")

print("\n--- CODE ---\n")
# Find code blocks
matches = re.findall(r'\\"(.*?use client.*?)\\"', html)
if matches:
    print(matches[0].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')[:1500])
else:
    matches = re.findall(r'"([^"]*?framer-motion[^"]*?)"', html)
    for m in matches:
        if 'export default function' in m or 'const' in m:
            print(m.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')[:1500])
            break
