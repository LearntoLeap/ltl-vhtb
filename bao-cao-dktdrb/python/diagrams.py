"""Ve so do khoi dang Simulink cho cac mo hinh trong build_all.m"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon

OUT = os.path.join(os.path.dirname(__file__), 'fig')
plt.rcParams['font.family'] = 'DejaVu Sans'
FS = 8


class D:
    def __init__(self, W, H, title=None):
        self.fig = plt.figure(figsize=(W / 100 * 1.0, (H + 30) / 100 * 1.0))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W); self.ax.set_ylim(H, -30); self.ax.axis('off')
        self.W, self.H = W, H
        if title:
            self.ax.text(10, -18, title, fontsize=9, color='#555', ha='left', va='center')

    def blk(self, x, y, w, h, txt, name=None, fc='white', fs=FS, sub=False, nin=1, nout=1, inl=None, outl=None):
        ax = self.ax
        ax.add_patch(Rectangle((x + 2, y + 2), w, h, fc='#c8c8c8', ec='none', zorder=1))
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec='black', lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, zorder=3)
        if name:
            ax.text(x + w / 2, y + h + 9, name, ha='center', va='center', fontsize=FS - 1, zorder=3)
        b = dict(x=x, y=y, w=w, h=h)
        b['i'] = [(x, y + h * (k + 1) / (nin + 1)) for k in range(nin)]
        b['o'] = [(x + w, y + h * (k + 1) / (nout + 1)) for k in range(nout)]
        if inl:
            for k, s in enumerate(inl):
                ax.text(x + 3, b['i'][k][1], s, fontsize=FS - 1.5, va='center', ha='left', zorder=3)
        if outl:
            for k, s in enumerate(outl):
                ax.text(x + w - 3, b['o'][k][1], s, fontsize=FS - 1.5, va='center', ha='right', zorder=3)
        return b

    def gain(self, x, y, txt, name=None, w=44, h=30, left=False):
        ax = self.ax
        if not left:
            pts = [(x, y), (x + w, y + h / 2), (x, y + h)]
        else:
            pts = [(x + w, y), (x, y + h / 2), (x + w, y + h)]
        ax.add_patch(Polygon([(p[0] + 2, p[1] + 2) for p in pts], fc='#c8c8c8', ec='none', zorder=1))
        ax.add_patch(Polygon(pts, fc='white', ec='black', lw=1.0, zorder=2))
        ax.text(x + w * (0.38 if not left else 0.62), y + h / 2, txt, ha='center', va='center', fontsize=FS - 0.5, zorder=3)
        if name:
            ax.text(x + w / 2, y + h + 9, name, ha='center', va='center', fontsize=FS - 1)
        if not left:
            return dict(i=[(x, y + h / 2)], o=[(x + w, y + h / 2)])
        return dict(i=[(x + w, y + h / 2)], o=[(x, y + h / 2)])

    def sum(self, x, y, signs='+-', r=11, name=None):
        ax = self.ax
        ax.add_patch(Circle((x + 1.5, y + 1.5), r, fc='#c8c8c8', ec='none', zorder=1))
        ax.add_patch(Circle((x, y), r, fc='white', ec='black', lw=1.0, zorder=2))
        pos = [(-r * 0.55, -r * 0.05), (-r * 0.05, r * 0.6), (-r * 0.05, -r * 0.55)]
        for k, s in enumerate(signs):
            dx, dy = pos[k]
            ax.text(x + dx, y + dy, s, fontsize=FS - 1, ha='center', va='center', zorder=3)
        if name:
            ax.text(x, y - r - 7, name, ha='center', va='center', fontsize=FS - 1.5)
        return dict(i=[(x - r, y), (x, y + r), (x, y - r)], o=[(x + r, y)])

    def scope(self, x, y, name='Scope', n=1):
        ax = self.ax
        w, h = 34, 30 + 10 * (n - 1)
        ax.add_patch(Rectangle((x + 2, y + 2), w, h, fc='#c8c8c8', ec='none', zorder=1))
        ax.add_patch(Rectangle((x, y), w, h, fc='white', ec='black', lw=1, zorder=2))
        ax.add_patch(Rectangle((x + 6, y + 6), w - 12, h - 12, fc='#e9f2ff', ec='#333', lw=0.8, zorder=3))
        ax.text(x + w / 2, y + h + 9, name, ha='center', fontsize=FS - 1)
        return dict(i=[(x, y + h * (k + 1) / (n + 1)) for k in range(n)])

    def step(self, x, y, name='Step', val=None):
        b = self.blk(x, y, 34, 30, '', name)
        self.ax.plot([x + 6, x + 17, x + 17, x + 28], [y + 22, y + 22, y + 8, y + 8], color='k', lw=1, zorder=4)
        if val:
            self.ax.text(x + 17, y - 6, val, ha='center', fontsize=FS - 1.5, color='#333')
        return b

    def const(self, x, y, v, name=None, w=40):
        return self.blk(x, y, w, 26, v, name)

    def integ(self, x, y, name='Integrator'):
        b = self.blk(x, y, 34, 32, '', name)
        self.ax.text(x + 17, y + 10, '1', ha='center', va='center', fontsize=FS)
        self.ax.plot([x + 10, x + 24], [y + 16, y + 16], 'k', lw=0.8)
        self.ax.text(x + 17, y + 23, 's', ha='center', va='center', fontsize=FS, style='italic')
        return b

    def sat(self, x, y, name='Saturation'):
        b = self.blk(x, y, 34, 30, '', name)
        self.ax.plot([x + 6, x + 12, x + 22, x + 28], [y + 22, y + 22, y + 8, y + 8], 'k', lw=1, zorder=4)
        self.ax.plot([x + 17, x + 17], [y + 4, y + 26], color='#999', lw=0.5)
        self.ax.plot([x + 4, x + 30], [y + 15, y + 15], color='#999', lw=0.5)
        return b

    def goto(self, x, y, tag, frm=False):
        ax = self.ax
        w, h = 40, 20
        if not frm:
            pts = [(x, y), (x + w - 8, y), (x + w, y + h / 2), (x + w - 8, y + h), (x, y + h)]
            port = dict(i=[(x, y + h / 2)])
        else:
            pts = [(x + 8, y), (x + w, y), (x + w, y + h), (x + 8, y + h), (x, y + h / 2)]
            port = dict(o=[(x + w, y + h / 2)])
        ax.add_patch(Polygon(pts, fc='white', ec='black', lw=1, zorder=2))
        ax.text(x + w / 2, y + h / 2, f'[{tag}]', ha='center', va='center', fontsize=FS - 1, zorder=3)
        return port

    def line(self, *pts, arrow=True, txt=None, txtpos=None, color='black', dot=False):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        self.ax.plot(xs, ys, color=color, lw=1.0, zorder=1.5)
        if arrow:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            self.ax.annotate('', xy=(x1, y1), xytext=(x0 + (x1 - x0) * 0.6, y0 + (y1 - y0) * 0.6),
                             arrowprops=dict(arrowstyle='-|>', color=color, lw=1.0, mutation_scale=9), zorder=4)
        if dot:
            self.ax.plot(*pts[0], 'o', color=color, ms=3, zorder=5)
        if txt:
            tx, ty = txtpos if txtpos else ((xs[0] + xs[1]) / 2, ys[0] - 6)
            self.ax.text(tx, ty, txt, fontsize=FS - 1.5, ha='center', va='bottom', color='#222')

    def conn(self, a, b, ai=0, bi=0, via=None, **kw):
        p0 = a['o'][ai]; p1 = b['i'][bi]
        pts = [p0]
        if via == 'h':
            mx = (p0[0] + p1[0]) / 2
            pts += [(mx, p0[1]), (mx, p1[1])]
        elif isinstance(via, list):
            pts += via
        pts.append(p1)
        self.line(*pts, **kw)

    def text(self, x, y, s, **kw):
        kw.setdefault('fontsize', FS)
        self.ax.text(x, y, s, **kw)

    def frame(self, x, y, w, h, label, color='#4a7bd0'):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=2', fc='none', ec=color, lw=1, ls='--'))
        self.ax.text(x + 6, y + 10, label, fontsize=FS - 0.5, color=color, va='center')

    def powergui(self, x, y):
        self.blk(x, y, 64, 26, 'Continuous', 'powergui', fs=FS - 1)
        self.ax.texts[-2].set_color('#1f4fd0')

    def save(self, name):
        self.fig.savefig(os.path.join(OUT, name), dpi=170, facecolor='white')
        plt.close(self.fig)


def motor_block(d, x, y, id_, name=None):
    return d.blk(x, y, 110, 74, f'DC Motor {id_}\n\nRa{id_}, La{id_}\nJ{id_}, B{id_}, kΦ{id_}', name or f'DC Machine {id_} (Subsystem)',
                 fc='#fffbe6', nin=2, nout=3, inl=['Va', 'TL'], outl=['θ', 'ω', 'ia'])


# ---------------------------------------------------------------- 1. mo hinh dong co
def fig_motor():
    d = D(1000, 360, 'DC_OpenLoop_700_1400 / DC Machine i (mô hình phương trình vi phân phần ứng – cơ)')
    st = d.step(30, 70, 'Step_Va', 'Va = 220 V')
    s1 = d.sum(130, 85, '+--', name='Sum_e')
    g1 = d.gain(175, 70, '1/La', 'L_inv')
    i1 = d.integ(250, 69, 'Int_i')
    gt = d.gain(340, 70, 'kΦ', 'G_Te')
    s2 = d.sum(440, 85, '+--', name='Sum_T')
    g2 = d.gain(485, 70, '1/J', 'J_inv')
    i2 = d.integ(560, 69, 'Int_w')
    i3 = d.integ(660, 69, 'Int_th')
    gr = d.gain(230, 160, 'Ra', 'G_R', left=True)
    ge = d.gain(300, 225, 'kΦ', 'G_E', left=True)
    gb = d.gain(500, 160, 'B', 'G_B', left=True)
    tl = d.step(380, 10, 'Step_TL', 'TL = Tn (tải)')
    d.conn(st, s1); d.conn(s1, g1); d.conn(g1, i1); d.conn(i1, gt); d.conn(gt, s2)
    d.conn(s2, g2); d.conn(g2, i2); d.conn(i2, i3)
    xi = i1['o'][0][0] + 15
    d.line((xi, 85), (xi, 175), gr['i'][0], dot=True)
    d.line(gr['o'][0], (130, 175), (130, 96))
    xw = i2['o'][0][0] + 18
    d.line((xw, 85), (xw, 240), ge['i'][0], dot=True)
    d.line(ge['o'][0], (100, 240), (100, 55), (130, 55), s1['i'][2])
    d.line((xw, 175), gb['i'][0], dot=True)
    d.line(gb['o'][0], (440, 175), (440, 96))
    d.line(tl['o'][0], (440, 25), (440, 74))
    mux = d.blk(770, 50, 8, 120, '', 'Mux', fc='black')
    sc = d.scope(870, 90, 'Scope', 3)
    tw = d.blk(860, 200, 70, 30, 'y1\n(timeseries)', 'To Workspace')
    d.line(i3['o'][0], (770, 85), txt='θ (goc)', txtpos=(735, 78))
    d.line((xw, 85), (xw, 60), (745, 60), (745, 110), (770, 110), dot=True, txt='ω', txtpos=(755, 104))
    d.line((xi, 85), (xi, 40), (757, 40), (757, 140), (770, 140), dot=True, txt='ia', txtpos=(763, 134))
    d.line((778, 110), sc['i'][1])
    d.line((820, 110), (820, 215), tw['i'][0], dot=True)
    d.text(180, 300, 'Phần điện:  La·dia/dt = Va − Ra·ia − kΦ·ω', fontsize=FS + 0.5)
    d.text(180, 320, 'Phần cơ:     J·dω/dt = kΦ·ia − B·ω − TL ,   dθ/dt = ω', fontsize=FS + 0.5)
    d.powergui(30, 290)
    d.save('d_motor.png')


# ---------------------------------------------------------------- 2. vong dong dien
def fig_current():
    d = D(1000, 420, 'Current_Loop_DCi : (a) PI dùng tham số động cơ + bù sức điện động ;  (b) PI không dùng tham số')
    for row, (y0, lab) in enumerate(((40, '(a)'), (240, '(b)'))):
        d.text(10, y0 + 40, lab, fontsize=FS + 2, fontweight='bold')
        r = d.blk(40, y0 + 25, 60, 30, 'Repeating\nSequence', 'i* (đặt)', fs=FS - 1.5)
        s = d.sum(150, y0 + 40, '+-')
        pi = d.blk(190, y0 + 22, 80, 36, 'PI(s)', 'PI_i: Kp=La·ωci, Ki=Ra·ωci' if row == 0 else 'PI_i: Kp=1, Ki=100', fs=FS + 1)
        d.conn(r, s); d.conn(s, pi)
        if row == 0:
            s2 = d.sum(320, y0 + 40, '++')
            d.conn(pi, s2)
            ff = d.gain(300, y0 + 112, 'kΦ', 'Bù E = kΦ·ω', left=True)
            d.line(ff['o'][0], (320, y0 + 127), (320, y0 + 51))
            nxt = s2
        else:
            nxt = pi
        sat = d.sat(370, y0 + 25, 'Sat ±220 V')
        d.conn(nxt, sat)
        br = d.blk(450, y0 + 18, 80, 44, 'H-Bridge\n(PWM, mô hình\ntrung bình)', None, fs=FS - 1.5)
        d.conn(sat, br)
        m = motor_block(d, 590, y0 + 5, 'i')
        d.conn(br, m, bi=0, via='h')
        tl = d.step(520, y0 + 85, 'TL = Tn')
        d.line(tl['o'][0], (570, y0 + 100), (570, m['i'][1][1]), m['i'][1])
        sc = d.scope(900, y0 + 15, 'Scope', 2)
        d.line(m['o'][2], (760, m['o'][2][1]), (760, y0 + 160), (150, y0 + 160), (150, y0 + 51), txt='ia (phản hồi)', txtpos=(450, y0 + 154))
        d.line((760, m['o'][2][1]), (840, m['o'][2][1]), (840, sc['i'][1][1]), sc['i'][1], dot=True)
        d.line((120, y0 + 40), (120, y0 + 0), (870, y0 + 0), (870, sc['i'][0][1]), sc['i'][0], dot=True, txt='i*', txtpos=(500, y0 - 6))
        if row == 0:
            d.line(m['o'][1], (790, m['o'][1][1]), (790, y0 + 127), ff['i'][0], txt='ω', txtpos=(800, y0 + 117))
    d.save('d_current.png')


# ---------------------------------------------------------------- 3. vong toc do
def fig_speed(with_cur=True):
    d = D(1000, 260, ('Speed_Cascade_DCi : PI tốc độ → giới hạn dòng → PI dòng điện → cầu H → động cơ' if with_cur else
                      'Speed_NoCurrent_DCi : PI tốc độ → điện áp trực tiếp (không có vòng dòng điện)'))
    st = d.step(30, 60, 'ω* (Step)')
    s = d.sum(120, 75, '+-')
    pw = d.blk(155, 55, 90, 40, 'PI(s) 2DOF', 'PI_w: Kp=J·ωcw/kΦ' if with_cur else 'PI_w: Kp=2, Ki=20', fs=FS + 0.5)
    d.conn(st, s); d.conn(s, pw)
    if with_cur:
        sat = d.sat(275, 60, 'Imax = 2.5·In')
        si = d.sum(350, 75, '+-')
        pi = d.blk(385, 55, 80, 40, 'PI(s)', 'PI_i: La·ωci, Ra·ωci', fs=FS + 1)
        d.conn(pw, sat); d.conn(sat, si, txt='i*', txtpos=(335, 68)); d.conn(si, pi)
        last = pi
    else:
        last = pw
    sv = d.sat(495, 60, 'Sat ±220 V')
    d.conn(last, sv)
    br = d.blk(560, 53, 70, 44, 'H-Bridge\n(mô hình\ntrung bình)', None, fs=FS - 1.5)
    d.conn(sv, br)
    m = motor_block(d, 680, 40, 'i')
    d.conn(br, m, bi=0, via='h', txt='Va', txtpos=(655, 62))
    tl = d.step(600, 130, 'TL (t = 1 s)')
    d.line(tl['o'][0], (660, 145), (660, m['i'][1][1]), m['i'][1])
    sc = d.scope(920, 40, 'Scope', 3)
    for k in range(3):
        d.line(m['o'][k], (850 + 10 * k, m['o'][k][1]), (850 + 10 * k, sc['i'][k][1]), sc['i'][k])
    d.line((860, m['o'][1][1]), (860, 215), (120, 215), (120, 86), dot=True, txt='ω (phản hồi tốc độ)', txtpos=(450, 209))
    if with_cur:
        d.line((870, m['o'][2][1]), (870, 185), (350, 185), (350, 86), dot=True, txt='ia (phản hồi dòng)', txtpos=(600, 179))
    d.save('d_speed_cur.png' if with_cur else 'd_speed_nocur.png')


# ---------------------------------------------------------------- 4. vong vi tri
def fig_pos(mode):
    ttl = {'full': 'Position_3Loop_DCi : vị trí (P + giới hạn √) → tốc độ (PI) → dòng điện (PI)',
           'speed': 'Position_2Loop_DCi : vị trí (P + giới hạn √) → tốc độ (PI → điện áp)',
           'direct': 'Position_Direct_DCi : PID vị trí → điện áp trực tiếp'}[mode]
    d = D(1000, 270, ttl)
    st = d.step(20, 60, 'θ* (Step 50 rad)')
    s = d.sum(100, 75, '+-')
    d.conn(st, s)
    if mode == 'direct':
        p = d.blk(135, 55, 100, 40, 'PID(s)', 'PID_θ: Kp=60, Ki=20, Kd=4', fs=FS + 1)
        d.conn(s, p); last = p
    else:
        p = d.blk(135, 55, 80, 40, 'P + √(2a|e|)\nsat ±ωn', 'Pos_P: Kθ = 15', fs=FS - 1)
        d.conn(s, p)
        sw = d.sum(255, 75, '+-')
        d.conn(p, sw, txt='ω*', txtpos=(235, 68))
        pw = d.blk(290, 55, 80, 40, 'PI(s)', 'PI_w' + (': J·ωcw/kΦ' if mode == 'full' else ': Kp=2, Ki=20'), fs=FS + 1)
        d.conn(sw, pw); last = pw
        if mode == 'full':
            sat = d.sat(395, 60, 'Imax')
            si = d.sum(465, 75, '+-')
            pi = d.blk(495, 55, 70, 40, 'PI(s)', 'PI_i', fs=FS + 1)
            d.conn(pw, sat); d.conn(sat, si); d.conn(si, pi); last = pi
    sv = d.sat(590, 60, '±220 V')
    d.conn(last, sv)
    m = motor_block(d, 680, 40, 'i')
    d.conn(sv, m, bi=0, via='h', txt='Va', txtpos=(655, 62))
    tl = d.step(610, 140, 'TL (t = 1 s)')
    d.line(tl['o'][0], (660, 155), (660, m['i'][1][1]), m['i'][1])
    sc = d.scope(920, 40, 'Scope', 3)
    for k in range(3):
        d.line(m['o'][k], (845 + 12 * k, m['o'][k][1]), (845 + 12 * k, sc['i'][k][1]), sc['i'][k])
    d.line((845, m['o'][0][1]), (845, 235), (100, 235), (100, 86), dot=True, txt='θ (phản hồi vị trí)', txtpos=(450, 229))
    if mode != 'direct':
        d.line((857, m['o'][1][1]), (857, 210), (255, 210), (255, 86), dot=True, txt='ω', txtpos=(560, 204))
    if mode == 'full':
        d.line((869, m['o'][2][1]), (869, 185), (465, 185), (465, 86), dot=True, txt='ia', txtpos=(700, 179))
    d.save(f'd_pos_{mode}.png')


# ---------------------------------------------------------------- 5. dong toc
def fig_sync():
    d = D(1000, 430, 'Sync_Speed_DC1_DC2 : bộ chọn chiến lược (1 – song song, 2 – chủ–tớ) + khâu bù chéo (cross-coupling)')
    rp = d.blk(20, 42, 60, 34, 'Hình thang\nω*(t)', 'Signal Builder', fs=FS - 1)
    c1 = d.blk(150, 25, 180, 70, 'Cascade 1\nPI_w1 → Imax → PI_i1', 'Speed Ctrl DC1', fc='#eef4ff', nin=3, inl=['ω*', 'ω1', 'Δi*'])
    m1 = motor_block(d, 410, 30, '1', 'DC1 – 700 W')
    d.conn(rp, c1, via='h')
    d.conn(c1, m1, bi=0, via='h')
    w1y = m1['o'][1][1]
    d.line(m1['o'][1], (560, w1y), (560, 150), (120, 150), (120, c1['i'][1][1]), c1['i'][1], txt='ω1', txtpos=(340, 144))
    t1 = d.step(345, 85, 'TL1 (t = 1.5 s)')
    d.line(t1['o'][0], (390, 100), (390, m1['i'][1][1]), m1['i'][1])
    sw = d.blk(40, 255, 50, 60, 'Multiport\nSwitch', 'Chiến lược', fs=FS - 2, nin=2, inl=['1', '2'])
    c2 = d.blk(150, 245, 180, 70, 'Cascade 2\nPI_w2 → Imax → PI_i2', 'Speed Ctrl DC2', fc='#eef4ff', nin=3, inl=['ω*', 'ω2', 'Δi*'])
    m2 = motor_block(d, 410, 250, '2', 'DC2 – 1400 W')
    d.conn(sw, c2, via='h')
    d.conn(c2, m2, bi=0, via='h')
    w2y = m2['o'][1][1]
    d.line(m2['o'][1], (620, w2y), (620, 370), (120, 370), (120, c2['i'][1][1]), c2['i'][1], txt='ω2', txtpos=(340, 364))
    t2 = d.step(345, 305, 'TL2 (t = 1.0 s)')
    d.line(t2['o'][0], (390, 320), (390, m2['i'][1][1]), m2['i'][1])
    d.line((95, 59), (95, 215), (25, 215), (25, sw['i'][0][1]), sw['i'][0], dot=True, txt='ω*', txtpos=(60, 209))
    d.line((560, 150), (560, 195), (12, 195), (12, sw['i'][1][1]), sw['i'][1], dot=True, txt='ω1 (chủ – tớ)', txtpos=(300, 189))
    se = d.sum(700, 170, '+-', name='e = ω1 − ω2')
    d.line((560, w1y), (650, w1y), (650, 170), se['i'][0], dot=True)
    d.line((620, w2y), (700, w2y), se['i'][1], dot=True)
    kc = d.gain(740, 155, 'Kc', 'Cross-coupling')
    d.conn(se, kc)
    d.line(kc['o'][0], (810, 170), (810, 8), (135, 8), (135, c1['i'][2][1]), c1['i'][2], txt='−Kc·e', txtpos=(480, 3))
    d.line((810, 170), (810, 410), (135, 410), (135, c2['i'][2][1]), c2['i'][2], dot=True, txt='+Kc·e', txtpos=(480, 404))
    sc = d.scope(905, 180, 'Scope ω1, ω2, e', 3)
    d.line((650, w1y), (870, w1y), (870, sc['i'][0][1]), sc['i'][0], dot=True)
    d.line((700, w2y), (885, w2y), (885, sc['i'][1][1]), sc['i'][1])
    d.line((725, 170), (720, 240), (895, 240), (895, sc['i'][2][1]), sc['i'][2], dot=True)
    d.save('d_sync.png')


# ---------------------------------------------------------------- 6. nhieu truc
def fig_multi():
    d = D(1000, 420, 'Multi_Axis_Position : bộ lập quỹ đạo đồng bộ + 3 vòng vị trí cascade')
    tg = d.blk(20, 160, 110, 80, 'Trajectory\nGenerator\n(đa thức bậc 5,\ncùng T = 0.8 s)', 'MATLAB Function', fs=FS - 1.5, nout=6,
               fc='#f2fff2')
    names = [('1', 'Trục 1: DC1, θ = 30 rad'), ('2', 'Trục 2: DC2, θ = 60 rad'), ('1', 'Trục 3: DC1, θ = −20 rad')]
    for k, (mid, nm) in enumerate(names):
        y = 30 + k * 130
        s = d.sum(210, y + 30, '+-')
        p = d.blk(240, y + 12, 70, 36, 'Kθ + √', 'Pos_P', fs=FS)
        sf = d.sum(345, y + 30, '++')
        c = d.blk(380, y + 8, 150, 44, 'PI_w → Imax → PI_i', f'Cascade trục {k+1}', fc='#eef4ff', fs=FS)
        m = motor_block(d, 590, y - 5, mid, nm)
        d.line(tg['o'][2 * k], (170, tg['o'][2 * k][1]), (170, y + 30), s['i'][0], txt='θ*', txtpos=(185, y + 22))
        d.line(tg['o'][2 * k + 1], (160 + 0, tg['o'][2 * k + 1][1]), (160, y + 3), (345, y + 3), sf['i'][2], txt='ω* (bù trước)', txtpos=(300, y - 3))
        d.conn(s, p); d.conn(p, sf); d.conn(sf, c); d.conn(c, m, bi=0, via='h')
        d.line(m['o'][0], (720, m['o'][0][1]), (720, y + 85), (210, y + 85), (210, y + 41), txt='θ', txtpos=(470, y + 79))
        d.line((720, m['o'][0][1]), (880, m['o'][0][1]), (880, 170 + 10 * k), (900, 170 + 10 * k), dot=True)
    sc = d.scope(900, 150, 'Scope θ1, θ2, θ3', 3)
    d.save('d_multi.png')


# ---------------------------------------------------------------- 7. ma khai bao
def fig_code(lines, name, w=11.5):
    fig = plt.figure(figsize=(w, 0.3 * len(lines) + 0.3))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
    n = len(lines)
    ax.set_xlim(0, 1); ax.set_ylim(n + 0.5, 0.2)
    ax.plot([0.048, 0.048], [0.2, n + 0.5], color='#ccc', lw=1)
    for k, ln in enumerate(lines, 1):
        ax.text(0.04, k, str(k), ha='right', va='center', family='DejaVu Sans Mono', fontsize=10, color='#888')
        if '%' in ln:
            code, cm = ln.split('%', 1)
            cm = '%' + cm
        else:
            code, cm = ln, ''
        ax.text(0.055, k, code, ha='left', va='center', family='DejaVu Sans Mono', fontsize=10, color='black')
        if cm:
            ax.text(0.055 + 0.00725 * len(code), k, cm, ha='left', va='center', family='DejaVu Sans Mono', fontsize=10, color='#228b22')
    fig.savefig(os.path.join(OUT, name), dpi=130, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    fig_motor(); fig_current(); fig_speed(True); fig_speed(False)
    for md in ('full', 'speed', 'direct'): fig_pos(md)
    fig_sync(); fig_multi()
    src = open(os.path.join(os.path.dirname(__file__), '..', 'matlab', 'thong_so_dong_co.m'), encoding='utf-8').read().splitlines()
    fig_code(src, 'h_code_thongso.png')
    print('ok')
