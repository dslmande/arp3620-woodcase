# -*- coding: utf-8 -*-
"""One DXF (R12, mm) per distinct part, seen from the part's front face (w = t).

    python3 dxf_out.py          -> ../production/dxf/*.dxf

Layers: OUTLINE, CUTOUT, DRILL, CSK_FRONT, CSK_BACK (countersink on the far
side, mill from the other face), PILOT (pilot hole, not through), ENGRAVE."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *
from parts import PARTS
from geom2d import fillet_poly

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'production', 'dxf')

LAYERS = {'OUTLINE': 7, 'CUTOUT': 1, 'DRILL': 5, 'CSK_FRONT': 3, 'CSK_BACK': 6, 'PILOT': 4,
          'ENGRAVE': 2, 'NOTE': 8}


def signature(p):
    r = lambda x: round(x, 3)
    return (p.material, r(p.t), tuple((r(a), r(b)) for a, b in p.outline), tuple(map(r, p.radii)),
            tuple(sorted((r(h.u), r(h.v), r(h.d), h.csk, h.side, h.kind) for h in p.holes)),
            tuple(tuple((r(a), r(b)) for a, b in c[0]) for c in p.cutouts), tuple(p.texts))


def groups():
    """Distinct parts with their quantity: [(part, qty, [keys])]"""
    out, seen = [], {}
    for p in PARTS:
        s = signature(p)
        if s in seen:
            out[seen[s]][1] += p.qty; out[seen[s]][2].append(p.key)
        else:
            seen[s] = len(out); out.append([p, p.qty, [p.key]])
    return out


class Dxf:
    def __init__(self):
        self.e = []

    def _g(self, *kv):
        for i in range(0, len(kv), 2):
            self.e.append('%d\n%s\n' % (kv[i], kv[i + 1]))

    def line(self, a, b, layer):
        self._g(0, 'LINE', 8, layer, 10, '%.4f' % a[0], 20, '%.4f' % a[1], 30, 0,
                11, '%.4f' % b[0], 21, '%.4f' % b[1], 31, 0)

    def arc(self, c, r, a0, a1, layer):
        self._g(0, 'ARC', 8, layer, 10, '%.4f' % c[0], 20, '%.4f' % c[1], 30, 0, 40, '%.4f' % r,
                50, '%.4f' % a0, 51, '%.4f' % a1)

    def circle(self, c, r, layer):
        self._g(0, 'CIRCLE', 8, layer, 10, '%.4f' % c[0], 20, '%.4f' % c[1], 30, 0, 40, '%.4f' % r)

    def text(self, p, h, s, layer, centre=True):
        if centre:
            self._g(0, 'TEXT', 8, layer, 10, '%.4f' % p[0], 20, '%.4f' % p[1], 30, 0, 40, h, 1, s,
                    72, 1, 11, '%.4f' % p[0], 21, '%.4f' % p[1], 31, 0)
        else:
            self._g(0, 'TEXT', 8, layer, 10, '%.4f' % p[0], 20, '%.4f' % p[1], 30, 0, 40, h, 1, s)

    def segs(self, segs, layer):
        for s in segs:
            if s[0] == 'L':
                self.line(s[1], s[2], layer)
            else:
                _, p, mid, q, c, r = s
                a = lambda pt: math.degrees(math.atan2(pt[1] - c[1], pt[0] - c[0])) % 360
                a0, am, a1 = a(p), a(mid), a(q)
                ccw = (am - a0) % 360 < (a1 - a0) % 360
                if ccw:
                    self.arc(c, r, a0, a1, layer)
                else:
                    self.arc(c, r, a1, a0, layer)

    def save(self, fn):
        hdr = ['0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n',
               '0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n%d\n' % len(LAYERS)]
        for n, c in LAYERS.items():
            hdr.append('0\nLAYER\n2\n%s\n70\n0\n62\n%d\n6\nCONTINUOUS\n' % (n, c))
        hdr.append('0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n')
        open(fn, 'w').write(''.join(hdr) + ''.join(self.e) + '0\nENDSEC\n0\nEOF\n')


def draw_part(d, p, ox=0.0, oy=0.0):
    """Part with the lower left corner of its bounding box at (ox, oy)."""
    u0, v0, u1, v1 = p.bbox()
    sh = lambda q: (q[0] - u0 + ox, q[1] - v0 + oy)
    def segs(pts, rad):
        return [(g[0],) + tuple(sh(q) if isinstance(q, tuple) else q for q in g[1:]) for g in fillet_poly(pts, rad)]
    d.segs(segs(p.outline, p.radii), 'OUTLINE')
    for pts, rad in p.cutouts:
        d.segs(segs(pts, rad), 'CUTOUT')
    for h in p.holes:
        c = sh((h.u, h.v))
        if h.kind == 'pilot':
            d.circle(c, h.d / 2, 'PILOT')
            continue
        d.circle(c, h.d / 2, 'DRILL')
        if h.csk:
            d.circle(c, h.csk / 2, 'CSK_FRONT' if h.side == 'front' else 'CSK_BACK')
    for u, v, s in p.texts:
        d.text(sh((u, v + PLATE_TEXT_H / 2)), PLATE_TEXT_H, s, 'ENGRAVE')


def part_dxf(p, qty, keys, fn):
    """Origin of the DXF = lower left corner of the part's bounding box."""
    d = Dxf()
    draw_part(d, p)
    d.text((0, -12), 5, '%s  %s  %s mm  qty %d  (%s)' % (NAME, p.name, p.material, qty, ', '.join(keys)),
           'NOTE', centre=False)
    d.text((0, -20), 3.5, 'seen from the front face; CSK_BACK = countersink on the far face; '
           'inside corners with dogbones R %s' % DOG_R, 'NOTE', centre=False)
    d.save(fn)


