# -*- coding: utf-8 -*-
"""Carpenter drawing (German): the same case as the CNC design, but with plain
butt joints for a workshop without CNC. Cut list, views, sections and simple
part sketches with straight edges only - no holes, no pockets, no radii.

    freecadcmd carpenter.py   -> ../production/carpenter/ARP3620_Woodcase_<REV>_Tischler.pdf
                                 ../production/carpenter/check_carpenter.txt

Part layout as in Rev0.1: walls stand on the base, front and rear wall run the
full length, end walls and cheeks sit between them, the filler behind the
control panel rests on two cleats. All dimensions come from params.py.
"""
import os, sys, math, datetime, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import FreeCAD as App, Part, TechDraw, Import
from FreeCAD import Vector as Vec, Matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Circle
from params import *
import parts as P0
from parts import Part as FlatPart, X, Y, Z, NX, NY
from geom2d import rect
import model

# Heights hang on KB_LIP (lower edge of the white key front), which is scaled
# from the Fatar drawing. Set to True once it has been measured on the keybed
# and entered in params.py; until then every sheet carries a DRAFT banner.
HEIGHTS_CONFIRMED = False
DOC_REV = REV + '-T1'          # carpenter variant of the case revision

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'production', 'carpenter')
PDF_NAME = 'ARP3620_Woodcase_%s_Tischler.pdf' % DOC_REV
STEP_REF = os.path.join(ROOT, 'production', '%s.step' % NAME)
TODAY = datetime.date.today().strftime('%d.%m.%Y')
SW, SH = 420.0, 297.0
RED = '#c0392b'
PT = 72 / 25.4
MAT = {12: 'Birke Multiplex 12', 9: 'Birke Multiplex 9', 6: 'Birke Multiplex 6'}


