"""Game pages (jeux/*.html, en/games/*.html): the two ways in, right under the artwork.
'Play now' goes straight into a solo game (?mode=solo), 'With friends' opens a room (?mode=salon).
Safe to run twice: pages already done are left alone."""
import re, glob, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
CSS = ('.cta{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}'
       '.cta a{display:flex;align-items:center;justify-content:center;gap:6px;text-align:center;font-family:"Bangers",Impact,sans-serif;letter-spacing:.04em;font-size:24px;border:3px solid #000;box-shadow:4px 4px 0 #000;padding:12px 6px;text-decoration:none;line-height:1.1}'
       '.cta .go{background:#D91F25;color:#fff}.cta .friends{background:#1E5BFF;color:#fff}'
       '.artlink{display:block;position:relative}.artlink::after{content:"▶";position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:64px;height:64px;border-radius:50%;background:#D91F25;color:#fff;border:3px solid #000;box-shadow:3px 3px 0 #000;font-size:28px;display:flex;align-items:center;justify-content:center;padding-left:4px;box-sizing:border-box}')
T = { 'fr':('▶ Jouer maintenant', '👥 Avec des amis', 'Jouer seul tout de suite contre des robots'),
      'en':('▶ Play now', '👥 With friends', 'Play alone right now against robots') }
n = 0
for f in sorted(glob.glob(R + 'jeux/*.html') + glob.glob(R + 'en/games/*.html')):
    s = open(f, encoding='utf-8').read()
    if 'class="cta"' in s: continue
    lang = 'en' if '/en/games/' in f else 'fr'
    m = re.search(r'<a class="play" href="([^"]+)">', s); base = m.group(1)
    solo, room = base + '&mode=solo', base + '&mode=salon'
    a, b, tip = T[lang]
    s = s.replace('</style>', CSS + '</style>', 1)
    s = re.sub(r'(<img class="art"[^>]*>)', lambda m: f'<a class="artlink" href="{solo}" aria-label="{tip}">{m.group(1)}</a>\n<div class="cta"><a class="go" href="{solo}">{a}</a><a class="friends" href="{room}">{b}</a></div>', s, count=1)
    s = s.replace(f'<a class="play" href="{base}">', f'<a class="play" href="{solo}">', 1)
    s = s.replace(f'<a class="btn" href="{base}">', f'<a class="btn" href="{solo}">', 1)
    open(f, 'w', encoding='utf-8').write(s); n += 1
print('pages', n)
