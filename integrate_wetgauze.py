# -*- coding: utf-8 -*-
"""Integrate wet gauze principles into management/decision/selector pages."""
import re

# ============ 1. management.html ============
s = open('management.html', encoding='utf-8').read()

old_row = '<tr><td>機械（濕乾紗布/沖洗/單絲纖維墊）</td><td>表淺腐肉</td><td>濕乾紗布疼痛且非選擇性</td></tr>'
new_rows = ('<tr><td>濕敷輔助自溶（濕潤紗布 wet-to-moist）</td><td>薄層、柔軟、鬆散腐肉之短期軟化</td>'
            '<td>擰至濕潤不滴水、乾燥前更換、腔洞鬆填；缺血性乾焦痂禁用；1–2 週無進展即轉換策略'
            '（詳<a href="dressings.html#wetgauze">換藥技術</a>）</td></tr>\n'
            '<tr><td>機械（沖洗/單絲纖維墊）</td><td>表淺腐肉</td>'
            '<td><b>wet-to-dry（紗布乾燥後硬撕）不建議常規使用</b>——非選擇性、疼痛、傷及肉芽與新生上皮</td></tr>')
assert old_row in s, 'mech row missing'
s = s.replace(old_row, new_rows)

old_key = '<div class="key">臨床網站最重要的邏輯：先確認血流與病因，再決定清創、壓迫、減壓、抗感染或免疫治療；進階敷料屬於輔助措施，不能取代病因治療。</div>'
new_key = (old_key + '\n<div class="warn"><b>濕敷換藥提醒</b>：濕潤紗布（wet-to-moist）僅適合在血流確認後，'
           '對薄層鬆散腐肉做「短期」輔助自溶清創；<b>缺血性乾焦痂不濕敷</b>、腔洞不塞緊、紗布黏住先浸濕再取。'
           '每日需換 3–4 次仍乾掉或滲漏，代表應改用其他敷料（<a href="dressings.html#wetgauze">完整原則</a>）。</div>')
assert s.count(old_key) >= 1
s = s.replace(old_key, new_key, 1)
s = re.sub(r'最後更新：[\d-]+', '最後更新：2026-08-28', s)
open('management.html', 'w', encoding='utf-8').write(s)
print('management.html updated')

# ============ 2. decision.html ============
d = open('decision.html', encoding='utf-8').read()

pairs = [
    ("核心治療：減壓（不可被敷料取代）＋清創＋感染控制；標準照護最佳化後才考慮進階治療。'",
     "核心治療：減壓（不可被敷料取代）＋清創＋感染控制；標準照護最佳化後才考慮進階治療。薄層鬆散腐肉可短期濕敷（wet-to-moist）輔助自溶——先確認血流，勿用 wet-to-dry。'"),
    ("灌流未恢復前：穩定乾性壞死保持乾燥保護、勿積極清創 → 避免不當壓迫。'",
     "灌流未恢復前：穩定乾性壞死保持乾燥保護、勿積極清創、勿濕敷軟化 → 避免不當壓迫。'"),
    ("依分期與滲出選敷料（見對照表）→ 大面積 Stage 3–4 備妥後考慮 NPWT。'",
     "依分期與滲出選敷料（見對照表）；少量鬆散腐肉可短期濕敷輔助自溶（乾燥前更換、勿塞緊）→ 大面積 Stage 3–4 備妥後考慮 NPWT。'"),
    ("links:[['management.html','糖足治療路徑'],['tools.html','SINBAD／WIfI 計分器'],['staging.html','分期系統']],",
     "links:[['management.html','糖足治療路徑'],['tools.html','SINBAD／WIfI 計分器'],['dressings.html#wetgauze','濕敷換藥原則']],"),
    ("links:[['staging.html','NPIAP 分期'],['management.html','壓瘡治療路徑'],['dressings.html','分期×敷料對照']],",
     "links:[['staging.html','NPIAP 分期'],['management.html','壓瘡治療路徑'],['dressings.html#wetgauze','敷料與濕敷']],"),
]
for old, new in pairs:
    assert old in d, old[:40]
    d = d.replace(old, new)
d = re.sub(r'最後更新：[\d-]+', '最後更新：2026-08-28', d)
open('decision.html', 'w', encoding='utf-8').write(d)
print('decision.html updated')

# ============ 3. selector.html ============
x = open('selector.html', encoding='utf-8').read()

# 3a. strengthen hydrogel/necrotic advice with wet-to-moist option
old_hydro = "html+=card('水膠 Hydrogel','乾燥壞死/腐肉：補水促自溶清創（缺血未排除前禁用）。','hydrogel',true);"
new_hydro = ("html+=card('水膠 Hydrogel 或 濕潤紗布（wet-to-moist）','乾燥壞死/腐肉：補水促自溶清創（缺血未排除前禁用）。"
             "濕敷限短期：擰至濕潤不滴水、乾燥前更換、勿用 wet-to-dry 硬撕。','hydrogel',true);")
assert old_hydro in x
x = x.replace(old_hydro, new_hydro)

# 3b. slough note: add wet gauze duration warning to necro note
old_note = "html+='<div class=\"notebox\">💡 黑色壞死的主要處置是「清創」（尖銳/自溶/酵素…見<a href=\"management.html\">清創決策</a>）；敷料是配合清創策略選的。</div>';"
new_note = ("html+='<div class=\"notebox\">💡 黑色壞死的主要處置是「清創」（尖銳/自溶/酵素…見<a href=\"management.html\">清創決策</a>）；"
            "敷料是配合清創策略選的。濕敷僅適合薄層鬆散腐肉短期軟化，厚硬壞死單靠濕紗布不足（<a href=\"dressings.html#wetgauze\">濕敷原則</a>）。</div>';")
assert old_note in x
x = x.replace(old_note, new_note)

# 3c. deep cavity packing: reinforce loose packing rule
old_pack = "html+=card('腔隙填充：藻酸鹽繩／凝膠纖維帶','鬆填勿塞緊；需可完整取出（記錄填入數量）。','ropes');"
new_pack = ("html+=card('腔隙填充：藻酸鹽繩／凝膠纖維帶（或依醫囑濕紗布鬆填）','鬆填勿塞緊；需可完整取出（記錄填入數量）；"
            "勿盲目填入看不到底部的竇道。','ropes');")
assert old_pack in x
x = x.replace(old_pack, new_pack)

# 3d. final reassessment note: add frequency-based switching rule
old_re = "html+='<div class=\"notebox\">📋 <b>再評估</b>：每次換藥觀察滲出/組織/感染變化並調整類別；4 週無進展→重新評估病因與是否切片（<a href=\"decision.html\">決策樹</a>）。健保給付與院內品項請依貴院處方集。</div>';"
new_re = ("html+='<div class=\"notebox\">📋 <b>再評估</b>：每次換藥觀察滲出/組織/感染變化並調整類別；"
          "使用濕紗布者若每日須換 3–4 次仍乾掉或滲漏，改用高吸收敷料；4 週無進展→重新評估病因與是否切片"
          "（<a href=\"decision.html\">決策樹</a>）。健保給付與院內品項請依貴院處方集。</div>';")
assert old_re in x
x = x.replace(old_re, new_re)

x = re.sub(r'最後更新：[\d-]+', '最後更新：2026-08-28', x)
open('selector.html', 'w', encoding='utf-8').write(x)
print('selector.html updated')

# verify all
from html.parser import HTMLParser
for f in ['management.html', 'decision.html', 'selector.html']:
    c = open(f, encoding='utf-8').read()
    HTMLParser().feed(c)
    assert 'wetgauze' in c, f
print('all 3 pages verified with wetgauze links')
