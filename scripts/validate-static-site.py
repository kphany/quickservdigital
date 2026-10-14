#!/usr/bin/env python3
import os
import re
import xml.etree.ElementTree as ET
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
required_metadata = {
    'title': re.compile(r'<title>\s*[^<]+\s*</title>', re.IGNORECASE),
    'description': re.compile(
        r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']+["\']',
        re.IGNORECASE,
    ),
    'robots directive': re.compile(
        r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']+["\']',
        re.IGNORECASE,
    ),
    'canonical URL': re.compile(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
    'viewport': re.compile(
        r'<meta\s+name=["\']viewport["\']\s+content=["\'][^"\']+["\']',
        re.IGNORECASE,
    ),
}
required_open_graph = ('og:type', 'og:title', 'og:description', 'og:url')
canonical_urls = set()

for html_file in HTML_FILES:
    text = html_file.read_text(encoding='utf-8', errors='ignore')
    for metadata_name, pattern in required_metadata.items():
        match = pattern.search(text)
        if not match:
            errors.append(f'{html_file.relative_to(ROOT)} -> missing {metadata_name}')
        elif metadata_name == 'canonical URL':
            canonical_urls.add(match.group(1))

    open_graph_values = {}
    for property_name in required_open_graph:
        pattern = re.compile(
            rf'<meta\s+property=["\']{re.escape(property_name)}["\']\s+content=["\']([^"\']+)["\']',
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            open_graph_values[property_name] = match.group(1)
        else:
            errors.append(
                f'{html_file.relative_to(ROOT)} -> missing {property_name} metadata'
            )

    canonical_match = required_metadata['canonical URL'].search(text)
    if canonical_match and open_graph_values.get('og:url') != canonical_match.group(1):
        errors.append(
            f'{html_file.relative_to(ROOT)} -> og:url does not match the canonical URL'
        )

    for match in link_pattern.findall(text):
        ref = match.strip()
        parsed_ref = urlsplit(ref)
        if parsed_ref.scheme or ref.startswith('//') or not parsed_ref.path:
            continue
        target = (html_file.parent / parsed_ref.path).resolve()
        if not target.exists():
            errors.append(f'{html_file.relative_to(ROOT)} -> missing target: {ref}')

try:
    sitemap_root = ET.parse(ROOT / 'sitemap.xml').getroot()
    sitemap_namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap_urls = [
        element.text.strip()
        for element in sitemap_root.findall('sm:url/sm:loc', sitemap_namespace)
        if element.text
    ]
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append('sitemap.xml -> contains duplicate URLs')

    missing_sitemap_urls = canonical_urls - set(sitemap_urls)
    for url in sorted(missing_sitemap_urls):
        errors.append(f'sitemap.xml -> missing canonical URL: {url}')

    unknown_sitemap_urls = set(sitemap_urls) - canonical_urls
    for url in sorted(unknown_sitemap_urls):
        errors.append(f'sitemap.xml -> URL has no matching page canonical: {url}')
except ET.ParseError as error:
    errors.append(f'sitemap.xml -> invalid XML: {error}')

if errors:
    for error in errors:
        print(error)
    raise SystemExit(f'Found {len(errors)} static-site validation errors')

print(
    f'Validation passed for {len(HTML_FILES)} HTML files, '
    f'{len(REQUIRED_FILES)} required assets, and {len(canonical_urls)} sitemap URLs.'
)