SHEET = (2500.0, 1250.0)     # plywood sheet, parts laid out in rows (not nested)
GAP = 20.0


def sheet_dxf(material, items, fn):
    """All parts of one material and their quantities in rows on 2500 x 1250 sheets."""
    d = Dxf()
    items = sorted(items, key=lambda it: -it[0].size()[1])
    x = y = 0.0; row = 0.0; sheet = 0; placed = []
    for p, qty, keys in items:
        for n in range(qty):
            w, h = p.size()
            if x + w > SHEET[0]:
                x, y, row = 0.0, y + row + GAP, 0.0
            if y + h > SHEET[1]:
                sheet += 1; x = y = row = 0.0
            ox, oy = x, y + sheet * (SHEET[1] + 200)
            draw_part(d, p, ox, oy)
            d.text((ox + w / 2, oy + h / 2), 6, keys[min(n, len(keys) - 1)], 'NOTE')
            x += w + GAP; row = max(row, h)
    for k in range(sheet + 1):
        y0 = k * (SHEET[1] + 200)
        for a, b in (((0, y0), (SHEET[0], y0)), ((SHEET[0], y0), (SHEET[0], y0 + SHEET[1])),
                     ((SHEET[0], y0 + SHEET[1]), (0, y0 + SHEET[1])), ((0, y0 + SHEET[1]), (0, y0))):
            d.line(a, b, 'NOTE')
    d.text((0, -15), 6, '%s  all parts %s mm, %d sheet(s) %d x %d, laid out in rows (nest as you like)'
           % (NAME, material, sheet + 1, SHEET[0], SHEET[1]), 'NOTE', centre=False)
    d.save(fn)
    return sheet + 1


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.dxf'):
            os.remove(os.path.join(OUT, f))
    G = groups()
    for p, qty, keys in G:
        if p.material.startswith('aluminium Z'):
            continue                    # bought profiles, not cut
        fn = os.path.join(OUT, '%s_%s.dxf' % (NAME, p.key))
        part_dxf(p, qty, keys, fn)
        print('%-40s qty %d  %s' % (os.path.basename(fn), qty, keys))
    for mat in sorted(set(p.material for p, _, _ in G if p.material.startswith('birch'))):
        tag = mat.split()[-1] + 'mm'
        fn = os.path.join(OUT, 'sheets', '%s_all_%s.dxf' % (NAME, tag))
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        n = sheet_dxf(mat, [g for g in G if g[0].material == mat], fn)
        print('%-40s %d sheet(s)' % (os.path.basename(fn), n))


main()
