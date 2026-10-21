"""Check the actual Jekyll output or the explicit configured publication view."""
import argparse
import json
from pathlib import Path
import re

ITEM = re.compile(r'\baegis-[a-z0-9]+(?:[.-][a-z0-9]+)*\b')
ROOT = Path(__file__).resolve().parents[1]

def check(root, actual=False):
    if actual:
        if (root/'data').exists() or (root/'scripts').exists():raise ValueError('Raw compiler sources published')
    else:
        if (root/'.nojekyll').exists():raise ValueError('Jekyll exclusion disabled')
        settings = '\n'.join(line for line in (root/'_config.yml').read_text().splitlines() if line.strip() and not line.lstrip().startswith('#'))
        if settings != 'exclude:\n  - data\n  - scripts':raise ValueError('Unexpected publication config')
    manifest = json.loads((ROOT/'data/ids/sources.json').read_text())
    # These are exact pinned source filenames, not issue IDs. Nothing else is exempt.
    source_paths = sorted({i['path'] for i in manifest},key=len,reverse=True)
    for p in root.rglob('*'):
        if not p.is_file():continue
        relative = p.relative_to(root)
        if not actual and (relative.parts[0] in ('data','scripts','_site') or any(x.startswith('.') or x=='node_modules' for x in relative.parts)):continue
        try:text=p.read_text()
        except UnicodeError:continue
        for source in source_paths:text=text.replace(source,'PINNED_SOURCE_PATH')
        if re.search(r'(?i)\b[a-z0-9.-]+\.(?:lan|svc)\b',text):raise ValueError(f'Internal service host in {relative}')
        found=ITEM.findall(text)
        if found:raise ValueError(f'Internal item reference in {relative}: {sorted(set(found))}')
    return True

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--site',type=Path);args=parser.parse_args()
    check(args.site or ROOT,bool(args.site));print('Public tree: no item references; raw data/scripts excluded')
