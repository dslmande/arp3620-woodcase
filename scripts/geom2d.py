# -*- coding: utf-8 -*-
"""Plane geometry shared by the 3D model, the DXF files and the drawing."""
import math


def fillet_poly(pts, radii=None):
    """Closed polygon with a corner radius per vertex.

    Returns segments ('L', p, q) and ('A', p, mid, q, centre, r) in order."""
    n = len(pts)
    radii = radii or [0.0] * n
    corners = []                    # per vertex: (t_in, t_out, arc or None)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        r = radii[i]
        if r <= 0:
            corners.append((p1, p1, None))
            continue
        d1 = _unit(p1[0] - p0[0], p1[1] - p0[1])
        d2 = _unit(p2[0] - p1[0], p2[1] - p1[1])
        cosang = max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1]))
        theta = math.acos(cosang)               # change of direction
        tl = r * math.tan(theta / 2.0)
        t1 = (p1[0] - d1[0] * tl, p1[1] - d1[1] * tl)
        t2 = (p1[0] + d2[0] * tl, p1[1] + d2[1] * tl)
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        s = 1.0 if cross > 0 else -1.0          # left turn -> centre on the left
        c = (t1[0] - d1[1] * r * s, t1[1] + d1[0] * r * s)
        m = _unit(t1[0] + t2[0] - 2 * c[0], t1[1] + t2[1] - 2 * c[1])
        mid = (c[0] + m[0] * r, c[1] + m[1] * r)
        corners.append((t1, t2, (t1, mid, t2, c, r)))
    segs = []
    for i in range(n):
        a = corners[i][1]
        b = corners[(i + 1) % n][0]
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-9:
            segs.append(('L', a, b))
        arc = corners[(i + 1) % n][2]
        if arc:
            segs.append(('A',) + arc)
    return segs


def _unit(x, y):
    l = math.hypot(x, y)
    return (x / l, y / l)


def arc_points(seg, n=12):
    """Points along an 'A' segment (for plotting)."""
    _, p, mid, q, c, r = seg
    a0 = math.atan2(p[1] - c[1], p[0] - c[0])
    am = math.atan2(mid[1] - c[1], mid[0] - c[0])
    a1 = math.atan2(q[1] - c[1], q[0] - c[0])
    # choose the sweep that passes through mid
    def norm(a):
        return a % (2 * math.pi)
    sweep = norm(a1 - a0)
    if norm(am - a0) > sweep:
        sweep -= 2 * math.pi
    return [(c[0] + r * math.cos(a0 + sweep * k / n), c[1] + r * math.sin(a0 + sweep * k / n))
            for k in range(n + 1)]


def seg_points(segs, n=12):
    out = []
    for s in segs:
        pts = [s[1], s[2]] if s[0] == 'L' else arc_points(s, n)
        if out and math.hypot(out[-1][0] - pts[0][0], out[-1][1] - pts[0][1]) < 1e-9:
            pts = pts[1:]
        out.extend(pts)
    return out


def poly_area(pts):
    return 0.5 * abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                         for i in range(len(pts))))


def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
