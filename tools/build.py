#!/usr/bin/env python3
"""Builds content pages: content/<slug>.html -> <slug>/index.html, and regenerates sitemap.xml.
Each content file starts with a JSON block:  <!--meta { "slug": "...", "title": "...", ... } -->
Run: python3 tools/build.py
"""
import json, re, datetime, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://pomodorodial.com'
layout = (ROOT / 'tools' / 'layout.html').read_text(encoding='utf-8')

def esc(s): return html.escape(s, quote=True)

pages = []
for f in sorted((ROOT / 'content').glob('*.html')):
    text = f.read_text(encoding='utf-8')
    m = re.match(r'\s*<!--meta\s*(\{.*?\})\s*-->\s*', text, re.S)
    if not m: raise SystemExit(f'{f}: missing <!--meta {{...}} --> block')
    meta = json.loads(m.group(1)); body = text[m.end():].rstrip() + '\n'
    slug = meta['slug'].strip('/'); url = f'{SITE}/{slug}/'
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
