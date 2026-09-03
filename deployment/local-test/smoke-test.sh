#!/usr/bin/env bash
set -euo pipefail

base_url="${BASE_URL:-http://127.0.0.1:12347}"
curl --fail --silent --show-error --max-time 10 \
  "$base_url/api/v1/travelservice/welcome"
curl --fail --silent --show-error --max-time 10 \
  "$base_url/api/v1/travelservice/trips" >/dev/null
echo
echo "Travel service smoke tests passed."