def fmt(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return s.replace('.', ',')


# ------------------------------------------------------------------ parts (butt joints)
LW = Y_REAR_IN - Y_IN                           # 286, between front and rear wall
H_FRONT = Z_TOP - Z_BASE                        # 50, cheek height at the front
H_REAR = Z_STRIP - Z_BASE                       # 73, cheek height under the strip
U_KNEE = Y_STRIP0 - Y_IN                        # 149.5, end of the slope
N0, N1, NH = CABLE_NOTCH                        # cable notch in the left cheek
WIN_X0, WIN_X1 = PLATE_X_RIGHT - WINDOW[1], PLATE_X_RIGHT - WINDOW[0]   # 261 .. 448 (case x)
WIN_VC = PLATE_Z0 + PLATE_H / 2 - Z_BASE        # window centre above the lower wall edge
WIN_V0, WIN_V1 = WIN_VC - WINDOW[2] / 2, WIN_VC + WINDOW[2] / 2
LID_END_L = D - 2 * T_LID_WALL                  # 292


class CP:
    """A carpenter part: flat outline + placement (parts.Part) plus cut list data."""
    def __init__(self, pos, name, group, fp, note=''):
        self.pos, self.name, self.group, self.fp, self.note = pos, name, group, fp, note
        self.solid = model.part_solid(fp)

    def dims(self):
        a, b = self.fp.size()
        return max(a, b), min(a, b), self.fp.t


def make_parts():
    L = []
    def add(pos, key, name, group, mat_t, t, outline, O, U=X, V=Y, N=Z, cutouts=(), note=''):
        fp = FlatPart(key, name, MAT[mat_t], t, outline, None, O=O, U=U, V=V, N=N)
        for c in cutouts:
            fp.cutouts.append((c, [0.0] * len(c)))
        L.append(CP(pos, name, group, fp, note))

    G1, G2, G3 = 'Korpus', 'Abdeckleiste (abnehmbar)', 'Deckel'
    add(1, 'base', 'Boden', G1, 9, T_BASE, rect(0, 0, W, D), (0, 0, 0),
        note='alle Wände stehen auf dem Boden')
    add(2, 'front', 'Vorderwand', G1, 12, T_WALL, rect(0, 0, W, WALL_H), (0, Y_IN, Z_BASE), X, Z, NY,
        note='volle Länge')
    add(3, 'rear', 'Rückwand', G1, 12, T_WALL, rect(0, 0, W, WALL_H), (0, D, Z_BASE), X, Z, NY,
        cutouts=[rect(WIN_X0, WIN_V0, WIN_X1, WIN_V1)], note='volle Länge, mit Fenster (Blatt 7)')
    for key, x0 in (('end_l', 0.0), ('end_r', W - T_WALL)):
        add(4, key, 'Seitenwand', G1, 12, T_WALL, rect(0, 0, LW, WALL_H), (x0, Y_IN, Z_BASE), Y, Z, X,
            note='zwischen Vorder- und Rückwand')
    cheek = [(0, 0), (LW, 0), (LW, H_REAR), (U_KNEE, H_REAR), (0, H_FRONT)]
    cheek_l = [(0, 0), (N0, 0), (N0, NH), (N1, NH), (N1, 0), (LW, 0), (LW, H_REAR), (U_KNEE, H_REAR), (0, H_FRONT)]
    add(5, 'cheek_l', 'Wange links', G1, 12, T_CHEEK, cheek_l, (X_CHEEK_L, Y_IN, Z_BASE), Y, Z, X,
        note='Schräge + Kabeldurchlass (Blatt 7)')
    add(6, 'cheek_r', 'Wange rechts', G1, 12, T_CHEEK, cheek, (X_CHEEK_R, Y_IN, Z_BASE), Y, Z, X,
        note='Schräge (Blatt 7), liegt an der Seitenwand')
    for i, ry in enumerate(KB_HOLE_Y):
        add(7, 'riser_%d' % (i + 1), 'Tastaturleiste', G1, 12, T_RISER,
            rect(0, 0, RISER_X1 - RISER_X0, RISER_W), (RISER_X0, Y_KB0 + ry - RISER_W / 2, Z_BASE),
            note='auf den Boden geleimt, Lage Blatt 8')
    add(8, 'filler', 'Füllstück hinter der Frontplatte', G1, 9, T_FILL, rect(0, 0, PANEL_OPEN, Y_REAR_IN - Y_FILL0),
        (X_PANEL_IN, Y_FILL0, Z_TOP - T_FILL), note='oben bündig mit den Wänden')
    for x0 in (X_PANEL_IN, X_CHEEK_L - FCLEAT):
        add(9, 'fcleat', 'Leiste unter dem Füllstück', G1, 12, FCLEAT, rect(0, 0, FCLEAT, Y_REAR_IN - Y_FILL0),
            (x0, Y_FILL0, Z_TOP - T_FILL - FCLEAT), note='an Seitenwand und Wange geleimt')
    for x0 in (X_KEYS_IN, X_CHEEK_R - CLEAT_W):
        add(10, 'cleat', 'Auflageleiste Abdeckleiste', G1, 12, CLEAT_H, rect(0, 0, CLEAT_W, Y_CLEAT1 - Y_CLEAT0),
            (x0, Y_CLEAT0, Z_STRIP0 - CLEAT_H), note='innen an die Wangen geleimt')
    add(11, 'strip', 'Abdeckleiste', G2, 9, T_STRIP, rect(0, 0, KEYS_OPEN, Y_REAR_IN - Y_STRIP0),
        (X_KEYS_IN, Y_STRIP0, Z_STRIP0), note='liegt lose auf Pos. 10, wird geschraubt')
    add(12, 'apron', 'Blende unter der Abdeckleiste', G2, 9, T_APRON, rect(0, 0, KEYS_OPEN, Z_STRIP0 - Z_APRON0),
        (X_KEYS_IN, Y_REAR_IN, Z_APRON0), X, Z, NY, note='unter Pos. 11 geleimt, hinten bündig')
    add(13, 'lid_top', 'Deckelplatte', G3, 6, T_LID_TOP, rect(0, 0, W, D), (0, 0, Z_LID1),
        note='liegt auf den Deckelwänden')
    for y0 in (T_LID_WALL, D):
        add(14, 'lid_fr', 'Deckel vorn/hinten', G3, 9, T_LID_WALL, rect(0, 0, W, LID_INSIDE), (0, y0, Z_LID0),
            X, Z, NY, note='volle Länge')
    for x0 in (0.0, W - T_LID_WALL):
        add(15, 'lid_end', 'Deckel Seite', G3, 9, T_LID_WALL, rect(0, 0, LID_END_L, LID_INSIDE),
            (x0, T_LID_WALL, Z_LID0), Y, Z, X, note='zwischen vorn und hinten')
    return L


PARTS = make_parts()


def cutlist():
    rows = {}
    for p in PARTS:
        l, b, t = p.dims()
        k = p.pos
        if k in rows:
            rows[k]['qty'] += 1
        else:
            rows[k] = dict(pos=p.pos, name=p.name, group=p.group, qty=1, L=l, B=b, T=t,
                           mat=p.fp.material, note=p.note)
    return [rows[k] for k in sorted(rows)]


# ------------------------------------------------------------------ sheet
class Sheet:
    def __init__(self, pdf, title, no, scale_note='mm'):
        self.pdf, self.title, self.no = pdf, title, no
        self.fig = plt.figure(figsize=(SW / 25.4, SH / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, SW); self.ax.set_ylim(0, SH); self.ax.axis('off')
        self.frame(scale_note)

    def text(self, x, y, s, h=2.6, ha='left', va='baseline', col='k', rot=0, weight='normal', family=None,
             alpha=1.0):
        self.ax.text(x, y, s, fontsize=h * PT / 0.72, ha=ha, va=va, color=col, rotation=rot,
                     fontweight=weight, family=family or 'DejaVu Sans', alpha=alpha)

    def line(self, pts, lw=0.25, col='k', ls='-'):
        self.ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=lw * PT, ls=ls,
                     solid_capstyle='round', solid_joinstyle='round')

    def frame(self, scale_note):
        a = self.ax
        a.add_patch(plt.Rectangle((10, 10), SW - 20, SH - 20, fill=False, lw=0.5 * PT))
        x0, y0, w, h = SW - 10 - 180, 10, 180, 28
        a.add_patch(plt.Rectangle((x0, y0), w, h, fill=False, lw=0.35 * PT))
        self.line([(x0, y0 + 16), (x0 + w, y0 + 16)], 0.2)
        self.line([(x0 + 120, y0), (x0 + 120, y0 + h)], 0.2)
        self.text(x0 + 3, y0 + 21, 'ARP 3620 Nachbau - Holzgehäuse', 4.0, weight='bold')
        self.text(x0 + 3, y0 + 10, self.title, 3.2)
        self.text(x0 + 3, y0 + 4, 'Ausführung Tischler (ohne CNC)  -  CC BY-SA 4.0  (c) 2026 Dsl-man.de', 2.0)
        self.text(x0 + 123, y0 + 21, '%s   %s' % (DOC_REV, TODAY), 3.0)
        self.text(x0 + 123, y0 + 13, 'Blatt %d von %d' % (self.no, N_SHEETS), 3.0)
        self.text(x0 + 123, y0 + 5, scale_note, 2.6)
        self.text(14, 14, 'Maße in mm, Holzmaße ohne Bezug.  Bohrungen und Ausschnitte für Elektronik sind '
                  'nicht eingezeichnet.', 2.0, col='#444')
        if not HEIGHTS_CONFIRMED:
            a.add_patch(plt.Rectangle((14, SH - 24), 230, 10, fc='#fff3cd', ec=RED, lw=0.4 * PT))
            self.text(17, SH - 20.6, 'ENTWURF - Höhen noch nicht freigegeben: Tastenfront-Unterkante am Keybed '
                      'messen (KB_LIP = %s angenommen)' % fmt(KB_LIP), 2.5, col=RED, weight='bold')

    def save(self):
        self.pdf.savefig(self.fig)
        if os.environ.get('DRAWING_PNG'):
            self.fig.savefig(os.path.join(os.environ['DRAWING_PNG'], 'tischler%02d.png' % self.no), dpi=110)
        plt.close(self.fig)

    def _arrow(self, x, y, dx, dy, s=1.6):
        n = (-dy, dx)
        self.ax.add_patch(Polygon([(x, y), (x + dx * s + n[0] * s * 0.28, y + dy * s + n[1] * s * 0.28),
                                   (x + dx * s - n[0] * s * 0.28, y + dy * s - n[1] * s * 0.28)],
                                  closed=True, fc=RED, ec='none'))

    def dim_h(self, x1, x2, y, txt, ext=None, h=2.4):
        if ext is not None:
            for x, e in zip((x1, x2), ext if isinstance(ext, (list, tuple)) else (ext, ext)):
                s = 1 if y > e else -1
                self.line([(x, e + s * 0.8), (x, y + s * 1.2)], 0.12, RED)
        self.line([(x1, y), (x2, y)], 0.15, RED)
        if abs(x2 - x1) > 4 + len(txt) * h * 0.6:
            self._arrow(x1, y, 1, 0); self._arrow(x2, y, -1, 0)
            self.text((x1 + x2) / 2, y + 0.8, txt, h, ha='center', col=RED)
        else:
            self._arrow(x1, y, -1, 0); self._arrow(x2, y, 1, 0)
            self.line([(x2, y), (x2 + 3, y)], 0.15, RED)
            self.text(x2 + 3.5, y + 0.8, txt, h, col=RED)

    def dim_v(self, y1, y2, x, txt, ext=None, h=2.4):
        if ext is not None:
            for yy, e in zip((y1, y2), ext if isinstance(ext, (list, tuple)) else (ext, ext)):
                s = 1 if x > e else -1
                self.line([(e + s * 0.8, yy), (x + s * 1.2, yy)], 0.12, RED)
        self.line([(x, y1), (x, y2)], 0.15, RED)
        if abs(y2 - y1) > 4 + len(txt) * h * 0.6:
            self._arrow(x, y1, 0, 1); self._arrow(x, y2, 0, -1)
            self.text(x - 0.8, (y1 + y2) / 2, txt, h, ha='center', va='bottom', col=RED, rot=90)
        else:
            self._arrow(x, y1, 0, -1); self._arrow(x, y2, 0, 1)
            side = -1 if ext is None or x <= (ext if not isinstance(ext, (list, tuple)) else ext[0]) else 1
            self.text(x + side * 1.2, (y1 + y2) / 2, txt, h, ha='right' if side < 0 else 'left', va='center',
                      col=RED)

    def balloon(self, x, y, tx, ty, n, h=2.4):
        self.line([(x, y), (tx, ty)], 0.12, '#333')
        self.ax.plot([x], [y], 'o', ms=1.0, color='#333')
        self.ax.add_patch(Circle((tx, ty), h * 0.95, fc='white', ec='k', lw=0.25 * PT, zorder=5))
        self.ax.text(tx, ty, str(n), fontsize=h * PT / 0.72, ha='center', va='center', zorder=6,
                     family='DejaVu Sans', fontweight='bold')

    def notes(self, x, y, title, lines, h=2.3, width=None, bullets=True):
        self.text(x, y, title, h + 0.6, weight='bold')
        y -= h * 1.9
        n = int((width or 190) / (h * 0.78))
        for l in lines:
            first = True
            for part in wrap(l, n):
                pre = ('- ' if first else '  ') if bullets else ('' if first else '    ')
                self.text(x, y, pre + part, h); y -= h * 1.5
                first = False
            y -= h * 0.35
        return y


def wrap(s, n):
    out, line = [], ''
    for w in s.split(' '):
        if len(line) + len(w) + 1 > n:
            out.append(line); line = w
        else:
            line = (line + ' ' + w).strip()
    if line:
        out.append(line)
    return out


# ------------------------------------------------------------------ projections
M_VIEW = {
    'top':   ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    'front': ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
    'rear':  ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
    'right': ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
    'left':  ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
}


def view_matrix(t):
    """Rows: screen x, screen y, towards the viewer (t)."""
    n = math.sqrt(sum(c * c for c in t)); t = [c / n for c in t]
    r = (-t[1], t[0], 0.0)                       # z x t
    n = math.hypot(r[0], r[1]); r = (r[0] / n, r[1] / n, 0.0)
    u = (t[1] * r[2] - t[2] * r[1], t[2] * r[0] - t[0] * r[2], t[0] * r[1] - t[1] * r[0])
    return (r, u, tuple(t))


def rot(shape, m):
    M = Matrix(m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0, m[2][0], m[2][1], m[2][2], 0)
    s = shape.copy(); s.transformShape(M); return s


def project(shapes, view, hidden=False):
    m = M_VIEW[view] if isinstance(view, str) else view
    comp = Part.makeCompound([rot(s, m) for s in shapes])
    r = TechDraw.projectEx(comp, Vec(0, 0, 1))
    def pl(cs):
        out = []
        for c in cs:
            if c.isNull():
                continue
            for e in c.Edges:
                pts = e.discretize(Deflection=0.2) if e.Length > 0.5 else [e.Vertexes[0].Point, e.Vertexes[-1].Point]
                out.append([(p.x, p.y) for p in pts])
        return out
    return pl([r[0], r[1], r[3]]), (pl([r[5], r[6], r[8]]) if hidden else [])


def to_screen(p, view):
    m = M_VIEW[view] if isinstance(view, str) else view
    return (sum(m[0][i] * p[i] for i in range(3)), sum(m[1][i] * p[i] for i in range(3)))


def place(sheet, polys, ox, oy, sc, lw=0.25, col='k', ls='-'):
    for pl in polys:
        sheet.line([(ox + x * sc, oy + y * sc) for x, y in pl], lw, col, ls)


def section_x(shapes_cols, xs, sc, ox, oy, sheet):
    """Section at x = xs, seen from +x towards -x (screen: y to the right, z up)."""
    half = Part.makeBox(4000, 4000, 4000, Vec(xs - 4000, -2000, -2000))
    behind, fills = [], []
    for s, col in shapes_cols:
        if not s.BoundBox.intersect(half.BoundBox):
            continue
        c = s.common(half)
        if c.isNull() or c.Volume < 1e-6:
            continue
        behind.append(c)
        for w in s.slice(Vec(1, 0, 0), xs):
            fills.append(([(v.y, v.z) for v in w.discretize(Deflection=0.1)], col))
    vis, _ = project(behind, 'right')
    for pts, (fc, hatch) in fills:
        sheet.ax.add_patch(Polygon([(ox + y * sc, oy + z * sc) for y, z in pts], closed=True, fc=fc, ec='k',
                                   lw=0.3 * PT, hatch=hatch))
    place(sheet, vis, ox, oy, sc, 0.18, '#444')


def centre(p):
    b = p.solid.BoundBox
    return ((b.XMin + b.XMax) / 2, (b.YMin + b.YMax) / 2, (b.ZMin + b.ZMax) / 2)


def solids(pred=lambda p: True):
    return [p.solid for p in PARTS if pred(p)]


BODY = lambda p: p.group == 'Korpus'
NOLID = lambda p: p.group != 'Deckel'


# ------------------------------------------------------------------ sheets
def sheet_overview(pdf, no):
    s = Sheet(pdf, 'Übersicht und Hinweise', no, 'Isometrie ohne Maßstab')
    # isometric views: body without lid, lid on its own
    m = view_matrix((-0.55, -1.0, 0.95))
    bvis, _ = project(solids(NOLID), m)
    lvis, _ = project(solids(lambda p: p.group == 'Deckel'), m)
    xs = [x for pl in bvis for x, _ in pl]; ys = [y for pl in bvis for _, y in pl]
    sc = 215.0 / (max(xs) - min(xs))
    ox, oy = 30 - min(xs) * sc, 150 - min(ys) * sc
    place(s, bvis, ox, oy, sc, 0.22)
    s.text(20, 262, 'Korpus mit Abdeckleiste, ohne Deckel', 3.2, weight='bold')
    lys = [y for pl in lvis for _, y in pl]
    lsc = sc * 0.55
    lox, loy = 30 - min(xs) * lsc, 62 - min(lys) * lsc
    place(s, lvis, lox, loy, lsc, 0.22)
    s.text(20, 62 + (max(lys) - min(lys)) * lsc + 8, 'Deckel (kleiner dargestellt)', 3.2, weight='bold')
    anchor = {1: ((860, 40, Z_BASE), (12, -14)), 2: ((520, 0, Z_BASE + 25), (6, -18)),
              3: ((800, D, Z_BASE + 35), (14, 14)), 4: ((0, 120, Z_BASE + 25), (-14, -8)),
              5: ((X_CHEEK_L + 6, 90, Z_TOP + 4), (-6, 22)), 6: ((X_CHEEK_R + 6, 110, Z_TOP + 8), (16, 14)),
              7: ((560, 86.5, Z_KB), (14, -24)), 8: ((100, 272, Z_TOP), (-12, 20)),
              9: ((X_PANEL_IN + T_WALL, 262, Z_TOP - T_FILL - 4), (-26, 14)),
              10: ((X_CHEEK_R - CLEAT_W, 190, Z_STRIP0 - 5), (22, -8)), 11: ((560, 230, Z_STRIP), (6, 20)),
              12: ((500, Y_REAR_IN - T_APRON, Z_APRON0 + 6), (-14, 24))}
    for n, (pt, (dx, dy)) in anchor.items():
        x, y = to_screen(pt, m)
        s.balloon(ox + x * sc, oy + y * sc, ox + x * sc + dx, oy + y * sc + dy, n)
    for n, (pt, (dx, dy)) in {13: ((450, 160, H_TOTAL), (6, 12)), 14: ((450, 0, Z_LID0 + 15), (8, -12)),
                              15: ((0, 160, Z_LID0 + 15), (-14, -6))}.items():
        x, y = to_screen(pt, m)
        s.balloon(lox + x * lsc, loy + y * lsc, lox + x * lsc + dx, loy + y * lsc + dy, n)

    t = ['Außenmaße Holz: %s x %s mm (Breite x Tiefe). Höhe: Wände %s, Wangen hinten %s, mit Deckel %s mm.'
         % (fmt(W), fmt(D), fmt(Z_TOP), fmt(Z_STRIP), fmt(H_TOTAL)),
         'Material: Birke Multiplex (Birkensperrholz) 12, 9 und 6 mm. Die Plattendicken vor dem Zuschnitt messen: '
         'weicht eine Dicke ab, ändern sich die Teile, die zwischen anderen sitzen (Seitenwände, Wangen, '
         'Füllstück, Deckel-Seiten). Die Außenmaße und die Funktionsmaße unten bleiben.',
         'Verbindungen stumpf: die Wände stehen auf dem Boden, Vorder- und Rückwand laufen über die volle '
         'Länge, Seitenwände und Wangen sitzen dazwischen. Leimen und Schrauben, Dübeln oder Lamellos nach '
         'Wahl des Tischlers - Schrauben von außen nur dort, wo später der Bezug (Tolex) darüber kommt.',
         'Keine Bohrungen, keine Fräsungen: Löcher für Tastatur, Frontplatte, Elektronik, Füße und Rückplatte '
         'bohrt Patrick nach dem Zusammenbau. Keine Radien: alle Kanten gerade.',
         'Bezug: das Gehäuse wird außen mit schwarzem Tolex bezogen. Holzfugen und Schraubenköpfe auf den '
         'Außenflächen bündig verspachteln.',
         'Abdeckleiste (Pos. 11 mit 12) bleibt abnehmbar: nicht einleimen, sie liegt auf den Leisten Pos. 10. '
         'Der Deckel (Pos. 13-15) ist ein eigener Kasten und liegt auf den Wänden.',
         'Nicht vom Tischler: Alu-Rückplatte 211 x 40 x 2, Gummifüße, Verschlüsse, Tolex, Tastatur, Elektronik.']
    y = s.notes(262, 262, 'Hinweise für den Tischler', t, 2.25, width=135)
    f = ['Lichte Weite zwischen den Wangen: %s (Tastatur %s + 2 x %s), nicht kleiner.'
         % (fmt(KEYS_OPEN), fmt(KB_W), fmt(GAP_KB_SIDE)),
         'Öffnung für die Frontplatte: %s x %s zwischen Seitenwand, Vorderwand, Wange und Füllstück, nicht kleiner. '
         'Die Frontplatte liegt nicht auf Holz auf, sie sitzt auf Bolzen vom Boden - keine Falz nötig.'
         % (fmt(PANEL_OPEN), fmt(Y_FILL0 - Y_IN)),
         'Oberkante der Wände %s über Unterkante Boden, rundum gleich. Füllstück oben bündig mit den Wänden.'
         % fmt(Z_TOP),
         'Tastaturleisten (Pos. 7) %s hoch, Oberkante %s über Unterkante Boden, auf den Boden geleimt.'
         % (fmt(T_RISER), fmt(Z_KB))]
    s.notes(262, y - 3, 'Funktionsmaße (genau einhalten)', f, 2.25, width=135)
    s.save()


def sheet_cutlist(pdf, no):
    s = Sheet(pdf, 'Zuschnittliste', no, 'mm')
    cols = [('Pos.', 22, 'c'), ('Bezeichnung', 30, 'l'), ('Stück', 108, 'c'), ('Länge', 128, 'r'),
            ('Breite', 150, 'r'), ('Dicke', 168, 'r'), ('Material', 176, 'l'), ('Bemerkung', 222, 'l')]
    y = 248
    s.text(20, 262, 'Zuschnittliste - alle Holzteile', 3.6, weight='bold')
    s.text(20, 256, 'Länge x Breite x Dicke in mm, Fertigmaß ohne Bezug. Wangen: Zuschnitt auf das umschreibende '
           'Rechteck, Form nach Blatt 7.', 2.3, col='#333')
    for name, x, al in cols:
        s.text(x if al != 'r' else x, y, name, 2.6, weight='bold', ha={'l': 'left', 'c': 'center', 'r': 'right'}[al])
    s.line([(18, y - 2), (402, y - 2)], 0.3)
    y -= 7
    group = None
    tot = {}
    for r in cutlist():
        if r['group'] != group:
            group = r['group']
            s.text(30, y, group, 2.6, weight='bold', col='#1f4e79'); y -= 6
        vals = [str(r['pos']), r['name'], str(r['qty']), fmt(r['L']), fmt(r['B']), fmt(r['T']), r['mat'], r['note']]
        for (name, x, al), v in zip(cols, vals):
            s.text(x, y, v, 2.5, ha={'l': 'left', 'c': 'center', 'r': 'right'}[al])
        s.line([(18, y - 2.2), (402, y - 2.2)], 0.1, '#bbb')
        a = r['qty'] * r['L'] * r['B'] / 1e6
        tot[r['mat']] = tot.get(r['mat'], 0) + a
        y -= 6
    y -= 4
    s.text(30, y, 'Plattenbedarf netto (ohne Verschnitt): ' +
           ',  '.join('%s: %s m²' % (k, fmt(round(v, 2))) for k, v in sorted(tot.items(), reverse=True)), 2.4)
    y -= 5
    s.text(30, y, 'Die Leisten Pos. 9 und 10 dürfen auch aus Massivholz sein (gleicher Querschnitt).', 2.4)
    s.save()


def sheet_views(pdf, no):
    s = Sheet(pdf, 'Ansichten (Vorderansicht, Draufsicht, Seitenansicht)', no, 'Maßstab 1:4')
    sc = 0.25
    allp = solids()
    # front view with lid
    vis, _ = project(allp, 'front')
    ox, oy = 45, 212
    place(s, vis, ox, oy, sc, 0.22)
    s.text(ox, oy + H_TOTAL * sc + 6, 'Vorderansicht mit Deckel', 3.0, weight='bold')
    zs = [0, Z_BASE, Z_TOP, H_TOTAL]
    for a, b in zip(zs, zs[1:]):
        s.dim_v(oy + a * sc, oy + b * sc, ox - 7, fmt(b - a), ext=ox)
    s.dim_v(oy, oy + H_TOTAL * sc, ox - 16, fmt(H_TOTAL), ext=ox)
    s.dim_h(ox, ox + W * sc, oy - 6, fmt(W), ext=oy)
    s.text(ox + W * sc + 4, oy + (Z_TOP + 12) * sc, 'Deckel', 2.2, va='center', col='#444')
    s.text(ox + W * sc + 4, oy + (Z_TOP - 25) * sc, 'Korpus', 2.2, va='center', col='#444')

    # top view without lid
    vis, hid = project(solids(NOLID), 'top', hidden=True)
    ox, oy = 45, 92
    place(s, hid, ox, oy, sc, 0.12, '#888', (0, (2, 1.5)))
    place(s, vis, ox, oy, sc, 0.22)
    s.text(ox, oy + D * sc + 18, 'Draufsicht ohne Deckel', 3.0, weight='bold')
    s.dim_h(ox, ox + W * sc, oy + D * sc + 11, fmt(W), ext=oy + D * sc)
    xs = [0, X_PANEL_IN, X_CHEEK_L, X_KEYS_IN, X_CHEEK_R, X_WALL_R, W]
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        s.dim_h(ox + a * sc, ox + b * sc, oy - 7 - (5 if b == W else 0), fmt(b - a), ext=oy)
    s.dim_v(oy, oy + D * sc, ox + W * sc + 8, fmt(D), ext=ox + W * sc)
    ys = [0, Y_IN, Y_STRIP0, Y_REAR_IN, D]
    for a, b in zip(ys, ys[1:]):
        s.dim_v(oy + a * sc, oy + b * sc, ox + W * sc + 18, fmt(b - a), ext=ox + W * sc)
    ps = [0, Y_IN, Y_FILL0, Y_REAR_IN, D]
    for a, b in zip(ps, ps[1:]):
        s.dim_v(oy + a * sc, oy + b * sc, ox - 8, fmt(b - a), ext=ox)
    s.text(ox + (X_PANEL_IN + 87) * sc, oy + (Y_IN + 117) * sc, 'Öffnung', 2.3, ha='center')
    s.text(ox + (X_PANEL_IN + 87) * sc, oy + (Y_IN + 117) * sc - 3.6, 'Frontplatte', 2.3, ha='center')
    s.text(ox + (X_PANEL_IN + 87) * sc, oy + (Y_FILL0 + 26) * sc, 'Füllstück 8', 2.2, ha='center', va='center',
           col='#555')
    s.text(ox + 540 * sc, oy + (Y_STRIP0 + 68) * sc, 'Abdeckleiste 11 (abnehmbar)', 2.3, ha='center',
           va='center', col='#555')
    s.text(ox + 540 * sc, oy + 52 * sc, 'Tastatur-Öffnung, Tastaturleisten 7', 2.3, ha='center', va='center',
           col='#555')
    s.text(ox, oy - 21, 'gestrichelt: verdeckte Kanten (Tastaturleisten unter der Abdeckleiste, Leisten 9 und 10)',
           2.0, col='#555')

    # left side view with lid (first angle: placed right of the front view)
    vis, _ = project(allp, 'left')
    ox, oy = 315, 212
    place(s, vis, ox + D * sc, oy, sc, 0.22)
    s.text(ox, oy + H_TOTAL * sc + 6, 'Seitenansicht von links', 3.0, weight='bold')
    s.dim_h(ox, ox + D * sc, oy - 6, fmt(D), ext=oy)
    s.text(ox + D * sc, oy - 12, 'vorn', 2.0, ha='right', col='#555')
    s.text(ox, oy - 12, 'hinten', 2.0, col='#555')

    # right side view without lid: cheek profile above the end wall
    vis, hid = project(solids(NOLID), 'right', hidden=True)
    ox, oy = 315, 140
    place(s, hid, ox, oy, sc, 0.12, '#888', (0, (2, 1.5)))
    place(s, vis, ox, oy, sc, 0.22)
    s.text(ox, oy + Z_STRIP * sc + 8, 'Seitenansicht von rechts, ohne Deckel', 3.0, weight='bold')
    s.dim_h(ox, ox + D * sc, oy - 6, fmt(D), ext=oy)
    s.dim_v(oy, oy + Z_TOP * sc, ox + D * sc + 6, fmt(Z_TOP), ext=ox + D * sc)
    s.dim_v(oy, oy + Z_STRIP * sc, ox + D * sc + 14, fmt(Z_STRIP), ext=ox + D * sc)
    s.text(ox, oy - 12, 'vorn', 2.0, col='#555')
    s.text(ox + D * sc, oy - 12, 'hinten', 2.0, ha='right', col='#555')
    s.text(ox, oy - 17, 'Wange 6 ragt über die Seitenwand', 2.0, col='#555')
    s.save()


def sheet_rear(pdf, no):
    s = Sheet(pdf, 'Rückansicht, Deckel', no, 'Maßstab 1:4')
    sc = 0.25
    # rear view without lid
    vis, _ = project(solids(NOLID), 'rear')
    ox, oy = 45, 215
    place(s, vis, ox + W * sc, oy, sc, 0.22)
    s.text(ox, oy + Z_STRIP * sc + 8, 'Rückansicht ohne Deckel', 3.0, weight='bold')
    xr = ox + W * sc
    a, b = xr - WIN_X1 * sc, xr - WIN_X0 * sc
    s.dim_h(ox, a, oy - 7, fmt(W - WIN_X1), ext=oy)
    s.dim_h(a, b, oy - 7, fmt(WIN_X1 - WIN_X0), ext=oy + (Z_BASE + WIN_V0) * sc)
    s.dim_h(b, xr, oy - 7, fmt(WIN_X0), ext=oy)
    s.dim_h(ox, xr, oy - 14, fmt(W), ext=oy)
    s.dim_v(oy, oy + Z_TOP * sc, xr + 6, fmt(Z_TOP), ext=xr)
    s.dim_v(oy, oy + Z_STRIP * sc, xr + 14, fmt(Z_STRIP), ext=xr)
    s.text((a + b) / 2, oy + (Z_BASE + WIN_VC) * sc, 'Fenster', 2.1, ha='center', va='center', col='#555')

    # lid: front view, top view, side view
    lid = solids(lambda p: p.group == 'Deckel')
    sh = [x.copy() for x in lid]
    for x in sh:
        x.translate(Vec(0, 0, -Z_LID0))
    vis, _ = project(sh, 'front')
    ox, oy = 45, 160
    place(s, vis, ox, oy, sc, 0.22)
    s.text(ox, oy + H_LID * sc + 6, 'Deckel - Vorderansicht', 3.0, weight='bold')
    s.dim_v(oy, oy + LID_INSIDE * sc, ox - 7, fmt(LID_INSIDE), ext=ox)
    s.dim_v(oy, oy + H_LID * sc, ox - 15, fmt(H_LID), ext=ox)
    s.dim_h(ox, ox + W * sc, oy - 6, fmt(W), ext=oy)

    vis, hid = project(sh, 'top', hidden=True)
    ox, oy = 45, 60
    place(s, hid, ox, oy, sc, 0.12, '#888', (0, (2, 1.5)))
    place(s, vis, ox, oy, sc, 0.22)
    s.text(ox, oy + D * sc + 6, 'Deckel - Draufsicht (gestrichelt: Deckelwände darunter)', 3.0, weight='bold')
    s.dim_h(ox, ox + W * sc, oy - 6, fmt(W), ext=oy)
    s.dim_v(oy, oy + D * sc, ox + W * sc + 6, fmt(D), ext=ox + W * sc)

    vis, _ = project(sh, 'left')
    ox, oy = 300, 160
    place(s, vis, ox + D * sc, oy, sc, 0.22)
    s.text(ox, oy + H_LID * sc + 6, 'Deckel - Seitenansicht', 3.0, weight='bold')
    s.dim_h(ox, ox + D * sc, oy - 6, fmt(D), ext=oy)

    t = ['Deckelplatte 13 liegt oben auf den vier Deckelwänden, bündig rundum.',
         'Deckel vorn/hinten 14 über die volle Länge %s, Deckel-Seiten 15 dazwischen (%s).' % (fmt(W), fmt(LID_END_L)),
         'Der Deckel liegt mit den Wänden auf den Korpuswänden, außen bündig. Innenhöhe %s über der Wandoberkante.'
         % fmt(LID_INSIDE),
         'Verschlüsse (4 Stück) und Griff setzt Patrick.']
    s.notes(300, 132, 'Deckel', t, 2.25, width=105)
    s.save()


def section_shapes():
    WOOD = ('#e2cfa6', '////')
    shp = [(p.solid, WOOD) for p in PARTS]
    refs = model.references()
    refc = {'frame': ('#d0d4d8', None), 'white': ('#f7f7f2', None), 'black': ('#333333', None),
            'panel': ('#b0b4b8', None), 'metal': ('#c4c9ce', None)}
    for k in ('ref_keybed_frame', 'ref_keys_white', 'ref_keys_black', 'ref_panel', 'ref_panel_standoffs'):
        sh, ck = refs[k]
        shp.append((sh, refc[ck]))
    return shp


def sheet_section_a(pdf, no):
    s = Sheet(pdf, 'Schnitt A-A (Tastatur)', no, 'Maßstab 1:1 (auf A3)')
    sc = 1.0
    xa = 440.0
    ox, oy = 50, 120
    section_x(section_shapes(), xa, sc, ox, oy, s)
    s.text(ox, oy + H_TOTAL + 26, 'Schnitt A-A bei x = %s (Tastatur), von rechts gesehen - vorn links' % fmt(xa),
           3.2, weight='bold')
    z_ordinates(s, [0, Z_BASE, Z_KB, Z_TOP, Z_STRIP0, Z_STRIP, Z_LID1, H_TOTAL], ox, oy, sc, -1)
    z_ordinates(s, [Z_APRON0, Z_STRIP0 - CLEAT_H], ox + D, oy, sc, +1)
    ys = [0, Y_IN, Y_KB0, Y_STRIP0, Y_REAR_IN, D]
    for a, b in zip(ys, ys[1:]):
        s.dim_h(ox + a, ox + b, oy + H_TOTAL + 6 + (6 if b - a < 8 else 0), fmt(b - a), ext=oy + H_TOTAL)
    for i, ry in enumerate(KB_HOLE_Y):
        y0 = Y_KB0 + ry - RISER_W / 2
        s.dim_h(ox, ox + y0, oy - 8 - 7 * i, fmt(y0), ext=(oy, oy + Z_BASE))
        s.dim_h(ox + y0, ox + y0 + RISER_W, oy - 8 - 7 * i, fmt(RISER_W), ext=oy + Z_BASE)
    callout(s, ox + 120, oy + Z_KB + 18, ox + 140, oy - 30, 'Tastatur Fatar TP/9S (grau, nur zur Orientierung)')
    callout(s, ox + Y_KB0 + KB_HOLE_Y[0] - 10, oy + Z_BASE + 6, ox + 20, oy - 30, 'Tastaturleiste 7')
    callout(s, ox + Y_STRIP0 + 100, oy + Z_STRIP - 4, ox + Y_STRIP0 + 60, oy + Z_LID1 - 3, 'Abdeckleiste 11')
    callout(s, ox + Y_REAR_IN - 4, oy + Z_APRON0 + 4, ox + D + 12, oy + Z_APRON0 - 12, 'Blende 12')
    callout(s, ox + Y_CLEAT0 + 40, oy + Z_STRIP0 - 6, ox + D + 12, oy + Z_STRIP0 + 6, 'Leiste 10 (dahinter)')
    callout(s, ox + D - 4, oy + Z_LID1 + 3, ox + D + 12, oy + H_TOTAL + 2, 'Deckel 13 / 14')
    callout(s, ox + Y_REAR_IN + 6, oy + Z_BASE + 6, ox + D + 12, oy + Z_BASE + 2, 'Rückwand 3 (Fenster)')
    callout(s, ox + 6, oy + Z_BASE + 20, ox + 4, oy - 40, 'Vorderwand 2')
    callout(s, ox + 60, oy + 4, ox + 62, oy - 40, 'Boden 1')
    t = ['Die Wände stehen auf dem Boden. Oberkante Wand %s, Abdeckleiste oben %s über Unterkante Boden.'
         % (fmt(Z_TOP), fmt(Z_STRIP)),
         'Tastaturleisten 7: Vorderkante %s und %s ab Außenseite Vorderwand.'
         % tuple(fmt(Y_KB0 + ry - RISER_W / 2) for ry in KB_HOLE_Y),
         'Die Tastatur ist nur zur Orientierung grau eingezeichnet.']
    s.notes(20, 62, 'Hinweise', t, 2.3, width=200)
    s.save()


def sheet_section_b(pdf, no):
    s = Sheet(pdf, 'Schnitt B-B (Frontplatte), Füllstück', no, 'Schnitt 1:1, Detail 1:2 (auf A3)')
    sc = 1.0
    xb = 100.0
    ox, oy = 50, 145
    section_x(section_shapes(), xb, sc, ox, oy, s)
    s.text(ox, oy + H_TOTAL + 20, 'Schnitt B-B bei x = %s (Frontplatte), von rechts gesehen - vorn links'
           % fmt(xb), 3.2, weight='bold')
    z_ordinates(s, [0, Z_BASE, Z_TOP - T_FILL - FCLEAT, Z_TOP - T_FILL, Z_TOP, Z_LID1, H_TOTAL], ox, oy, sc, -1)
    ys = [0, Y_IN, Y_FILL0, Y_REAR_IN, D]
    for a, b in zip(ys, ys[1:]):
        s.dim_h(ox + a, ox + b, oy + H_TOTAL + 6, fmt(b - a), ext=oy + H_TOTAL)
    callout(s, ox + 150, oy + Z_TOP - 1, ox + 150, oy + Z_LID1 - 8, 'Frontplatte (Leiterplatte, nur zur Orientierung)')
    callout(s, ox + Y_FILL0 + 30, oy + Z_TOP - 4, ox + D + 12, oy + Z_TOP + 6, 'Füllstück 8')
    callout(s, ox + Y_FILL0 + 30, oy + Z_TOP - T_FILL - 6, ox + D + 12, oy + Z_TOP - 16, 'Leiste 9 (dahinter)')
    callout(s, ox + Y_IN + GAP_PANEL + PANEL_HOLES[0][1], oy + Z_BASE + 25, ox + 70, oy + Z_BASE + 25,
            'Bolzen M3 (setzt Patrick)')

    # filler with cleats, seen from the front, 1:2
    sc = 0.5
    ox, oy = 50, 70
    fw = PANEL_OPEN
    outline(s, [(0, FCLEAT), (fw, FCLEAT), (fw, FCLEAT + T_FILL), (0, FCLEAT + T_FILL)], ox, oy, sc)
    outline(s, [(0, 0), (FCLEAT, 0), (FCLEAT, FCLEAT), (0, FCLEAT)], ox, oy, sc)
    outline(s, [(fw - FCLEAT, 0), (fw, 0), (fw, FCLEAT), (fw - FCLEAT, FCLEAT)], ox, oy, sc)
    s.line([(ox, oy - 6), (ox, oy + 16)], 0.2, '#888', (0, (3, 1.5)))
    s.line([(ox + fw * sc, oy - 6), (ox + fw * sc, oy + 16)], 0.2, '#888', (0, (3, 1.5)))
    s.text(ox, oy + 26, 'Füllstück 8 auf Leisten 9 - von vorn gesehen (1:2)', 3.0, weight='bold')
    s.text(ox - 2, oy - 4, 'Seitenwand 4', 2.0, ha='right', col='#555')
    s.text(ox + fw * sc + 2, oy - 4, 'Wange 5', 2.0, col='#555')
    s.dim_h(ox, ox + fw * sc, oy + (FCLEAT + T_FILL) * sc + 6, fmt(fw), ext=oy + (FCLEAT + T_FILL) * sc)
    s.dim_v(oy + FCLEAT * sc, oy + (FCLEAT + T_FILL) * sc, ox + fw * sc + 8, fmt(T_FILL), ext=ox + fw * sc)
    s.dim_v(oy, oy + FCLEAT * sc, ox + fw * sc + 8, fmt(FCLEAT), ext=ox + fw * sc)
    t = ['Füllstück 8: %s x %s, liegt hinter der Frontplatten-Öffnung zwischen linker Seitenwand und Wange 5, '
         'hinten an der Rückwand, oben bündig mit den Wänden (Oberkante %s).'
         % (fmt(fw), fmt(Y_REAR_IN - Y_FILL0), fmt(Z_TOP)),
         'Leisten 9: %s x %s x %s, unter dem Füllstück an Seitenwand und Wange geleimt.'
         % (fmt(Y_REAR_IN - Y_FILL0), fmt(FCLEAT), fmt(FCLEAT)),
         'Die Frontplatte liegt nicht auf dem Holz auf, sie sitzt auf Bolzen vom Boden. Eine Falz ist nicht nötig.']
    s.notes(200, 98, 'Füllstück', t, 2.3, width=200)
    s.save()


def z_ordinates(s, zs, x_edge, oy, sc, side=-1, h=2.3):
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


def outline(s, pts, ox, oy, sc, lw=0.35, col='k', ls='-'):
    q = [(ox + u * sc, oy + v * sc) for u, v in pts]
    s.line(q + [q[0]], lw, col, ls)


def sheet_parts(pdf, no):
    s = Sheet(pdf, 'Teile: Wangen, Rückwand', no, 'Wangen 1:2, Rückwand 1:4')
    sc = 0.5
    for i, key in enumerate(('cheek_l', 'cheek_r')):
        p = next(q for q in PARTS if q.fp.key == key)
        ox, oy = 40 + i * 190, 190
        outline(s, p.fp.outline, ox, oy, sc)
        title = ('Wange links (Pos. 5)' if key == 'cheek_l' else 'Wange rechts (Pos. 6)')
        s.text(ox, oy + H_REAR * sc + 16, title + ' - vorn links (niedrige Seite)', 2.9, weight='bold')
        s.dim_h(ox, ox + LW * sc, oy - 8 - (8 if key == 'cheek_l' else 0), fmt(LW), ext=oy)
        s.dim_h(ox, ox + U_KNEE * sc, oy + H_REAR * sc + 7, fmt(U_KNEE), ext=(oy + H_FRONT * sc, oy + H_REAR * sc))
        s.dim_v(oy, oy + H_FRONT * sc, ox - 7, fmt(H_FRONT), ext=ox)
        s.dim_v(oy, oy + H_REAR * sc, ox + LW * sc + 7, fmt(H_REAR), ext=ox + LW * sc)
        if key == 'cheek_l':
            s.dim_h(ox, ox + N0 * sc, oy - 8, fmt(N0), ext=oy)
            s.dim_h(ox + N0 * sc, ox + N1 * sc, oy - 8, fmt(N1 - N0), ext=oy)
            s.dim_h(ox + N1 * sc, ox + LW * sc, oy - 8, fmt(LW - N1), ext=oy)
            s.dim_v(oy, oy + NH * sc, ox + (N0 - 8) * sc, fmt(NH), ext=ox + N0 * sc)
            s.text(ox + (N0 + N1) / 2 * sc, oy + NH * sc + 3, 'Kabeldurchlass', 2.1, ha='center', col='#555')
        y = oy - 26 if key == 'cheek_l' else oy - 18
        for l in ('Dicke %s. Schräge gerade von %s auf %s Höhe, dann waagerecht.' % (fmt(T_CHEEK), fmt(H_FRONT),
                                                                                  fmt(H_REAR)),
                  'Steht zwischen Vorder- und Rückwand auf dem Boden.' if key == 'cheek_l' else
                  'Steht zwischen Vorder- und Rückwand, liegt an der rechten Seitenwand an.') + \
                (('Kabeldurchlass rechteckig von der Unterkante aus aussägen.',) if key == 'cheek_l' else ()):
            s.text(ox, y, l, 2.1, col='#333'); y -= 4

    # rear wall 1:4, seen from outside
    sc = 0.25
    ox, oy = 40, 85
    outline(s, [(0, 0), (W, 0), (W, WALL_H), (0, WALL_H)], ox, oy, sc)
    wa, wb = W - WIN_X1, W - WIN_X0                      # from the left, seen from outside
    outline(s, [(wa, WIN_V0), (wb, WIN_V0), (wb, WIN_V1), (wa, WIN_V1)], ox, oy, sc, 0.3)
    s.text(ox, oy + WALL_H * sc + 10, 'Rückwand (Pos. 3) - von außen gesehen, Fenster rechteckig aussägen', 2.9,
           weight='bold')
    s.dim_h(ox, ox + wa * sc, oy - 7, fmt(wa), ext=oy)
    s.dim_h(ox + wa * sc, ox + wb * sc, oy - 7, fmt(wb - wa), ext=oy + WIN_V0 * sc)
    s.dim_h(ox + wb * sc, ox + W * sc, oy - 7, fmt(W - wb), ext=oy)
    s.dim_h(ox, ox + W * sc, oy - 14, fmt(W), ext=oy)
    s.dim_v(oy, oy + WIN_V0 * sc, ox + W * sc + 8, fmt(WIN_V0), ext=ox + W * sc)
    s.dim_v(oy + WIN_V0 * sc, oy + WIN_V1 * sc, ox + W * sc + 8, fmt(WIN_V1 - WIN_V0), ext=ox + W * sc)
    s.dim_v(oy + WIN_V1 * sc, oy + WALL_H * sc, ox + W * sc + 8, fmt(WALL_H - WIN_V1), ext=ox + W * sc)
    s.dim_v(oy, oy + WALL_H * sc, ox + W * sc + 18, fmt(WALL_H), ext=ox + W * sc)
    s.text(ox, oy - 22, 'Höhenmaße ab Unterkante Rückwand. Fenster %s x %s, Ecken eckig - die Alu-Anschlussplatte '
           'deckt es von außen ab.' % (fmt(wb - wa), fmt(WIN_V1 - WIN_V0)), 2.1, col='#333')
    s.save()


def sheet_base(pdf, no):
    s = Sheet(pdf, 'Teile: Boden, Abdeckleiste, Leisten, Zusammenbau', no, 'Boden 1:4, sonst 1:2')
    sc = 0.25
    ox, oy = 40, 175
    outline(s, [(0, 0), (W, 0), (W, D), (0, D)], ox, oy, sc, 0.35)
    for p in PARTS:
        if p.group != 'Korpus' or p.fp.key in ('base', 'filler', 'cleat', 'fcleat'):
            continue
        b = p.solid.BoundBox
        outline(s, [(b.XMin, b.YMin), (b.XMax, b.YMin), (b.XMax, b.YMax), (b.XMin, b.YMax)], ox, oy, sc, 0.18,
                '#555', (0, (3, 1.5)))
    s.text(ox, oy + D * sc + 8, 'Boden (Pos. 1) von oben, vorn unten - gestrichelt: was darauf steht', 2.9,
           weight='bold')
    yr = [Y_KB0 + ry - RISER_W / 2 for ry in KB_HOLE_Y]
    for i, y0 in enumerate(yr):
        s.dim_v(oy, oy + y0 * sc, ox + W * sc + 7 + 9 * i, fmt(y0), ext=ox + RISER_X1 * sc)
    s.dim_v(oy, oy + D * sc, ox + W * sc + 25, fmt(D), ext=ox + W * sc)
    s.dim_h(ox, ox + RISER_X0 * sc, oy - 7, fmt(RISER_X0), ext=oy + yr[0] * sc)
    s.dim_h(ox + RISER_X0 * sc, ox + RISER_X1 * sc, oy - 7, fmt(RISER_X1 - RISER_X0), ext=oy + yr[0] * sc)
    s.dim_h(ox + RISER_X1 * sc, ox + W * sc, oy - 7, fmt(W - RISER_X1), ext=oy)
    s.dim_h(ox, ox + W * sc, oy - 14, fmt(W), ext=oy)
    for y0 in yr:
        s.text(ox + (RISER_X0 + RISER_X1) / 2 * sc, oy + (y0 + RISER_W / 2) * sc, 'Tastaturleiste 7', 2.0,
               ha='center', va='center', col='#555')
    s.text(ox + 95 * sc, oy + 140 * sc, 'Frontplatte', 2.0, ha='center', col='#555')
    s.text(ox, oy - 21, 'Tastaturleisten 7 (%s x %s x %s) auf den Boden leimen; ihre Lage passt zu den '
           'Schraublöchern der Tastatur, die Patrick bohrt.' % (fmt(RISER_X1 - RISER_X0), fmt(RISER_W),
                                                               fmt(T_RISER)), 2.1, col='#333')

    # strip with apron: cross-section 1:2
    sc = 0.5
    ox, oy = 40, 80
    sd = Y_REAR_IN - Y_STRIP0
    ah = Z_STRIP0 - Z_APRON0
    outline(s, [(0, ah), (sd, ah), (sd, ah + T_STRIP), (0, ah + T_STRIP)], ox, oy, sc)
    outline(s, [(sd - T_APRON, 0), (sd, 0), (sd, ah), (sd - T_APRON, ah)], ox, oy, sc)
    s.text(ox, oy + (ah + T_STRIP) * sc + 14, 'Abdeckleiste 11 + Blende 12, Querschnitt', 2.9,
           weight='bold')
    s.dim_h(ox, ox + sd * sc, oy + (ah + T_STRIP) * sc + 6, fmt(sd), ext=oy + (ah + T_STRIP) * sc)
    s.dim_h(ox + (sd - T_APRON) * sc, ox + sd * sc, oy - 6, fmt(T_APRON), ext=oy)
    s.dim_v(oy + ah * sc, oy + (ah + T_STRIP) * sc, ox - 6, fmt(T_STRIP), ext=ox)
    s.dim_v(oy, oy + ah * sc, ox + sd * sc + 7, fmt(ah), ext=ox + sd * sc)
    s.text(ox, oy - 14, 'Blende 12 unter die Abdeckleiste leimen, hinten bündig, Länge %s.' % fmt(KEYS_OPEN),
           2.1, col='#333')
    s.text(ox, oy - 18, 'Die Abdeckleiste liegt lose auf den Leisten 10 (nicht einleimen).', 2.1, col='#333')

    # strip cleat on a cheek: 1:2
    ox, oy = 152, 82
    p = next(q for q in PARTS if q.fp.key == 'cheek_r')
    outline(s, p.fp.outline, ox, oy, sc, 0.18, '#777')
    c0 = Y_CLEAT0 - Y_IN
    cl = Y_CLEAT1 - Y_CLEAT0
    cv0 = Z_STRIP0 - CLEAT_H - Z_BASE
    outline(s, [(c0, cv0), (c0 + cl, cv0), (c0 + cl, cv0 + CLEAT_H), (c0, cv0 + CLEAT_H)], ox, oy, sc, 0.35)
    s.text(ox, oy + H_REAR * sc + 14, 'Leiste 10 innen an der Wange (beide Wangen), vorn links', 2.9,
           weight='bold')
    s.dim_h(ox, ox + c0 * sc, oy + H_REAR * sc + 6, fmt(c0), ext=oy + (cv0 + CLEAT_H) * sc)
    s.dim_h(ox + c0 * sc, ox + (c0 + cl) * sc, oy + H_REAR * sc + 6, fmt(cl), ext=oy + (cv0 + CLEAT_H) * sc)
    s.dim_v(oy + (cv0 + CLEAT_H) * sc, oy + H_REAR * sc, ox + LW * sc + 7, fmt(H_REAR - cv0 - CLEAT_H),
            ext=ox + LW * sc)
    s.dim_v(oy + cv0 * sc, oy + (cv0 + CLEAT_H) * sc, ox + LW * sc + 7, fmt(CLEAT_H), ext=ox + LW * sc)
    s.dim_v(oy, oy + cv0 * sc, ox + LW * sc + 7, fmt(cv0), ext=ox + LW * sc)
    s.text(ox, oy - 8, 'Leiste 10: %s x %s x %s, %s breit quer zur Wange. Oberkante %s unter der Wangen-'
           'Oberkante (= Dicke Abdeckleiste).' % (fmt(cl), fmt(CLEAT_W), fmt(CLEAT_H), fmt(CLEAT_W), fmt(T_STRIP)),
           2.1, col='#333')
    s.text(ox, oy - 12, 'Abstand vorn ab Wangen-Vorderkante; hinten endet sie an der Blende 12.', 2.1, col='#333')

    t = ['1. Tastaturleisten 7 auf den Boden 1 leimen.',
         '2. Vorderwand 2 und Rückwand 3 auf den Boden, Seitenwände 4 dazwischen.',
         '3. Wangen 5 und 6 zwischen Vorder- und Rückwand: Wange 6 an der rechten Seitenwand, Wange 5 mit '
         '%s Innenmaß zur linken Seitenwand.' % fmt(PANEL_OPEN),
         '4. Leisten 9 und Füllstück 8 hinter der Frontplatten-Öffnung, Leisten 10 innen an die Wangen.',
         '5. Abdeckleiste 11 und Blende 12 als eigenes Teil verleimen, lose einlegen.',
         '6. Deckel 13-15 als eigener Kasten.']
    s.notes(40, 52, 'Zusammenbau', t, 2.25, width=185, bullets=False)
    s.save()


N_SHEETS = 8


# ------------------------------------------------------------------ checks
def check(log):
    out = []
    w = out.append
    w('Carpenter variant %s - checks against params.py and %s' % (DOC_REV, os.path.basename(STEP_REF)))
    w('KB_LIP = %s (%s)' % (fmt(KB_LIP), 'measured' if HEIGHTS_CONFIRMED else 'NOT measured, draft'))
    w('')
    # 1. collisions between the carpenter parts
    bad = []
    for a, b in itertools.combinations(PARTS, 2):
        v = a.solid.common(b.solid).Volume
        if v > 1e-3:
            bad.append('%s / %s: %.1f mm3' % (a.fp.key, b.fp.key, v))
    w('1. overlap between carpenter parts: %s' % ('none' if not bad else '; '.join(bad)))
    # 2. reference bodies (keybed, panel, boards) against the wood
    refs = model.references()
    hits = []
    for k, (sh, _) in refs.items():
        if k in ('ref_feet', 'ref_latches', 'ref_plate_parts'):
            continue
        for p in PARTS:
            if sh.BoundBox.intersect(p.solid.BoundBox) and sh.common(p.solid).Volume > 1e-3:
                hits.append('%s / %s' % (k, p.fp.key))
    w('2. reference bodies inside wood: %s' % ('none' if not hits else '; '.join(hits)))
    # 3. clearances that the carpenter must keep
    def dist(a, b):
        return a.distToShape(b)[0]
    get = lambda key: [p.solid for p in PARTS if p.fp.key == key][0]
    cl = [('keybed -> left cheek', refs['ref_keybed_frame'][0], get('cheek_l'), GAP_KB_SIDE),
          ('keybed -> right cheek', refs['ref_keybed_frame'][0], get('cheek_r'), GAP_KB_SIDE),
          ('panel -> left end wall', refs['ref_panel'][0], get('end_l'), GAP_PANEL),
          ('panel -> left cheek', refs['ref_panel'][0], get('cheek_l'), GAP_PANEL),
          ('panel -> front wall', refs['ref_panel'][0], get('front'), GAP_PANEL),
          ('panel -> filler', refs['ref_panel'][0], get('filler'), GAP_PANEL),
          ('lid top -> strip', get('lid_top'), get('strip'), 5.0),
          ('board 3620 parts -> filler cleats', refs['ref_board3620_parts'][0],
           Part.makeCompound([p.solid for p in PARTS if p.fp.key == 'fcleat']), 1.0)]
    w('3. clearances (mm)            actual   min')
    for label, a, b, need in cl:
        d = dist(a, b)
        w('   %-28s %6.2f %6.2f  %s' % (label, d, need, 'ok' if d >= need - 1e-6 else 'FAIL'))
    # 4. compare with the CNC STEP: envelope per part and the union of all wood
    doc = App.newDocument('ref')
    Import.insert(STEP_REF, doc.Name)
    step = {}
    for o in doc.Objects:
        if o.TypeId == 'Part::Feature' and o.Shape.Solids:
            step.setdefault(o.Label.rstrip('0123456789'), []).append(o.Shape)
    wood_step = [s for k, v in step.items() if k != 'Rear plate' for s in v]
    S = wood_step[0].fuse(wood_step[1:]).removeSplitter()
    M = PARTS[0].solid.fuse([p.solid for p in PARTS[1:]]).removeSplitter()
    bS, bM = S.BoundBox, M.BoundBox
    w('4. overall envelope   STEP %s x %s x %s   carpenter %s x %s x %s' % (
        fmt(bS.XLength), fmt(bS.YLength), fmt(bS.ZLength), fmt(bM.XLength), fmt(bM.YLength), fmt(bM.ZLength)))
    extra = M.cut(S); missing = S.cut(M)
    w('   wood in carpenter, not in STEP: %.0f mm3 (holes, dogbones, fit gaps, radii, filler cleats %.0f)'
      % (extra.Volume, 2 * FCLEAT * FCLEAT * (Y_REAR_IN - Y_FILL0)))
    w('   wood in STEP, not in carpenter: %.0f mm3 - expected: only the rounded corners of the cable notch (R%s)'
      % (missing.Volume, fmt(CABLE_NOTCH_R)))
    w('   and of the rear window (R%s), which are square here. Anything else would be a mistake.' % fmt(WINDOW[3]))
    big = [s for s in missing.Solids if s.Volume > 50]
    for s_ in big:
        b = s_.BoundBox
        w('     corner %.0f mm3 at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (s_.Volume, b.XMin, b.XMax, b.YMin, b.YMax,
                                                                      b.ZMin, b.ZMax))
    bige = sorted([s for s in extra.Solids if s.Volume > 500], key=lambda s_: -s_.Volume)
    for s_ in bige:
        b = s_.BoundBox
        w('     + %.0f mm3 at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (s_.Volume, b.XMin, b.XMax, b.YMin, b.YMax,
                                                                     b.ZMin, b.ZMax))
    # 5. cut list against params.py, computed independently
    exp = {1: (W, D, T_BASE), 2: (W, Z_TOP - T_BASE, T_WALL), 3: (W, Z_TOP - T_BASE, T_WALL),
           4: (D - 2 * T_WALL, Z_TOP - T_BASE, T_WALL), 5: (D - 2 * T_WALL, Z_STRIP - T_BASE, T_CHEEK),
           6: (D - 2 * T_WALL, Z_STRIP - T_BASE, T_CHEEK), 7: (RISER_X1 - RISER_X0, RISER_W, T_RISER),
           8: (X_CHEEK_L - T_WALL, D - T_WALL - Y_FILL0, T_FILL), 9: (D - T_WALL - Y_FILL0, FCLEAT, FCLEAT),
           10: (Y_CLEAT1 - Y_CLEAT0, CLEAT_W, CLEAT_H), 11: (X_CHEEK_R - X_KEYS_IN, Y_REAR_IN - Y_STRIP0, T_STRIP),
           12: (KB_W + 2 * GAP_KB_SIDE, Z_STRIP - T_STRIP - Z_APRON0, T_APRON), 13: (W, D, T_LID_TOP),
           14: (W, H_LID - T_LID_TOP, T_LID_WALL), 15: (D - 2 * T_LID_WALL, H_LID - T_LID_TOP, T_LID_WALL)}
    w('5. cut list vs params.py and STEP bounding boxes')
    w('   STEP boxes include the CNC tabs and fingers (base +9, finger joints +12/24, tabs into the lid top +6),')
    w('   so they are larger than the butt-joint parts by exactly those joint depths.')
    w('   pos name                                 L x B x D            params        STEP part (bbox, incl. tabs)')
    stepname = {1: 'Base', 2: 'Front wall', 3: 'Rear wall', 4: 'End wall left', 5: 'Cheek left', 6: 'Cheek right',
                7: 'Keybed riser', 8: 'Filler behind the panel', 10: 'Strip cleat', 11: 'Strip behind the keys',
                12: 'Apron under the strip', 13: 'Lid top', 14: 'Lid front/rear', 15: 'Lid end'}
    for r in cutlist():
        e = tuple(sorted(exp[r['pos']], reverse=True)[:2]) + (exp[r['pos']][2],)
        got = (r['L'], r['B'], r['T'])
        ok = all(abs(a - b) < 1e-6 for a, b in zip(sorted(got[:2]), sorted(e[:2]))) and abs(got[2] - e[2]) < 1e-6
        sn = stepname.get(r['pos'])
        sb = ''
        if sn and sn in step:
            b = step[sn][0].BoundBox
            sb = '%s x %s x %s' % tuple(fmt(v) for v in sorted((b.XLength, b.YLength, b.ZLength), reverse=True))
        elif r['pos'] == 9:
            sb = '(not in Rev0.2: filler held by tabs)'
        w('   %2d  %-36s %-20s %-4s  %s' % (r['pos'], r['name'], '%s x %s x %s' % (fmt(got[0]), fmt(got[1]),
                                                                                 fmt(got[2])),
                                         'ok' if ok else 'FAIL', sb))
    App.closeDocument(doc.Name)
    with open(log, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('\n'.join(out).encode('ascii', 'replace').decode())


def main():
    os.makedirs(OUT, exist_ok=True)
    fn = os.path.join(OUT, PDF_NAME)
    with PdfPages(fn) as pdf:
        sheet_overview(pdf, 1)
        sheet_cutlist(pdf, 2)
        sheet_views(pdf, 3)
        sheet_rear(pdf, 4)
        sheet_section_a(pdf, 5)
        sheet_section_b(pdf, 6)
        sheet_parts(pdf, 7)
        sheet_base(pdf, 8)
        d = pdf.infodict()
        d['Title'] = 'ARP 3620 Holzgehäuse - Ausführung Tischler %s' % DOC_REV
        d['Author'] = 'Dsl-man.de'
    print('wrote', fn)
    if not os.environ.get('NO_CHECK'):
        check(os.path.join(OUT, 'check_carpenter.txt'))


main()
