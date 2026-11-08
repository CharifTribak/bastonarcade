# Builds the itch.io version of the site into a folder: index.html at the root, plus lib/, img/ and fonts/.
# Links to the site's other pages (game pages, English pages, legal notice) go to bastonarcade.com in a new tab.
# Usage: python3 tools/itch_build.py <output folder>
import os, re, shutil, sys
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
D = (sys.argv[1] if len(sys.argv) > 1 else 'dist/itch').rstrip('/') + '/'
shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
s = open(A + 'index.html', encoding='utf-8').read()
s = re.sub(r'href="((?:jeux|en)/[^"]+|legal\.html)"', r'href="https://bastonarcade.com/\1" target="_blank" rel="noopener"', s)
open(D + 'index.html', 'w', encoding='utf-8').write(s)
for d in ['lib', 'img', 'fonts']:
    shutil.copytree(A + d, D + d, ignore=shutil.ignore_patterns('*.md'))
print('itch build in', D, sum(len(f) for _, _, f in os.walk(D)), 'files')
