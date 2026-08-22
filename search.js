/* WoundSite 全站搜尋 (方案A: 純前端索引) */
(function(){
  // ---------- inject search bar above <nav> ----------
  var header = document.querySelector('header');
  if (!header) return;
  var bar = document.createElement('div');
  bar.className = 'searchbar';
  bar.innerHTML = '<div class="searchbar-inner">'
    + '<span class="sicon">🔍</span>'
    + '<input type="search" id="siteSearchInput" placeholder="搜尋全站…" autocomplete="off">'
    + '<button id="siteSearchClear" title="清除" style="display:none">✕</button>'
    + '</div>'
    + '<div id="siteSearchResults" class="sresults" style="display:none"></div>';
  header.appendChild(bar);

  var input = document.getElementById('siteSearchInput');
  var clearBtn = document.getElementById('siteSearchClear');
  var box = document.getElementById('siteSearchResults');
  var idx = (typeof SEARCH_INDEX !== 'undefined') ? SEARCH_INDEX : [];

  function esc(s){ return s.replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function hilite(text, terms){
    var out = esc(text);
    terms.forEach(function(t){
      if (!t) return;
      var re = new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
      out = out.replace(re, '<mark>$1</mark>');
    });
    return out;
  }

  function snippet(text, terms, len){
    var low = text.toLowerCase();
    var pos = -1;
    for (var i = 0; i < terms.length; i++){
      pos = low.indexOf(terms[i].toLowerCase());
      if (pos >= 0) break;
    }
    if (pos < 0) pos = 0;
    var start = Math.max(0, pos - Math.floor(len / 3));
    var s = text.slice(start, start + len);
    if (start > 0) s = '…' + s;
    if (start + len < text.length) s += '…';
    return s;
  }

  function search(q){
    var terms = q.trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    var scored = [];
    for (var i = 0; i < idx.length; i++){
      var e = idx[i];
      var hay = (e.h + ' ' + e.x).toLowerCase();
      var score = 0, ok = true;
      for (var j = 0; j < terms.length; j++){
        var t = terms[j].toLowerCase();
        if (hay.indexOf(t) < 0){ ok = false; break; }
        // heading hit weighs more; page-title hit weighs most
        if (e.pt.toLowerCase().indexOf(t) >= 0) score += 6;
        if (e.h.toLowerCase().indexOf(t) >= 0) score += 4;
        score += 1;
      }
      if (ok) scored.push([score, e]);
    }
    scored.sort(function(a, b){ return b[0] - a[0]; });
    return scored.slice(0, 30);
  }

  function render(q){
    var res = search(q);
    var terms = q.trim().split(/\s+/).filter(Boolean);
    if (!q.trim()){ box.style.display = 'none'; box.innerHTML = ''; clearBtn.style.display='none'; return; }
    clearBtn.style.display = 'inline';
    if (!res.length){
      box.innerHTML = '<div class="sr-none">找不到「' + esc(q) + '」的結果。試試其他關鍵字（例如：糖尿病足、WIfI、藻酸鹽、燙傷、破傷風）。</div>';
      box.style.display = 'block';
      return;
    }
    // dedupe: max 2 entries per page+heading
    var seen = {}, html = '<div class="sr-count">共 ' + res.length + ' 筆結果（最多顯示 30 筆）</div>';
    res.forEach(function(pair){
      var e = pair[1];
      var key = e.p + '#' + e.h;
      seen[key] = (seen[key] || 0) + 1;
      if (seen[key] > 1) return;
      html += '<a class="sr-item" href="' + e.p + '">'
        + '<div class="sr-title">' + (e.pub ? '🩷 ' : '') + esc(e.pt)
        + (e.h ? ' <span class="sr-h">› ' + hilite(e.h, terms) + '</span>' : '') + '</div>'
        + '<div class="sr-snip">' + hilite(snippet(e.x, terms, 120), terms) + '</div>'
        + '</a>';
    });
    box.innerHTML = html;
    box.style.display = 'block';
  }

  var timer = null;
  input.addEventListener('input', function(){
    clearTimeout(timer);
    var v = input.value;
    timer = setTimeout(function(){ render(v); }, 150);
  });
  input.addEventListener('keydown', function(ev){
    if (ev.key === 'Escape'){ input.value = ''; render(''); input.blur(); }
    if (ev.key === 'Enter'){
      var first = box.querySelector('a.sr-item');
      if (first) location.href = first.getAttribute('href');
    }
  });
  clearBtn.addEventListener('click', function(){ input.value = ''; render(''); input.focus(); });
  document.addEventListener('click', function(ev){
    if (!bar.contains(ev.target)) box.style.display = 'none';
  });
  input.addEventListener('focus', function(){ if (input.value.trim()) render(input.value); });
})();

// 語言切換器：記錄使用者手動選擇（autolang 之後永久尊重此偏好）
(function(){
  var sw = document.querySelector('.langsw');
  if (!sw) return;
  sw.addEventListener('click', function(ev){
    var a = ev.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var lang = 'tw';
    if (href.indexOf('en/') !== -1) lang = 'en';
    else if (href.indexOf('cn/') !== -1) lang = 'cn';
    try { localStorage.setItem('ws_lang', lang); } catch(e){}
  });
})();
