# -*- coding: utf-8 -*-
"""Read the DXF files back (own parser, independent of parts.py) and plot them,
so the files that go to the shop are what gets looked at.

    python3 dxf_preview.py      -> ../model/dxf_preview.png"""
import os, sys, math, glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COL = {'OUTLINE': 'k', 'CUTOUT': 'r', 'DRILL': 'b', 'CSK_FRONT': 'g', 'CSK_BACK': 'm', 'PILOT': 'c',
       'ENGRAVE': 'orange', 'NOTE': '#999'}


def read(fn):
    lines = [l.rstrip('\r\n') for l in open(fn)]
    pairs = [(int(lines[i]), lines[i + 1]) for i in range(0, len(lines) - 1, 2)]
    ents, cur, inside = [], None, False
    for c, v in pairs:
        if c == 2 and v == 'ENTITIES':
            inside = True; continue
        if not inside:
            continue
        if c == 0:
            if cur: ents.append(cur)
            cur = {'type': v} if v not in ('ENDSEC', 'EOF') else None
        elif cur is not None:
            cur.setdefault(c, v)
    return ents


def plot(ax, ents):
    for e in ents:
        L, col = e.get(8), COL.get(e.get(8), 'k')
        f = lambda c: float(e[c])
        if e['type'] == 'LINE':
            ax.plot([f(10), f(11)], [f(20), f(21)], color=col, lw=0.6)
        elif e['type'] == 'CIRCLE':
            ax.add_patch(plt.Circle((f(10), f(20)), f(40), fill=False, color=col, lw=0.5))
        elif e['type'] == 'ARC':
            a0, a1 = f(50), f(51)
            if a1 < a0: a1 += 360
            n = 24
            pts = [(f(10) + f(40) * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                    f(20) + f(40) * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=0.6)
        elif e['type'] == 'TEXT' and L == 'ENGRAVE':
            ax.text(f(11), f(21), e[1], fontsize=4, ha='center', va='center', color=col)
        elif e['type'] == 'TEXT':
            ax.set_title(e[1], fontsize=6) if f(40) > 4 else None


files = sorted(glob.glob(os.path.join(ROOT, 'production', 'dxf', '*.dxf')))
n = len(files)
cols = 3
rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(18, 3.2 * rows))
for ax, fn in zip(axs.flat, files):
    plot(ax, read(fn))
    ax.set_aspect('equal'); ax.autoscale_view(); ax.tick_params(labelsize=5)
for ax in list(axs.flat)[n:]:
    ax.axis('off')
fig.tight_layout()
out = os.path.join(ROOT, 'model', 'dxf_preview.png')
fig.savefig(out, dpi=130)
print('wrote', out)
