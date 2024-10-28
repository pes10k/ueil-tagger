#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

DIR="$(cd "$(dirname "$0")" && pwd)";
source "$DIR/../bin/activate";
echo '```' > README.txt;
$DIR/run.py --help >> README.txt;

if [[ -f "$DIR/config.toml" ]]; then
  API_KEY=$(grep -Eo 'action-network-api-key = "(.*)"' config.toml | sed -E 's/action-network-api-key = "(.*)".*/\1/g');
  sed -i "" "s/$API_KEY/None/g" README.txt;
fi;

if [[ -f "$DIR/app_state/last_run.txt" ]]; then
  LAST_DATE=$(cat "$DIR/app_state/last_run.txt");
  sed -i "" "s/$LAST_DATE/None/g" README.txt;
fi;

echo '```' >> README.txt;
