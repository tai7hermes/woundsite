# -*- coding: utf-8 -*-
"""Build search-index.js for WoundSite (方案A: 自建輕量全文索引).
Scans all *.html pages, extracts sections keyed by headings (h1/h2/h3/summary),
outputs search-index.js with `const SEARCH_INDEX = [...]` for offline file:// use.
Run from ~/WoundSite_MVP:  python3 build_search_index.py
"""
import glob
import json
import re
from html.parser import HTMLParser

PAGE_TITLES = {}
PUB_PAGES = {'public_acute.html', 'public_chronic.html', 'public_warning.html', 'public_triage.html'}
SKIP_FILES = set()

HEADINGS = {'h1', 'h2', 'h3', 'summary'}
SKIP_TAGS = {'script', 'style', 'nav', 'footer', 'header'}


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.skip_depth = 0
        self.cur_heading = ''
        self.cur_tag = None
        self.heading_buf = []
        self.text_buf = []
        self.sections = []  # (heading, text)
        self.title = ''
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        if tag == 'main':
            self.in_main = True
            return
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.in_main and self.skip_depth == 0 and tag in HEADINGS:
            self._flush_section()
            self.cur_tag = tag
            self.heading_buf = []

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'main':
            self._flush_section()
            self.in_main = False
            return
        if tag in SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.in_main and tag in HEADINGS and self.cur_tag == tag:
            self.cur_heading = ' '.join(''.join(self.heading_buf).split())
            self.cur_tag = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if not self.in_main or self.skip_depth:
            return
        if self.cur_tag in HEADINGS:
            self.heading_buf.append(data)
        else:
            self.text_buf.append(data)

    def _flush_section(self):
        text = ' '.join(''.join(self.text_buf).split())
        if text and (self.cur_heading or text):
            self.sections.append((self.cur_heading, text))
        self.text_buf = []


def main():
    entries = []
    for f in sorted(glob.glob('*.html')):
        if f in SKIP_FILES:
            continue
        html = open(f, encoding='utf-8').read()
        ex = Extractor()
        ex.feed(html)
        page_title = ex.title.split('|')[0].strip() or f
        for heading, text in ex.sections:
            # chunk long sections to ~500 chars for snippet quality
            chunks = [text[i:i + 500] for i in range(0, len(text), 500)] or ['']
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 10 and not heading:
                    continue
                entries.append({
                    'p': f,
                    'pt': page_title,
                    'h': heading if i == 0 else heading + '（續）',
                    'x': chunk,
                    'pub': 1 if f in PUB_PAGES else 0,
                })
    js = 'const SEARCH_INDEX = ' + json.dumps(entries, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open('search-index.js', 'w', encoding='utf-8').write(js)
    print(f'search-index.js written: {len(entries)} entries, {len(js)//1024} KB')


if __name__ == '__main__':
    main()
