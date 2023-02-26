$version = "X.X.X"

Remove-Item -LiteralPath ".\dist" -Force -Recurse

pip3 install -r requirements.txt

(Get-Content -path .\index.py -Raw) -replace '{{version}}',"$version" | Set-Content -Path .\index.py

python3 -m PyInstaller index.py --name ntl-flux-console --onefile --icon=imgs/ntl.ico -w

Compress-Archive -Path ".\dist\*" -DestinationPath ".\dist\ntl-flux-console-windows-$version.zip"