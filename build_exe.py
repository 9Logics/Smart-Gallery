import os
import sys
import subprocess

def build():
    print("=======================================")
    print("   Smart Gallery - Exe Build Script")
    print("=======================================")
    print("\n1. Ensuring PyInstaller is installed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print("\n2. Generating build configuration...")
    spec_command = [
        "pyi-makespec",
        "--onedir",
        "--windowed", # Hides the console window
        "--add-data=app/templates;app/templates",
        "--add-data=app/static;app/static",
        "--hidden-import=webview.platforms.edgechromium",
        "--hidden-import=flask",
        "--hidden-import=app.bridge_api",
        "--hidden-import=numpy._core._exceptions",
        "--hidden-import=numpy._core._multiarray_umath",
        "--hidden-import=numpy._core._multiarray_math",
        "--collect-all=torch",
        "--collect-all=transformers",
        "--collect-all=torchvision",
        "--collect-all=numpy",
        "--collect-all=scipy",
        "--collect-all=cv2",
        "app.py"
    ]
    subprocess.run(spec_command, check=True)
    
    print("\n3. Patching configuration to fix Python 3.11 ML compilation bugs...")
    # Fixes 'SystemError: error return without exception set' in ast.py
    # caused by PyTorch's deeply nested code structures in Python 3.11
    with open("app.spec", "r", encoding="utf-8") as f:
        spec_content = f.read()
        
    if "sys.setrecursionlimit" not in spec_content:
        spec_content = "import sys\nsys.setrecursionlimit(5000)\n\n" + spec_content
        with open("app.spec", "w", encoding="utf-8") as f:
            f.write(spec_content)
            
    print("\n4. Compiling the application (This will take a few minutes)...")
    build_command = [
        "pyinstaller",
        "--noconfirm",
        "app.spec"
    ]
    subprocess.run(build_command, check=True)
    
    print("\n=======================================")
    print("BUILD COMPLETE! 🎉")
    print("You can find your compiled application in:")
    print(os.path.abspath(os.path.join("dist", "app", "app.exe")))
    print("=======================================")

if __name__ == '__main__':
    build()
