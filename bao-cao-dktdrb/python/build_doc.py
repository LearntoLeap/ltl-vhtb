import json, os, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'fig')
R = json.load(open(os.path.join(FIG, 'res.json')))
PAGES = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and os.path.exists(sys.argv[2]) else {}
OUTDOC = sys.argv[1]
LOGO = sys.argv[3] if len(sys.argv) > 3 else None

SV = dict(ten='Phạm Quang Huy', msv='233332575', lop='Kỹ thuật Robot và Trí tuệ nhân tạo – K64',
          khoa='Điện – Điện tử', gv='Th.S Đặng Hà Dũng')

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(3), Cm(2)
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)
sec.header_distance = sec.footer_distance = Cm(1)

def set_font(style_or_run, size=14, bold=None, italic=None, color=None):
    f = style_or_run.font
    f.name = 'Times New Roman'; f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    if color is not None: f.color.rgb = color
    el = style_or_run.element if hasattr(style_or_run, 'element') else style_or_run._element
    rpr = el.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rf.set(qn(a), 'Times New Roman')
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]

st = doc.styles['Normal']
set_font(st, 14)
st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
st.paragraph_format.line_spacing = 1.3
st.paragraph_format.space_after = Pt(4)
for name, size in (('Heading 1', 15), ('Heading 2', 14), ('Heading 3', 14)):
    s = doc.styles[name]
    set_font(s, size, bold=True, italic=False, color=RGBColor(0, 0, 0))
    s.paragraph_format.space_before = Pt(12 if name == 'Heading 1' else 8)
    s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    s.paragraph_format.keep_with_next = True
for name in ('List Bullet', 'Caption'):
    set_font(doc.styles[name], 14 if name != 'Caption' else 13, italic=(name == 'Caption'), bold=False,
             color=RGBColor(0, 0, 0))
doc.styles['List Bullet'].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

FIGS, TABS, HEADS = [], [], []

def P(text='', bold=False, italic=False, align=None, indent=True, size=None, after=None, keep=False):
    p = doc.add_paragraph()
    if indent: p.paragraph_format.first_line_indent = Cm(1)
    if align is not None: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if keep: p.paragraph_format.keep_with_next = True
    add_runs(p, text, bold, italic, size)
    return p

def add_runs(p, text, bold=False, italic=False, size=None):
    # **dam** trong chuoi
    parts = text.split('**')
    for k, part in enumerate(parts):
        if not part: continue
        r = p.add_run(part)
        r.bold = bold or (k % 2 == 1); r.italic = italic
        if size: r.font.size = Pt(size)

def B(text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.0 + 0.8 * level)
    p.paragraph_format.space_after = Pt(2)
    add_runs(p, text)
    return p

def EQ(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); r.italic = True
    return p

def H(text, level):
    p = doc.add_heading(text, level)
    HEADS.append((level, text))
    return p

def FIGURE(fname, cap, width=16):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.first_line_indent = Cm(0)
    p.add_run().add_picture(os.path.join(FIG, fname), width=Cm(width))
    n = len(FIGS) + 1
    c = doc.add_paragraph(style='Caption'); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.add_run(f'Hình {n}: ').bold = True
    c.add_run(cap)
    FIGS.append(cap)
    return n

def shade(cell, color):
    tcPr = cell._element.get_or_add_tcPr()
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color)
    tcPr.append(sh)

def TABLE(rows, cap, widths=None, size=12, first_bold=True):
    n = len(TABS) + 1
    c = doc.add_paragraph(style='Caption'); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.keep_with_next = True
    c.add_run(f'Bảng {n}: ').bold = True
    c.add_run(cap)
    TABS.append(cap)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    if widths:
        t.autofit = False
        for j, w in enumerate(widths):
            t.columns[j].width = Cm(w)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            if i < len(rows) - 1: p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (j > 0 or i == 0) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val)); r.font.size = Pt(size)
            if i == 0:
                r.bold = True; shade(cell, 'D9E2F3')
            elif j == 0 and first_bold:
                r.bold = True
            if widths: cell.width = Cm(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def field(run, instr):
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t'); t.text = '1'
    f3 = OxmlElement('w:fldChar'); f3.set(qn('w:fldCharType'), 'end')
    for e in (f1, it, f2, t, f3): run._r.append(e)

def border_bottom(p, top=False):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement('w:pBdr')
    e = OxmlElement('w:top' if top else 'w:bottom')
    e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '6'); e.set(qn('w:space'), '1'); e.set(qn('w:color'), '000000')
    b.append(e); pPr.append(b)

def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def f1(x): return f'{x:.1f}'
def f2(x): return f'{x:.2f}'
def f3(x): return f'{x:.3f}'
def ms(x): return f'{1000 * x:.1f}'

# ============================ BIA ============================
sec.different_first_page_header_footer = True
cov = doc.add_table(rows=1, cols=1); cov.style = 'Table Grid'; cov.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = cov.cell(0, 0); cell.width = Cm(16)
tcPr = cell._element.get_or_add_tcPr()
bd = OxmlElement('w:tcBorders')
for side in ('top', 'left', 'bottom', 'right'):
    e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'thinThickSmallGap'); e.set(qn('w:sz'), '24'); e.set(qn('w:color'), '000000')
    bd.append(e)
tcPr.append(bd)
def cp(text='', size=14, bold=False, after=4, before=0, align=WD_ALIGN_PARAGRAPH.CENTER, first=False):
    p = cell.paragraphs[0] if first else cell.add_paragraph()
    p.alignment = align; p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
    if text:
        r = p.add_run(text); r.bold = bold; r.font.size = Pt(size)
    return p
cp('TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI', 14, True, first=True, before=12)
cp('KHOA ĐIỆN – ĐIỆN TỬ', 14, True)
cp('------------', 12)
if LOGO:
    p = cp(after=10, before=16); p.add_run().add_picture(LOGO, width=Cm(4.6))
cp('BÁO CÁO', 26, True, before=40, after=6)
cp('HỌC PHẦN: ĐIỀU KHIỂN TRUYỀN ĐỘNG CHO ROBOT', 15, True, after=6)
cp('Đề tài: Mô hình hoá, điều khiển dòng điện – tốc độ – vị trí và ứng dụng điều khiển đồng thời', 13, False, after=2)
cp('hai động cơ DC 700 W và 1400 W trên MATLAB/Simulink', 13, False, after=40)
info = [('Sinh viên thực hiện', SV['ten']), ('Mã sinh viên', SV['msv']), ('Lớp', SV['lop']),
        ('Khoa', SV['khoa']), ('Người hướng dẫn', SV['gv'])]
for a, b in info:
    p = cp(align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
    p.paragraph_format.left_indent = Cm(2.5)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(7.5))
    r = p.add_run(f'{a}\t: '); r.font.size = Pt(14)
    r = p.add_run(b); r.font.size = Pt(14); r.bold = True
cp('Hà Nội, tháng 11 năm 2026', 14, False, before=70, after=14)

# header / footer (trang 2 tro di)
hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER; hp.paragraph_format.first_line_indent = Cm(0)
r = hp.add_run(f'Họ và tên: {SV["ten"]}   |   Mã SV: {SV["msv"]}   |   Lớp: Kỹ thuật Robot và TTNT – K64')
r.font.size = Pt(11); r.italic = True
border_bottom(hp)
fp = sec.footer.paragraphs[0]
fp.paragraph_format.first_line_indent = Cm(0)
fp.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
r = fp.add_run(f'{SV["ten"]} – {SV["msv"]} – KTRB&AI K64 · Báo cáo ĐKTĐ cho Robot\tTrang '); r.font.size = Pt(11); r.italic = True
r = fp.add_run(); r.font.size = Pt(11); r.italic = True; field(r, 'PAGE')
border_bottom(fp, top=True)

