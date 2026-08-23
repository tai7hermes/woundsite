# -*- coding: utf-8 -*-
"""Build zh-CN (simplified) versions of Phase A pages into cn/ using OpenCC tw2sp
+ medical term fixes + asset path rewrite + lang attr + language switcher.
Usage: python3 i18n_build_cn.py  (run from ~/WoundSite_MVP)
"""
import os
import re
from opencc import OpenCC

CC = OpenCC('tw2sp')

PHASE_PAGES = ['index.html', 'healing.html', 'acute.html', 'chronic.html', 'staging.html',
               'management.html', 'dressing_principles.html', 'dressings.html', 'library.html',
               'tools.html', 'burns.html', 'decision.html', 'selector.html', 'tetanus.html',
               'education.html', 'cases.html', 'quiz.html', 'terms.html', 'updates.html', 'about.html',
               'public_healing.html', 'public_acute.html', 'public_chronic.html',
               'public_dressing_change.html', 'public_warning.html', 'public_triage.html',
               'classification.html']

# Post-OpenCC medical/term corrections (TW->CN clinical usage), applied on simplified text
TERM_FIX = [
    ('循证指引', '循证指南'),
    ('指引', '指南'),
    ('敷料与湿敷换药', '敷料与湿敷换药'),  # keep
    ('压疮', '压疮'),
    ('压力性损伤', '压力性损伤'),
    ('矽胶', '硅胶'),
    ('矽膠', '硅胶'),
    ('硅酮', '硅酮'),
    ('壹', '一'),
]

ASSET_REWRITES = [
    ('href="style.css"', 'href="../style.css"'),
    ('src="search-index.js"', 'src="../search-index.js"'),
    ('src="search.js"', 'src="../search.js"'),
    ('src="images/', 'src="../images/'),
    ('href="images/', 'href="../images/'),
    ('href="cards/', 'href="../cards/'),
]

# Language-specific image variants: TC filename -> SC filename (applied only in cn/ build)
IMG_LANG_SWAP = [
    ('four_phases_tw.webp', 'four_phases_cn.webp'),
    ('dfu_edu_tw.webp', 'dfu_edu_cn.webp'),
    ('pressure_edu_tw.webp', 'pressure_edu_cn.webp'),
    ('arterial_edu_tw.webp', 'arterial_edu_cn.webp'),
    ('venous_edu_tw.webp', 'venous_edu_cn.webp'),
    ('radiation_edu_tw.webp', 'radiation_edu_cn.webp'),
    ('malignant_edu_tw.webp', 'malignant_edu_cn.webp'),
    ('dressing_select_tw.webp', 'dressing_select_cn.webp'),
]

SITE = 'https://wound7.com'


def hreflang_block(page):
    """4 alternate links per Google i18n spec; x-default -> TC main site."""
    root = '' if page != 'index.html' else ''
    tw = f'{SITE}/{page}' if page != 'index.html' else f'{SITE}/'
    en = f'{SITE}/en/{page}' if page != 'index.html' else f'{SITE}/en/'
    cn = f'{SITE}/cn/{page}' if page != 'index.html' else f'{SITE}/cn/'
    return (f'<link rel="alternate" hreflang="zh-Hant" href="{tw}">\n'
            f'<link rel="alternate" hreflang="zh-Hans" href="{cn}">\n'
            f'<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{tw}">')


def inject_hreflang(html, page):
    """Remove old hreflang lines, insert fresh block before </head>."""
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', html)
    return html.replace('</head>', hreflang_block(page) + '\n</head>', 1)


def lang_switcher(page, current):
    """current in {'tw','cn','en'}; page like 'acute.html'"""
    tw = f'../{page}' if current != 'tw' else page
    cn = f'cn/{page}' if current == 'tw' else (page if current == 'cn' else f'../cn/{page}')
    en = f'en/{page}' if current == 'tw' else (page if current == 'en' else f'../en/{page}')
    def item(label, href, active):
        if active:
            return f'<span class="active">{label}</span>'
        return f'<a href="{href}">{label}</a>'
    return ('<div class="langsw">'
            + item('EN', en, current == 'en') + '<i>|</i>'
            + item('繁', tw, current == 'tw') + '<i>|</i>'
            + item('简', cn, current == 'cn')
            + '</div>')


def rewrite_internal_links(html, phase_set):
    """Inside cn/: links to phase pages stay relative (same dir); others go up to TC root."""
    def repl(m):
        href = m.group(1)
        if href.startswith(('http', '#', 'mailto', '../')):
            return m.group(0)
        base = href.split('#')[0]
        if base in phase_set or base == '':
            return m.group(0)
        return f'href="../{href}"'
    return re.sub(r'href="([^"]+)"', repl, html)


def build_cn(page):
    src = open(page, encoding='utf-8').read()
    # strip the root-only auto-language-redirect script (must not propagate to cn/)
    src = re.sub(r'<script id="autolang">.*?</script>\n?', '', src, flags=re.S)
    # protect script blocks? OpenCC only maps CJK; JS strings contain Chinese to convert too (good for tools pages later)
    out = CC.convert(src)
    for a, b in TERM_FIX:
        out = out.replace(a, b)
    out = out.replace('lang="zh-Hant"', 'lang="zh-CN"')
    for a, b in ASSET_REWRITES:
        out = out.replace(a, b)
    for a, b in IMG_LANG_SWAP:
        out = out.replace(a, b)
    out = rewrite_internal_links(out, set(PHASE_PAGES))
    # remove any switcher copied from the TC source, then inject the cn one
    out = re.sub(r'<div class="langsw">.*?</div>', '', out, flags=re.S)
    out = re.sub(r'(<header><div class="brand">[^<]*</div>)', r'\1' + lang_switcher(page, 'cn'), out, count=1)
    out = inject_hreflang(out, page)
    # add disclaimer note about partial translation for non-phase links
    os.makedirs('cn', exist_ok=True)
    open(os.path.join('cn', page), 'w', encoding='utf-8').write(out)
    return len(out)


def inject_switcher_tw(page):
    """Add/refresh language switcher + hreflang on the TC original page."""
    s = open(page, encoding='utf-8').read()
    s = re.sub(r'<div class="langsw">.*?</div>', '', s, flags=re.S)
    s = re.sub(r'(<header><div class="brand">[^<]*</div>)', r'\1' + lang_switcher(page, 'tw'), s, count=1)
    s = inject_hreflang(s, page)
    open(page, 'w', encoding='utf-8').write(s)


def inject_hreflang_en(page):
    """en/ pages are hand-translated; only refresh their hreflang block."""
    p = os.path.join('en', page)
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8').read()
    open(p, 'w', encoding='utf-8').write(inject_hreflang(s, page))


def write_sitemap():
    urls = []
    for page in PHASE_PAGES:
        for prefix in ('', 'en/', 'cn/'):
            loc = f'{SITE}/{prefix}' if page == 'index.html' else f'{SITE}/{prefix}{page}'
            urls.append(f'  <url><loc>{loc}</loc></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(urls) + '\n</urlset>\n')
    open('sitemap.xml', 'w', encoding='utf-8').write(xml)
    return len(urls)


if __name__ == '__main__':
    for p in PHASE_PAGES:
        n = build_cn(p)
        inject_switcher_tw(p)
        inject_hreflang_en(p)
        print(f'cn/{p} built ({n//1024} KB); switcher+hreflang injected into {p} & en/{p}')
    print(f'sitemap.xml: {write_sitemap()} URLs')
    print('done')
