import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cases import *

OUT = os.path.join(os.path.dirname(__file__), 'fig')
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.grid': True,
                     'grid.alpha': 0.35, 'lines.linewidth': 1.7})
R_, B_, Y_ = '#e8221b', '#1a1aee', '#b5b500'
LBL = ['goc (rad)', '<Speed wm (rad/s)>', '<Armature current ia (A)>']
RES = {}

def dec(o, s=10):
    return {k: (v[..., ::s] if isinstance(v, np.ndarray) else v) for k, v in o.items()}

def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches='tight')
    plt.close(fig)

def scope(ax3, o, k=0, title=None, ref=None, vlines=()):
    t = o['t']
    data = [o['th'][k], o['w'][k], o['i'][k]]
    for r, ax in enumerate(ax3):
        ax.plot(t, data[r], color=[R_, B_, Y_][r])
        if ref is not None and ref[0] == r:
            ax.plot(t, ref[1], 'k--', lw=1.1, label='giá trị đặt')
            ax.legend(loc='lower right', fontsize=8)
        ax.set_title(LBL[r] if (r or title is None) else f'{title} – goc', fontsize=10,
                     fontweight='bold' if r == 0 and title else 'normal')
        for v in vlines:
            ax.axvline(v, color='k', ls='--', lw=0.9)
    ax3[-1].set_xlabel('t (s)')

def scope_fig(o, ttl, name, **kw):
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 5.2), sharex=True)
    fig.suptitle(ttl, fontweight='bold')
    scope(ax, o, **kw)
    fig.tight_layout(); save(fig, name)

def scope2(oL, oR, tL, tR, ttl, name, **kw):
    fig, ax = plt.subplots(3, 2, figsize=(10.5, 5.4), sharex=True)
    if ttl: fig.suptitle(ttl, fontweight='bold')
    scope(ax[:, 0], oL, title=tL, **kw.get('L', {}))
    scope(ax[:, 1], oR, title=tR, **kw.get('R', {}))
    fig.tight_layout(); save(fig, name)

# ================= I. danh gia thong so =================
ol = [dec(open_loop(m)) for m in (M1, M2)]
for k, (m, o) in enumerate(zip((M1, M2), ol)):
    t = o['t']; w = o['w'][0]; i = o['i'][0]
    me = metrics(t, w, w[-1], 0.0)
    RES[f'ol{k+1}'] = dict(w=w[-1], rpm=w[-1] / RPM, i=i[-1], ipk=i.max(), tpk=t[i.argmax()], ts=me['ts'], tr=me['tr'])
    scope_fig(o, f'Động cơ {k+1} ({m["P"]} W): Va = 220 V, tải định mức Tn = {m["Tn"]:.2f} N·m',
              f'h_ol_dc{k+1}.png')

fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True)
for k, o in enumerate(ol):
    ax[0].plot(o['t'], o['w'][0], label=f'DC{k+1}')
    ax[1].plot(o['t'], o['i'][0], label=f'DC{k+1}')
ax[0].axhline(M1['wn'], color='C0', ls=':', lw=1); ax[0].axhline(M2['wn'], color='C1', ls=':', lw=1)
ax[0].set_ylabel('Tốc độ (rad/s)'); ax[1].set_ylabel('Dòng phần ứng (A)'); ax[1].set_xlabel('t (s)')
ax[0].legend(); ax[1].legend()
ax[0].set_title('So sánh 2 động cơ khi cấp 220 V, tải định mức', fontweight='bold')
fig.tight_layout(); save(fig, 'h_ol_sosanh.png')

