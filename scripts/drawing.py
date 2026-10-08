# -*- coding: utf-8 -*-
"""Production drawing, A3 landscape, several sheets -> one PDF.

    freecadcmd drawing.py        -> ../production/ARP3620_Woodcase_RevX_drawing.pdf
"""
import os, sys, math, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import FreeCAD as App, Part, TechDraw
from FreeCAD import Vector as Vec, Matrix
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Circle, PathPatch
from matplotlib.path import Path
import matplotlib.image as mpimg
from params import *
from parts import PARTS, BY_KEY, kb_holes_xy
from geom2d import fillet_poly, seg_points
import model

ROOT = os.path.dirname(HERE)
PROD = os.path.join(ROOT, 'production')
IMG = os.path.join(ROOT, 'images')
TODAY = datetime.date.today().strftime('%d.%m.%Y')
SW, SH = 420.0, 297.0
RED = '#c0392b'
FS = 2.6          # text height in mm (converted to points below)
PT = 72 / 25.4    # points per mm


def distinct():
    def sig(p):
        r = lambda x: round(x, 3)
        return (p.material, r(p.t), tuple((r(a), r(b)) for a, b in p.outline),
                tuple(sorted((r(h.u), r(h.v), r(h.d), h.csk, h.side, h.kind) for h in p.holes)),
                tuple(tuple((r(a), r(b)) for a, b in c[0]) for c in p.cutouts), tuple(p.texts))
    out, seen = [], {}
    for p in PARTS:
        s = sig(p)
        if s in seen:
            out[seen[s]][1] += 1; out[seen[s]][2].append(p.key)
        else:
            seen[s] = len(out); out.append([p, 1, [p.key]])
    return out


# ------------------------------------------------------------------ sheet helpers
class Sheet:
    def __init__(self, pdf, title, no, scale_note=''):
        self.pdf, self.title, self.no = pdf, title, no
        self.fig = plt.figure(figsize=(SW / 25.4, SH / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, SW); self.ax.set_ylim(0, SH); self.ax.axis('off')
        self.frame(scale_note)

    def text(self, x, y, s, h=FS, ha='left', va='baseline', col='k', rot=0, weight='normal', family=None):
        self.ax.text(x, y, s, fontsize=h * PT / 0.72, ha=ha, va=va, color=col, rotation=rot,
                     fontweight=weight, family=family or 'DejaVu Sans')

    def line(self, pts, lw=0.25, col='k', ls='-'):
        self.ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=lw * PT, ls=ls,
                     solid_capstyle='round', solid_joinstyle='round')

    def frame(self, scale_note):
        a = self.ax
        a.add_patch(plt.Rectangle((10, 10), SW - 20, SH - 20, fill=False, lw=0.5 * PT))
        # title block
        x0, y0, w, h = SW - 10 - 180, 10, 180, 28
        a.add_patch(plt.Rectangle((x0, y0), w, h, fill=False, lw=0.35 * PT))
        self.line([(x0, y0 + 16), (x0 + w, y0 + 16)], 0.2)
        self.line([(x0 + 120, y0), (x0 + 120, y0 + h)], 0.2)
        self.text(x0 + 3, y0 + 21, 'ARP 3620 replica - wooden case', 4.0, weight='bold')
        self.text(x0 + 3, y0 + 10, self.title, 3.2)
        self.text(x0 + 3, y0 + 4, 'CC BY-SA 4.0  (c) 2026 Dsl-man.de  -  github.com/dslmande/arp3620-woodcase', 2.0)
        self.text(x0 + 123, y0 + 21, '%s   %s' % (REV, TODAY), 3.0)
        self.text(x0 + 123, y0 + 13, 'sheet %d' % self.no, 3.0)
        self.text(x0 + 123, y0 + 5, scale_note or 'mm', 2.6)

    def save(self):
        self.pdf.savefig(self.fig); plt.close(self.fig)

    # ---- dimensions (sheet coordinates)
    def _arrow(self, x, y, dx, dy, s=1.6):
        n = (-dy, dx)
        self.ax.add_patch(Polygon([(x, y), (x + dx * s + n[0] * s * 0.28, y + dy * s + n[1] * s * 0.28),
                                   (x + dx * s - n[0] * s * 0.28, y + dy * s - n[1] * s * 0.28)],
                                  closed=True, fc=RED, ec='none'))

    def dim_h(self, x1, x2, y, txt, ext=None, h=2.4):
        """horizontal dimension at height y; ext = y of the feature (extension lines)"""
        if ext is not None:
            for x, e in zip((x1, x2), ext if isinstance(ext, (list, tuple)) else (ext, ext)):
                s = 1 if y > e else -1
                self.line([(x, e + s * 0.8), (x, y + s * 1.2)], 0.12, RED)
        self.line([(x1, y), (x2, y)], 0.15, RED)
        if abs(x2 - x1) > 4:
            self._arrow(x1, y, 1, 0); self._arrow(x2, y, -1, 0)
            self.text((x1 + x2) / 2, y + 0.8, txt, h, ha='center', col=RED)
        else:
            self._arrow(x1, y, -1, 0); self._arrow(x2, y, 1, 0)
            self.text(x2 + 2, y + 0.8, txt, h, col=RED)

    def dim_v(self, y1, y2, x, txt, ext=None, h=2.4):
        if ext is not None:
            for yy, e in zip((y1, y2), ext if isinstance(ext, (list, tuple)) else (ext, ext)):
                s = 1 if x > e else -1
                self.line([(e + s * 0.8, yy), (x + s * 1.2, yy)], 0.12, RED)
        self.line([(x, y1), (x, y2)], 0.15, RED)
        if abs(y2 - y1) > 4:
            self._arrow(x, y1, 0, 1); self._arrow(x, y2, 0, -1)
            self.text(x - 0.8, (y1 + y2) / 2, txt, h, ha='center', va='bottom', col=RED, rot=90)
        else:
            self._arrow(x, y1, 0, -1); self._arrow(x, y2, 0, 1)
            self.text(x - 0.8, y2 + 2, txt, h, ha='center', va='bottom', col=RED, rot=90)


