#!/usr/bin/env python3
"""Check published page link, image and frame targets, including deferred embeds."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

class Targets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        names = {'a': ('href',), 'img': ('src',), 'iframe': ('src', 'data-src')}.get(tag, ())
        for name in names:
            if attrs.get(name):
                self.urls.add(attrs[name])

def check(url):
    if url.startswith(('#', 'mailto:', 'tel:')):
        return None
    parts = urlsplit(url)
    if not parts.scheme and not parts.netloc:
        target = ROOT / unquote(parts.path).lstrip('/')
        if target.is_dir():
            target = target / 'index.html'
        return None if target.is_file() else f'{url}: missing local target'
    if parts.scheme != 'https':
        return f'{url}: unsupported link scheme'
    try:
        request = Request(url, headers={'User-Agent': 'Intigraph-Link-Check/1.0'})
        with urlopen(request, timeout=30) as response:
            if response.status != 200:
                return f'{url}: HTTP {response.status}'
    except Exception as error:
        return f'{url}: {error}'
    return None

if __name__ == '__main__':
    parser = Targets()
    parser.feed((ROOT / 'index.html').read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        errors = [error for error in pool.map(check, sorted(parser.urls)) if error]
    for error in errors:
        print(error)
    print(f'Checked {len(parser.urls)} unique page targets; {len(errors)} failures')
    raise SystemExit(bool(errors))