ol2 = [dec(open_loop(m, TL_mode='step')) for m in (M1, M2)]
fig, ax = plt.subplots(3, 1, figsize=(7.2, 5.6), sharex=True)
for k, (m, o) in enumerate(zip((M1, M2), ol2)):
    t = o['t']
    ax[0].plot(t, o['w'][0] / RPM, label=f'DC{k+1}')
    ax[1].plot(t, o['i'][0], label=f'DC{k+1}')
    ax[2].plot(t, m['kPhi'] * o['i'][0] * o['w'][0], label=f'DC{k+1}: P điện từ')
    n0 = np.searchsorted(t, 0.49)
    RES[f'nl{k+1}'] = dict(w0=o['w'][0][n0], n0=o['w'][0][n0] / RPM, i0=o['i'][0][n0], wL=o['w'][0][-1], nL=o['w'][0][-1] / RPM, iL=o['i'][0][-1])
for a in ax: a.axvline(0.5, color='k', ls='--', lw=0.9)
ax[0].axhline(2050, color='C0', ls=':'); ax[0].axhline(2550, color='C1', ls=':')
ax[0].set_ylabel('n (vòng/phút)'); ax[1].set_ylabel('ia (A)'); ax[2].set_ylabel('P (W)'); ax[2].set_xlabel('t (s)')
for a in ax: a.legend(fontsize=8, loc='right')
ax[0].set_title('Khởi động không tải, đóng tải định mức tại t = 0.5 s', fontweight='bold')
fig.tight_layout(); save(fig, 'h_ol_dongtai.png')

# ================= II.1 vong dong dien =================
for k, m in enumerate((M1, M2)):
    a = dec(current_loop(m, True), 2); b = dec(current_loop(m, False), 2)
    t = a['t']
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 5.8), sharex=True)
    ax[0].plot(t, a['ref'][0], 'k--', lw=1.2, label='i* (đặt)')
    ax[0].plot(t, a['i'][0], color=B_, label='PI dùng tham số ĐC (Kp=L·ωc, Ki=R·ωc, bù E)')
    ax[0].plot(t, b['i'][0], color=R_, label=f'PI không dùng tham số (Kp={PI_I_GENERIC["Kp"]:g}, Ki={PI_I_GENERIC["Ki"]:g})')
    ax[0].set_ylabel('ia (A)'); ax[0].legend(fontsize=7.5, loc='upper left')
    ax[0].set_title(f'Động cơ {k+1} ({m["P"]} W): đáp ứng vòng điều khiển dòng điện', fontweight='bold')
    ax[1].plot(t, a['ref'][0] - a['i'][0], color=B_, label='dùng tham số')
    ax[1].plot(t, b['ref'][0] - b['i'][0], color=R_, label='không dùng tham số')
    ax[1].set_ylabel('sai số i* − ia (A)'); ax[1].legend(fontsize=8)
    ax[2].plot(t, a['va'][0], color=B_, label='dùng tham số'); ax[2].plot(t, b['va'][0], color=R_, label='không dùng tham số')
    ax[2].set_ylabel('Va (V)'); ax[2].set_xlabel('t (s)'); ax[2].legend(fontsize=8)
    fig.tight_layout(); save(fig, f'h_cur_dc{k+1}.png')
    for tag, o in (('mb', a), ('gn', b)):
        tt, ii = o['t'], o['i'][0]
        n1 = np.searchsorted(tt, 0.0699)
        me = metrics(tt[:n1], ii[:n1], m['In'], 0.02)
        e2 = 2 * m['In'] - ii[np.searchsorted(tt, 0.1199)]
        e1 = m['In'] - ii[n1]
        RES[f'cur{k+1}{tag}'] = dict(tr=me['tr'], os=me['os'], ts=me['ts'], e1=e1, e2=e2, e2p=100 * e2 / (2 * m['In']),
                                    iae=float(np.sum(np.abs(o['ref'][0] - ii)) * (tt[1] - tt[0])))