def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


# ------------------------------------------------------------------ projections
M_VIEW = {
    'top':   ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    'front': ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
    'rear':  ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
    'right': ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
    'left':  ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
}


def rot(shape, view):
    r = M_VIEW[view]
    m = Matrix(r[0][0], r[0][1], r[0][2], 0, r[1][0], r[1][1], r[1][2], 0, r[2][0], r[2][1], r[2][2], 0)
    s = shape.copy(); s.transformShape(m); return s


def project(shapes, view, hidden=False):
    comp = Part.makeCompound([rot(s, view) for s in shapes])
    r = TechDraw.projectEx(comp, Vec(0, 0, 1))
    vis = [r[0], r[1], r[3]]
    hid = [r[5], r[6], r[8]] if hidden else []
    def pl(cs):
        out = []
        for c in cs:
            for e in c.Edges:
                pts = e.discretize(Deflection=0.2) if e.Length > 0.5 else [e.Vertexes[0].Point, e.Vertexes[-1].Point]
                out.append([(p.x, p.y) for p in pts])
        return out
    return pl(vis), pl(hid)


def place(sheet, polys, ox, oy, sc, lw=0.25, col='k', ls='-'):
    for pl in polys:
        sheet.line([(ox + x * sc, oy + y * sc) for x, y in pl], lw, col, ls)


def section_x(shapes_cols, xs, sc, ox, oy, sheet):
    """Section at x = xs, looking from +x towards -x (screen: y to the right, z up).
    Cut faces filled, the material behind the cut drawn as visible edges."""
    half = Part.makeBox(4000, 4000, 4000, Vec(xs - 4000, -2000, -2000))
    behind = []
    fills = []
    for s, col in shapes_cols:
        if not s.BoundBox.intersect(half.BoundBox):
            continue
        c = s.common(half)
        if c.isNull() or c.Volume < 1e-6:
            continue
        behind.append(c)
        for w in s.slice(Vec(1, 0, 0), xs):
            pts = [(v.y, v.z) for v in w.discretize(Deflection=0.1)]
            fills.append((pts, col))
    vis, _ = project(behind, 'right')
    for pts, col in fills:
        fc, hatch = col
        sheet.ax.add_patch(Polygon([(ox + y * sc, oy + z * sc) for y, z in pts], closed=True, fc=fc, ec='k',
                                   lw=0.3 * PT, hatch=hatch))
    place(sheet, vis, ox, oy, sc, 0.18, '#444')


# ------------------------------------------------------------------ part drawing
def part_outline(sheet, p, ox, oy, sc, flip_v=False):
    """Draw a part in its (u, v) plane, origin (u0, v0) of the bbox at (ox, oy)."""
    u0, v0, u1, v1 = p.bbox()
    T = lambda q: (ox + (q[0] - u0) * sc, oy + (q[1] - v0) * sc)
    sheet.line([T(q) for q in seg_points(fillet_poly(p.outline, p.radii), 24)] +
               [T(seg_points(fillet_poly(p.outline, p.radii), 24)[0])], 0.35)
    for pts, rad in p.cutouts:
        sp = seg_points(fillet_poly(pts, rad), 12)
        sheet.line([T(q) for q in sp] + [T(sp[0])], 0.3)
    for h in p.holes:
        c = T((h.u, h.v))
        if h.kind == 'pilot':
            sheet.ax.add_patch(Circle(c, max(0.35, h.d / 2 * sc), fill=False, ec='#0a7', lw=0.15 * PT))
            continue
        sheet.ax.add_patch(Circle(c, max(0.35, h.d / 2 * sc), fill=False, ec='k', lw=0.2 * PT))
        if h.csk:
            sheet.ax.add_patch(Circle(c, h.csk / 2 * sc, fill=False, ec='#2a5' if h.side == 'front' else '#a3a',
                                      lw=0.15 * PT, ls='-' if h.side == 'front' else '--'))
    for u, v, s in p.texts:
        x, y = T((u, v))
        sheet.text(x, y, s, PLATE_TEXT_H * sc, ha='center', col='#b8860b')
    return T


