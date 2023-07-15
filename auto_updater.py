import requests
import subprocess
import importlib
import sys

try:
    importlib.import_module("pygame")
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", "pygame"])
    importlib.import_module("pygame")

url = "https://raw.githubusercontent.com/MrCreeps/TIMEALIVE/main/game.py"
response = requests.get(url)

if response.status_code == 200:
    exec(response.text, globals())
else:
    print(f"Failed to download: {response.status_code}")