# ================= II.2 vong toc do =================
WREF = {1: 200.0, 2: 250.0}
for k, m in enumerate((M1, M2), 1):
    a = dec(speed_loop(m, WREF[k], True)); b = dec(speed_loop(m, WREF[k], False))
    rw = (1, a['ref'][0])
    scope2(a, b, f'DC{k}: có vòng dòng điện', f'DC{k}: không có vòng dòng điện',
           f'Động cơ {k} ({m["P"]} W): điều khiển tốc độ, ω* = {WREF[k]:.0f} rad/s, tải Tn tại 1 s',
           f'h_spd_dc{k}.png', L=dict(ref=rw, vlines=(1.0,)), R=dict(ref=(1, b['ref'][0]), vlines=(1.0,)))
    for tag, o in (('c', a), ('n', b)):
        t, w, i, va = o['t'], o['w'][0], o['i'][0], o['va'][0]
        n1 = np.searchsorted(t, 0.999)
        me = metrics(t[:n1], w[:n1], WREF[k], 0.1)
        drop = WREF[k] - w[n1:].min()
        rec = t[n1:][np.where(np.abs(w[n1:] - WREF[k]) > 0.01 * WREF[k])[0][-1]] - 1.0 if np.any(np.abs(w[n1:] - WREF[k]) > 0.01 * WREF[k]) else 0
        RES[f'spd{k}{tag}'] = dict(tr=me['tr'], os=me['os'], ts=me['ts'], ipk=np.abs(i).max(), ipkr=np.abs(i).max() / m['In'],
                                   drop=drop, rec=rec, ess=WREF[k] - w[-1], va=va[-1], iend=i[-1])
    if k == 1: sp1 = (a, b)
    else: sp2 = (a, b)
fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True)
for (a, b), k in ((sp1, 1), (sp2, 2)):
    ax[0].plot(a['t'], a['w'][0], label=f'DC{k} – có vòng dòng'); ax[0].plot(b['t'], b['w'][0], '--', label=f'DC{k} – không vòng dòng')
    ax[1].plot(a['t'], a['i'][0], label=f'DC{k} – có vòng dòng'); ax[1].plot(b['t'], b['i'][0], '--', label=f'DC{k} – không vòng dòng')
ax[0].set_ylabel('ω (rad/s)'); ax[1].set_ylabel('ia (A)'); ax[1].set_xlabel('t (s)')
ax[0].legend(fontsize=7.5, ncol=2); ax[1].legend(fontsize=7.5, ncol=2)
ax[0].set_title('So sánh điều khiển tốc độ có / không có vòng dòng điện', fontweight='bold')
fig.tight_layout(); save(fig, 'h_spd_sosanh.png')

# ================= II.3 vong vi tri =================
THREF = 50.0
MODES = [('full', 'Vị trí + tốc độ + dòng điện'), ('speed', 'Vị trí + tốc độ'), ('direct', 'Điều khiển trực tiếp vị trí (PID)')]
for k, m in enumerate((M1, M2), 1):
    fig, ax = plt.subplots(3, 1, figsize=(7.4, 6.2), sharex=True)
    for j, (md, nm) in enumerate(MODES):
        o = dec(pos_loop(m, THREF, md))
        t = o['t']
        if j == 0: ax[0].plot(t, o['ref'][0], 'k--', lw=1.1, label='θ* = 50 rad')
        ax[0].plot(t, o['th'][0], label=nm, color=[B_, R_, '#2a9d2a'][j])
        ax[1].plot(t, o['w'][0], color=[B_, R_, '#2a9d2a'][j], label=nm)
        ax[2].plot(t, o['i'][0], color=[B_, R_, '#2a9d2a'][j], label=nm)
        th, i = o['th'][0], o['i'][0]
        n1 = np.searchsorted(t, 0.999)
        me = metrics(t[:n1], th[:n1], THREF, 0.1)
        RES[f'pos{k}{md}'] = dict(tr=me['tr'], os=me['os'], ts=me['ts'], ipk=np.abs(i).max(), ipkr=np.abs(i).max() / m['In'],
                                  dev=THREF - th[n1:].min(), ess=THREF - th[-1], wmax=o['w'][0].max())
    for a in ax: a.axvline(1.0, color='k', ls=':', lw=0.9)
    ax[0].set_ylabel('θ (rad)'); ax[1].set_ylabel('ω (rad/s)'); ax[2].set_ylabel('ia (A)'); ax[2].set_xlabel('t (s)')
    ax[0].legend(fontsize=7.5, loc='lower right'); ax[2].legend(fontsize=7.5)
    ax[0].set_title(f'Động cơ {k} ({m["P"]} W): điều khiển vị trí θ* = 50 rad, tải 0.5·Tn tại 1 s', fontweight='bold')
    fig.tight_layout(); save(fig, f'h_pos_dc{k}.png')
    # anh phong to quanh dich
    fig, ax = plt.subplots(1, 1, figsize=(7.2, 2.8))
    for j, (md, nm) in enumerate(MODES):
        o = dec(pos_loop(m, THREF, md))
        ax.plot(o['t'], o['th'][0], color=[B_, R_, '#2a9d2a'][j], label=nm)
    ax.axhline(THREF, color='k', ls='--', lw=1); ax.set_ylim(THREF - 2, THREF + 1.5); ax.set_xlim(0.2, 1.5)
    ax.set_ylabel('θ (rad)'); ax.set_xlabel('t (s)'); ax.legend(fontsize=7.5)
    ax.set_title(f'Động cơ {k}: phóng to vùng lân cận vị trí đích', fontweight='bold')
    fig.tight_layout(); save(fig, f'h_pos_zoom_dc{k}.png')