def hole_table(sheet, p, x, y, title=None, cols=1, fs=2.0, maxw=None, skip_notes=()):
    """Holes grouped by size/countersink/note, coordinates from the lower left corner."""
    u0, v0, _, _ = p.bbox()
    g = {}
    for h in p.holes:
        if any(s in h.note for s in skip_notes):
            continue
        k = (h.kind, h.d, h.csk, h.side, h.note)
        g.setdefault(k, []).append((h.u - u0, h.v - v0))
    yy = y
    if title:
        sheet.text(x, yy, title, fs + 0.4, weight='bold'); yy -= fs * 1.7
    for (kind, d, csk, side, note), pts in sorted(g.items(), key=lambda kv: -kv[0][1]):
        head = ('pilot %s' % fmt(d)) if kind == 'pilot' else ('dia %s' % fmt(d))
        if csk:
            head += ' csk %s %s' % (fmt(csk), 'this face' if side == 'front' else 'far face')
        head += '  (%d x)  %s' % (len(pts), note)
        sheet.text(x, yy, head, fs, weight='bold'); yy -= fs * 1.45
        pts = sorted(pts, key=lambda q: (round(q[1], 1), q[0]))
        s = '  '.join('%s/%s' % (fmt(a), fmt(b)) for a, b in pts)
        # wrap
        words, line = s.split('  '), ''
        width = maxw or 180
        per = max(1, int(width / (fs * 0.62 * 11)))
        for i in range(0, len(words), per):
            sheet.text(x + 2, yy, '  '.join(words[i:i + per]), fs, family='DejaVu Sans Mono'); yy -= fs * 1.35
        yy -= fs * 0.4
    return yy


def seen_from(p):
    return {(0, 0, 1): 'seen from above', (0, 0, -1): 'seen from below', (0, -1, 0): 'seen from the front',
            (0, 1, 0): 'seen from the rear', (1, 0, 0): 'seen from the right',
            (-1, 0, 0): 'seen from the left'}[tuple(int(round(c)) for c in p.N)]


def part_block(sheet, p, qty, keys, ox, oy, sc, dims=True, label=True, extra=None):
    u0, v0, u1, v1 = p.bbox()
    T = part_outline(sheet, p, ox, oy, sc)
    w, h = (u1 - u0) * sc, (v1 - v0) * sc
    if dims:
        sheet.dim_h(ox, ox + w, oy - 6, fmt(u1 - u0), ext=oy)
        sheet.dim_v(oy, oy + h, ox - 6, fmt(v1 - v0), ext=ox)
    if label:
        sheet.text(ox, oy + h + 7.5, '%s  -  %d x' % (p.name, qty), 2.9, weight='bold')
        sheet.text(ox, oy + h + 3, '%s mm, %s   [%s]' % (p.material, seen_from(p), ', '.join(keys)), 2.1,
                   col='#333')
    if extra:
        extra(sheet, T, sc)
    return T


# ------------------------------------------------------------------ hardware and cut list
def hardware():
    base = BY_KEY['base']
    n = lambda key, s: sum(1 for h in BY_KEY[key].holes if s in h.note)
    asm = n('base', 'assembly screw')
    walls = n('front', 'screw 4 x 40') + n('rear', 'screw 4 x 40')
    return [
        ('Tolex, black (vinyl case covering), approx. %.1f m2 incl. 25 %% waste' % tolex_area(), 'outside, see covering notes'),
        ('contact cement for tolex, wood glue (PVAc)', ''),
        ('%d x countersunk wood screw 4 x 30' % asm, 'base -> walls, cheeks, risers (from below)'),
        ('%d x countersunk wood screw 4 x 40' % walls, 'front/rear wall -> end walls and cheeks'),
        ('6 x countersunk wood screw 3.5 x 20, black', 'strip -> cleats (removable strip)'),
        ('6 x wood screw 3 x 20', 'apron -> strip (from above, under the tolex) and cleats -> cheeks'),
        ('4 x countersunk screw 3.5 x 16, black', 'rear plate'),
        ('10 x keybed screw from below through base and riser',
         'length ~ 21 mm + thread in the keybed foot; type to be confirmed on the keybed (hole 4.5)'),
        ('4 x M3 standoff, total length %s mm (e.g. 40 + 8, female/male)' % fmt(Z_PANEL0 - Z_BASE),
         'panel corners, M3 x 12 countersunk from below, M3 x 6 black from the top'),
        ('10 x M3 standoff %s mm, 10 x M3 x 12 countersunk' % fmt(STANDOFF), 'emulator (6), power supply (4)'),
        ('6 x rubber foot dia %s x %s with screw' % (fmt(FOOT_D), fmt(FOOT_H)), ''),
        ('4 x draw latch (case latch), small, ~40 mm wide', 'lid: 2 front, 2 rear, centre on the lid joint'),
        ('rear plate parts: 2 x DIN 5-pin panel socket, DC jack 5.5/2.1, 2 x toggle switch, USB extension (option)',
         'hole sizes on the plate are placeholders - confirm with the chosen parts'),
        ('optional: 8 x case corner, carrying handle', ''),
    ]


def tolex_area():
    # walls outside + base edges + wrap over the top (12 + 20 mm) + cheeks both faces + strip + filler + lid
    a = 2 * (W + D) * (Z_TOP + 20)                         # body outside incl. base edge and wrap
    for k in ('cheek_l', 'cheek_r'):
        from geom2d import poly_area
        a += 2 * poly_area(BY_KEY[k].outline) + 300 * T_CHEEK
    s = BY_KEY['strip']; a += (s.size()[0] + 30) * (s.size()[1] + 30)
    f = BY_KEY['filler']; a += (f.size()[0] + 20) * (f.size()[1] + 20)
    a += (W + 40) * (D + 40) + 2 * (W + D) * (H_LID + 25)  # lid
    return a * 1.25 / 1e6