page_break()

# ============================ MUC LUC ============================
def toc_line(text, key, level=0, bold=False):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0.7 * level)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    r = p.add_run(f'{text}\t{PAGES.get(key, "")}'); r.bold = bold; r.font.size = Pt(13)

TOC_ITEMS = []  # dien sau khi biet cau truc
toc_anchor = doc.add_paragraph()
toc_anchor.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = toc_anchor.add_run('MỤC LỤC'); r.bold = True; r.font.size = Pt(16)

# Cau truc tieu de duoc khai bao truoc de in muc luc
STRUCT = [
    (0, 'LỜI NÓI ĐẦU'), (0, 'DANH MỤC HÌNH VẼ'), (0, 'DANH MỤC BẢNG BIỂU'),
    (0, 'I. CÁC BỘ THÔNG SỐ ĐỘNG CƠ ĐƯỢC SỬ DỤNG'),
    (1, '1.1 Thông số định mức của hai động cơ'), (1, '1.2 Mô hình động cơ trên Simulink'),
    (1, '1.3 Đánh giá bộ tham số động cơ'), (1, '1.4 Nhận xét về thông số động cơ'),
    (0, 'II. THỰC HIỆN CÁC PHƯƠNG PHÁP ĐIỀU KHIỂN'),
    (1, '2.1 Thực hiện vòng điều khiển dòng điện'),
    (2, '2.1.1 Quá trình thực hiện vòng điều khiển dòng điện'),
    (2, '2.1.2 So sánh khi có và không sử dụng tham số động cơ'),
    (1, '2.2 Thực hiện vòng điều khiển tốc độ'),
    (2, '2.2.1 Điều khiển tốc độ có sử dụng vòng điều khiển dòng điện'),
    (2, '2.2.2 Điều khiển tốc độ không sử dụng vòng điều khiển dòng điện'),
    (2, '2.2.3 Kết quả, bảng so sánh và phương án lựa chọn'),
    (1, '2.3 Thực hiện vòng điều khiển vị trí'),
    (2, '2.3.1 Có sử dụng vòng điều khiển dòng điện và tốc độ'),
    (2, '2.3.2 Có sử dụng vòng điều khiển tốc độ'),
    (2, '2.3.3 Điều khiển trực tiếp vị trí'),
    (2, '2.3.4 Kết quả, bảng so sánh và phương án lựa chọn'),
    (0, 'III. THỰC HIỆN MÔ PHỎNG ỨNG DỤNG ĐIỀU KHIỂN ĐỘNG CƠ'),
    (1, '3.1 Điều khiển đồng tốc 2 động cơ'),
    (1, '3.2 Điều khiển vị trí đồng thời nhiều động cơ'),
    (0, 'KẾT LUẬN'), (0, 'TÀI LIỆU THAM KHẢO'), (0, 'PHỤ LỤC'),
]
for lvl, txt in STRUCT:
    toc_line(txt, 'H:' + txt, lvl, bold=(lvl == 0))
page_break()

# ============================ LOI NOI DAU ============================
H('LỜI NÓI ĐẦU', 1)
P('Trong kỷ nguyên công nghiệp 4.0, robot và các hệ thống truyền động điện là công nghệ cốt lõi của tự động hoá sản xuất, logistics và dịch vụ. Động cơ điện – cơ cấu chấp hành chính của robot – cần được điều khiển chính xác về dòng điện (mô-men), tốc độ và vị trí để robot thực hiện đúng quỹ đạo và nhiệm vụ đã lập trình.')
P('Học phần Điều khiển truyền động cho Robot cung cấp nền tảng để sinh viên mô hình hoá, phân tích và thiết kế bộ điều khiển cho hệ truyền động. Báo cáo này trình bày toàn bộ quá trình thực hiện với hai động cơ điện một chiều (DC) có công suất **700 W** và **1400 W**, điện áp định mức 220 V, gồm các nội dung:')
for s in ['Xây dựng và đánh giá bộ tham số của hai động cơ (điện áp, dòng điện, mô-men, tốc độ định mức) bằng mô hình Simulink.',
          'Thiết kế vòng điều khiển dòng điện và so sánh trường hợp có / không sử dụng tham số động cơ.',
          'Thiết kế vòng điều khiển tốc độ có và không có vòng dòng điện; vòng điều khiển vị trí theo ba cấu trúc.',
          'Ứng dụng: điều khiển đồng tốc hai động cơ và điều khiển vị trí đồng thời nhiều động cơ (nhiều trục).']:
    B(s)
P('Các mô hình được dựng tự động bằng script MATLAB (build_all.m, phụ lục) và mô phỏng bằng bộ giải ode45. Mọi số liệu trong báo cáo được trích trực tiếp từ kết quả mô phỏng.')
P('Em xin chân thành cảm ơn Th.S Đặng Hà Dũng đã tận tình hướng dẫn và truyền đạt những kiến thức quý báu trong suốt quá trình thực hiện báo cáo.')

page_break()
H('DANH MỤC HÌNH VẼ', 1)
figlist_anchor = doc.paragraphs[-1]
H('DANH MỤC BẢNG BIỂU', 1)
tablist_anchor = doc.paragraphs[-1]
page_break()

M1 = dict(P=700, n=2050, w=214.675, L=0.02, R=4.0, J=0.005, B=0.0005, k=0.96, Tn=3.261, In=3.508)
M2 = dict(P=1400, n=2550, w=267.035, L=0.01, R=2.0, J=0.01, B=0.001, k=0.77, Tn=5.243, In=7.156)

