#!/usr/bin/env python3
"""Builds content pages: content/<slug>.html -> <slug>/index.html, and regenerates sitemap.xml.
Each content file starts with a JSON block:  <!--meta { "slug": "...", "title": "...", ... } -->
Run: python3 tools/build.py
"""
import json, re, datetime, pathlib, html, hashlib, base64, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://pomodorodial.com'
layout = (ROOT / 'tools' / 'layout.html').read_text(encoding='utf-8')
CHECK = '--check' in sys.argv

# Content Security Policy. index.html has one inline script, allowed by its SHA-256 hash; the hash is recomputed here
# on every build, so run this script (or --check) after editing index.html.
CSP = ("default-src 'self'; script-src 'self' {extra}https://static.cloudflareinsights.com https://challenges.cloudflare.com; "
       "connect-src 'self' https://api.pomodorodial.com https://cloudflareinsights.com https://challenges.cloudflare.com; "
       "frame-src https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
       "manifest-src 'self'; worker-src 'self'; base-uri 'none'; form-action 'self'; object-src 'none'; upgrade-insecure-requests")
CSP_RE = re.compile(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">')
def csp_meta(extra=''): return '<meta http-equiv="Content-Security-Policy" content="%s">' % CSP.format(extra=extra)
def with_csp(text, meta):
    if CSP_RE.search(text): return CSP_RE.sub(meta, text)
    anchor = '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    if anchor not in text: raise SystemExit('viewport meta not found; cannot place the CSP')
    return text.replace(anchor, anchor + meta + '\n', 1)

idx = ROOT / 'index.html'; s = idx.read_text(encoding='utf-8')
a = s.index('<script>\n(() => {') + len('<script>'); b_ = s.index('</script>', a)
digest = base64.b64encode(hashlib.sha256(s[a:b_].encode('utf-8')).digest()).decode()
updated = with_csp(s, csp_meta("'sha256-%s' " % digest))
if updated != s:
    if CHECK: print('index.html: Content-Security-Policy hash is stale. Run: python3 tools/build.py'); sys.exit(1)
    idx.write_text(updated, encoding='utf-8'); print('index.html: CSP hash updated')
else:
    print('index.html: CSP up to date')
if CHECK: sys.exit(0)
layout = with_csp(layout, csp_meta())

def esc(s): return html.escape(s, quote=True)

pages = []
for f in sorted((ROOT / 'content').glob('*.html')):
    text = f.read_text(encoding='utf-8')
    m = re.match(r'\s*<!--meta\s*(\{.*?\})\s*-->\s*', text, re.S)
    if not m: raise SystemExit(f'{f}: missing <!--meta {{...}} --> block')
    meta = json.loads(m.group(1)); body = text[m.end():].rstrip() + '\n'
    slug = meta['slug'].strip('/'); url = f'{SITE}/{slug}/'
    if not re.fullmatch(r'[a-z0-9-]+(/[a-z0-9-]+)*', slug): raise SystemExit(f'{f}: slug {slug!r} may only contain a-z, 0-9 and dashes')
    published = meta.get('published', datetime.date.today().isoformat()); updated = meta.get('updated', published)
    crumb = meta.get('crumb', meta.get('h1', meta['title']))
    ld = [{
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Pomodoro Dial', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': crumb, 'item': url}
        ]
    }]
    if meta.get('type', 'WebPage') == 'Article':
        ld.append({'@type': 'Article', 'headline': meta.get('h1', meta['title']), 'description': meta['description'],
                   'datePublished': published, 'dateModified': updated, 'mainEntityOfPage': url,
                   'image': SITE + '/og-image.png',
                   'author': {'@type': 'Organization', 'name': 'Pomodoro Dial', 'url': SITE + '/about/'},
                   'publisher': {'@type': 'Organization', 'name': 'Pomodoro Dial', 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/icon-512.png'}}})
    else:
        ld.append({'@type': 'WebPage', 'name': meta['title'], 'description': meta['description'], 'url': url, 'dateModified': updated})
    jsonld = json.dumps({'@context': 'https://schema.org', '@graph': ld}, ensure_ascii=False)
    out = layout
    for k, v in {'title': esc(meta['title']), 'description': esc(meta['description']), 'canonical': url,
                 'ogtype': 'article' if meta.get('type') == 'Article' else 'website', 'ogtitle': esc(meta.get('ogtitle', meta.get('h1', meta['title']))),
                 'jsonld': jsonld, 'crumb': esc(crumb), 'body': body}.items():
        out = out.replace('{{' + k + '}}', v)
    dest = ROOT / slug / 'index.html'; dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding='utf-8')
    pages.append((url, updated, meta.get('priority', '0.7')))
    print(f'built /{slug}/  ({len(out)//1024} KB)')

home_mtime = datetime.date.fromtimestamp((ROOT / 'index.html').stat().st_mtime).isoformat()
entries = [(SITE + '/', home_mtime, '1.0')] + pages
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url, mod, pri in entries:
    xml += ['  <url>', f'    <loc>{url}</loc>', f'    <lastmod>{mod}</lastmod>', f'    <priority>{pri}</priority>', '  </url>']
xml.append('</urlset>')
(ROOT / 'sitemap.xml').write_text('\n'.join(xml) + '\n', encoding='utf-8')
print(f'sitemap.xml: {len(entries)} URLs')
