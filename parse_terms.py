# -*- coding: utf-8 -*-
"""Parse wound terms docx -> /tmp/wound_terms.json"""
import zipfile, re, json

docx = '/Users/tai7hermes/.hermes/cache/documents/doc_8f84017e4c9e_Wound_Related_Terms_English_Simplified_Traditional_Chinese.docx'
with zipfile.ZipFile(docx) as z:
    xml = z.read('word/document.xml').decode('utf-8')

paras = []
for pm in re.findall(r'<w:p[ >].*?</w:p>', xml, re.S):
    texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', pm)
    paras.append(''.join(texts).strip())

ncells = xml.count('<w:tc>')
print('paragraphs:', len(paras), '| table cells:', ncells)

terms = []
cur_letter = None
buf = []
for t in paras:
    if not t:
        continue
    if re.fullmatch(r'[A-Z]', t):
        cur_letter = t
        buf = []
        continue
    if t in ('English', '简体中文', '繁體中文'):
        continue
    if cur_letter is None:
        continue
    buf.append(t)
    if len(buf) == 3:
        terms.append({'l': cur_letter, 'en': buf[0], 'sc': buf[1], 'tc': buf[2]})
        buf = []

print('terms parsed:', len(terms))
if buf:
    print('WARNING leftover buffer:', buf)
letters = sorted(set(t['l'] for t in terms))
print('letters:', ''.join(letters))
print('first:', terms[0])
print('last:', terms[-1])
with open('/tmp/wound_terms.json', 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False)
print('saved /tmp/wound_terms.json')
