#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

REDACT_PLACEHOLDER="-----";

DIR="$(cd "$(dirname "$0")" && pwd)";
CONFIG_FILE="$DIR/config.toml"

# shellcheck disable=SC1091
source "$DIR/../bin/activate";
"$DIR"/run.py --help > README.txt;

# If the current install has a config file, then make sure the
# values in the config file don't wind up in the public README.
if [[ -f "$CONFIG_FILE" ]]; then
  for KEY_TO_REDACT in "action-network-api-key" "cache-dir"; do
    VALUE_TO_REDACT=$(grep -Eo "$KEY_TO_REDACT = \"(.*)\"" "$CONFIG_FILE" | sed -E "s/$KEY_TO_REDACT = \"(.*)\"/\1/");
    if [[ -n "$VALUE_TO_REDACT" ]]; then
      sed -E -i "" "s/$VALUE_TO_REDACT\)/$REDACT_PLACEHOLDER)/" README.txt;
    fi;
  done;
fi;

# Similarly, make sure any local-state specific values don't show up in the
# shared README.
if [[ -f "$DIR/app_state/last_run.txt" ]]; then
  LAST_DATE=$(cat "$DIR/app_state/last_run.txt");
  sed -i "" "s/$LAST_DATE/$REDACT_PLACEHOLDER/g" README.txt;
fi;

# Clean up any ugly, new line "$REDACTED's".
perl -0777 -i -pe "s/\n[ ]+$REDACT_PLACEHOLDER\)/ $REDACT_PLACEHOLDER\)/g" README.txt;