# ------------------------------------------------------------------ sheets
def sheet_overview(pdf, no):
    s = Sheet(pdf, 'Overview', no, 'renders not to scale')
    ims = [('%s_front.png' % NAME, (12, 150, 200, 112.5)), ('%s_open.png' % NAME, (212, 150, 196, 110)),
           ('%s_rear.png' % NAME, (12, 42, 180, 101)), ('%s_closed.png' % NAME, (196, 60, 140, 79))]
    for fn, (x, y, w, h) in ims:
        p = os.path.join(IMG, fn)
        if os.path.exists(p):
            s.ax.imshow(mpimg.imread(p), extent=(x, x + w, y, y + h), zorder=0)
    s.ax.set_xlim(0, SW); s.ax.set_ylim(0, SH)
    t = ['Outside: %s x %s mm, height %s (walls) / %s (strip) / %s with lid, plus feet %s'
         % (fmt(W), fmt(D), fmt(Z_TOP), fmt(Z_STRIP), fmt(H_TOTAL), fmt(FOOT_H)),
         'Birch plywood 12 / 9 / 6 mm, covered in black tolex, lid with 4 latches',
         'Keybed Fatar TP/9S 49 on two 12 mm risers, control panel 170 x 230 flush with the walls',
         'Electronics bay under the removable strip: bus emulator 160 x 110, power supply 126 x 80',
         'Rear plate (aluminium 2 mm): USB (option), DC IN, POWER, SUPPLY 2600/INT, MIDI IN, MIDI OUT']
    s.text(342, 140, 'Key data', 3.2, weight='bold')
    yy = 134
    for l in t:
        for part in _wrap(l, 34):
            s.text(342, yy, part, 2.2); yy -= 3.6
        yy -= 1.5
    s.save()


def _wrap(s, n):
    out, line = [], ''
    for w in s.split(' '):
        if len(line) + len(w) + 1 > n:
            out.append(line); line = w
        else:
            line = (line + ' ' + w).strip()
    if line: out.append(line)
    return out


def sheet_views(pdf, no, case, refs):
    s = Sheet(pdf, 'General arrangement', no, 'scale 1:4')
    sc = 0.25
    body = [case[p.key] for p in PARTS if not p.key.startswith('lid')]
    rs = [refs[k][0] for k in ('ref_keybed_frame', 'ref_keys_white', 'ref_keys_black', 'ref_panel', 'ref_feet')]
    # top view without lid
    vis, _ = project(body + rs, 'top')
    ox, oy = 40, 175
    place(s, vis, ox, oy, sc, 0.2)
    s.text(ox, oy + D * sc + 6, 'Top view, lid removed', 3.0, weight='bold')
    s.dim_h(ox, ox + W * sc, oy + D * sc + 2.5 + 8, fmt(W), ext=oy + D * sc)
    xs = [0, X_PANEL_IN, X_CHEEK_L, X_KEYS_IN, X_CHEEK_R, W]
    for a, b in zip(xs, xs[1:]):
        s.dim_h(ox + a * sc, ox + b * sc, oy - 8, fmt(b - a) if b != W else '12+12', ext=oy)
    s.dim_v(oy, oy + D * sc, ox + W * sc + 8, fmt(D), ext=ox + W * sc)
    ys = [0, Y_KB0, Y_STRIP0, Y_KB1, Y_REAR_IN, D]
    for a, b in zip(ys, ys[1:]):
        s.dim_v(oy + a * sc, oy + b * sc, ox + W * sc + 18, fmt(b - a), ext=ox + W * sc)
    s.text(ox + W * sc + 22, oy + (Y_KB0 + Y_KB1) / 2 * sc, 'keybed', 2.2, va='center')
    s.text(ox + W * sc + 22, oy + (Y_KB1 + Y_REAR_IN) / 2 * sc, 'bay', 2.2, va='center')
    ps = [0, Y_PANEL0, Y_PANEL1, Y_FILL0, Y_REAR_IN]
    for a, b in zip(ps, ps[1:]):
        s.dim_v(oy + a * sc, oy + b * sc, ox - 8, fmt(b - a), ext=ox)
    s.text(ox + (X_PANEL_IN + 85) * sc, oy + (Y_PANEL0 + 115) * sc, 'control panel', 2.4, ha='center')
    s.text(ox + (X_PANEL_IN + 85) * sc, oy + (Y_FILL0 + 26) * sc, 'filler', 2.2, ha='center', va='center', col='#555')
    s.text(ox + 550 * sc, oy + (Y_STRIP0 + 68) * sc, 'strip (removable)', 2.4, ha='center', va='center', col='#555')

    # front view with lid
    allc = [case[p.key] for p in PARTS] + [refs['ref_feet'][0], refs['ref_latches'][0]]
    vis, _ = project(allc, 'front')
    ox, oy = 40, 115
    place(s, vis, ox, oy, sc, 0.2)
    s.text(ox, oy + H_TOTAL * sc + 6, 'Front view with lid', 3.0, weight='bold')
    zs = [0, Z_TOP, H_TOTAL]
    for a, b in zip(zs, zs[1:]):
        s.dim_v(oy + a * sc, oy + b * sc, ox - 8, fmt(b - a), ext=ox)
    s.dim_v(oy - FOOT_H * sc, oy, ox - 16, fmt(FOOT_H), ext=ox)

    # rear view without lid
    vis, _ = project(body + rs + [refs['ref_plate_parts'][0]], 'rear')
    ox, oy = 40 + W * sc, 60
    place(s, vis, ox, oy, sc, 0.2)            # rear view runs from -W..0
    s.text(ox - W * sc, oy + Z_STRIP * sc + 6, 'Rear view, lid removed', 3.0, weight='bold')
    s.dim_v(oy, oy + Z_TOP * sc, ox + 8, fmt(Z_TOP), ext=ox)
    s.dim_v(oy, oy + Z_STRIP * sc, ox + 16, fmt(Z_STRIP), ext=ox)
    xr = ox - PLATE_X_RIGHT * sc
    s.dim_h(ox - W * sc, xr, oy - 8, fmt(W - PLATE_X_RIGHT), ext=oy)
    s.dim_h(xr, xr + PLATE_L * sc, oy - 8, fmt(PLATE_L), ext=oy)

    # right side view
    vis, _ = project(allc, 'right')
    ox, oy = 300, 110
    place(s, vis, ox, oy, sc, 0.2)
    s.text(ox, oy + H_TOTAL * sc + 6, 'Right side, with lid', 3.0, weight='bold')
    s.dim_h(ox, ox + D * sc, oy - FOOT_H * sc - 6, fmt(D), ext=oy)
    s.save()


