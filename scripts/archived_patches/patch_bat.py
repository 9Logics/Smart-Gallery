import os
import re

path = 'app/routes/system.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

better_bat = """            bat_content = f\"\"\"@echo off
:wait_loop
tasklist /fi "PID eq {os.getpid()}" | find "{os.getpid()}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
move /y "{temp_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
\"\"\""""

code = re.sub(r'bat_content\s*=\s*f"""@echo off\ntimeout.*?%~f0"\n"""', better_bat, code, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated bat script logic.")
