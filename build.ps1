$version = "X.X.X"
$python_version = "3.10.8"

$venv = Get-ChildItem -Directory -Filter *.venv | select -First 1 -ExpandProperty Name
$bin_folder = "bin"
$bin_folder_exist = Test-Path -Path "$PWD/$venv/$bin_folder"
if (!$bin_folder_exist) { $bin_folder = "Scripts" }
$pip = "$PWD/$venv/$bin_folder/pip.exe"
$python = "$PWD/$venv/$bin_folder/python.exe"
$version_number = (python --version 2>&1).Split(" ")[-1]
if ($version_number -ne $python_version) { Write-Host "Python $python_version NOT present"; exit; }

Remove-Item -LiteralPath ".\dist" -Force -Recurse
Remove-Item -LiteralPath ".\build" -Force -Recurse

& $pip install -r requirements.txt

$currentCommitTag = git describe --tags --exact-match HEAD 2>$null
if ($currentCommitTag) { $version = $currentCommitTag } else { Write-Host "The current commit is not associated with any tags" }
(Get-Content -path .\index.py -Raw) -replace "0.0.0","$version" | Set-Content -NoNewline -Path .\index.py

& $python -m PyInstaller index.py --name ntl-flux-console --onefile --icon=imgs/ntl.ico -w
Compress-Archive -Path ".\dist\*" -DestinationPath ".\dist\ntl-flux-console-windows-$version.zip"