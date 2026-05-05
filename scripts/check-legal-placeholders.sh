#!/bin/sh
set -e
dir="${1:-public}"
rc=0
for pattern in '{{CONTACT_EMAIL_HELLER}}' '{{CONTACT_EMAIL_LEBOULANGER}}' '{{SITE_DOMAIN}}'; do
  hits=$(grep -rl "$pattern" "$dir" 2>/dev/null || true)
  if [ -n "$hits" ]; then
    echo "ERROR: Unfilled placeholder $pattern found in:"
    echo "$hits" | sed 's/^/  /'
    rc=1
  fi
done
if [ -d "$dir/legal" ]; then
  for pattern in 'TODO' 'FIXME'; do
    hits=$(grep -rl "$pattern" "$dir"/legal/ 2>/dev/null || true)
    if [ -n "$hits" ]; then
      echo "ERROR: $pattern found in legal pages:"
      echo "$hits" | sed 's/^/  /'
      rc=1
    fi
  done
fi
exit $rc