def z_ordinates(s, zs, x_edge, oy, sc, side=-1, h=2.3):
    """Height marks: a tick from the edge outwards and the value; labels nudged apart."""
    last = -1e9
    for z in sorted(zs):
        y = oy + z * sc
        ty = max(y, last + h * 1.25)
        last = ty
        x1 = x_edge + side * 6
        s.line([(x_edge + side * 1, y), (x1, y)], 0.12, RED)
        if abs(ty - y) > 0.1:
            s.line([(x1, y), (x1 + side * 2, ty)], 0.12, RED)
        s.text(x1 + side * 2.5, ty - h * 0.35, fmt(z), h, ha='right' if side < 0 else 'left', col=RED)


def callout(s, x, y, tx, ty, text, h=2.3):
    s.line([(x, y), (tx, ty)], 0.12, '#333')
    s.ax.plot([x], [y], 'o', ms=1.2, color='#333')
    s.text(tx + (1 if tx >= x else -1), ty, text, h, ha='left' if tx >= x else 'right', va='center', col='#222')


def sheet_sections(pdf, no, case, refs):
    s = Sheet(pdf, 'Sections', no, 'scale 1:1')
    sc = 1.0
    WOOD = ('#e2cfa6', '////')
    shp = []
    for p in PARTS:
        shp.append((case[p.key], ('#c9c9c9', None) if p.key == 'plate' else WOOD))
    refc = {'frame': ('#d0d4d8', None), 'white': ('#f7f7f2', None), 'black': ('#333333', None),
            'panel': ('#b0b4b8', None), 'pcb': ('#4c9a5c', None), 'parts': ('#e8eef4', 'xx'),
            'metal': ('#9aa3ab', None), 'rubber': ('#222222', None)}
    for k, (sh, ck) in refs.items():
        shp.append((sh, refc[ck]))

    # section A-A through the keyboard and the power supply
    xa = 440.0
    ox, oy = 45, 168
    section_x(shp, xa, sc, ox, oy, s)
    s.text(ox, oy + H_TOTAL + 15, 'Section A-A at x = %s (keyboard, power supply), seen from the right' % fmt(xa),
           3.0, weight='bold')
    z_ordinates(s, [0, Z_BASE, Z_KB, Z_TOP, Z_STRIP0, Z_STRIP, Z_LID1, H_TOTAL], ox, oy, sc, -1)
    z_ordinates(s, [Z_APRON0, Z_KB + KB_WHITE, Z_KB + KB_BLACK], ox + D, oy, sc, +1)
    ys = [0, Y_IN, Y_KB0, Y_STRIP0, Y_KB1, Y_REAR_IN, D]
    for a_, b_ in zip(ys, ys[1:]):
        s.dim_h(ox + a_, ox + b_, oy + H_TOTAL + 5 + (4 if b_ - a_ < 8 else 0), fmt(b_ - a_), ext=oy + H_TOTAL)
    callout(s, ox + Y_KB0 + 70, oy + Z_KB + 22, ox + 70, oy + Z_KB + 22, 'Fatar TP/9S 49 (simplified)')
    callout(s, ox + Y_KB0 + KB_HOLE_Y[0] - 8, oy + Z_BASE + 6, ox + 30, oy + Z_BASE + 26, 'riser 12')
    callout(s, ox + Y_KB1 + 45, oy + Z_BASE + 30, ox + Y_KB1 + 45, oy + Z_TOP + 5, 'power supply (envelope)')
    callout(s, ox + Y_STRIP0 + 100, oy + Z_STRIP - 4, ox + Y_STRIP0 + 100, oy + Z_LID1 - 3, 'strip 9 (removable)')
    callout(s, ox + Y_REAR_IN - 4, oy + Z_APRON0 + 5, ox + D + 22, oy + Z_STRIP + 2, 'apron')
    callout(s, ox + D + TOLEX + 1, oy + PLATE_Z0 + 30, ox + D + 22, oy + PLATE_Z0 + 18, 'rear plate + socket')
    callout(s, ox + D - 30, oy + Z_LID1 + 3, ox + D + 22, oy + H_TOTAL - 2, 'lid')
    callout(s, ox + Y_REAR_IN + 6, oy + Z_BASE + 8, ox + D + 22, oy + Z_BASE + 4, 'rear wall (window)')

    # section B-B through the control panel
    xb = 100.0
    ox, oy = 45, 52
    section_x(shp, xb, sc, ox, oy, s)
    s.text(ox, oy + H_TOTAL + 15, 'Section B-B at x = %s (control panel)' % fmt(xb), 3.0, weight='bold')
    zb = Z_PANEL0 - BOARD_SPACER
    z_ordinates(s, [0, Z_BASE, zb - PCB_T - BOARD_PARTS_BELOW, zb, Z_PANEL0, Z_TOP], ox, oy, sc, -1)
    ys = [0, Y_PANEL0, Y_PANEL1, Y_FILL0, Y_REAR_IN, D]
    for a_, b_ in zip(ys, ys[1:]):
        s.dim_h(ox + a_, ox + b_, oy + H_TOTAL + 5 + (4 if b_ - a_ < 8 else 0), fmt(b_ - a_), ext=oy + H_TOTAL)
    callout(s, ox + 150, oy + Z_TOP - 1, ox + 150, oy + Z_TOP + 12, 'control panel 2 mm')
    callout(s, ox + 120, oy + zb - 12, ox + D + 22, oy + zb - 4, '3620 board (envelope)')
    callout(s, ox + Y_FILL0 + 30, oy + Z_TOP - 4, ox + D + 22, oy + Z_TOP + 4, 'filler')
    callout(s, ox + Y_PANEL0 + 12.5, oy + Z_BASE + 30, ox + 60, oy + Z_TOP + 12, 'standoff M3 (panel corner)')

    n = ['Heights follow from the keybed: the lower edge of the white key fronts (%s above the mounting plane,' % fmt(KB_LIP),
         'scaled from the Fatar drawing) sits %s above the wall top. Measure it on the real keybed before cutting -' % fmt(LIP_ABOVE_WALL),
         'all heights follow from it (params.py: KB_LIP). Board spacer %s and %s for parts and plugs under the'
         % (fmt(BOARD_SPACER), fmt(BOARD_PARTS_BELOW)),
         '3620 board are estimates. Electronics are simplified boxes (parts height emulator %s, power supply %s).'
         % (fmt(EMU_PARTS), fmt(NT_PARTS))]
    for i, l in enumerate(n):
        s.text(20, 33 - i * 3.4, l, 1.9)
    s.save()