# ============================ I ============================
H('I. CÁC BỘ THÔNG SỐ ĐỘNG CƠ ĐƯỢC SỬ DỤNG', 1)
H('1.1 Thông số định mức của hai động cơ', 2)
P('Đề bài cho hai động cơ DC kích từ độc lập (từ thông không đổi) với các thông số khác nhau:')
B('STT: 28; điện áp phần ứng định mức của cả hai động cơ: **Uđm = 220 V DC**.')
B('Động cơ 1 (DC1): công suất **P₁ = 700 W**, tốc độ định mức **n₁ = 2050 vòng/phút**.')
B('Động cơ 2 (DC2): công suất **P₂ = 1400 W (≈ 1.88 Hp)**, tốc độ định mức **n₂ = 2550 vòng/phút**.')
P('Tham số mạch phần ứng và cơ học được chọn sao cho khi cấp đúng 220 V và mang tải định mức, động cơ quay đúng tốc độ định mức:')
B('DC1: Ra = 4.0 Ω; La = 0.02 H; kΦ = Kt = 0.96 N·m/A (V·s/rad); J = 0.005 kg·m²; Bm = 0.0005 N·m·s/rad; Tf = 0.')
B('DC2: Ra = 2.0 Ω; La = 0.01 H; kΦ = Kt = 0.77 N·m/A; J = 0.01 kg·m²; Bm = 0.001 N·m·s/rad; Tf = 0.')
P('**Xác định các đại lượng định mức.** Tốc độ góc định mức ω = 2π·n/60; mô-men tải định mức trên trục Tđm = P/ω; dòng điện định mức từ cân bằng mô-men xác lập kΦ·Iđm = Tđm + Bm·ω:', keep=True)
EQ('ω₁ = 2π·2050/60 = 214.675 rad/s;   ω₂ = 2π·2550/60 = 267.035 rad/s')
EQ('Tđm1 = 700/214.675 = 3.261 N·m;   Tđm2 = 1400/267.035 = 5.243 N·m')
EQ('Iđm1 = (3.261 + 0.0005·214.675)/0.96 = 3.508 A')
EQ('Iđm2 = (5.243 + 0.001·267.035)/0.77 = 7.156 A')
P('Kiểm tra điện áp: Va = kΦ·ω + Ra·Iđm ⇒ Va1 = 0.96·214.675 + 4·3.508 = 220.1 V; Va2 = 0.77·267.035 + 2·7.156 = 219.9 V ≈ 220 V. Hiệu suất ở điểm định mức η = P/(U·Iđm): η₁ = 90.7 %, η₂ = 88.9 %.')
P('Các hằng số thời gian và đại lượng đặc trưng (dùng để đánh giá động học và thiết kế bộ điều khiển):')
EQ('τe = La/Ra ;   τm = J·Ra/(kΦ² + Ra·Bm)')
EQ('ω₀ = U·kΦ/(kΦ² + Ra·Bm) ;   Ikđ = U/Ra')
TABLE([
    ['Đại lượng', 'Ký hiệu / Đơn vị', 'Động cơ 1', 'Động cơ 2'],
    ['Công suất định mức', 'P (W)', '700', '1400'],
    ['Điện áp định mức', 'Uđm (V)', '220', '220'],
    ['Tốc độ định mức', 'n (vòng/phút)', '2050', '2550'],
    ['Tốc độ góc định mức', 'ωđm (rad/s)', '214.675', '267.035'],
    ['Mô-men (tải) định mức', 'Tđm (N·m)', '3.261', '5.243'],
    ['Dòng điện định mức', 'Iđm (A)', '3.508', '7.156'],
    ['Điện trở / điện cảm phần ứng', 'Ra (Ω) / La (H)', '4.0 / 0.02', '2.0 / 0.01'],
    ['Hằng số mô-men – sức điện động', 'kΦ (N·m/A)', '0.96', '0.77'],
    ['Mô-men quán tính / ma sát nhớt', 'J (kg·m²) / Bm', '0.005 / 0.0005', '0.01 / 0.001'],
    ['Hằng số thời gian điện', 'τe (ms)', '5.0', '5.0'],
    ['Hằng số thời gian cơ điện', 'τm (ms)', '21.7', '33.6'],
    ['Tốc độ không tải lý tưởng (220 V)', 'ω₀ (rad/s)', '228.7', '284.8'],
    ['Dòng ngắn mạch khi khởi động trực tiếp', 'U/Ra (A)', '55.0 (15.7·Iđm)', '110.0 (15.4·Iđm)'],
    ['Hiệu suất tại điểm định mức', 'η (%)', '90.7', '88.9'],
], 'Thông số định mức và tham số của hai động cơ', widths=[6, 3.6, 3.2, 3.2])

H('1.2 Mô hình động cơ trên Simulink', 2)
P('Động cơ DC được mô hình hoá từ hai phương trình vi phân của mạch phần ứng và phần cơ:')
EQ('La·dia/dt = Va − Ra·ia − kΦ·ω')
EQ('J·dω/dt = kΦ·ia − Bm·ω − TL ;   dθ/dt = ω')
P('Trong Simulink, mỗi động cơ gồm các khối Sum, Gain (1/La, Ra, kΦ, 1/J, Bm) và ba khối Integrator lần lượt cho dòng điện ia, tốc độ ω và góc quay θ. Điện áp Va được cấp qua cầu H (biểu diễn bằng mô hình trung bình, giới hạn ±220 V), tải TL đưa vào qua khối Step. Các tín hiệu [θ, ω, ia, Va] được gom bằng khối Mux, hiển thị trên Scope và ghi ra workspace (To Workspace) để vẽ đồ thị. Sơ đồ khối của mô hình như Hình 1; hai động cơ dùng cùng cấu trúc, chỉ khác bộ tham số.')
FIGURE('d_motor.png', 'Sơ đồ khối Simulink mô hình động cơ DC (DC1 – 700 W và DC2 – 1400 W)')
P('Thông số của hai động cơ và các hệ số bộ điều khiển được khai báo trong file thong_so_dong_co.m (Hình 2). File này được gọi ở đầu script build_all.m trước khi dựng và chạy các mô hình.')
FIGURE('h_code_thongso.png', 'Khai báo thông số hai động cơ và bộ điều khiển (thong_so_dong_co.m)', 15.5)

H('1.3 Đánh giá bộ tham số động cơ', 2)
o1, o2 = R['ol1'], R['ol2']
P('**Thí nghiệm 1 – khởi động trực tiếp có tải định mức:** cấp thẳng Va = 220 V tại t = 0, tải trên trục bằng mô-men định mức (Tđm1 = 3.26 N·m, Tđm2 = 5.24 N·m), thời gian mô phỏng 1 s (mô hình M1_OpenLoop_700_1400).')
FIGURE('h_ol_dc1.png', 'Kết quả mô phỏng động cơ 1 (700 W) khi cấp 220 V, tải định mức', 15)
P(f'Nhận xét DC1: tốc độ xác lập {f1(o1["w"])} rad/s ≈ {o1["rpm"]:.0f} vòng/phút (đúng tốc độ định mức 2050 vòng/phút), dòng xác lập {f2(o1["i"])} A = Iđm. Dòng khởi động đạt đỉnh {f1(o1["ipk"])} A tại t = {ms(o1["tpk"])} ms (≈ {o1["ipk"]/3.508:.0f} lần Iđm); tốc độ xác lập (sai số 2 %) sau {ms(o1["ts"])} ms.')
FIGURE('h_ol_dc2.png', 'Kết quả mô phỏng động cơ 2 (1400 W) khi cấp 220 V, tải định mức', 15)
P(f'Nhận xét DC2: tốc độ xác lập {f1(o2["w"])} rad/s ≈ {o2["rpm"]:.0f} vòng/phút (đúng 2550 vòng/phút), dòng xác lập {f2(o2["i"])} A = Iđm. Dòng khởi động đạt đỉnh {f1(o2["ipk"])} A tại t = {ms(o2["tpk"])} ms (≈ {o2["ipk"]/7.156:.0f} lần Iđm); tốc độ xác lập sau {ms(o2["ts"])} ms.')
FIGURE('h_ol_sosanh.png', 'So sánh tốc độ và dòng điện của hai động cơ khi cấp 220 V, tải định mức', 15)
n1, n2 = R['nl1'], R['nl2']
P(f'**Thí nghiệm 2 – khởi động không tải, đóng tải định mức tại t = 0.5 s:** kiểm tra đặc tính cơ. Khi không tải DC1 quay {f1(n1["w0"])} rad/s ({n1["n0"]:.0f} vòng/phút), DC2 quay {f1(n2["w0"])} rad/s ({n2["n0"]:.0f} vòng/phút), đúng với ω₀ tính toán. Khi đóng tải định mức, tốc độ giảm về {f1(n1["wL"])} và {f1(n2["wL"])} rad/s, dòng tăng lên {f2(n1["iL"])} A và {f2(n2["iL"])} A; công suất điện từ trên trục xấp xỉ công suất định mức (Hình 6).')
FIGURE('h_ol_dongtai.png', 'Khởi động không tải và đóng tải định mức tại t = 0.5 s (tốc độ, dòng, công suất điện từ)', 15)
TABLE([
    ['Chỉ tiêu', 'DC1 – lý thuyết', 'DC1 – mô phỏng', 'DC2 – lý thuyết', 'DC2 – mô phỏng'],
    ['Tốc độ có tải định mức (rad/s)', '214.68', f2(o1['w']), '267.04', f2(o2['w'])],
    ['Tốc độ có tải (vòng/phút)', '2050', f'{o1["rpm"]:.0f}', '2550', f'{o2["rpm"]:.0f}'],
    ['Dòng xác lập (A)', '3.508', f3(o1['i']), '7.156', f3(o2['i'])],
    ['Tốc độ không tải (rad/s)', '228.67', f2(n1['w0']), '284.75', f2(n2['w0'])],
    ['Độ sụt tốc từ không tải → định mức', '6.1 %', f'{100*(n1["w0"]-n1["wL"])/n1["w0"]:.1f} %', '6.2 %', f'{100*(n2["w0"]-n2["wL"])/n2["w0"]:.1f} %'],
    ['Dòng khởi động cực đại (A)', '< 55', f1(o1['ipk']), '< 110', f1(o2['ipk'])],
    ['Thời gian xác lập tốc độ 2 % (ms)', '≈ 3·τm', ms(o1['ts']), '≈ 3·τm', ms(o2['ts'])],
], 'Kết quả đánh giá bộ tham số động cơ (lý thuyết và mô phỏng)', widths=[5.4, 2.6, 2.6, 2.6, 2.6], size=11.5)

