#!/bin/bash
brew install python-tk
python3 -m venv venv
source venv/bin/activate

version="0.0.0"
function extract-tag {
  current_commit_tag=$(git describe --tags --exact-match HEAD 2>/dev/null)
  if [ -n "$current_commit_tag" ]; then
    version="$current_commit_tag"
  else
    echo "The current commit is not associated with any tags"
  fi
}
function build {
  extract-tag
  sed -i '' "s/0\.0\.0/$version/g" "./index.py"
  rm -rf "./dist"
  pip install -r requirements.txt
  python -m PyInstaller index.py --name ntl-flux-console --onefile --icon=imgs/ntl.ico -w
}

function bundle {
  xattr -cr dist/ntl-flux-console.app
  codesign --force --deep --sign - dist/ntl-flux-console.app
  brew install create-dmg
  rm -f ntl-flux-console.dmg
  create-dmg --volname "NTL Flux Console" --window-size 600 400 --app-drop-link 450 150 ntl-flux-console.dmg dist/ntl-flux-console.app
}

build # Python 3.13
bundle