def sheet_base(pdf, no, G):
    s = Sheet(pdf, 'Base', no, 'scale 1:3')
    p, q, k = next(g for g in G if g[0].key == 'base')
    sc = 1 / 3
    ox, oy = 25, 160
    part_block(s, p, q, k, ox, oy, sc)
    s.text(ox, oy - 15, 'seen from above (inside). Countersinks: dashed = on the underside. Coordinates x/y from the front left corner.', 2.2)
    yy = hole_table(s, p, 25, 140, cols=1, fs=1.9, maxw=370)
    s.save()


def sheet_walls(pdf, no, G):
    s = Sheet(pdf, 'Walls', no, 'scale 1:3')
    sc = 1 / 3
    get = lambda key: next(g for g in G if key in g[2])
    p, q, k = get('front'); part_block(s, p, q, k, 30, 236, sc)
    s.text(30, 222, 'Countersinks on this face (outside), heads under the tolex.', 2.0)
    hole_table(s, p, 30, 216, fs=1.9, maxw=300)
    p, q, k = get('rear'); T = part_block(s, p, q, k, 30, 150, sc)
    pts = p.cutouts[0][0]
    u0, v0, u1, v1 = pts[0][0], pts[0][1], pts[2][0], pts[2][1]
    s.dim_h(30, T((u0, 0))[0], 150 - 12, fmt(u0), ext=150)
    s.dim_h(T((u0, 0))[0], T((u1, 0))[0], 150 - 12, fmt(u1 - u0), ext=150)
    xr = 30 + W * sc
    s.dim_v(150, T((0, v0))[1], xr + 8, fmt(v0), ext=T((u1, 0))[0])
    s.dim_v(T((0, v0))[1], T((0, v1))[1], xr + 16, fmt(v1 - v0), ext=T((u1, 0))[0])
    s.text(xr + 20, T((0, v1))[1] + 1, 'window, corners R %s' % fmt(WINDOW[3]), 2.0)
    s.text(30, 128, 'Seen from inside. Countersinks on the far face (outside), heads under the tolex. '
                    'Window for the bodies of the rear plate parts.', 2.0)
    hole_table(s, p, 30, 122, fs=1.9, maxw=300)
    p, q, k = get('end_l'); part_block(s, p, q, k, 30, 60, sc)
    s.text(140, 75, 'End walls: plain, no holes - screws come through the front/rear wall and the base.', 2.0)
    s.save()


