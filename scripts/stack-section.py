#!/usr/bin/env python3
"""Render/check website cards from the pinned canonical Tambo table; no network I/O."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

START = '<!-- stack-cards:start -->'
END = '<!-- stack-cards:end -->'
ROOT = Path(__file__).resolve().parents[1]


def components(text):
    start, end = '<!-- stack-table:start -->', '<!-- stack-table:end -->'
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('canonical table markers must appear exactly once')
    block = text.split(start, 1)[1].split(end, 1)[0]
    rows = []
    for line in block.splitlines():
        if not line.startswith('|') or line.startswith(('| tool |', '|---')):
            continue
        match = re.fullmatch(r'\| \[([a-z][a-z-]*)\]\((https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\) \| (.+) \|', line)
        if not match:
            raise ValueError('unrecognized canonical row')
        name, url, description = match.groups()
        if name in {r[0] for r in rows} or url in {r[1] for r in rows}:
            raise ValueError('duplicate canonical component')
        if any(c in description for c in '<>'):
            raise ValueError('canonical description must be plain text')
        rows.append((name, url, description))
    if len(rows) != 12:
        raise ValueError('canonical stack requires twelve components')
    return rows


def render(rows):
    return '\n'.join('    <div data-stack-component="' + html.escape(name, quote=True) + '"><b><a href="'
                     + html.escape(url, quote=True) + '">' + html.escape(name) + '</a></b><span>'
                     + html.escape(description) + '</span></div>' for name, url, description in rows)


def check_source(root):
    raw = (root / 'data/stack-table.md').read_bytes()
    pin = json.loads((root / 'data/stack-source.json').read_text())
    if (pin.get('repository') != 'scbrown/tambo' or pin.get('path') != 'docs/stack-table.md'
            or not re.fullmatch(r'[0-9a-f]{40}', pin.get('commit') or '')
            or pin.get('sha256') != hashlib.sha256(raw).hexdigest()):
        raise ValueError('canonical source identity/hash mismatch')
    return components(raw.decode('utf-8'))


def update_document(document, rows):
    if document.count(START) != 1 or document.count(END) != 1:
        raise ValueError('website stack markers must appear exactly once')
    before, rest = document.split(START, 1)
    _, after = rest.split(END, 1)
    return before + START + '\n' + render(rows) + '\n    ' + END + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='print verified canonical component rows')
    parser.add_argument('--write', action='store_true', help='replace only marked generated cards')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        rows = check_source(args.root)
        page = args.root / 'index.html'
        old = page.read_text()
        new = update_document(old, rows)
        if args.write:
            page.write_text(new)
        elif old != new:
            raise ValueError('website stack differs from canonical table; run scripts/stack-section.py --write')
        if args.json:
            print(json.dumps(rows))
        else:
            print('canonical stack: twelve exact cards/links; source hash verified')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
