# -*- coding: utf-8 -*-
"""Align decision.html & selector.html with the streamlined dressing_principles.html:
- selector: add 八字口訣 quick-reference band + 5-step flow alignment; antimicrobial 1–2週; 再評估 2–4週
- decision: result-node links point to dressing_principles.html; date bumps
"""
import re

# ============ selector.html ============
s = open('selector.html', encoding='utf-8').read()

# 1. Add 口訣 key band under the warn banner, linking to the streamlined principles page
old_warn = '<div class="warn">⚠️ 敷料是配角——請先確認病因治療已到位（糖足減壓、靜脈壓迫、動脈重建、壓瘡減壓）。本工具輸出為「類別」建議；品牌例僅供辨識，非優劣排序。</div>'
new_warn = (old_warn + '\n<div class="key">八字口訣（詳<a href="dressing_principles.html">敷料與濕敷換藥</a>）：'
            '<b>乾要保濕・濕要吸收・髒要清創・臭要控菌・深要填塞・痛要不沾・皮膚要保護・缺血先看血流</b>。'
            '選擇順序：先排除嚴重缺血與感染 → 滲液量 → 深度死腔 → 疼痛出血與周邊皮膚 → 頻率與追蹤。</div>')
assert old_warn in s
s = s.replace(old_warn, new_warn)

# 2. Antimicrobial card: align to 1–2 週 re-evaluation (IWGDF/IDSA, streamlined ch.4)
old_ag = "html+=card('限期抗菌敷料（銀／碘／PHMB）','2 週原則：使用後再評估，有效則續用一輪，無效即停換策略。不作常規預防。全身性感染徵象→系統性抗生素（IWGDF/IDSA）。','silver');"
new_ag = "html+=card('限期抗菌敷料（銀／碘／PHMB）','限期使用，1–2 週重新評估：有效則續用一輪，無效即停換策略；不作常規預防。全身性感染徵象→系統性抗生素（IWGDF/IDSA 2023）。','silver');"
assert old_ag in s
s = s.replace(old_ag, new_ag)

# 3. Reassessment note: 2–4 週 window per streamlined guidance
old_re = ("html+='<div class=\"notebox\">📋 <b>再評估</b>：每次換藥觀察滲出/組織/感染變化並調整類別；使用濕紗布者若每日須換 3–4 次仍乾掉或滲漏，"
          "改用高吸收敷料；4 週無進展→重新評估病因與是否切片（<a href=\"decision.html\">決策樹</a>）。健保給付與院內品項請依貴院處方集。</div>';")
new_re = ("html+='<div class=\"notebox\">📋 <b>再評估</b>：每一次換藥都是一次重新評估——觀察滲出/組織/感染變化並調整類別；"
          "使用濕紗布者若每日須換 3–4 次仍乾掉或滲漏，改用高吸收敷料；<b>2–4 週未明顯改善→重新評估血流、感染、壓力、營養、惡性變化與敷料策略</b>"
          "（<a href=\"decision.html\">決策樹</a>／<a href=\"dressing_principles.html\">敷料使用原則</a>）。健保給付與院內品項請依貴院處方集。</div>';")
assert old_re in s
s = s.replace(old_re, new_re)

# 4. footer refs
s = re.sub(r'最後更新：[\d-]+', '最後更新：2026-08-31', s)
open('selector.html', 'w', encoding='utf-8').write(s)
print('selector.html aligned')

# ============ decision.html ============
d = open('decision.html', encoding='utf-8').read()

# 1. venous node: add dressing direction link to principles page
old_v = "links:[['management.html','靜脈治療路徑'],['staging.html','CEAP 分類'],['dressings.html','敷料對照']],"
if old_v in d:
    d = d.replace(old_v, "links:[['management.html','靜脈治療路徑'],['staging.html','CEAP 分類'],['dressing_principles.html','敷料使用原則']],")
    print('decision: venous links updated')
else:
    # fallback: find venous links line
    m = re.search(r"r_venous:.*?links:\[(.*?)\],", d, re.S)
    print('decision venous links present:', bool(m), m.group(1)[:80] if m else '')

# 2. rename link labels for consistency with new page name
d = d.replace("['dressing_principles.html#wetgauze','濕敷換藥原則']", "['dressing_principles.html#wetgauze','濕敷換藥技術']")
d = d.replace("['dressing_principles.html#wetgauze','敷料與濕敷']", "['dressing_principles.html','敷料與濕敷換藥']")

# 3. footer date
d = re.sub(r'最後更新：[\d-]+', '最後更新：2026-08-31', d)
open('decision.html', 'w', encoding='utf-8').write(d)
print('decision.html aligned')

# verify
from html.parser import HTMLParser
for f in ['selector.html', 'decision.html']:
    c = open(f, encoding='utf-8').read()
    HTMLParser().feed(c)
    assert 'dressing_principles.html' in c, f
sx = open('selector.html', encoding='utf-8').read()
for k in ['八字口訣', '1–2 週重新評估', '2–4 週未明顯改善', '每一次換藥都是一次重新評估']:
    assert k in sx, k
dx = open('decision.html', encoding='utf-8').read()
for k in ['濕敷換藥技術', '敷料使用原則']:
    assert k in dx, k
print('both pages verified')