def sheet_cheeks(pdf, no, G):
    s = Sheet(pdf, 'Cheeks', no, 'scale 1:2')
    get = lambda key: next(g for g in G if key in g[2])
    sc = 0.5
    for key, oy in (('cheek_l', 175), ('cheek_r', 70)):
        p, q, k = get(key)
        ox = 40
        T = part_block(s, p, q, k, ox, oy, sc)
        uk = Y_STRIP0 - Y_IN
        ytop = oy + (Z_STRIP - Z_BASE) * sc
        s.dim_h(ox, T((uk, 0))[0], oy + (Z_TOP - Z_BASE) * sc - 8, fmt(uk) + ' to the corner (rounded R ' + fmt(CHEEK_KNEE_R) + ')', ext=[oy + (Z_TOP - Z_BASE) * sc, ytop])
        s.dim_v(oy, T((0, Z_TOP - Z_BASE))[1], ox - 13, fmt(Z_TOP - Z_BASE), ext=ox)
        L = p.size()[0]
        s.text(ox + L * sc + 8, ytop - 4, 'front edge (left) against the front wall,', 2.1)
        s.text(ox + L * sc + 8, ytop - 8, 'rear edge against the rear wall.', 2.1)
        s.text(ox + L * sc + 8, ytop - 12, 'Slope from %s to %s high, blending into the' % (fmt(Z_TOP - Z_BASE), fmt(Z_STRIP - Z_BASE)), 2.1)
        s.text(ox + L * sc + 8, ytop - 16, 'flat top with R %s (tangent points in the DXF).' % fmt(CHEEK_KNEE_R), 2.1)
        s.text(ox + L * sc + 8, ytop - 20, 'Tolex on both faces and the top edge.', 2.1)
        if key == 'cheek_l':
            n0, n1, nh = CABLE_NOTCH
            s.dim_h(ox, T((n0, 0))[0], oy - 13, fmt(n0), ext=oy)
            s.dim_h(T((n0, 0))[0], T((n1, 0))[0], oy - 13, fmt(n1 - n0), ext=oy)
            s.dim_v(oy, T((0, nh))[1], T(((n0 + n1) / 2, 0))[0], fmt(nh))
            s.text(ox + L * sc + 8, ytop - 26, 'Cable notch %s x %s, corners R %s: cables' % (fmt(n1 - n0), fmt(nh), fmt(CABLE_NOTCH_R)), 2.1)
            s.text(ox + L * sc + 8, ytop - 30, 'from the electronics bay to the panel section.', 2.1)
    s.save()


def sheet_inner(pdf, no, G):
    s = Sheet(pdf, 'Strip, risers, cleats, filler', no, 'scale 1:3 / 1:2')
    get = lambda key: next(g for g in G if key in g[2])
    sc = 1 / 3
    p, q, k = get('strip'); part_block(s, p, q, k, 25, 210, sc)
    hole_table(s, p, 270, 262, fs=1.9, maxw=120)
    s.text(25, 200, 'seen from above; screws into the cleats on the cheeks, countersunk on top (black screws)', 2.0)
    p, q, k = get('apron'); part_block(s, p, q, k, 25, 170, sc)
    s.text(25, 160, 'glued under the rear edge of the strip, flush with its rear edge; reaches 10 mm below the wall top', 2.0)
    p, q, k = get('riser_1'); part_block(s, p, q, k, 25, 130, sc)
    hole_table(s, p, 270, 140, fs=1.9, maxw=120)
    s.text(25, 120, 'two risers along the rows of keybed feet, glued and screwed onto the base', 2.0)
    sc2 = 0.5
    p, q, k = get('cleat_l'); part_block(s, p, q, k, 30, 80, sc2)
    s.text(30, 66, 'glued + 2 screws to the cheek,', 1.9)
    s.text(30, 62.5, 'top %s below the strip top' % fmt(T_STRIP), 1.9)
    p, q, k = get('fcleat_l'); part_block(s, p, q, k, 30, 40, sc2)
    s.text(30, 26, 'carry the filler (left wall, left cheek)', 1.9)
    p, q, k = get('filler'); part_block(s, p, q, k, 140, 60, sc2)
    s.text(140, 46, 'glued onto the cleats, flush with the wall top', 1.9)
    s.save()


def sheet_lid(pdf, no, G):
    s = Sheet(pdf, 'Lid', no, 'scale 1:4')
    get = lambda key: next(g for g in G if key in g[2])
    sc = 0.25
    p, q, k = get('lid_top'); part_block(s, p, q, k, 30, 170, sc)
    p, q, k = get('lid_front'); part_block(s, p, q, k, 30, 120, sc)
    p, q, k = get('lid_end_l'); part_block(s, p, q, k, 30, 75, sc)
    n = ['Walls %s mm, inside height %s above the case walls (%s clear above the strip).'
         % (fmt(T_LID_WALL), fmt(LID_INSIDE), fmt(Z_LID1 - Z_STRIP)),
         'Front and rear walls run through, the ends sit between them, the top lies on the walls.',
         'Glue and pin; tolex outside and around the lower edge.',
         'The lid sits on the case walls, flush outside. 4 latches centred on the joint (2 front, 2 rear)',
         'keep it in place; the latches also locate it sideways.']
    for i, l in enumerate(n):
        s.text(150, 82 - i * 4.2, l, 2.2)
    s.save()


