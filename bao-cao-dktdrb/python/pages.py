import sys, json, re, pymupdf
pdf, meta, out = sys.argv[1:4]
m = json.load(open(meta))
d = pymupdf.open(pdf)
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
texts = [norm(p.get_text()) for p in d]
res = {}
start = 2  # bo qua bia + muc luc (tim tu trang 3)
def find(s, frm):
    s = norm(s)[:60]
    for i in range(frm, len(texts)):
        if s in texts[i]: return i
    return None
cur = start
for h in m['heads']:
    i = find(h, cur)
    if i is None: print('miss', h); continue
    res['H:' + h] = i + 1; cur = i
# hinh / bang: tim caption "Hình k: cap" sau danh muc
lists_end = res.get('H:I. CÁC BỘ THÔNG SỐ ĐỘNG CƠ ĐƯỢC SỬ DỤNG', 5) - 1
for pre, key in (('Hình', 'figs'), ('Bảng', 'tabs')):
    for k, cap in enumerate(m[key], 1):
        i = find(f'{pre} {k}: {cap}', lists_end)
        if i is None: print('miss', pre, k); continue
        res[f'{pre}{k}'] = i + 1
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=0)
print(len(d), 'pages')
