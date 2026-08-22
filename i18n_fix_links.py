# -*- coding: utf-8 -*-
"""Fix en/ pages: now that ALL 27 pages are translated, rewrite href="../X.html"
to href="X.html" for every translated page X — EXCEPT inside the langsw block
(繁 link must keep ../PAGE) . Same fix for cn/ pages (rebuilt by script already,
but nav there was generated with the full set so verify only)."""
import glob
import re

ALL_PAGES = {'index.html', 'healing.html', 'acute.html', 'chronic.html', 'staging.html',
             'management.html', 'dressing_principles.html', 'dressings.html', 'library.html',
             'tools.html', 'burns.html', 'decision.html', 'selector.html', 'tetanus.html',
             'education.html', 'cases.html', 'quiz.html', 'terms.html', 'updates.html', 'about.html',
             'public_healing.html', 'public_acute.html', 'public_chronic.html',
             'public_dressing_change.html', 'public_warning.html', 'public_triage.html',
             'classification.html'}

LANGSW_RE = re.compile(r'<div class="langsw">.*?</div>', re.S)


def fix_file(path):
    s = open(path, encoding='utf-8').read()
    m = LANGSW_RE.search(s)
    placeholder = '\x00LANGSW\x00'
    langsw = m.group(0) if m else ''
    if m:
        s = s[:m.start()] + placeholder + s[m.end():]

    def repl(mm):
        target = mm.group(1)
        base = target.split('#')[0]
        if base in ALL_PAGES:
            return f'href="{target}"'
        return mm.group(0)

    s = re.sub(r'href="\.\./([^"]+)"', repl, s)
    if m:
        s = s.replace(placeholder, langsw)
    open(path, 'w', encoding='utf-8').write(s)


changed = 0
for f in glob.glob('en/*.html'):
    before = open(f, encoding='utf-8').read()
    fix_file(f)
    after = open(f, encoding='utf-8').read()
    if before != after:
        changed += 1
        n = len(re.findall(r'href="\.\./[a-z_]+\.html', before)) - len(re.findall(r'href="\.\./[a-z_]+\.html', after))
        print(f'{f}: {n} links localized')
print('en/ files changed:', changed)

# verify: no ../X.html links remain outside langsw for translated pages
for f in glob.glob('en/*.html') + glob.glob('cn/*.html'):
    s = open(f, encoding='utf-8').read()
    m = LANGSW_RE.search(s)
    body = s[:m.start()] + s[m.end():] if m else s
    bad = [x for x in re.findall(r'href="\.\./([^"]+\.html[^"]*)"', body) if x.split('#')[0] in ALL_PAGES]
    assert not bad, (f, bad[:5])
print('verified: no stale ../ links to translated pages (outside langsw)')
