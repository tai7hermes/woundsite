#!/usr/bin/env python3
"""check_i18n_sync.py — WoundSite 三語版同步檢查（防漂移）

用法：python3 check_i18n_sync.py
在每次繁中主站內容更新後執行；若英/簡版未同步會列出漂移項目並以非零碼結束。

檢查項目：
 1. 頁面覆蓋：root 的每個 *.html 都要有 en/ 與 cn/ 對應頁
 2. 結構簽章：HTML 標籤序列（不含文字）三語必須一致 → 內容區塊增刪未同步會被抓到
 3. 互動答案：data-a 序列與 data-q 題號三語一致（quiz/cases 等）
 4. QB 題庫：quiz.html 的 a: 答案索引序列一致
 5. 資產路徑：en/cn 頁不得引用未加 ../ 的 style.css / search*.js
 6. 語言切換器：三語每頁都要有 langsw 且指向正確對應頁
 7. 最後更新日：root 頁的「最後更新」日期若晚於 en/cn 頁 → 疑似未同步（警告）
"""
import os, re, sys, glob
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_SIG = set()  # 結構簽章豁免頁（如刻意不同結構者）

INLINE_TAGS = {'b', 'i', 'em', 'strong', 'br', 'u', 'sub', 'sup'}  # 行內格式差異視為合法

class TagSig(HTMLParser):
    def __init__(self):
        super().__init__(); self.sig = []
    def handle_starttag(self, tag, attrs):
        if tag not in INLINE_TAGS:
            self.sig.append(tag)
    def handle_endtag(self, tag):
        if tag not in INLINE_TAGS:
            self.sig.append('/' + tag)

def tag_signature(path):
    p = TagSig()
    s = open(path, encoding='utf-8').read()
    # langsw 區塊的 span/a 位置因 active 語言不同而合法差異，比對前剝除
    s = re.sub(r'<div class="langsw">.*?</div>', '', s, flags=re.S)
    p.feed(s)
    return p.sig

def read(path):
    return open(path, encoding='utf-8').read()

def find_date(s):
    m = re.search(r'(?:最後更新|最后更新|Last updated)[：:]?\s*(\d{4}-\d{2}-\d{2})', s)
    return m.group(1) if m else None

def main():
    os.chdir(ROOT)
    pages = sorted(os.path.basename(p) for p in glob.glob('*.html'))
    errors, warns = [], []

    for lang in ('en', 'cn'):
        for f in pages:
            if not os.path.exists(os.path.join(lang, f)):
                errors.append(f'[覆蓋] 缺 {lang}/{f}')

    for f in pages:
        s_root = read(f)
        # langsw on root
        if 'langsw' not in s_root:
            errors.append(f'[切換器] {f} 無 langsw')
        elif f'en/{f}' not in s_root or f'cn/{f}' not in s_root:
            errors.append(f'[切換器] {f} langsw 目標錯誤')
        d_root = find_date(s_root)

        try:
            sig_root = tag_signature(f)
        except Exception as e:
            errors.append(f'[解析] {f}: {e}'); continue

        for lang in ('en', 'cn'):
            lp = os.path.join(lang, f)
            if not os.path.exists(lp):
                continue
            s = read(lp)
            # assets
            for pat in ('href="style.css"', 'src="search.js"', 'src="search-index.js"'):
                if pat in s:
                    errors.append(f'[資產] {lp} 引用未加 ../ 的 {pat}')
            # langsw
            if 'langsw' not in s:
                errors.append(f'[切換器] {lp} 無 langsw')
            elif f'../{f}' not in s:
                errors.append(f'[切換器] {lp} 未指回繁中 ../{f}')
            # structural signature
            if f not in SKIP_SIG:
                try:
                    sig = tag_signature(lp)
                    if sig != sig_root:
                        # find first divergence for readability
                        i = next((k for k, (a, b) in enumerate(zip(sig_root, sig)) if a != b),
                                 min(len(sig_root), len(sig)))
                        errors.append(f'[結構] {lp} 標籤序列與繁中版不一致'
                                      f'（root {len(sig_root)} vs {lang} {len(sig)} 個標籤，'
                                      f'第 {i} 個起分歧）→ 疑似內容未同步')
                except Exception as e:
                    errors.append(f'[解析] {lp}: {e}')
            # interactive answers
            for pat, name in ((r'data-a="(\d)"', 'data-a'), (r'\ba\s*:\s*(\d+)', 'QB a:'),
                              (r'data-q="([^"]+)"', 'data-q')):
                a_root = re.findall(pat, s_root)
                a_lang = re.findall(pat, s)
                if a_root and a_root != a_lang:
                    errors.append(f'[答案] {lp} {name} 序列與繁中版不一致'
                                  f'（{len(a_root)} vs {len(a_lang)}）')
            # last-updated drift
            d = find_date(s)
            if d_root and d and d_root > d:
                warns.append(f'[日期] {f} 繁中 {d_root} 晚於 {lang} 版 {d} → 疑似未同步翻譯')

    print(f'檢查 {len(pages)} 頁 ×3 語言')
    for w in warns:
        print('⚠️ ', w)
    if errors:
        for e in errors:
            print('❌ ', e)
        print(f'\n共 {len(errors)} 項漂移，{len(warns)} 項警告 — 請同步 en/ 與 cn/ 後再推送')
        sys.exit(1)
    print(f'✅ 三語同步 OK（{len(warns)} 項日期警告）')
    sys.exit(0)

if __name__ == '__main__':
    main()
