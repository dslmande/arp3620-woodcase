# -*- coding: utf-8 -*-
"""Shaded views (painter's algorithm with matplotlib, no extra packages).

    freecadcmd render.py         -> ../images/*.png
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from params import *
from parts import PARTS
import model

ROOT = os.path.dirname(HERE)
IMG = os.path.join(ROOT, 'images'); os.makedirs(IMG, exist_ok=True)

COL = {'tolex': '#3a3a3c', 'paint': '#2c2c2e', 'alu': '#1f1f21', 'panel': '#b8bbbf',
       'white': '#f1eee6', 'black': '#18181a', 'frame': '#5a5d61', 'pcb': '#2e6b3c',
       'parts': '#8c939b', 'metal': '#a7adb3', 'rubber': '#151515'}
INNER = {'risers', 'riser_1', 'riser_2', 'cleat_l', 'cleat_r', 'fcleat_l', 'fcleat_r', 'apron'}


def tris_of(shape, maxlen=25.0):
    pts, tris = shape.tessellate(0.3)
    P = np.array([[p.x, p.y, p.z] for p in pts])
    out = []
    stack = [P[list(t)] for t in tris]
    while stack:
        t = stack.pop()
        l = [np.linalg.norm(t[(i + 1) % 3] - t[i]) for i in range(3)]
        i = int(np.argmax(l))
        if l[i] > maxlen:
            a, b, c = t[i], t[(i + 1) % 3], t[(i + 2) % 3]
            m = (a + b) / 2
            stack.append(np.array([a, m, c])); stack.append(np.array([m, b, c]))
        else:
            out.append(t)
    return out


def scene(lid=False, refs=True, explode=0.0, only=None):
    items = []
    case = model.case_solids(render=True)
    for p in PARTS:
        if p.key.startswith('lid') and not lid:
            continue
        if only and p.key not in only:
            continue
        s = case[p.key]
        if explode and p.key in ('strip', 'apron'):
            s = s.copy(); s.translate(model.Vec(0, 0, explode))
        if explode and p.key.startswith('lid'):
            s = s.copy(); s.translate(model.Vec(0, 0, 2.2 * explode))
        col = 'alu' if p.key == 'plate' else ('paint' if p.key in INNER else 'tolex')
        items.append((s, col))
    if refs:
        for k, (s, col) in model.references().items():
            if only and k not in only:
                continue
            if k == 'ref_latches' and not lid:
                continue
            items.append((s, col))
    return items


def render(items, view, up=(0, 0, 1), fname='view.png', size=(16, 9), light=(-0.35, -0.8, 0.9), zoom=1.0,
           dpi=150, title=None):
    v = np.array(view, float); v /= np.linalg.norm(v)            # from scene towards the camera
    upv = np.array(up, float)
    r = np.cross(upv, v); r /= np.linalg.norm(r)
    u = np.cross(v, r)
    L = np.array(light, float); L /= np.linalg.norm(L)
    polys, cols, depth = [], [], []
    for shape, ck in items:
        base = np.array(matplotlib.colors.to_rgb(COL[ck]))
        for t in tris_of(shape):
            n = np.cross(t[1] - t[0], t[2] - t[0])
            nl = np.linalg.norm(n)
            if nl < 1e-9:
                continue
            n /= nl
            if np.dot(n, v) < 0:          # back face
                continue
            shade = 0.38 + 0.62 * max(0.0, float(np.dot(n, L)))
            shade += 0.12 * max(0.0, float(np.dot(n, v)))
            c = np.clip(base * shade + 0.05 * (1 - base) * shade, 0, 1)
            polys.append([(float(np.dot(p, r)), float(np.dot(p, u))) for p in t])
            cols.append(c)
            depth.append(float(np.mean(t @ v)))
    order = np.argsort(depth)
    fig = plt.figure(figsize=size, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.add_collection(PolyCollection([polys[i] for i in order], facecolors=[cols[i] for i in order],
                                     edgecolors=[cols[i] for i in order], linewidths=0.25))
    xs = [p[0] for pl in polys for p in pl]; ys = [p[1] for pl in polys for p in pl]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    wx, wy = (max(xs) - min(xs)) / zoom, (max(ys) - min(ys)) / zoom
    asp = size[0] / size[1]
    half = max(wx / 2 * 1.06, wy / 2 * 1.06 * asp)
    ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half / asp, cy + half / asp)
    ax.set_aspect('equal'); ax.axis('off')
    fig.patch.set_facecolor('white')
    if title:
        ax.text(0.015, 0.03, title, transform=ax.transAxes, fontsize=13, color='#333')
    fig.savefig(os.path.join(IMG, fname), dpi=dpi, facecolor='white')
    plt.close(fig)
    print('wrote', fname, len(polys), 'triangles')


if True:  # freecadcmd does not run scripts as __main__
    tag = NAME
    render(scene(), (-0.55, -1.0, 0.85), fname=tag + '_front.png',
           title='ARP 3620 wooden case %s - without lid' % REV)
    outer = {'base', 'front', 'rear', 'end_l', 'end_r', 'plate', 'lid_top', 'lid_front', 'lid_rear',
             'lid_end_l', 'lid_end_r', 'ref_latches', 'ref_feet'}
    render(scene(lid=True, only=outer), (-0.55, -1.0, 0.75), fname=tag + '_closed.png',
           title='with lid')
    render(scene(), (0.6, 1.0, 0.7), fname=tag + '_rear.png', light=(0.4, 0.9, 0.8),
           title='rear: connector plate')
    render(scene(explode=60.0), (-0.45, -1.0, 1.1), fname=tag + '_open.png',
           title='strip lifted: electronics bay (emulator, power supply)')
