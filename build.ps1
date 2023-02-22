pip3 install -r requirements.txt

python3 -m PyInstaller index.py --name ntl-console --onefile --icon=imgs/ntl.ico -w

Copy-Item 'imgs' 'dist' -Recurse -Force