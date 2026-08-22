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
               'tools.html', 'burns.html', 'decision.html', 'selector.html', 'tetanus.html']

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
            + item('繁', tw, current == 'tw') + '<i>|</i>'
            + item('简', cn, current == 'cn') + '<i>|</i>'
            + item('EN', en, current == 'en')
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
    # protect script blocks? OpenCC only maps CJK; JS strings contain Chinese to convert too (good for tools pages later)
    out = CC.convert(src)
    for a, b in TERM_FIX:
        out = out.replace(a, b)
    out = out.replace('lang="zh-Hant"', 'lang="zh-CN"')
    for a, b in ASSET_REWRITES:
        out = out.replace(a, b)
    out = rewrite_internal_links(out, set(PHASE_PAGES))
    # inject language switcher into header
    out = re.sub(r'(<header><div class="brand">[^<]*</div>)', r'\1' + lang_switcher(page, 'cn'), out, count=1)
    # add disclaimer note about partial translation for non-phase links
    os.makedirs('cn', exist_ok=True)
    open(os.path.join('cn', page), 'w', encoding='utf-8').write(out)
    return len(out)


def inject_switcher_tw(page):
    """Add/refresh language switcher on the TC original page."""
    s = open(page, encoding='utf-8').read()
    s = re.sub(r'<div class="langsw">.*?</div>', '', s, flags=re.S)
    s = re.sub(r'(<header><div class="brand">[^<]*</div>)', r'\1' + lang_switcher(page, 'tw'), s, count=1)
    open(page, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    for p in PHASE_PAGES:
        n = build_cn(p)
        inject_switcher_tw(p)
        print(f'cn/{p} built ({n//1024} KB); switcher injected into {p}')
    print('done')
