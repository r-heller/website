#!/bin/sh
# Phase 6 CI gate: gzipped JS for /overview/ must stay ≤ 320 KB.
# Cytoscape + fcose are CDN-hosted and not counted against our budget here.
set -e
dir="${1:-public}/js/overview"
if [ ! -d "$dir" ]; then
  echo "ERROR: $dir not found"; exit 1
fi
LIMIT=327680  # 320 KB
total=0
for f in "$dir"/*.js; do
  [ -f "$f" ] || continue
  size=$(gzip -c "$f" | wc -c)
  total=$((total + size))
  printf "  %-30s %6d bytes (gz)\n" "$(basename "$f")" "$size"
done
echo "  TOTAL gzip: $total bytes (limit $LIMIT)"
if [ "$total" -gt "$LIMIT" ]; then
  echo "ERROR: overview JS bundle exceeds budget"; exit 1
fi