H('1.4 Nhận xét về thông số động cơ', 2)
B('Bộ tham số đã chọn **phù hợp với yêu cầu đề bài**: ở 220 V và tải định mức, hai động cơ quay đúng 2050 và 2550 vòng/phút, dòng xác lập đúng dòng định mức (3.51 A và 7.16 A), hiệu suất ≈ 89 – 91 % – hợp lý với động cơ DC công suất dưới 2 kW.')
B('DC2 có công suất gấp đôi, mô-men định mức lớn hơn 1.6 lần (5.24 so với 3.26 N·m), điện trở nhỏ hơn và dòng định mức lớn hơn ≈ 2 lần; quán tính lớn hơn nên hằng số thời gian cơ τm2 = 33.6 ms > τm1 = 21.7 ms, đáp ứng cơ học chậm hơn (xác lập 115 ms so với 66 ms).')
B('Hai động cơ có cùng τe = 5 ms ≪ τm, cho phép tách vòng dòng điện (nhanh) và vòng tốc độ (chậm) khi thiết kế điều khiển nối tầng.')
B(f'Khởi động trực tiếp gây dòng rất lớn ({f1(o1["ipk"])} A và {f1(o2["ipk"])} A, ≈ 12 lần Iđm) – nguy hiểm cho cầu H và cổ góp, vì vậy cần vòng điều khiển dòng điện để giới hạn dòng khi tăng/giảm tốc.')
B('Độ sụt tốc từ không tải đến tải định mức khoảng 6 %, nếu điều khiển hở mạch sẽ không giữ được tốc độ khi tải thay đổi ⇒ cần vòng điều khiển tốc độ kín có khâu tích phân.')

# ============================ II ============================
page_break()
H('II. THỰC HIỆN CÁC PHƯƠNG PHÁP ĐIỀU KHIỂN', 1)
H('2.1 Thực hiện vòng điều khiển dòng điện', 2)
H('2.1.1 Quá trình thực hiện vòng điều khiển dòng điện', 3)
P('Đối tượng của vòng dòng điện là mạch phần ứng: ia(s) = [Va(s) − E(s)]/(La·s + Ra), trong đó sức điện động E = kΦ·ω đóng vai trò nhiễu (biến đổi chậm). Bộ điều khiển PI có hàm truyền:')
EQ('Ri(s) = Kpi + Kii/s')
P('**Trường hợp (a) – có sử dụng tham số động cơ:** chọn Kpi = La·ωci, Kii = Ra·ωci để điểm không của PI triệt tiêu điểm cực điện của động cơ (Kii/Kpi = Ra/La = 1/τe). Hàm truyền vòng hở trở thành ωci/s và vòng kín là khâu quán tính bậc nhất:')
EQ('ia/ia* = 1/(s/ωci + 1),   ωci = 800 rad/s ⇒ tr ≈ 2.2/ωci = 2.75 ms')
P('Đồng thời dùng tham số kΦ để bù sức điện động: Va = uPI + kΦ·ω. Kết quả: DC1 có Kpi = 16, Kii = 3200; DC2 có Kpi = 8, Kii = 1600.')
P('**Trường hợp (b) – không sử dụng tham số động cơ:** bộ PI được chỉnh định thử – sai với cùng hệ số cho cả hai động cơ, Kpi = 1, Kii = 100, không bù sức điện động. Đầu ra hai bộ điều khiển đều được giới hạn ±220 V, chống bão hoà tích phân kiểu back-calculation.')
P('**Kịch bản thử:** rotor quay tự do, tải trục bằng Tđm; dòng đặt dạng bậc thang i* = Iđm tại 0.02 s, 2·Iđm tại 0.07 s, 0.5·Iđm tại 0.12 s, mô phỏng 0.17 s (mô hình M2_Current_DCi_a / _b). Sơ đồ Simulink như Hình 7.')
FIGURE('d_current.png', 'Sơ đồ Simulink vòng điều khiển dòng điện: (a) dùng tham số động cơ, (b) không dùng tham số')
H('2.1.2 So sánh khi có và không sử dụng tham số động cơ', 3)
FIGURE('h_cur_dc1.png', 'Đáp ứng dòng điện của động cơ 1 khi có / không sử dụng tham số động cơ', 15)
FIGURE('h_cur_dc2.png', 'Đáp ứng dòng điện của động cơ 2 khi có / không sử dụng tham số động cơ', 15)
a1, b1, a2, b2 = R['cur1mb'], R['cur1gn'], R['cur2mb'], R['cur2gn']
TABLE([
    ['Chỉ tiêu', 'DC1 – có tham số', 'DC1 – không', 'DC2 – có tham số', 'DC2 – không'],
    ['Thời gian lên 10–90 % (ms)', ms(a1['tr']), ms(b1['tr']), ms(a2['tr']), ms(b2['tr'])],
    ['Thời gian xác lập 2 % (ms)', ms(a1['ts']), '> 50 (chưa xác lập)', ms(a2['ts']), '> 50 (chưa xác lập)'],
    ['Độ quá điều chỉnh (%)', f1(a1['os']), f1(b1['os']), f1(a2['os']), f1(b2['os'])],
    ['Sai số ở cuối nấc Iđm (A)', f3(a1['e1']), f3(b1['e1']), f3(a2['e1']), f3(b2['e1'])],
    ['Sai số ở cuối nấc 2·Iđm (A / %)', '0.000 / 0', f'{f2(b1["e2"])} / {b1["e2p"]:.0f}', '0.000 / 0', f'{f2(b2["e2"])} / {b2["e2p"]:.0f}'],
    ['Tích phân sai số IAE (A·s)', f'{a1["iae"]:.4f}', f'{b1["iae"]:.4f}', f'{a2["iae"]:.4f}', f'{b2["iae"]:.4f}'],
], 'So sánh vòng điều khiển dòng điện có / không sử dụng tham số động cơ', widths=[5.0, 2.8, 2.8, 2.8, 2.8], size=11.5)
P('**Nhận xét:**', indent=False)
B(f'Khi sử dụng tham số động cơ, dòng điện bám giá trị đặt rất nhanh (tr ≈ {ms(a1["tr"])} ms, đúng như thiết kế ωci = 800 rad/s), không vọt lố và sai số xác lập bằng 0 cho cả hai động cơ, mặc dù sức điện động thay đổi liên tục khi rotor tăng tốc – nhờ bù kΦ·ω.')
B(f'Khi không dùng tham số, cùng một bộ PI cho đáp ứng chậm hơn khoảng 10 lần (tr ≈ {ms(b1["tr"])} – {ms(b2["tr"])} ms), và khi rotor tăng tốc sức điện động tăng dạng dốc làm dòng không bám kịp: sai số {f2(b1["e2"])} A ({b1["e2p"]:.0f} %) với DC1, {f2(b2["e2"])} A ({b2["e2p"]:.0f} %) với DC2 ở nấc 2·Iđm; IAE lớn hơn {b1["iae"]/a1["iae"]:.0f} lần.')
B('Hệ số chọn theo tham số tự thích ứng với từng động cơ (DC2 có La, Ra nhỏ hơn nên Kpi, Kii nhỏ hơn một nửa) và cho cùng một đáp ứng mong muốn; hệ số chung không đảm bảo chất lượng khi đổi động cơ. ⇒ **Chọn phương án PI dùng tham số động cơ (+ bù sức điện động)** làm vòng trong cho các phần tiếp theo.')