# ================= III.1 dong toc =================
STR = [('parallel', 'Song song (cùng ω*)'), ('master', 'Chủ – tớ (ω2* = ω1)'), ('cross', 'Song song + bù chéo')]
SO = {s: dec(sync_speed(s)) for s, _ in STR}
fig, ax = plt.subplots(3, 3, figsize=(12, 6.6), sharex=True)
for j, (s, nm) in enumerate(STR):
    o = SO[s]; t = o['t']
    ax[0, j].plot(t, o['ref'][0], 'k--', lw=1, label='ω*')
    ax[0, j].plot(t, o['w'][0], color=B_, label='ω1 (DC1)'); ax[0, j].plot(t, o['w'][1], color=R_, label='ω2 (DC2)')
    ax[0, j].set_title(nm, fontweight='bold'); ax[0, j].legend(fontsize=7)
    ax[1, j].plot(t, o['w'][0] - o['w'][1], color='#7b2cbf'); ax[1, j].set_title('Sai lệch đồng tốc ω1 − ω2 (rad/s)')
    ax[2, j].plot(t, o['i'][0], color=B_, label='ia1'); ax[2, j].plot(t, o['i'][1], color=R_, label='ia2')
    ax[2, j].set_title('Dòng phần ứng (A)'); ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel('t (s)')
    for a in ax[:, j]:
        a.axvline(1.0, color='C1', ls=':', lw=1); a.axvline(1.5, color='C0', ls=':', lw=1)
    e = o['w'][0] - o['w'][1]
    def mx(a_, b_):
        ii = (t >= a_) & (t < b_); return float(np.abs(e[ii]).max())
    RES[f'sync_{s}'] = dict(ramp=mx(0.1, 0.6), L2=mx(1.0, 1.5), L1=mx(1.5, 2.0), dec=mx(2.0, 2.6),
                            rms=float(np.sqrt((e ** 2).mean())), dth=float(np.abs(o['th'][0] - o['th'][1]).max()),
                            ip1=float(np.abs(o['i'][0]).max()), ip2=float(np.abs(o['i'][1]).max()))
fig.suptitle('Điều khiển đồng tốc 2 động cơ (tải Tn2 vào DC2 tại 1.0 s, tải Tn1 vào DC1 tại 1.5 s)', fontweight='bold')
fig.tight_layout(); save(fig, 'h_sync_all.png')
fig, ax = plt.subplots(2, 1, figsize=(7.4, 4.8), sharex=True)
for j, (s, nm) in enumerate(STR):
    o = SO[s]
    ax[0].plot(o['t'], o['w'][0] - o['w'][1], label=nm)
    ax[1].plot(o['t'], o['th'][0] - o['th'][1], label=nm)
