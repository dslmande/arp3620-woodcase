# -*- coding: utf-8 -*-
"""Joints for a CNC-cut case that is plugged together: finger joints at the
wall corners, tabs into notches at plate edges, tabs through slots.

A part's outline is its plain polygon plus a step profile along straight,
axis-parallel edges. Features are given in the part's own (u, v) coordinates:
(a0, a1, off) = from a0 to a1 along the edge, off > 0 sticks out (tab),
off < 0 cuts in (notch). Every sharp inside corner left over gets a dogbone,
so a round end mill can cut it and a square tab still seats."""
import math
from params import FIT
from geom2d import DOG


def bands(z0, z1, n):
    w = (z1 - z0) / n
    return [(z0 + k * w, z0 + (k + 1) * w, k) for k in range(n)]


def fingers(z0, z1, n, mine, depth, base='inner'):
    """Finger joint over z0..z1 in n equal bands, 'mine' = indices of the bands
    this part owns. base='inner': the plain edge lies on the inner line and the
    own bands stick out by depth; base='outer': the plain edge is the outer face
    and the other bands are cut in. Both give the same part; FIT is split over
    the two parts at every band boundary inside z0..z1."""
    out = []
    for a, b, k in bands(z0, z1, n):
        own = k in mine
        if base == 'inner' and own:
            out.append((a + (FIT / 2 if a > z0 + 1e-9 else 0), b - (FIT / 2 if b < z1 - 1e-9 else 0), depth))
        if base == 'outer' and not own:
            out.append((a - (FIT / 2 if a > z0 + 1e-9 else 0), b + (FIT / 2 if b < z1 - 1e-9 else 0), -depth))
    return out


def tabs(centres, w, depth):
    return [(c - w / 2, c + w / 2, depth) for c in centres]


def notches(centres, w, depth):
    """Notches for tabs of width w: FIT wider than the tab."""
    return [(c - w / 2 - FIT / 2, c + w / 2 + FIT / 2, -depth) for c in centres]


def slot(u0, u1, v0, v1):
    """Through slot (cutout) for a tab u0..u1 x v0..v1, FIT larger all round."""
    h = FIT / 2
    return ([(u0 - h, v0 - h), (u1 + h, v0 - h), (u1 + h, v1 + h), (u0 - h, v1 + h)], [DOG] * 4)


def tab_line(a, b, pitch):
    """Evenly spaced centres from a to b, about 'pitch' apart."""
    n = max(1, int(round((b - a) / pitch)))
    return [a + (b - a) * k / n for k in range(n + 1)]


def _unit(x, y):
    l = math.hypot(x, y)
    return (x / l, y / l)


def profile(pts, radii, feats):
    """Polygon pts (counter-clockwise) with radii, plus feats {edge index: [(a0, a1, off)]},
    edge i runs from pts[i] to pts[i + 1]. Returns (pts, radii) with dogbones."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    assert area > 0, 'outline must be counter-clockwise'
    E = []
    for i in range(n):
        A, B = pts[i], pts[(i + 1) % n]
        d = _unit(B[0] - A[0], B[1] - A[1])
        nrm = (d[1], -d[0])                                  # outward for a ccw polygon
        L = math.hypot(B[0] - A[0], B[1] - A[1])
        fs = []
        for a0, a1, off in feats.get(i, []):
            ax = 0 if abs(d[1]) < 1e-9 else 1
            assert abs(d[1 - ax]) < 1e-9, 'features only on axis-parallel edges'
            sg = 1 if d[ax] > 0 else -1
            s0, s1 = sorted(((a0 - A[ax]) * sg, (a1 - A[ax]) * sg))
            s0, s1 = max(0.0, s0), min(L, s1)
            assert s1 > s0, 'feature outside edge %d' % i
            fs.append((s0, s1, off))
        fs.sort()
        for (a, b, _), (c, _, _) in zip(fs, fs[1:]):
            assert c >= b - 1e-9, 'overlapping features on edge %d' % i
        E.append((A, d, nrm, L, fs))

    def P(e, s, off):
        A, d, nrm, _, _ = e
        return (A[0] + s * d[0] + off * nrm[0], A[1] + s * d[1] + off * nrm[1])

    def off_start(e):
        return next((f[2] for f in e[4] if f[0] <= 1e-9), 0.0)

    def off_end(e):
        return next((f[2] for f in e[4] if f[1] >= e[3] - 1e-9), 0.0)

    out = []                                                 # [(pt, radius)]
    for i in range(n):
        ea, eb = E[i - 1], E[i]
        oa, ob = off_end(ea), off_start(eb)
        V = pts[i]
        if abs(oa) < 1e-12 and abs(ob) < 1e-12:
            out.append((V, radii[i]))
        elif abs(ea[2][0] * eb[2][0] + ea[2][1] * eb[2][1]) < 1e-9:      # perpendicular edges
            out.append(((V[0] + oa * ea[2][0] + ob * eb[2][0], V[1] + oa * ea[2][1] + ob * eb[2][1]), 0.0))
        else:
            out.append(((V[0] + oa * ea[2][0], V[1] + oa * ea[2][1]), 0.0))
            out.append(((V[0] + ob * eb[2][0], V[1] + ob * eb[2][1]), 0.0))
        for s0, s1, off in eb[4]:
            if s0 > 1e-9:
                out += [(P(eb, s0, 0), 0.0), (P(eb, s0, off), 0.0)]
            if s1 < eb[3] - 1e-9:
                out += [(P(eb, s1, off), 0.0), (P(eb, s1, 0), 0.0)]
    # drop duplicates and straight-through points
    changed = True
    while changed:
        changed = False
        m = len(out)
        for k in range(m):
            p0, (p1, r1), p2 = out[k - 1][0], out[k], out[(k + 1) % m][0]
            dup = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 1e-9
            cr = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])
            dt = (p1[0] - p0[0]) * (p2[0] - p1[0]) + (p1[1] - p0[1]) * (p2[1] - p1[1])
            if dup or (r1 == 0 and abs(cr) < 1e-9 and dt > 0):
                del out[k]; changed = True; break
    # dogbones in every sharp inside corner
    m = len(out)
    res_p, res_r = [], []
    for k in range(m):
        p0, (p1, r1), p2 = out[k - 1][0], out[k], out[(k + 1) % m][0]
        cr = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])
        res_p.append(p1)
        res_r.append(DOG if (r1 == 0 and cr < -1e-9) else r1)
    return res_p, res_r
