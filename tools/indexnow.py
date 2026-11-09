# Tells IndexNow (Bing, Yandex, Seznam, Naver…) which pages of bastonarcade.com changed: the URLs whose <lastmod> in
# sitemap.xml differs from the previous version (git ref given as argument), plus the new ones.
# Usage: python3 tools/indexnow.py <previous git ref>
import json, os, re, subprocess, sys, urllib.request
HOST = 'bastonarcade.com'
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
KEY = next(f[:-4] for f in os.listdir(R) if re.fullmatch(r'[0-9a-f]{32}\.txt', f))
pairs = lambda xml: dict(re.findall(r'<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>', xml))
now = pairs(open(R + 'sitemap.xml').read())
before = {}
ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD~1'
try: before = pairs(subprocess.check_output(['git', '-C', R, 'show', ref + ':sitemap.xml'], text=True, stderr=subprocess.DEVNULL))
except Exception: pass
urls = [u for u, d in now.items() if before.get(u) != d]
if not urls: print('nothing changed'); sys.exit(0)
body = json.dumps({ 'host':HOST, 'key':KEY, 'keyLocation':'https://' + HOST + '/' + KEY + '.txt', 'urlList':urls }).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={ 'Content-Type':'application/json; charset=utf-8' })
try:
    with urllib.request.urlopen(req, timeout=30) as r: print('IndexNow', r.status, len(urls), 'URLs'); print('\n'.join(urls))
except urllib.error.HTTPError as e:
    print('IndexNow error', e.code, e.read()[:300]); sys.exit(1 if e.code not in (202,) else 0)
