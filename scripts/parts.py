# -*- coding: utf-8 -*-
"""Every manufactured part as a flat outline with holes and cut-outs.

A part lives in its own (u, v) plane and has a thickness t along w.
Placement: P = O + u*U + v*V + w*N, w in 0..t, always with N = U x V, so a
drawing in (u, v) shows the part from its front face (w = t).
The same data feed the 3D model (build.py), the DXF files (dxf_out.py)
and the drawing (drawing.py)."""
from params import *
from geom2d import rect

X = (1, 0, 0); Y = (0, 1, 0); Z = (0, 0, 1)
NX = (-1, 0, 0); NY = (0, -1, 0)


class Hole:
    def __init__(self, u, v, d, csk=None, side='front', kind='drill', note='', covered=False):
        self.u, self.v, self.d = u, v, d
        self.covered = covered  # screw head hidden under the tolex (left out of the renders)
        self.csk = csk          # countersink diameter (90 deg) or None
        self.side = side        # 'front' = w = t side, 'back' = w = 0 side
        self.kind = kind        # 'drill' (through) or 'pilot' (not modelled in 3D)
        self.note = note


class Part:
    def __init__(self, key, name, material, t, outline, radii=None, O=(0, 0, 0), U=X, V=Y, N=Z,
                 qty=1, cover='', note=''):
        self.key, self.name, self.material, self.t = key, name, material, t
        self.outline, self.radii = outline, radii or [0.0] * len(outline)
        self.O, self.U, self.V, self.N = O, U, V, N
        self.qty, self.cover, self.note = qty, cover, note
        self.holes, self.cutouts, self.texts = [], [], []   # cutouts: (pts, radii)
        self.mirror_of = None                               # placed copies share one drawing

    def bbox(self):
        us = [p[0] for p in self.outline]; vs = [p[1] for p in self.outline]
        return min(us), min(vs), max(us), max(vs)

    def size(self):
        u0, v0, u1, v1 = self.bbox()
        return u1 - u0, v1 - v0

    def to3d(self, u, v, w=0.0):
        return tuple(self.O[i] + u * self.U[i] + v * self.V[i] + w * self.N[i] for i in range(3))


PLY12, PLY9, PLY6 = "birch plywood 12", "birch plywood 9", "birch plywood 6"
ALU2 = "aluminium 2"


def kb_holes_xy():
    """Keybed fixing holes in case x/y."""
    x0 = X_KEYS_IN + GAP_KB_SIDE
    return [(x0 + hx, Y_KB0 + hy) for hy in KB_HOLE_Y for hx in KB_HOLE_X]


def screw_line(a, b, pitch=SCREW_PITCH, end=25.0):
    """Evenly spaced screw positions between a and b, first/last 'end' from the ends."""
    l = b - a - 2 * end
    n = max(1, int(round(l / pitch)))
    return [a + end + l * k / n for k in range(n + 1)]


