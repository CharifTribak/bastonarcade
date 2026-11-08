# Builds the itch.io version in itch-build/: index.html at the root, links to the site's other pages sent to
# bastonarcade.com in a new tab, plus lib/, img/ and fonts/. Run from the repository root.
import re, os, shutil
D = 'itch-build/'
shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
s = open('index.html', encoding='utf-8').read()
s = re.sub(r'href="((?:jeux|en)/[^"]+|legal\.html)"', r'href="https://bastonarcade.com/\1" target="_blank" rel="noopener"', s)
open(D + 'index.html', 'w', encoding='utf-8').write(s)
for d in ['lib', 'img', 'fonts']:
    shutil.copytree(d, D + d, ignore=shutil.ignore_patterns('*.md'))
print('itch build ready:', sum(len(f) for _, _, f in os.walk(D)), 'files')
