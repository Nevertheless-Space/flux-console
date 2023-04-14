$version = "X.X.X"

$venv = Get-ChildItem -Directory -Filter *.venv | select -First 1 -ExpandProperty Name
$pip = "$PWD/$venv/Scripts/pip.exe"
$python = "$PWD/$venv/Scripts/python.exe"

Remove-Item -LiteralPath ".\dist" -Force -Recurse

& $pip install -r requirements.txt

(Get-Content -path .\index.py -Raw) -replace "0.0.0","$version" | Set-Content -NoNewline -Path .\index.py

& $python -m PyInstaller index.py --name ntl-flux-console --onefile --icon=imgs/ntl.ico -w

Compress-Archive -Path ".\dist\*" -DestinationPath ".\dist\ntl-flux-console-windows-$version.zip"