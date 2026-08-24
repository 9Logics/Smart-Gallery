import tkinter as tk
from tkinter import filedialog
import sys

def main():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title="Select Media Folder")
        root.destroy()
        if folder_path:
            print(folder_path.replace('/', '\\'))
    except Exception:
        pass

if __name__ == '__main__':
    main()
