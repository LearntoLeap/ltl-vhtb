"""Cac kich ban mo phong cho bao cao."""
import numpy as np
from sim import *

DT = 1e-5

# ---------------- I. ho mach vong: Va = 220 V, tai dinh muc ----------------
def open_loop(m, T=1.0, TL_mode='rated'):
    p = Plant(m)
    def ctrl(t, ps, dt):
        return [U], [U]
    if TL_mode == 'rated':
        TL = lambda t: [m['Tn']]
    else:  # khoi dong khong tai, dong tai dinh muc tai 0.5 s
        TL = lambda t: [step(t, 0.5, m['Tn'])]
    return run(T, DT, ctrl, [p], TL)


# ---------------- II.1 vong dong dien ----------------
def iref_profile(m, t):
    In = m['In']
    if t < 0.02: return 0.0
    if t < 0.07: return In
    if t < 0.12: return 2 * In
    return 0.5 * In

def current_loop(m, model_based=True, T=0.17):
    p = Plant(m)
    if model_based:
        c = PI(m['Kpi'], m['Kii'], lim=U)
    else:
        c = PI(PI_I_GENERIC['Kp'], PI_I_GENERIC['Ki'], lim=U)
    def ctrl(t, ps, dt):
        r = iref_profile(m, t)
        u = c(r, ps[0].i, dt)
        if model_based:  # bu suc dien dong E = kPhi*w (dung tham so dong co)
            u += m['kPhi'] * ps[0].w
        return [u], [r]
    TL = lambda t: [m['Tn']]
    return run(T, DT, ctrl, [p], TL)


# ---------------- II.2 vong toc do ----------------
def speed_loop(m, wref, with_current=True, T=1.6, t0=0.1, tL=1.0, Lfrac=1.0):
    p = Plant(m)
    if with_current:
        cw = PI(m['Kpw'], m['Kiw'], lim=m['Imax'], b=0.5)
        ci = PI(m['Kpi'], m['Kii'], lim=U)
    else:
        g = pi_w_volt(m)
        cw = PI(g['Kp'], g['Ki'], lim=U, b=0.5)
    def ctrl(t, ps, dt):
        r = step(t, t0, wref)
        if with_current:
            istar = cw(r, ps[0].w, dt)
            u = ci(istar, ps[0].i, dt)
        else:
            u = cw(r, ps[0].w, dt)
        return [u], [r]
    TL = lambda t: [step(t, tL, Lfrac * m['Tn'])]
    return run(T, DT, ctrl, [p], TL)


# ---------------- II.3 vong vi tri ----------------
KTH = 15.0  # he so P vi tri (1/s)
def amax(m):  # gia toc ham cho phep (60 % gia toc lon nhat khi dong = Imax)
    return 0.6 * m['kPhi'] * m['Imax'] / m['J']

def pos_P(m, e):
    # bo dieu khien P vi tri co gioi han goc can bac hai (ham kip truoc dich)
    a = amax(m)
    return np.sign(e) * min(KTH * abs(e), np.sqrt(2 * a * abs(e)), m['wn'])
def pid_direct(m):
    # PID vi tri -> dien ap, chinh dinh thu nghiem
    return dict(Kp=60.0, Ki=20.0, Kd=4.0)

def pos_loop(m, thref, mode='full', T=1.5, t0=0.1, tL=1.0, Lfrac=0.5):
    p = Plant(m)
    wlim = m['wn']
    if mode == 'full':
        cth = PI(KTH, 0.0, lim=wlim)
        cw = PI(m['Kpw'], m['Kiw'], lim=m['Imax'])
        ci = PI(m['Kpi'], m['Kii'], lim=U)
    elif mode == 'speed':
        cth = PI(KTH, 0.0, lim=wlim)
        g = pi_w_volt(m)
        cw = PI(g['Kp'], g['Ki'], lim=U)
    else:
        g = pid_direct(m)
        cth = PI(g['Kp'], g['Ki'], lim=U, Kd=g['Kd'], Kb=1.0)
    def ctrl(t, ps, dt):
        r = step(t, t0, thref)
        pp = ps[0]
        if mode == 'full':
            ws = pos_P(m, r - pp.th)
            u = ci(cw(ws, pp.w, dt), pp.i, dt)
        elif mode == 'speed':
            u = cw(pos_P(m, r - pp.th), pp.w, dt)
        else:
            u = cth(r, pp.th, dt)
        return [u], [r]
    TL = lambda t: [step(t, tL, Lfrac * m['Tn'])]
    return run(T, DT, ctrl, [p], TL)