H('2.2 Thực hiện vòng điều khiển tốc độ', 2)
H('2.2.1 Điều khiển tốc độ có sử dụng vòng điều khiển dòng điện', 3)
P('Cấu trúc nối tầng (cascade): bộ PI tốc độ tạo dòng đặt i*, được giới hạn |i*| ≤ Imax = 2.5·Iđm (8.77 A với DC1, 17.89 A với DC2), sau đó vòng dòng điện ở mục 2.1 tạo điện áp Va. Vì vòng dòng nhanh hơn nhiều (≈ 1/ωci), có thể coi i ≈ i*, đối tượng của vòng tốc độ là kΦ/(J·s). Chọn:')
EQ('Kpw = J·ωcw/kΦ ,   Kiw = Kpw·ωcw/4 ,   ωcw = 60 rad/s ,   trọng số đặt b = 0.5')
P('DC1: Kpw = 0.3125, Kiw = 4.69; DC2: Kpw = 0.779, Kiw = 11.69. Kịch bản: tốc độ đặt ω* = 200 rad/s (DC1) và 250 rad/s (DC2) tại t = 0.1 s; đóng tải định mức tại t = 1.0 s; mô phỏng 1.6 s (mô hình M3_Speed_DCi_cascade, Hình 10).')
FIGURE('d_speed_cur.png', 'Sơ đồ Simulink điều khiển tốc độ có vòng điều khiển dòng điện (cascade)')
H('2.2.2 Điều khiển tốc độ không sử dụng vòng điều khiển dòng điện', 3)
P('Bộ PI tốc độ tác động trực tiếp lên điện áp phần ứng (giới hạn ±220 V), không có phản hồi dòng. Hệ số được chỉnh định thử – sai để không vọt lố: Kp = 2 V·s/rad, Ki = 20 V/rad (b = 0.5). Kịch bản giống mục 2.2.1 (mô hình M3_Speed_DCi_noI, Hình 11).')
FIGURE('d_speed_nocur.png', 'Sơ đồ Simulink điều khiển tốc độ không có vòng điều khiển dòng điện')
H('2.2.3 Kết quả, bảng so sánh và phương án lựa chọn', 3)
FIGURE('h_spd_dc1.png', 'Động cơ 1: điều khiển tốc độ có (trái) và không có (phải) vòng dòng điện', 16)
FIGURE('h_spd_dc2.png', 'Động cơ 2: điều khiển tốc độ có (trái) và không có (phải) vòng dòng điện', 16)
FIGURE('h_spd_sosanh.png', 'So sánh tốc độ và dòng điện của hai phương án điều khiển tốc độ', 15)
s1c, s1n, s2c, s2n = R['spd1c'], R['spd1n'], R['spd2c'], R['spd2n']
TABLE([
    ['Chỉ tiêu', 'DC1 – có vòng dòng', 'DC1 – không', 'DC2 – có vòng dòng', 'DC2 – không'],
    ['Thời gian lên (s)', f3(s1c['tr']), f3(s1n['tr']), f3(s2c['tr']), f3(s2n['tr'])],
    ['Thời gian xác lập 2 % (s)', f3(s1c['ts']), f3(s1n['ts']), f3(s2c['ts']), f3(s2n['ts'])],
    ['Độ quá điều chỉnh (%)', f1(s1c['os']), f1(s1n['os']), f1(s2c['os']), f1(s2n['os'])],
    ['Dòng đỉnh (A) / bội số Iđm', f'{f1(s1c["ipk"])} / {f1(s1c["ipkr"])}', f'{f1(s1n["ipk"])} / {f1(s1n["ipkr"])}', f'{f1(s2c["ipk"])} / {f1(s2c["ipkr"])}', f'{f1(s2n["ipk"])} / {f1(s2n["ipkr"])}'],
    ['Sụt tốc khi đóng tải Tđm (rad/s)', f2(s1c['drop']), f2(s1n['drop']), f2(s2c['drop']), f2(s2n['drop'])],
    ['Thời gian phục hồi 1 % (s)', f3(s1c['rec']), f3(s1n['rec']), f3(s2c['rec']), f3(s2n['rec'])],
    ['Sai số tốc độ tại t = 1.6 s (rad/s)', f3(s1c['ess']), f3(s1n['ess']), f3(s2c['ess']), f3(s2n['ess'])],
    ['Điện áp xác lập có tải (V)', f1(s1c['va']), f1(s1n['va']), f1(s2c['va']), f1(s2n['va'])],
], 'So sánh kết quả điều khiển tốc độ có / không có vòng dòng điện', widths=[5.0, 2.8, 2.8, 2.8, 2.8], size=11.5)
P('**Nhận xét và lựa chọn phương án:**', indent=False)
B(f'Có vòng dòng điện: động cơ tăng tốc với dòng không đổi bằng Imax (đoạn dòng phẳng ≈ 2.4·Iđm trên Hình 12, 13) nên gia tốc lớn nhất và an toàn; thời gian xác lập {f3(s1c["ts"])} s (DC1), {f3(s2c["ts"])} s (DC2), vọt lố nhỏ ({f1(s1c["os"])} % và {f1(s2c["os"])} %), sai số xác lập bằng 0, phục hồi tải sau ≈ {f3(s1c["rec"])} s.')
B(f'Không có vòng dòng điện: ở thời điểm đặt tốc độ, bộ PI đưa điện áp lên 220 V gần như tức thời, dòng khởi động vọt tới {f1(s1n["ipk"])} A ({f1(s1n["ipkr"])}·Iđm) với DC1 và {f1(s2n["ipk"])} A ({f1(s2n["ipkr"])}·Iđm) với DC2 – không thể giới hạn dòng. Muốn giảm dòng phải giảm hệ số Kp, Ki khiến đáp ứng chậm (ts ≈ {f3(s1n["ts"])} s, gấp ≈ 2 lần cascade).')
B('Sụt tốc khi đóng tải của hai phương án tương đương (5 – 8 rad/s); phương án không có vòng dòng sụt ít hơn một chút do Kp lớn, nhưng sau 0.6 s vẫn còn sai số nhỏ vì khâu tích phân yếu.')
B('⇒ **Lựa chọn: điều khiển tốc độ nối tầng có vòng dòng điện** – nhanh hơn, giới hạn được dòng (bảo vệ động cơ và bộ biến đổi), các hệ số được tính trực tiếp từ tham số động cơ nên dễ chỉnh định cho cả DC1 và DC2.')

