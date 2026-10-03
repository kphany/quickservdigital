#!/usr/bin/env python3
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = [
    'index.html',
    'about.html',
    'services.html',
    'contact.html',
    'cambodia.html',
    'styles.css',
    'script.js',
    'logo.png',
    'robots.txt',
    'sitemap.xml',
    'wrangler.jsonc',
    'pricing.html',
    'terms-of-service.html',
    'privacy-policy.html',
    'refund-cancellation.html',
]

HTML_FILES = [
    p for p in ROOT.rglob('*.html')
    if '.git' not in p.parts and 'node_modules' not in p.parts
]

missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
if missing:
    raise SystemExit(f'Missing required files: {missing}')

errors = []
link_pattern = re.compile(r'\b(?:href|src)=["\']([^"\']+)["\']', re.IGNORECASE)
for html_file in HTML_FILES:
    text = html_file.read_text(encoding='utf-8', errors='ignore')
    for match in link_pattern.findall(text):
        ref = match.strip()
        parsed_ref = urlsplit(ref)
        if parsed_ref.scheme or ref.startswith('//') or not parsed_ref.path:
            continue
        target = (html_file.parent / parsed_ref.path).resolve()
        if not target.exists():
            errors.append(f'{html_file.relative_to(ROOT)} -> missing target: {ref}')

if errors:
    for error in errors:
        print(error)
    raise SystemExit(f'Found {len(errors)} broken local links')

print(f'Validation passed for {len(HTML_FILES)} HTML files and {len(REQUIRED_FILES)} required assets.')
