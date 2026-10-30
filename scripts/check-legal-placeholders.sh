#!/bin/sh
# Validate the actual rendered legal routes, including missing-build failures.
set -eu
python3 - "${1:-public}" <<'PY'
from pathlib import Path
import re
import sys
root = Path(sys.argv[1])
required = ['index.html', 'impressum/index.html', 'privacy/index.html']
errors = [f'Missing built page: {name}' for name in required if not (root / name).is_file()]
for path in root.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    relative = path.relative_to(root)
    patterns = [r'\{\{[^{}]+\}\}']
    if any(part in {'legal', 'impressum', 'privacy', 'datenschutz'} for part in relative.parts):
        patterns.append(r'\b(?:TODO|FIXME)\b')
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            errors.append(f'{relative}: unresolved marker {match.group(0)}')
if errors:
    print('\n'.join('ERROR: ' + error for error in errors), file=sys.stderr)
    raise SystemExit(1)
print('Built legal routes and placeholder checks passed')
PY
