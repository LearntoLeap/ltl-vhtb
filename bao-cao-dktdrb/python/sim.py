"""Mo phong dong co DC + cac vong dieu khien (tuong duong mo hinh Simulink trong build_all.m).
Tich phan Euler buoc nho dt = 1e-5 s (sai lech so voi ode45 khong dang ke)."""
import numpy as np

U = 220.0
RPM = 2 * np.pi / 60

def motor(P, n, L, R, J, B, kPhi):
    wn = n * RPM
    Tn = P / wn
    In = (Tn + B * wn) / kPhi
    m = dict(P=P, n=n, wn=wn, L=L, R=R, J=J, B=B, kPhi=kPhi, Tn=Tn, In=In, Imax=2.5 * In)
    wci, wcw = 800.0, 60.0
    m.update(Kpi=L * wci, Kii=R * wci, Kpw=J * wcw / kPhi)
    m['Kiw'] = m['Kpw'] * wcw / 4
    return m

M1 = motor(700, 2050, 0.02, 4.0, 0.005, 0.0005, 0.96)
M2 = motor(1400, 2550, 0.01, 2.0, 0.01, 0.001, 0.77)

# He so khi KHONG dung tham so dong co (chinh tay, giong nhau cho ca 2 dong co)
PI_I_GENERIC = dict(Kp=1.0, Ki=100.0)
# PI toc do -> dien ap (khong co vong dong)
def pi_w_volt(m):
    # chinh dinh theo thuc nghiem: Kp ~ 1 V/(rad/s), Ki ~ 10 V/rad
    return dict(Kp=2.0, Ki=20.0)


class PI:
    """PI (2DOF: b*r - y cho khau P) + bao hoa + chong bao hoa back-calculation."""
    def __init__(self, Kp, Ki, lim=np.inf, b=1.0, Kb=None, Kd=0.0, N=100.0):
        self.Kp, self.Ki, self.lim, self.b = Kp, Ki, lim, b
        self.Kb = (Ki / Kp if Kp else 0.0) if Kb is None else Kb
        self.Kd, self.N = Kd, N
        self.xi = 0.0
        self.xd = 0.0  # trang thai bo loc dao ham

    def __call__(self, r, y, dt):
        e = r - y
        ud = 0.0
        if self.Kd:
            # D(s) = Kd*N*s/(s+N) tac dong len -y (tranh "derivative kick")
            ud = self.Kd * self.N * (-y - self.xd)
            self.xd += dt * self.N * (-y - self.xd)
        u0 = self.Kp * (self.b * r - y) + self.xi + ud
        u = float(np.clip(u0, -self.lim, self.lim))
        self.xi += dt * (self.Ki * e + self.Kb * (u - u0))
        return u


def step(t, t0, a, b=0.0):
    return a if t >= t0 else b


class Plant:
    def __init__(self, m):
        self.m = m
        self.i = self.w = self.th = 0.0

    def update(self, va, TL, dt):
        m = self.m
        va = float(np.clip(va, -U, U))
        di = (va - m['R'] * self.i - m['kPhi'] * self.w) / m['L']
        dw = (m['kPhi'] * self.i - m['B'] * self.w - TL) / m['J']
        self.i += dt * di
        self.th += dt * self.w
        self.w += dt * dw
        return va


def run(T, dt, ctrl, plants, TLfun):
    """ctrl(t, plants, dt) -> list of voltages; TLfun(t) -> list of loads.
    Tra ve dict mang: t, th[k], w[k], i[k], va[k], + extra log."""
    n = int(round(T / dt)) + 1
    t = np.arange(n) * dt
    K = len(plants)
    out = {k: np.zeros((K, n)) for k in ('th', 'w', 'i', 'va', 'ref')}
    for j in range(n):
        tj = t[j]
        vas, refs = ctrl(tj, plants, dt)
        TLs = TLfun(tj)
        for k, p in enumerate(plants):
            out['th'][k, j], out['w'][k, j], out['i'][k, j] = p.th, p.w, p.i
            out['ref'][k, j] = refs[k]
            out['va'][k, j] = p.update(vas[k], TLs[k], dt)
    out['t'] = t
    return out


# ------------------------------------------------------------------ chi tieu
def metrics(t, y, r_final, t0, band=0.02):
    """thoi gian len 10-90 %, do vot lo %, thoi gian xac lap (2 %), sai so xac lap"""
    y0 = y[np.searchsorted(t, t0)]
    dy = r_final - y0
    s = (y - y0) / dy
    idx = t >= t0
    tt, ss = t[idx], s[idx]
    try:
        t10 = tt[np.argmax(ss >= 0.1)]
        t90 = tt[np.argmax(ss >= 0.9)]
        tr = t90 - t10 if np.any(ss >= 0.9) else np.nan
    except Exception:
        tr = np.nan
    os_ = max(0.0, (ss.max() - 1) * 100)
    out = np.abs(ss - 1) > band
    ts = (tt[np.where(out)[0][-1]] - t0) if out.any() else 0.0
    return dict(tr=tr, os=os_, ts=ts)
