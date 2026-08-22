# -*- coding: utf-8 -*-
"""Generate terms.html (886-term trilingual glossary) from /tmp/wound_terms.json"""
import json
import re

terms = json.load(open('/tmp/wound_terms.json', encoding='utf-8'))
letters = sorted(set(t['l'] for t in terms))

NAV = '''<nav><ul><li><a href="index.html">首頁</a></li><li><a href="acute.html">急性傷口</a></li><li><a href="chronic.html">慢性傷口</a></li><li><a href="staging.html">分期系統</a></li><li><a href="management.html">治療與警示</a></li><li><a href="dressings.html">敷料中心</a></li></ul>
<ul><li><a href="tools.html">計分工具</a></li><li><a href="burns.html">燒傷面積</a></li><li><a href="decision.html">決策樹</a></li><li><a href="selector.html">敷料選擇器</a></li><li><a href="tetanus.html">破傷風</a></li></ul>
<ul><li><a href="library.html" class="active">指南文獻庫</a></li><li><a href="education.html">教學專區</a></li><li><a href="about.html">關於本站</a></li></ul>
<ul class="pub"><li class="lbl">🩷 民眾傷口衛教</li><li><a href="public_acute.html">常見急性傷口</a></li><li><a href="public_chronic.html">常見慢性傷口</a></li><li><a href="public_warning.html">傷口惡化警訊</a></li><li><a href="public_triage.html">三級就醫警示</a></li></ul></nav>'''

rows = []
for L in letters:
    sub = [t for t in terms if t['l'] == L]
    rows.append(f'<tr class="letter-row" id="letter-{L}"><td colspan="3">{L}</td></tr>')
    for t in sub:
        en = t['en'].replace('&', '&amp;').replace('<', '&lt;')
        sc = t['sc'].replace('&', '&amp;').replace('<', '&lt;')
        tc = t['tc'].replace('&', '&amp;').replace('<', '&lt;')
        rows.append(f'<tr class="term"><td>{en}</td><td>{sc}</td><td>{tc}</td></tr>')

letter_links = ' '.join(f'<a href="#letter-{L}">{L}</a>' for L in letters)

html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>傷口相關術語對照表 | 傷口照護循證指引</title>
<link rel="stylesheet" href="style.css">
<style>
.letterbar{{position:sticky;top:0;background:var(--pale);border:1px solid var(--line);border-radius:10px;padding:8px 12px;margin:12px 0;z-index:5;font-size:.95rem;line-height:2}}
.letterbar a{{display:inline-block;min-width:26px;text-align:center;font-weight:700;border-radius:6px;padding:1px 4px}}
.letterbar a:hover{{background:var(--blue);color:#fff;text-decoration:none}}
.termfilter{{display:flex;align-items:center;gap:8px;background:#fff;border:1.5px solid var(--line);border-radius:10px;padding:8px 14px;margin:12px 0}}
.termfilter input{{flex:1;border:0;outline:0;font-size:.95rem;font-family:inherit;background:transparent;color:var(--dark)}}
#termCount{{font-size:.82rem;color:var(--mid);white-space:nowrap}}
table.terms td:first-child{{font-weight:600;color:var(--navy)}}
tr.letter-row td{{background:var(--navy);color:#fff;font-weight:800;font-size:1.05rem;letter-spacing:.1em}}
@media (prefers-color-scheme: dark){{
  .letterbar{{background:#232a3a;border-color:#39405a}}
  .termfilter{{background:#1e2330;border-color:#39405a}}
  .termfilter input{{color:#dfe3ea}}
}}
</style>
</head>
<body>
<header><div class="brand">🩹 傷口照護循證指引</div></header>
{NAV}
<main>
<div class="crumb">首頁 / <a href="library.html">指南文獻庫</a> / 傷口相關術語對照表</div>
<h1>Wound-Related Terms 傷口相關術語對照表</h1>
<p>英文–簡體中文–繁體中文三語對照索引，共 <b>{len(terms)}</b> 個詞條（臨床名詞、專有名詞、縮寫、分類系統、敷料類別與產品名），依英文字母排序。</p>
<div class="warn">翻譯說明：無可核實官方本地名稱的註冊產品名保留英文，並翻譯其通用描述；產品名稱及上市情況可能因地區而異。</div>

<div class="termfilter">🔎 <input type="search" id="termFilter" placeholder="即時篩選：輸入英文或中文（例如 debridement、清創、藻酸鹽…）" autocomplete="off"><span id="termCount">{len(terms)} 條</span></div>

<div class="letterbar">{letter_links}</div>

<table class="terms" id="termTable">
<tr><th style="width:40%">English</th><th style="width:30%">简体中文</th><th style="width:30%">繁體中文</th></tr>
{chr(10).join(rows)}
</table>

<p class="small">資料來源：使用者提供之三語對照索引（2026-08，886 詞條，重複與大小寫變體已合併）。最後更新：2026-08-26</p>
</main>
<footer>傷口照護循證指引 © 2026 ・ <a href="library.html">回指南文獻庫</a></footer>

<script>
(function(){{
  var input = document.getElementById('termFilter');
  var count = document.getElementById('termCount');
  var rows = Array.prototype.slice.call(document.querySelectorAll('#termTable tr.term'));
  var letterRows = Array.prototype.slice.call(document.querySelectorAll('#termTable tr.letter-row'));
  var total = rows.length;
  function apply(){{
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function(r){{
      var hit = !q || r.textContent.toLowerCase().indexOf(q) >= 0;
      r.style.display = hit ? '' : 'none';
      if (hit) shown++;
    }});
    letterRows.forEach(function(lr){{
      var any = false, n = lr.nextElementSibling;
      while (n && !n.classList.contains('letter-row')) {{
        if (n.style.display !== 'none') {{ any = true; break; }}
        n = n.nextElementSibling;
      }}
      lr.style.display = (any || !q) ? '' : 'none';
    }});
    count.textContent = (q ? shown : total) + ' 條';
  }}
  var timer = null;
  input.addEventListener('input', function(){{ clearTimeout(timer); timer = setTimeout(apply, 120); }});
}})();
</script>
<script src="search-index.js"></script>
<script src="search.js"></script>
</body>
</html>
'''
open('terms.html', 'w', encoding='utf-8').write(html)
print('terms.html written:', len(html)//1024, 'KB,', len(terms), 'terms')