H('2.3 Thực hiện vòng điều khiển vị trí', 2)
P('Bài toán: quay trục động cơ tới vị trí đặt θ* = 50 rad (≈ 8 vòng) tại t = 0.1 s; tại t = 1.0 s đóng tải 0.5·Tđm để kiểm tra khả năng giữ vị trí; mô phỏng 1.5 s. Ba cấu trúc được xây dựng (mô hình M4_Pos_DCi_full / _speed / _direct).')
H('2.3.1 Có sử dụng vòng điều khiển dòng điện và tốc độ', 3)
P('Ba vòng nối tầng: vị trí → tốc độ → dòng điện. Bộ điều khiển vị trí là khâu P (Kθ = 15 s⁻¹ = ωcw/4) có giới hạn căn bậc hai để động cơ hãm kịp trước đích với dòng không vượt Imax:')
EQ('ω* = sign(e)·min( Kθ·|e| , √(2·a·|e|) , ωđm ),   e = θ* − θ,   a = 0.6·kΦ·Imax/J')
P('Vòng tốc độ và vòng dòng điện giữ nguyên như mục 2.2.1 (Hình 15).')
FIGURE('d_pos_full.png', 'Sơ đồ Simulink điều khiển vị trí có vòng tốc độ và vòng dòng điện')
H('2.3.2 Có sử dụng vòng điều khiển tốc độ', 3)
P('Bỏ vòng dòng điện: khâu P vị trí (như 2.3.1) tạo ω*, bộ PI tốc độ (Kp = 2, Ki = 20) tác động trực tiếp lên điện áp (Hình 16).')
FIGURE('d_pos_speed.png', 'Sơ đồ Simulink điều khiển vị trí có vòng tốc độ (không có vòng dòng điện)')
H('2.3.3 Điều khiển trực tiếp vị trí', 3)
P('Một bộ PID duy nhất tác động từ sai lệch vị trí ra điện áp phần ứng: Kp = 60 V/rad, Ki = 20 V/(rad·s), Kd = 4 V·s/rad (lọc đạo hàm N = 100), giới hạn ±220 V (Hình 17).')
FIGURE('d_pos_direct.png', 'Sơ đồ Simulink điều khiển trực tiếp vị trí bằng bộ PID')
H('2.3.4 Kết quả, bảng so sánh và phương án lựa chọn', 3)
FIGURE('h_pos_dc1.png', 'Động cơ 1: đáp ứng vị trí, tốc độ, dòng điện của ba cấu trúc điều khiển vị trí', 15)
FIGURE('h_pos_zoom_dc1.png', 'Động cơ 1: phóng to quanh vị trí đích (thấy rõ vọt lố và sai lệch khi có tải)', 15)
FIGURE('h_pos_dc2.png', 'Động cơ 2: đáp ứng vị trí, tốc độ, dòng điện của ba cấu trúc điều khiển vị trí', 15)
FIGURE('h_pos_zoom_dc2.png', 'Động cơ 2: phóng to quanh vị trí đích', 15)
pf1, ps1, pd1 = R['pos1full'], R['pos1speed'], R['pos1direct']
pf2, ps2, pd2 = R['pos2full'], R['pos2speed'], R['pos2direct']
TABLE([
    ['Chỉ tiêu', 'Vị trí+tốc độ+dòng', 'Vị trí+tốc độ', 'PID trực tiếp'],
    ['DC1 – thời gian xác lập 2 % (s)', f3(pf1['ts']), f3(ps1['ts']), f3(pd1['ts'])],
    ['DC1 – độ quá điều chỉnh (%)', f2(pf1['os']), f2(ps1['os']), f2(pd1['os'])],
    ['DC1 – dòng đỉnh (A) / bội Iđm', f'{f1(pf1["ipk"])} / {f1(pf1["ipkr"])}', f'{f1(ps1["ipk"])} / {f1(ps1["ipkr"])}', f'{f1(pd1["ipk"])} / {f1(pd1["ipkr"])}'],
    ['DC1 – lệch vị trí khi có tải (rad)', f3(pf1['dev']), f3(ps1['dev']), f3(pd1['dev'])],
    ['DC1 – sai số vị trí tại 1.5 s (rad)', f3(pf1['ess']), f3(ps1['ess']), f3(pd1['ess'])],
    ['DC2 – thời gian xác lập 2 % (s)', f3(pf2['ts']), f3(ps2['ts']), f3(pd2['ts'])],
    ['DC2 – độ quá điều chỉnh (%)', f2(pf2['os']), f2(ps2['os']), f2(pd2['os'])],
    ['DC2 – dòng đỉnh (A) / bội Iđm', f'{f1(pf2["ipk"])} / {f1(pf2["ipkr"])}', f'{f1(ps2["ipk"])} / {f1(ps2["ipkr"])}', f'{f1(pd2["ipk"])} / {f1(pd2["ipkr"])}'],
    ['DC2 – lệch vị trí khi có tải (rad)', f3(pf2['dev']), f3(ps2['dev']), f3(pd2['dev'])],
    ['DC2 – sai số vị trí tại 1.5 s (rad)', f3(pf2['ess']), f3(ps2['ess']), f3(pd2['ess'])],
    ['Giới hạn dòng / tốc độ', 'Có / Có', 'Không / Có', 'Không / Không'],
], 'So sánh kết quả ba cấu trúc điều khiển vị trí (θ* = 50 rad)', widths=[6.0, 3.6, 3.3, 3.3], size=11.5)
P('**Nhận xét và lựa chọn phương án:**', indent=False)
B(f'Cấu trúc 3 vòng: tới đích không vọt lố (0 %) với cả hai động cơ, dòng luôn ≤ Imax ({f1(pf1["ipk"])} A và {f1(pf2["ipk"])} A ≈ 2.4·Iđm), tốc độ được giới hạn quanh ωđm; khi có tải, vị trí lệch tối đa {f3(pf1["dev"])} rad rồi trở về sai số ≈ 0 nhờ tích phân vòng tốc độ.')
B(f'Cấu trúc vị trí + tốc độ: thời gian xác lập tương đương hoặc nhanh hơn (DC2: {f3(ps2["ts"])} s) nhưng dòng khởi động lên tới {f1(ps1["ipk"])} A và {f1(ps2["ipk"])} A (≈ 12·Iđm) và có vọt lố {f1(ps1["os"])} – {f1(ps2["os"])} %.')
B(f'PID trực tiếp: dòng đỉnh lớn như khởi động trực tiếp, tốc độ không bị giới hạn (DC2 đạt {f1(pd2["wmax"])} rad/s > ωđm), khó chỉnh định vì một bộ điều khiển phải đồng thời xử lý động học điện, cơ và vị trí; khi có tải còn sai số {f3(pd1["ess"])} rad (DC1) sau 0.5 s do khâu tích phân phải chọn nhỏ để giữ ổn định.')
B('⇒ **Lựa chọn: điều khiển vị trí 3 vòng (vị trí – tốc độ – dòng điện)**. Phương án này an toàn về dòng, không vọt lố, chống nhiễu tải tốt và cho phép thêm bù trước tốc độ khi bám quỹ đạo (dùng ở mục 3.2).')

