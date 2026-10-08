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


def part_dxf(p, qty, keys, fn):
    d = Dxf()
    d.segs(fillet_poly(p.outline, p.radii), 'OUTLINE')
    for pts, rad in p.cutouts:
        d.segs(fillet_poly(pts, rad), 'CUTOUT')
    for h in p.holes:
        if h.kind == 'pilot':
            d.circle((h.u, h.v), h.d / 2, 'PILOT')
            continue
        d.circle((h.u, h.v), h.d / 2, 'DRILL')
        if h.csk:
            d.circle((h.u, h.v), h.csk / 2, 'CSK_FRONT' if h.side == 'front' else 'CSK_BACK')
    for u, v, s in p.texts:
        d.text((u, v + PLATE_TEXT_H / 2), PLATE_TEXT_H, s, 'ENGRAVE')
    u0, v0, u1, v1 = p.bbox()
    d.text((u0, v0 - 12), 5, '%s  %s  %s mm  qty %d  (%s)' % (NAME, p.name, p.material, qty, ', '.join(keys)),
           'NOTE', centre=False)
    d.text((u0, v0 - 20), 3.5, 'seen from the front face; CSK_BACK = countersink on the far face', 'NOTE', centre=False)
    d.save(fn)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.dxf'):
            os.remove(os.path.join(OUT, f))
    for p, qty, keys in groups():
        fn = os.path.join(OUT, '%s_%s.dxf' % (NAME, p.key))
        part_dxf(p, qty, keys, fn)
        print('%-40s qty %d  %s' % (os.path.basename(fn), qty, keys))


main()
