#!/usr/bin/env python3
import os
import re
from pathlib import Path

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
]

HTML_FILES = [
    p for p in ROOT.rglob('*.html')
    if '.git' not in p.parts and 'node_modules' not in p.parts
]

missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
if missing:
    raise SystemExit(f'Missing required files: {missing}')

errors = []
link_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
for html_file in HTML_FILES:
    text = html_file.read_text(encoding='utf-8', errors='ignore')
    for match in link_pattern.findall(text):
        ref = match.strip()
        if ref.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:')):
            continue
        target = (html_file.parent / ref.split('#', 1)[0]).resolve()
        if not target.exists():
            errors.append(f'{html_file.relative_to(ROOT)} -> missing target: {ref}')

if errors:
    for error in errors:
        print(error)
    raise SystemExit(f'Found {len(errors)} broken local links')

print(f'Validation passed for {len(HTML_FILES)} HTML files and {len(REQUIRED_FILES)} required assets.')
