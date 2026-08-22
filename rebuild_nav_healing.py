# -*- coding: utf-8 -*-
"""Rebuild nav on ALL pages: Row1 adds 癒合原理 after 首頁; pub row adds 傷口癒合 after 濕敷換藥.
Also add updates.html announcements."""
import glob
import re

ROWS = [
    [('index.html', '首頁'), ('healing.html', '癒合原理'), ('acute.html', '急性傷口'), ('chronic.html', '慢性傷口'),
     ('staging.html', '分期系統'), ('management.html', '治療與警示'), ('dressings.html', '敷料與濕敷')],
    [('tools.html', '計分工具'), ('burns.html', '燒傷面積'), ('decision.html', '決策樹'),
     ('selector.html', '敷料選擇器'), ('tetanus.html', '破傷風')],
    [('library.html', '指南文獻庫'), ('education.html', '教學專區'), ('updates.html', '指南更新追蹤'),
     ('about.html', '關於本站')],
]
PUB_ROW = [('public_acute.html', '常見急性傷口'), ('public_chronic.html', '常見慢性傷口'),
           ('public_healing.html', '傷口癒合'), ('public_dressing_change.html', '濕敷換藥'),
           ('public_warning.html', '傷口惡化警訊'), ('public_triage.html', '三級就醫警示')]


def build_nav(active_file):
    rows_html = []
    for row in ROWS:
        items = []
        for href, label in row:
            cls = ' class="active"' if href == active_file else ''
            items.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
        rows_html.append('<ul>' + ''.join(items) + '</ul>')
    items = ['<li class="lbl">🩷 民眾傷口衛教</li>']
    for href, label in PUB_ROW:
        cls = ' class="active"' if href == active_file else ''
        items.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    rows_html.append('<ul class="pub">' + ''.join(items) + '</ul>')
    return '<nav>' + '\n'.join(rows_html) + '</nav>'


for f in glob.glob('*.html'):
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<nav>.*?</nav>', s, re.S)
    if not m:
        print('NO NAV:', f)
        continue
    active = f
    if f in ('quiz.html', 'cases.html'):
        active = 'education.html'
    elif f == 'classification.html':
        active = 'acute.html'
    elif f == 'terms.html':
        active = 'library.html'
    s = s[:m.start()] + build_nav(active) + s[m.end():]
    open(f, 'w', encoding='utf-8').write(s)
print('nav rebuilt on', len(glob.glob('*.html')), 'pages')

# announcements
s = open('updates.html', encoding='utf-8').read()
new_ann = ('<div class="ann"><div class="d">2026-08-29</div><b>新增「傷口癒合原理」雙版本</b>：'
           '專業版（癒合四階段機轉、急慢性生物學差異、TIME/TIMERS 評估、量化追蹤、停滯與異常癒合、轉診訊號、紀錄最小資料集）'
           '置於第一列導覽；民眾版「傷口是怎麼癒合的？」置於粉紅衛教列。</div>\n')
anchor = s.find('<div class="ann">')
s = s[:anchor] + new_ann + s[anchor:]
s = re.sub(r'最後更新：[\d-]+', '最後更新：2026-08-29', s)
open('updates.html', 'w', encoding='utf-8').write(s)
print('announcement added')

# verify
from html.parser import HTMLParser
expected_row1 = ['index.html', 'healing.html', 'acute.html', 'chronic.html', 'staging.html', 'management.html', 'dressings.html']
expected_pub = ['public_acute.html', 'public_chronic.html', 'public_healing.html', 'public_dressing_change.html', 'public_warning.html', 'public_triage.html']
for f in sorted(glob.glob('*.html')):
    c = open(f, encoding='utf-8').read()
    HTMLParser().feed(c)
    nav = re.search(r'<nav>(.*?)</nav>', c, re.S).group(1)
    uls = re.findall(r'<ul[^>]*>(.*?)</ul>', nav, re.S)
    assert len(uls) == 4, (f, len(uls))
    assert re.findall(r'href="([^"]+)"', uls[0]) == expected_row1, (f, 'row1')
    assert re.findall(r'href="([^"]+)"', uls[3]) == expected_pub, (f, 'pub')
print('all pages verified: row1 has 癒合原理, pub row has 傷口癒合')