ax[0].set_ylabel('ω1 − ω2 (rad/s)'); ax[1].set_ylabel('θ1 − θ2 (rad)'); ax[1].set_xlabel('t (s)')
ax[0].legend(fontsize=8); ax[0].set_title('So sánh sai lệch đồng tốc và sai lệch góc giữa 2 trục', fontweight='bold')
fig.tight_layout(); save(fig, 'h_sync_err.png')

# ================= III.2 vi tri nhieu dong co =================
MP = {md: dec(multi_pos(md)) for md in ('step', 'traj')}
CC = [B_, R_, '#2a9d2a']
for md, nm in (('step', 'Đặt vị trí dạng bậc thang (không phối hợp)'), ('traj', 'Quỹ đạo đa thức bậc 5 đồng bộ T = 0.8 s')):
    o = MP[md]; t = o['t']
    fig, ax = plt.subplots(3, 1, figsize=(7.4, 6.4), sharex=True)
    for k, (n, m, tg) in enumerate(AXES):
        ax[0].plot(t, o['ref'][k], '--', color=CC[k], lw=1)
        ax[0].plot(t, o['th'][k], color=CC[k], label=n)
        ax[1].plot(t, o['th'][k] / tg, color=CC[k], label=n)
        ax[2].plot(t, o['i'][k], color=CC[k], label=n)
    ax[0].set_ylabel('θ (rad)'); ax[1].set_ylabel('θ/θđích'); ax[2].set_ylabel('ia (A)'); ax[2].set_xlabel('t (s)')
    for a in ax: a.legend(fontsize=7.5, loc='upper right'); a.axvline(1.2, color='k', ls=':', lw=0.9)
    ax[0].set_title(nm, fontweight='bold'); ax[1].set_title('Tiến trình chuẩn hoá của các trục', fontsize=10)
    fig.tight_layout(); save(fig, f'h_multi_{md}.png')
    for k, (n, m, tg) in enumerate(AXES):
        th = o['th'][k]; ii = t < 1.2
        me = metrics(t[ii], th[ii], tg, 0.1)
        err = o['ref'][k] - th
        t98 = t[np.argmax(np.abs(th / tg) >= 0.98)]
        RES[f'mp_{md}{k}'] = dict(t98=t98, os=me['os'], ipk=float(np.abs(o['i'][k]).max()),
                                  ipkr=float(np.abs(o['i'][k]).max() / m['In']),
                                  trk=float(np.abs(err[(t > 0.1) & (t < 0.9)]).max()),
                                  dev=float(np.abs(err[(t > 1.2) & (t < 1.6)]).max()))
    prog = np.array([o['th'][k] / AXES[k][2] for k in range(3)])
    ii = (t > 0.1) & (t < 1.2)
    RES[f'mp_{md}_spread'] = float((prog.max(0) - prog.min(0))[ii].max())
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.4), sharey=True)
for j, md in enumerate(('step', 'traj')):
    o = MP[md]
    for k, (n, m, tg) in enumerate(AXES):
        ax[j].plot(o['t'], o['th'][k] / tg, color=CC[k], label=n)
    ax[j].set_xlim(0, 1.2); ax[j].set_xlabel('t (s)')
    ax[j].set_title(['Bậc thang: các trục đến đích lệch nhau', 'Quỹ đạo đồng bộ: các trục đến đích cùng lúc'][j], fontweight='bold', fontsize=10)
    ax[j].legend(fontsize=8)
ax[0].set_ylabel('θ/θđích')
fig.tight_layout(); save(fig, 'h_multi_sosanh.png')

json.dump({k: {a: float(b) for a, b in v.items()} if isinstance(v, dict) else v for k, v in RES.items()},
          open(os.path.join(OUT, 'res.json'), 'w'), indent=1)
print('done')