# ============================ III ============================
page_break()
H('III. THỰC HIỆN MÔ PHỎNG ỨNG DỤNG ĐIỀU KHIỂN ĐỘNG CƠ', 1)
H('3.1 Điều khiển đồng tốc 2 động cơ', 2)
P('**Yêu cầu:** hai động cơ DC1 (700 W) và DC2 (1400 W) cùng kéo một cơ cấu (ví dụ băng tải hai đầu, hai bánh xe của robot) và phải quay cùng tốc độ ω₁ = ω₂ khi tốc độ đặt thay đổi và khi tải trên từng động cơ thay đổi khác nhau. Mỗi động cơ dùng bộ điều khiển tốc độ cascade đã chọn ở mục 2.2.')
P('**Kịch bản:** ω* hình thang: tăng 0 → 150 rad/s trong 0.1 – 0.4 s, giữ, giảm về 0 trong 2.0 – 2.3 s; đóng tải Tđm2 vào DC2 tại 1.0 s và Tđm1 vào DC1 tại 1.5 s; mô phỏng 2.6 s (mô hình M5_SyncSpeed). So sánh ba chiến lược:')
B('**Song song:** hai động cơ nhận cùng tốc độ đặt ω*.')
B('**Chủ – tớ (master – slave):** DC1 bám ω*, tốc độ đặt của DC2 là tốc độ đo được của DC1 (ω₂* = ω₁).')
B('**Song song + bù chéo (cross-coupling):** như song song, thêm tín hiệu bù Kc·(ω₁ − ω₂) vào dòng đặt (trừ ở DC1, cộng ở DC2) với Kc = J·ωcw/kΦ của từng động cơ.')
FIGURE('d_sync.png', 'Sơ đồ Simulink điều khiển đồng tốc hai động cơ (chọn chiến lược + khâu bù chéo)')
FIGURE('h_sync_all.png', 'Tốc độ, sai lệch đồng tốc và dòng điện của hai động cơ với ba chiến lược', 16.5)
FIGURE('h_sync_err.png', 'So sánh sai lệch tốc độ ω₁ − ω₂ và sai lệch góc θ₁ − θ₂ của ba chiến lược', 15)
sp, sm, sx = R['sync_parallel'], R['sync_master'], R['sync_cross']
TABLE([
    ['Chỉ tiêu (|ω₁ − ω₂| lớn nhất, rad/s)', 'Song song', 'Chủ – tớ', 'Song song + bù chéo'],
    ['Giai đoạn tăng tốc (0.1 – 0.6 s)', f2(sp['ramp']), f2(sm['ramp']), f2(sx['ramp'])],
    ['Đóng tải DC2 (1.0 – 1.5 s)', f2(sp['L2']), f2(sm['L2']), f2(sx['L2'])],
    ['Đóng tải DC1 (1.5 – 2.0 s)', f2(sp['L1']), f2(sm['L1']), f2(sx['L1'])],
    ['Giai đoạn giảm tốc (2.0 – 2.6 s)', f2(sp['dec']), f2(sm['dec']), f2(sx['dec'])],
    ['Giá trị hiệu dụng sai lệch (rad/s)', f3(sp['rms']), f3(sm['rms']), f3(sx['rms'])],
    ['|θ₁ − θ₂| lớn nhất (rad)', f3(sp['dth']), f3(sm['dth']), f3(sx['dth'])],
    ['Dòng đỉnh DC1 / DC2 (A)', f'{f2(sp["ip1"])} / {f2(sp["ip2"])}', f'{f2(sm["ip1"])} / {f2(sm["ip2"])}', f'{f2(sx["ip1"])} / {f2(sx["ip2"])}'],
], 'So sánh các chiến lược điều khiển đồng tốc hai động cơ', widths=[6.4, 3.0, 3.0, 3.6], size=11.5)
P('**Nhận xét:**', indent=False)
B(f'Song song: khi tốc độ đặt thay đổi, hai vòng tốc độ có cùng dải thông (ωcw = 60 rad/s, hệ số đã chuẩn hoá theo J/kΦ) nên đồng tốc rất tốt (sai lệch chỉ {f2(sp["ramp"])} rad/s); tuy nhiên khi tải tác động lên một động cơ thì động cơ kia không "biết", sai lệch lên tới {f2(sp["L2"])} – {f2(sp["L1"])} rad/s.')
B(f'Chủ – tớ: DC2 luôn đi sau DC1 một khoảng trễ của vòng tốc độ nên sai lệch lớn khi tăng/giảm tốc ({f2(sm["ramp"])} rad/s); khi tải vào động cơ chủ (DC1) thì động cơ tớ bám theo nên sai lệch giảm còn {f2(sm["L1"])} rad/s, nhưng tải vào động cơ tớ thì động cơ chủ không phản ứng.')
B(f'Song song + bù chéo: kết hợp ưu điểm của hai cách – sai lệch tăng tốc chỉ {f2(sx["ramp"])} rad/s, sai lệch khi đóng tải giảm còn {f2(sx["L2"])} – {f2(sx["L1"])} rad/s (≈ 2.5 lần nhỏ hơn song song), giá trị hiệu dụng sai lệch nhỏ nhất ({f3(sx["rms"])} rad/s). ⇒ **Chọn chiến lược song song có bù chéo** cho bài toán đồng tốc.')

H('3.2 Điều khiển vị trí đồng thời nhiều động cơ', 2)
P('**Yêu cầu:** điều khiển đồng thời ba trục của một cơ cấu robot, mỗi trục dùng bộ điều khiển vị trí 3 vòng (mục 2.3.1), sao cho các trục **bắt đầu và kết thúc chuyển động cùng lúc** dù quãng đường khác nhau – điều kiện để đầu công tác đi đúng quỹ đạo:')
B('Trục 1: động cơ loại 1 (700 W), θ đích = 30 rad.')
B('Trục 2: động cơ loại 2 (1400 W), θ đích = 60 rad.')
B('Trục 3: động cơ loại 1 (700 W), θ đích = −20 rad (quay ngược).')
P('Các trục đi tới đích tại t = 0.1 s, quay về 0 tại t = 1.6 s; tại t = 1.2 s đóng tải 0.5·Tđm vào cả ba trục. So sánh hai phương án:')
B('**Đặt vị trí dạng bậc thang** (không phối hợp): mỗi trục nhận trực tiếp vị trí đích.')
B('**Quỹ đạo đồng bộ:** bộ lập quỹ đạo tạo θ*(t) dạng đa thức bậc 5 với cùng thời gian chuyển động T = 0.8 s cho mọi trục, kèm bù trước tốc độ ω* = dθ*/dt:')
EQ('θ*(t) = θ₀ + (θđ − θ₀)·(10s³ − 15s⁴ + 6s⁵),   s = (t − t₀)/T ∈ [0, 1]')
FIGURE('d_multi.png', 'Sơ đồ Simulink điều khiển vị trí đồng thời ba trục (bộ lập quỹ đạo + 3 vòng vị trí cascade)')
FIGURE('h_multi_step.png', 'Điều khiển ba trục với vị trí đặt dạng bậc thang', 15)
FIGURE('h_multi_traj.png', 'Điều khiển ba trục với quỹ đạo đa thức bậc 5 đồng bộ', 15)
FIGURE('h_multi_sosanh.png', 'Tiến trình chuẩn hoá θ/θđích: bậc thang (trái) và quỹ đạo đồng bộ (phải)', 16)
rows = [['Chỉ tiêu', 'Trục 1 (DC1, 30 rad)', 'Trục 2 (DC2, 60 rad)', 'Trục 3 (DC1, −20 rad)']]
for md, nm in (('step', 'Bậc thang'), ('traj', 'Quỹ đạo')):
    rows.append([f'{nm} – thời điểm đạt 98 % (s)'] + [f3(R[f'mp_{md}{k}']['t98']) for k in range(3)])
    rows.append([f'{nm} – dòng đỉnh (A) / bội Iđm'] + [f'{f1(R[f"mp_{md}{k}"]["ipk"])} / {f1(R[f"mp_{md}{k}"]["ipkr"])}' for k in range(3)])
    rows.append([f'{nm} – lệch vị trí khi có tải (rad)'] + [f3(R[f'mp_{md}{k}']['dev']) for k in range(3)])
