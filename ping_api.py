import urllib.request
import json
import sys

try:
    req = urllib.request.Request("http://127.0.0.1:5000/api/photos")
    with urllib.request.urlopen(req) as response:
        photos = json.loads(response.read().decode())
        
    for p in photos:
        if "Rashtrapati" in str(p.get("place_name")):
            print("Found photo:", p.get("filename"))
            print("place_name:", p.get("place_name"))
            print("full_address:", p.get("full_address"))
            print("---")
            break
except Exception as e:
    print(f"Error: {e}")
