// Builds the published copy of the site in _site/: the same files, with the code shrunk (comments, spaces and long
// local names removed) so phones download and read less. The repository keeps the readable source.
// Run by .github/workflows/pages.yml:  npm i --no-save terser@5.31.6 && node tools/build_site.js
const fs = require('fs'), path = require('path'), { minify } = require('terser');
const ROOT = path.join(__dirname, '..'), OUT = path.join(ROOT, '_site');
const SKIP = new Set(['.git', '.github', 'tools', 'supabase', 'node_modules', '_site', 'package.json', 'package-lock.json']);
const TERSER = { compress:{ passes:1 }, mangle:true, format:{ comments:false, inline_script:true, ascii_only:false } };

function copy(dir, out){
  fs.mkdirSync(out, { recursive:true });
  for (const f of fs.readdirSync(dir)){
    if (SKIP.has(f) || f.endsWith('.md')) continue;
    const a = path.join(dir, f), b = path.join(out, f);
    if (fs.statSync(a).isDirectory()) copy(a, b); else fs.copyFileSync(a, b);
  }
}
// CSS: comments out, each line trimmed (the rules themselves are left as written)
const css = t => t.replace(/\/\*[\s\S]*?\*\//g, '').split('\n').map(l => l.trim()).filter(Boolean).join('\n');

(async () => {
  fs.rmSync(OUT, { recursive:true, force:true });
  copy(ROOT, OUT);
  const before = {}, after = {};
  // the page: every inline script (not the JSON-LD data) and the style block
  let html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8'); before.html = html.length;
  const parts = []; let last = 0;
  const re = /<script(\s[^>]*)?>([\s\S]*?)<\/script>/g; let m;
  while ((m = re.exec(html))){
    const attrs = m[1] || '';
    if (/\bsrc=/.test(attrs) || /ld\+json/.test(attrs) || !m[2].trim()) continue;
    const r = await minify(m[2], TERSER);
    parts.push(html.slice(last, m.index), '<script' + attrs + '>', r.code, '</script>'); last = m.index + m[0].length;
  }
  parts.push(html.slice(last)); html = parts.join('');
  html = html.replace(/<style>([\s\S]*?)<\/style>/g, (_, c) => '<style>' + css(c) + '</style>');
  fs.writeFileSync(path.join(OUT, 'index.html'), html); after.html = html.length;
  // the English table
  const en = fs.readFileSync(path.join(ROOT, 'lib/en.js'), 'utf8'); before.en = en.length;
  const r = await minify(en, TERSER); fs.writeFileSync(path.join(OUT, 'lib/en.js'), r.code); after.en = r.code.length;
  console.log('index.html', before.html, '->', after.html, '| lib/en.js', before.en, '->', after.en);
})().catch(e => { console.error(e); process.exit(1); });