def sheet_plate(pdf, no, G):
    s = Sheet(pdf, 'Rear plate', no, 'scale 1:1')
    get = lambda key: next(g for g in G if key in g[2])
    p, q, k = get('plate')
    ox, oy = 30, 200
    T = part_block(s, p, q, k, ox, oy, 1.0)
    prev = 0.0
    for u in sorted(set(round(it[0], 2) for it in PLATE_ITEMS)):
        s.dim_h(T((prev, 0))[0], T((u, 0))[0], oy - 14, fmt(u - prev), ext=oy)
        prev = u
    s.dim_v(oy, T((0, PLATE_ITEMS[0][1]))[1], ox + PLATE_L + 8, fmt(PLATE_ITEMS[0][1]), ext=ox + PLATE_L)
    hole_table(s, p, ox, 172, fs=2.0, maxw=220)
    n = ['Aluminium 2 mm, black anodised, legend engraved or printed white.',
         'Seen from outside (from the rear of the case).',
         'Mounted on the outside of the rear wall, over the tolex,',
         'with 4 countersunk screws 3.5 x 16 (pilot holes in the rear wall).',
         'Seen from the rear, the plate starts %s from the left end of the case;' % fmt(W - PLATE_X_RIGHT),
         'its lower edge is %s above the underside of the base.' % fmt(PLATE_Z0),
         'The window in the rear wall takes the bodies of the parts.',
         'Behind the emulator only 25 mm depth is free; the deep USB',
         'extension sits at the left end, behind the power supply.',
         'Hole sizes are placeholders until the parts are chosen.']
    for i, l in enumerate(n):
        s.text(150, 168 - i * 4.4, l, 2.2, weight='bold' if i == len(n) - 1 else 'normal')
    s.save()


def sheet_lists(pdf, no, G):
    s = Sheet(pdf, 'Cut list, hardware, assembly', no, '')
    y = 270
    s.text(20, y, 'Cut list (finished sizes, mm)', 3.2, weight='bold'); y -= 6
    hdr = ('part', 'qty', 'material', 'length', 'width', 'covering / finish')
    xs = (20, 90, 102, 140, 158, 176)
    for x, h in zip(xs, hdr):
        s.text(x, y, h, 2.2, weight='bold')
    y -= 4.2
    area = {}
    for p, q, k in G:
        l, w = p.size()
        for x, v in zip(xs, (p.name, str(q), p.material, fmt(l), fmt(w), p.cover)):
            s.text(x, y, v, 2.1)
        area[p.material] = area.get(p.material, 0) + l * w * q / 1e6
        y -= 3.8
    y -= 2
    s.text(20, y, 'net area: ' + ',  '.join('%s mm: %.2f m2' % (m, a) for m, a in area.items()), 2.1); y -= 8

    s.text(20, y, 'Hardware', 3.2, weight='bold'); y -= 6
    for a, b in hardware():
        s.text(20, y, '- ' + a, 2.1)
        if b:
            y -= 3.4
            s.text(24, y, b, 1.9, col='#555')
        y -= 4.0

    x2, y2 = 300, 270
    s.text(x2 - 0, y2, 'Assembly', 3.2, weight='bold'); y2 -= 6
    steps = ['Cut all parts, drill and countersink as per DXF (CSK_BACK = countersink on the far face).',
             'Check KB_LIP and the screws on the real keybed first; fit the keybed onto the risers dry.',
             'Risers onto the base (glue + screws from below).',
             'Cheeks and end walls onto the base, then front and rear wall (glue, screws through the base and the walls).',
             'Cleats onto the cheeks, filler cleats, filler glued in.',
             'Apron glued and screwed under the strip; the strip stays removable.',
             'Lid: front, rear, ends, top - glue and pins.',
             'Fill the screw heads, sand, round all outside edges to about R2.',
             'Paint the inside black, then tolex outside with contact cement; wrap 20 mm over the top edges. Strip, filler and cheeks get tolex on all visible faces.',
             'Rear plate, latches, feet; panel on its standoffs, electronics on the base, keybed screwed from below.']
    for i, st in enumerate(steps):
        lines = _wrap('%d. %s' % (i + 1, st), 52)
        for l in lines:
            s.text(x2, y2, l, 2.1); y2 -= 3.5
        y2 -= 1.2
    y2 -= 4
    s.text(x2, y2, 'Open points', 3.2, weight='bold'); y2 -= 6
    for st in ['KB_LIP %s (key front lower edge) scaled from the Fatar drawing - measure.' % fmt(KB_LIP),
               'Keybed screw type and length (foot hole 4.5).',
               'Board spacer %s and parts height under the 3620 board.' % fmt(BOARD_SPACER),
               'Rear plate parts and their hole sizes.',
               'Latch type; optional handle and case corners.']:
        for l in _wrap('- ' + st, 52):
            s.text(x2, y2, l, 2.1); y2 -= 3.5
    s.save()


def main():
    case = model.case_solids()
    refs = model.references()
    G = distinct()
    out = os.path.join(PROD, NAME + '_drawing.pdf')
    with PdfPages(out) as pdf:
        n = 1
        for f in (sheet_overview,):
            f(pdf, n); n += 1
        sheet_views(pdf, n, case, refs); n += 1
        sheet_sections(pdf, n, case, refs); n += 1
        sheet_base(pdf, n, G); n += 1
        sheet_walls(pdf, n, G); n += 1
        sheet_cheeks(pdf, n, G); n += 1
        sheet_inner(pdf, n, G); n += 1
        sheet_lid(pdf, n, G); n += 1
        sheet_plate(pdf, n, G); n += 1
        sheet_lists(pdf, n, G); n += 1
        d = pdf.infodict()
        d['Title'] = 'ARP 3620 wooden case %s' % REV
        d['Author'] = 'Dsl-man.de'
    print('wrote', out)


main()
