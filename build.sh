#!/bin/bash

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
  sed -i "s/0\.0\.0/$version/g" "$base_path/index.py"
  rm -rf "$base_path/dist"
  pip install -r requirements.txt
  python -m PyInstaller index.py --name ntl-flux-console --onefile --icon=imgs/ntl.ico -w
}

build # Python 3.10.8