def make_parts():
    P = []

    # ------------------------------------------------------------ base
    base = Part('base', 'Base', PLY9, T_BASE, rect(0, 0, W, D), O=(0, 0, 0),
                cover='underside painted black, top edge covered by the tolex of the walls')
    for x, y in kb_holes_xy():
        base.holes.append(Hole(x, y, 5.0, csk=10.0, side='back', note='keybed, screw from below'))
    for x, y in FEET:
        base.holes.append(Hole(x, y, 2.5, kind='pilot', side='back', note='foot'))
    for hx, hy in PANEL_HOLES:
        base.holes.append(Hole(X_PANEL_IN + GAP_PANEL + hx, Y_PANEL0 + hy, 3.4, csk=6.5, side='back',
                               note='panel standoff M3'))
    for hx, hy in EMU_HOLES:
        base.holes.append(Hole(EMU_X0 + hx, EMU_Y0 + hy, 3.4, csk=6.5, side='back', note='emulator standoff M3'))
    for hx, hy in NT_HOLES:
        base.holes.append(Hole(NT_X0 + hx, NT_Y0 + hy, 3.4, csk=6.5, side='back', note='power supply standoff M3'))
    # assembly screws from below: walls, cheeks, risers
    asm = []
    for x in screw_line(0, W):
        asm += [(x, T_WALL / 2), (x, D - T_WALL / 2)]
    for y in screw_line(Y_IN, Y_REAR_IN):
        for x in (T_WALL / 2, W - T_WALL / 2, X_CHEEK_L + T_CHEEK / 2, X_CHEEK_R + T_CHEEK / 2):
            if not (x < X_CHEEK_L and CABLE_NOTCH[0] < y - Y_IN < CABLE_NOTCH[1] and x > T_WALL) \
               and not (abs(x - (X_CHEEK_L + T_CHEEK / 2)) < 1 and CABLE_NOTCH[0] < y - Y_IN < CABLE_NOTCH[1]):
                asm.append((x, y))
    for ry in (KB_HOLE_Y[0], KB_HOLE_Y[1]):
        for x in screw_line(RISER_X0, RISER_X1, pitch=170.0):
            if min(abs(x - kx) for kx, _ in kb_holes_xy()) > 25:
                asm.append((x, Y_KB0 + ry))
    for x, y in asm:
        base.holes.append(Hole(x, y, 4.0, csk=8.0, side='back', note='assembly screw 4 x 30'))
    P.append(base)

    # ------------------------------------------------------------ outer walls
    # N = -y: the front wall is seen from outside (front face = outer face),
    # the rear wall from inside (front face = inner face)
    for key, name, y0 in (('front', 'Front wall', T_WALL), ('rear', 'Rear wall', D)):
        w = Part(key, name, PLY12, T_WALL, rect(0, 0, W, WALL_H), O=(0, y0, Z_BASE), U=X, V=Z, N=NY,
                 cover='tolex outside, over the top edge, 20 mm down the inside')
        side = 'front' if key == 'front' else 'back'          # countersinks always outside
        for x in (T_WALL / 2, X_CHEEK_L + T_CHEEK / 2, X_CHEEK_R + T_CHEEK / 2, W - T_WALL / 2):
            for v in (15.0, 35.0):
                w.holes.append(Hole(x, v, 4.0, csk=8.0, side=side, covered=True,
                                    note='screw 4 x 40 into end wall / cheek'))
        if key == 'rear':
            u0, u1, h, r = WINDOW
            vc = PLATE_Z0 + PLATE_H / 2 - Z_BASE
            xa, xb = PLATE_X_RIGHT - u1, PLATE_X_RIGHT - u0
            w.cutouts.append((rect(xa, vc - h / 2, xb, vc + h / 2), [r] * 4))
            for su, sv in PLATE_SCREWS:
                w.holes.append(Hole(PLATE_X_RIGHT - su, PLATE_Z0 + sv - Z_BASE, 2.5, kind='pilot',
                                    side='back', note='rear plate, screw 3.5 x 16'))
        P.append(w)

    for key, name, x0 in (('end_l', 'End wall', 0.0), ('end_r', 'End wall', W - T_WALL)):
        e = Part(key, name, PLY12, T_WALL, rect(0, 0, Y_REAR_IN - Y_IN, WALL_H),
                 O=(x0, Y_IN, Z_BASE), U=Y, V=Z, N=X, cover='tolex outside, over the top edge')
        P.append(e)

    # ------------------------------------------------------------ cheeks
    L = Y_REAR_IN - Y_IN                      # 286
    hf = Z_TOP - Z_BASE                       # 50 at the front
    hs = Z_STRIP - Z_BASE                     # 73 under the strip
    uk = Y_STRIP0 - Y_IN                      # 149.5, knee
    for key, name, x0 in (('cheek_l', 'Cheek left', X_CHEEK_L), ('cheek_r', 'Cheek right', X_CHEEK_R)):
        if key == 'cheek_l':
            n0, n1, nh = CABLE_NOTCH
            pts = [(0, 0), (n0, 0), (n0, nh), (n1, nh), (n1, 0), (L, 0), (L, hs), (uk, hs), (0, hf)]
            rad = [0, 0, CABLE_NOTCH_R, CABLE_NOTCH_R, 0, 0, 0, CHEEK_KNEE_R, 0]
        else:
            pts = [(0, 0), (L, 0), (L, hs), (uk, hs), (0, hf)]
            rad = [0, 0, 0, CHEEK_KNEE_R, 0]
        c = Part(key, name, PLY12, T_CHEEK, pts, rad, O=(x0, Y_IN, Z_BASE), U=Y, V=Z, N=X,
                 cover='tolex on both faces and the top edge')
        P.append(c)

    # ------------------------------------------------------------ risers
    for i, ry in enumerate(KB_HOLE_Y):
        yc = Y_KB0 + ry
        r = Part('riser_%d' % (i + 1), 'Keybed riser', PLY12, T_RISER,
                 rect(0, 0, RISER_X1 - RISER_X0, RISER_W), O=(RISER_X0, yc - RISER_W / 2, Z_BASE),
                 cover='black paint')
        for x, y in kb_holes_xy():
            if abs(y - yc) < 1:
                r.holes.append(Hole(x - RISER_X0, RISER_W / 2, 5.0, note='keybed screw'))
        P.append(r)

    # ------------------------------------------------------------ strip, apron, cleats (removable unit)
    sl = X_CHEEK_R - X_KEYS_IN                # 689
    sd = Y_REAR_IN - Y_STRIP0                 # 136.5
    s = Part('strip', 'Strip behind the keys', PLY9, T_STRIP, rect(0, 0, sl, sd), [0, 0, 0, 0],
             O=(X_KEYS_IN, Y_STRIP0, Z_STRIP0), cover='tolex on top, front edge and ends')
    for y in STRIP_SCREW_Y:
        for u in (CLEAT_W / 2, sl - CLEAT_W / 2):
            s.holes.append(Hole(u, y - Y_STRIP0, 4.0, csk=8.0, side='front', note='screw 3.5 x 20 into cleat'))
    P.append(s)
    a = Part('apron', 'Apron under the strip', PLY9, T_APRON, rect(0, 0, sl, Z_STRIP0 - Z_APRON0),
             O=(X_KEYS_IN, Y_REAR_IN, Z_APRON0), U=X, V=Z, N=NY,
             cover='black paint, glued and screwed under the strip')
    P.append(a)
    for key, x0 in (('cleat_l', X_KEYS_IN), ('cleat_r', X_CHEEK_R - CLEAT_W)):
        cl = Part(key, 'Strip cleat', PLY12, CLEAT_W,
                  rect(0, 0, Y_CLEAT1 - Y_CLEAT0, CLEAT_H), O=(x0, Y_CLEAT0, Z_STRIP0 - CLEAT_H), U=Y, V=Z, N=X,
                  cover='black paint', note='cut from 15 mm strips of 12 mm plywood')
        P.append(cl)

    # ------------------------------------------------------------ filler behind the panel
    f = Part('filler', 'Filler behind the panel', PLY9, T_FILL, rect(0, 0, PANEL_OPEN, Y_REAR_IN - Y_FILL0),
             O=(X_PANEL_IN, Y_FILL0, Z_TOP - T_FILL), cover='tolex on top and front edge')
    P.append(f)
    for key, x0 in (('fcleat_l', X_PANEL_IN), ('fcleat_r', X_CHEEK_L - FCLEAT)):
        fc = Part(key, 'Filler cleat', PLY12, FCLEAT, rect(0, 0, Y_REAR_IN - Y_FILL0, FCLEAT),
                  O=(x0, Y_FILL0, Z_TOP - T_FILL - FCLEAT), U=Y, V=Z, N=X, cover='black paint')
        P.append(fc)

    # ------------------------------------------------------------ lid
    lt = Part('lid_top', 'Lid top', PLY6, T_LID_TOP, rect(0, 0, W, D), O=(0, 0, Z_LID1),
              cover='tolex outside')
    P.append(lt)
    for key, name, y0 in (('lid_front', 'Lid front/rear', T_LID_WALL), ('lid_rear', 'Lid front/rear', D)):
        P.append(Part(key, name, PLY9, T_LID_WALL, rect(0, 0, W, LID_INSIDE), O=(0, y0, Z_LID0),
                      U=X, V=Z, N=NY, cover='tolex outside and over the lower edge'))
    for key, name, x0 in (('lid_end_l', 'Lid end', 0.0), ('lid_end_r', 'Lid end', W - T_LID_WALL)):
        P.append(Part(key, name, PLY9, T_LID_WALL, rect(0, 0, D - 2 * T_LID_WALL, LID_INSIDE),
                      O=(x0, T_LID_WALL, Z_LID0), U=Y, V=Z, N=X, cover='tolex outside and over the lower edge'))

    # ------------------------------------------------------------ rear plate
    pl = Part('plate', 'Rear plate', ALU2, T_PLATE, rect(0, 0, PLATE_L, PLATE_H), [PLATE_R] * 4,
              O=(PLATE_X_RIGHT, D + TOLEX, PLATE_Z0), U=NX, V=Z, N=Y,
              cover='black anodised, engraved white (or printed)')
    for su, sv in PLATE_SCREWS:
        pl.holes.append(Hole(su, sv, PLATE_SCREW_D, csk=PLATE_SCREW_CSK, side='front', note='screw 3.5 x 16'))
    for u, v, top, bot, holes in PLATE_ITEMS:
        for du, dv, d in holes:
            pl.holes.append(Hole(u + du, v + dv, d, note=top))
        pl.texts.append((u, v + 13.0, top))
        if bot:
            pl.texts.append((u, v - 13.0 - PLATE_TEXT_H, bot))
    P.append(pl)
    return P


PARTS = make_parts()
BY_KEY = {p.key: p for p in PARTS}