# ---------------- III.1 dong toc 2 dong co ----------------
def wprofile(t, W=150.0):
    # hinh thang: tang 0.1-0.4 s, giu, giam 2.0-2.3 s
    if t < 0.1: return 0.0
    if t < 0.4: return W * (t - 0.1) / 0.3
    if t < 2.0: return W
    if t < 2.3: return W * (2.3 - t) / 0.3
    return 0.0

def sync_speed(strategy='parallel', T=2.6):
    ps = [Plant(M1), Plant(M2)]
    C = []
    for m in (M1, M2):
        C.append((PI(m['Kpw'], m['Kiw'], lim=m['Imax']), PI(m['Kpi'], m['Kii'], lim=U)))
    KC1, KC2 = M1['J']*60/M1['kPhi'], M2['J']*60/M2['kPhi']
    def ctrl(t, pl, dt):
        r1 = wprofile(t)
        if strategy == 'parallel':
            r2 = r1
        elif strategy == 'master':
            r2 = pl[0].w           # chu - to: dat DC2 = toc do do duoc cua DC1
        else:  # cross: song song + bu sai lech chéo (cross-coupling)
            r2 = r1
        refs = [r1, r2]
        us = []
        for k in range(2):
            cw, ci = C[k]
            rk = refs[k]
            ist = cw(rk, pl[k].w, dt)
            if strategy == 'cross':
                # bu cheo (cross-coupling) tren tin hieu dat dong: Kc*(w1 - w2)
                e = pl[0].w - pl[1].w
                ist += (-KC1 if k == 0 else KC2) * e
            us.append(ci(ist, pl[k].i, dt))
        return us, refs
    TL = lambda t: [step(t, 1.5, M1['Tn']), step(t, 1.0, M2['Tn'])]
    return run(T, DT, ctrl, ps, TL)


# ---------------- III.2 vi tri dong thoi nhieu dong co ----------------
AXES = [  # (ten, dong co, goc dich rad)
    ('Trục 1 (DC1)', M1, 30.0),
    ('Trục 2 (DC2)', M2, 60.0),
    ('Trục 3 (DC1)', M1, -20.0),
]
TMOVE, T0, TBACK = 0.8, 0.1, 1.6

def quintic(t, t0, T, a, b):
    if t <= t0: return a, 0.0
    if t >= t0 + T: return b, 0.0
    s = (t - t0) / T
    pos = a + (b - a) * (10 * s**3 - 15 * s**4 + 6 * s**5)
    vel = (b - a) * (30 * s**2 - 60 * s**3 + 30 * s**4) / T
    return pos, vel

def multi_pos(mode='traj', T=2.6):
    ps = [Plant(m) for _, m, _ in AXES]
    C = [(PI(KTH, 0.0, lim=m['wn']), PI(m['Kpw'], m['Kiw'], lim=m['Imax']), PI(m['Kpi'], m['Kii'], lim=U))
         for _, m, _ in AXES]
    def ctrl(t, pl, dt):
        us, refs = [], []
        for k, (_, m, tgt) in enumerate(AXES):
            if mode == 'traj':
                if t < TBACK:
                    r, v = quintic(t, T0, TMOVE, 0.0, tgt)
                else:
                    r, v = quintic(t, TBACK, TMOVE, tgt, 0.0)
            else:
                r = tgt if T0 <= t < TBACK else 0.0
                v = 0.0
            cth, cw, ci = C[k]
            ws = pos_P(m, r - pl[k].th) + v     # bu truoc toc do
            ws = float(np.clip(ws, -m['wn'], m['wn']))
            us.append(ci(cw(ws, pl[k].w, dt), pl[k].i, dt))
            refs.append(r)
        return us, refs
    TL = lambda t: [step(t, 1.2, 0.5 * m['Tn']) for _, m, _ in AXES]
    return run(T, DT, ctrl, ps, TL)