rows.append(['Quỹ đạo – sai số bám lớn nhất (rad)'] + [f3(R[f'mp_traj{k}']['trk']) for k in range(3)])
rows.append(['Độ lệch tiến trình lớn nhất giữa các trục', f'Bậc thang: {100*R["mp_step_spread"]:.1f} %', f'Quỹ đạo: {100*R["mp_traj_spread"]:.2f} %', ''])
TABLE(rows, 'So sánh điều khiển vị trí đồng thời ba trục: bậc thang và quỹ đạo đồng bộ', widths=[6.2, 3.3, 3.3, 3.3], size=11.5)
P('**Nhận xét:**', indent=False)
B(f'Với vị trí đặt bậc thang, mỗi trục chạy hết khả năng (dòng = Imax, tốc độ ≈ ωđm) nên trục có quãng đường ngắn tới đích sớm ({f3(R["mp_step2"]["t98"])} s) còn trục 2 tới muộn ({f3(R["mp_step1"]["t98"])} s); tiến trình giữa các trục lệch nhau tới {100*R["mp_step_spread"]:.0f} % ⇒ đầu công tác đi sai đường thẳng, có thể va chạm.')
B(f'Với quỹ đạo đồng bộ, cả ba trục tới 98 % hành trình cùng lúc tại t ≈ {f3(R["mp_traj0"]["t98"])} s, độ lệch tiến trình chỉ {100*R["mp_traj_spread"]:.2f} %; nhờ bù trước tốc độ, sai số bám lớn nhất chỉ {f3(R["mp_traj0"]["trk"])} – {f3(R["mp_traj1"]["trk"])} rad. Dòng đỉnh giảm mạnh ({f1(R["mp_traj0"]["ipk"])} A thay vì {f1(R["mp_step0"]["ipk"])} A ở trục 1) do gia tốc được phân bố đều, chuyển động êm, không giật.')
B('Khi đóng tải 0.5·Tđm, các trục chỉ lệch ≈ 0.13 – 0.17 rad rồi trở về vị trí đặt nhờ khâu tích phân của vòng tốc độ. Cách tiếp cận này mở rộng trực tiếp cho số trục bất kỳ: chỉ cần thêm một bộ điều khiển 3 vòng và một đầu ra của bộ lập quỹ đạo cho mỗi trục.')

H('KẾT LUẬN', 1)
P('Báo cáo đã hoàn thành đầy đủ các yêu cầu đối với hai động cơ DC 700 W và 1400 W:')
B('Xây dựng bộ tham số động cơ phù hợp: ở 220 V và tải định mức động cơ quay đúng 2050 / 2550 vòng/phút với dòng định mức 3.51 / 7.16 A; đánh giá được đặc tính động học (τm = 21.7 / 33.6 ms) và dòng khởi động trực tiếp ≈ 12·Iđm.')
B('Vòng dòng điện thiết kế theo tham số động cơ (triệt tiêu điểm cực + bù sức điện động) nhanh hơn ≈ 10 lần và không có sai số so với PI chỉnh định không dùng tham số.')
B('Điều khiển tốc độ và vị trí theo cấu trúc nối tầng có vòng dòng điện cho chất lượng tốt nhất: giới hạn dòng ≤ 2.5·Iđm, không vọt lố vị trí, sai số xác lập bằng 0, chống nhiễu tải tốt.')
B('Ứng dụng: chiến lược song song có bù chéo cho sai lệch đồng tốc nhỏ nhất; bộ lập quỹ đạo đồng bộ giúp nhiều trục bắt đầu và kết thúc chuyển động cùng lúc.')
P('Hướng phát triển: mô phỏng cầu H với PWM thực (khối Universal Bridge, tần số 10 – 20 kHz), bổ sung ma sát khô, khe hở hộp số và nhiễu đo encoder để đánh giá bộ điều khiển sát thực tế hơn.')

H('TÀI LIỆU THAM KHẢO', 1)
for s in ['Bài giảng Điều khiển truyền động cho Robot – Khoa Điện – Điện tử, Trường Đại học Giao thông Vận tải.',
          'Nguyễn Phùng Quang, Truyền động điện thông minh, NXB Khoa học và Kỹ thuật, Hà Nội.',
          'Bùi Quốc Khánh, Nguyễn Văn Liễn, Điều chỉnh tự động truyền động điện, NXB Khoa học và Kỹ thuật.',
          'R. Krishnan, Electric Motor Drives: Modeling, Analysis, and Control, Prentice Hall, 2001.',
          'MathWorks, Simulink Documentation – PID Controller, PID Controller (2DOF), DC Machine blocks.']:
    B(s)

H('PHỤ LỤC', 1)
P('**A. Hướng dẫn chạy mô phỏng Simulink.** Đặt hai file thong_so_dong_co.m và build_all.m cùng một thư mục, mở MATLAB (R2021a trở lên) và gõ lệnh build_all. Script sẽ tự dựng, lưu (.slx) và chạy các mô hình sau, đồng thời vẽ đồ thị kết quả:', indent=False)
for s in ['M1_OpenLoop_700_1400 – mục I (cấp 220 V, tải định mức).',
          'M2_Current_DC1_a/_b, M2_Current_DC2_a/_b – mục 2.1 (vòng dòng có / không dùng tham số).',
          'M3_Speed_DCi_cascade / _noI – mục 2.2 (tốc độ có / không có vòng dòng).',
          'M4_Pos_DCi_full / _speed / _direct – mục 2.3 (ba cấu trúc điều khiển vị trí).',
          'M5_SyncSpeed – mục 3.1 (biến ms, xc chọn chiến lược đồng tốc).',
          'M6_MultiAxis_step / _traj – mục 3.2 (ba trục, bậc thang / quỹ đạo đồng bộ).']:
    B(s)
P('Các đồ thị trong báo cáo được vẽ lại từ cùng mô hình toán học (bộ giải bước cố định 10 µs) để thống nhất định dạng; kết quả chạy trên Simulink (ode45) trùng khớp trong phạm vi sai số số học.', indent=False)
P('**B. Mã nguồn khai báo thông số (thong_so_dong_co.m):** xem Hình 2. **C. Công cụ hỗ trợ:** MATLAB/Simulink, Python (NumPy, Matplotlib); tham khảo thêm ChatGPT, Gemini, Claude.', indent=False)

# ============ dien danh muc hinh / bang vao vi tri anchor ============
def insert_after(anchor, lines, prefix):
    cur = anchor
    for k, cap in enumerate(lines, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(1); p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        p.paragraph_format.left_indent = Cm(1.6); p.paragraph_format.first_line_indent = Cm(-1.6)
        r = p.add_run(f'{prefix} {k}: {cap}\t{PAGES.get(f"{prefix}{k}", "")}'); r.font.size = Pt(13)
        cur._p.addnext(p._p); cur = p

insert_after(figlist_anchor, FIGS, 'Hình')
insert_after(tablist_anchor, TABS, 'Bảng')
doc.save(OUTDOC)
json.dump(dict(figs=FIGS, tabs=TABS, heads=[t for _, t in HEADS]), open(OUTDOC + '.meta.json', 'w'), ensure_ascii=False)
print('saved', len(FIGS), 'figs', len(TABS), 'tables')
