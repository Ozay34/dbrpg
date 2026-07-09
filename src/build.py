import subprocess

subprocess.call(r'pyinstaller -F --add-data "assets/;assets/" src/main.py')