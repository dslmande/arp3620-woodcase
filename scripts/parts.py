# -*- coding: utf-8 -*-
"""Every manufactured part as a flat outline with holes and cut-outs.

A part lives in its own (u, v) plane and has a thickness t along w.
Placement: P = O + u*U + v*V + w*N, w in 0..t, always with N = U x V, so a
drawing in (u, v) shows the part from its front face (w = t).
The same data feed the 3D model (build.py), the DXF files (dxf_out.py)
and the drawing (drawing.py). Joints: see joints.py."""
from params import *
from geom2d import rect
from joints import fingers, tabs, notches, slot, tab_line, profile

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
ALUZ = "aluminium Z 20 x 20 x 2"


def kb_holes_xy():
    """Keybed fixing holes in case x/y."""
    x0 = X_KEYS_IN + GAP_KB_SIDE
    return [(x0 + hx, Y_KB0 + hy) for hy in KB_HOLE_Y for hx in KB_HOLE_X]


def screw_line(a, b, pitch=SCREW_PITCH, end=25.0):
    """Evenly spaced screw positions between a and b, first/last 'end' from the ends."""
    l = b - a - 2 * end
    n = max(1, int(round(l / pitch)))
    return [a + end + l * k / n for k in range(n + 1)]


# ------------------------------------------------------------------ joint positions
# tab centres; u/v are the coordinates of the part that carries the tab
FW_TABS = tab_line(70.0, 840.0, 130.0)                  # front/rear wall -> base, x
END_TABS = tab_line(50.0, Y_REAR_IN - Y_IN - 50.0, 95.0)  # end walls, right cheek -> base, y - Y_IN
CL_TABS = [45.0, 133.0]                                  # left cheek -> base (in front of the cable notch)
FILL_SIDE = [(Y_REAR_IN - Y_FILL0) / 2]                  # filler -> end wall / cheek, y - Y_FILL0
FILL_REAR = [45.0, PANEL_OPEN - 45.0]                    # filler -> rear wall, x - X_PANEL_IN
APRON_TABS = tab_line(60.0, KEYS_OPEN - 60.0, 140.0)     # apron -> strip, x - X_KEYS_IN
CLEAT_TABS = [25.0, Y_CLEAT1 - Y_CLEAT0 - 25.0]          # cleat -> cheek, symmetric
LID_TABS_X = tab_line(70.0, W - 70.0, 130.0)             # lid front/rear -> lid top, x
LID_TABS_Y = tab_line(70.0, D - 70.0, 85.0)              # lid ends -> lid top, y

ALL5 = set(range(N_FINGER))
END_OWN = {k for k in ALL5 if k % 2 == 0}                # end walls own the bottom, middle and top finger
LID_END_OWN = {k for k in range(N_FINGER_LID) if k % 2 == 0}


def jpart(key, name, material, t, pts, radii, feats, **kw):
    p2, r2 = profile(pts, radii or [0.0] * len(pts), feats)
    return Part(key, name, material, t, p2, r2, **kw)


def make_parts():
    P = []
    LW = Y_REAR_IN - Y_IN                     # 286, end wall and cheek length between the walls

    # ------------------------------------------------------------ base
    # walls stand on the base, their tabs fill notches in its edges (flush underneath)
    bf = {0: notches(FW_TABS, TAB_W, T_WALL),
          2: notches(FW_TABS, TAB_W, T_WALL),
          3: notches([Y_IN + c for c in END_TABS], TAB_W, T_WALL),
          1: notches([Y_IN + c for c in END_TABS], TAB_W, T_WALL + T_CHEEK)}   # end wall + right cheek
    base = jpart('base', 'Base', PLY9, T_BASE, rect(0, 0, W, D), None, bf, O=(0, 0, 0),
                 cover='underside painted black, edges covered by the tolex of the walls')
    for c in CL_TABS:
        base.cutouts.append(slot(X_CHEEK_L, X_CHEEK_L + T_CHEEK, Y_IN + c - TAB_W / 2, Y_IN + c + TAB_W / 2))
    for x, y in FEET:
        base.holes.append(Hole(x, y, 2.5, kind='pilot', side='back', note='foot'))
    for hx, hy in PANEL_HOLES:
        base.holes.append(Hole(X_PANEL_IN + GAP_PANEL + hx, Y_PANEL0 + hy, 3.4, csk=6.5, side='back',
                               note='panel standoff M3'))
    for hx, hy in EMU_HOLES:
        base.holes.append(Hole(EMU_X0 + hx, EMU_Y0 + hy, 3.4, csk=6.5, side='back', note='emulator standoff M3'))
    for hx, hy in NT_HOLES:
        base.holes.append(Hole(NT_X0 + hx, NT_Y0 + hy, 3.4, csk=6.5, side='back', note='power supply standoff M3'))
    for i, ry in enumerate(KB_HOLE_Y):
        yb = Y_KB0 + ry + (Z_BOTTOM_OFF if i == 0 else -Z_BOTTOM_OFF)   # bottom flange centre
        for x in screw_line(RISER_X0, RISER_X1, pitch=170.0):
            base.holes.append(Hole(x, yb, 4.5, csk=9.0, side='back', note='Z profile M4 x 12'))
    P.append(base)

    # ------------------------------------------------------------ outer walls
    # N = -y: the front wall is seen from outside (front face = outer face),
    # the rear wall from inside (front face = inner face)
    cheek_tab = slot(X_CHEEK_L, X_CHEEK_L + T_CHEEK, *CHEEK_TAB_V)
    for key, name, y0 in (('front', 'Front wall', T_WALL), ('rear', 'Rear wall', D)):
        f = {0: tabs(FW_TABS, TAB_W, T_BASE),
             3: fingers(0, WALL_H, N_FINGER, ALL5 - END_OWN, T_WALL, base='outer'),
             1: fingers(0, WALL_H, N_FINGER, ALL5 - END_OWN, T_WALL + T_CHEEK, base='outer')}
        if key == 'rear':
            f[2] = notches([X_PANEL_IN + c for c in FILL_REAR], FILLER_TAB_W + 6, T_FILL)
        w = jpart(key, name, PLY12, T_WALL, rect(0, 0, W, WALL_H), None, f,
                  O=(0, y0, Z_BASE), U=X, V=Z, N=NY,
                  cover='tolex outside, over the top edge, 20 mm down the inside')
        w.cutouts.append(cheek_tab)
        if key == 'rear':
            u0, u1, h, r = WINDOW
            vc = PLATE_Z0 + PLATE_H / 2 - Z_BASE
            xa, xb = PLATE_X_RIGHT - u1, PLATE_X_RIGHT - u0
            w.cutouts.append((rect(xa, vc - h / 2, xb, vc + h / 2), [r] * 4))
            for su, sv in PLATE_SCREWS:
                w.holes.append(Hole(PLATE_X_RIGHT - su, PLATE_Z0 + sv - Z_BASE, 2.5, kind='pilot',
                                    side='back', note='rear plate, screw 3.5 x 16'))
        P.append(w)

    for key, name, x0 in (('end_l', 'End wall left', 0.0), ('end_r', 'End wall right', W - T_WALL)):
        f = {0: tabs(END_TABS, TAB_W, T_BASE),
             1: fingers(0, WALL_H, N_FINGER, END_OWN, T_WALL),
             3: fingers(0, WALL_H, N_FINGER, END_OWN, T_WALL)}
        if key == 'end_l':
            f[2] = notches([Y_FILL0 - Y_IN + c for c in FILL_SIDE], FILLER_TAB_W, T_FILL)
        e = jpart(key, name, PLY12, T_WALL, rect(0, 0, LW, WALL_H), None, f,
                  O=(x0, Y_IN, Z_BASE), U=Y, V=Z, N=X, cover='tolex outside, over the top edge')
        P.append(e)

    # ------------------------------------------------------------ cheeks
    hf = Z_TOP - Z_BASE                       # 50 at the front
    hs = Z_STRIP - Z_BASE                     # 73 under the strip
    uk = Y_STRIP0 - Y_IN                      # 149.5, knee
    cleat_v = (Z_STRIP0 - CLEAT_H - Z_BASE, Z_STRIP0 - Z_BASE)       # 52 .. 64
    cleat_slots = [slot(Y_CLEAT0 - Y_IN + c - CLEAT_TAB_W / 2, Y_CLEAT0 - Y_IN + c + CLEAT_TAB_W / 2, *cleat_v)
                   for c in CLEAT_TABS]
    for key, name, x0 in (('cheek_l', 'Cheek left', X_CHEEK_L), ('cheek_r', 'Cheek right', X_CHEEK_R)):
        if key == 'cheek_l':
            n0, n1, nh = CABLE_NOTCH
            pts = [(0, 0), (n0, 0), (n0, nh), (n1, nh), (n1, 0), (LW, 0), (LW, hs), (uk, hs), (0, hf)]
            rad = [0, 0, CABLE_NOTCH_R, CABLE_NOTCH_R, 0, 0, 0, CHEEK_KNEE_R, 0]
            f = {0: tabs(CL_TABS, TAB_W, T_BASE),
                 5: tabs([sum(CHEEK_TAB_V) / 2], CHEEK_TAB_V[1] - CHEEK_TAB_V[0], T_WALL),
                 8: tabs([sum(CHEEK_TAB_V) / 2], CHEEK_TAB_V[1] - CHEEK_TAB_V[0], T_WALL)}
        else:
            # stands against the right end wall: shares its tabs and fingers (24 mm deep joints)
            pts = [(0, 0), (LW, 0), (LW, hs), (uk, hs), (0, hf)]
            rad = [0, 0, 0, CHEEK_KNEE_R, 0]
            f = {0: tabs(END_TABS, TAB_W, T_BASE),
                 1: fingers(0, WALL_H, N_FINGER, END_OWN, T_WALL),
                 4: fingers(0, WALL_H, N_FINGER, END_OWN, T_WALL)}
        c = jpart(key, name, PLY12, T_CHEEK, pts, rad, f, O=(x0, Y_IN, Z_BASE), U=Y, V=Z, N=X,
                  cover='tolex on both faces and the top edge')
        c.cutouts += cleat_slots
        if key == 'cheek_l':
            for cs in FILL_SIDE:
                u = Y_FILL0 - Y_IN + cs
                c.cutouts.append(slot(u - FILLER_TAB_W / 2, u + FILLER_TAB_W / 2, Z_TOP - T_FILL - Z_BASE, Z_TOP - Z_BASE))
        P.append(c)

    # ------------------------------------------------------------ keybed frame: two Z profiles
    # cross-section in (u = y - hole row, v = z - Z_BASE), extruded along x;
    # holes are not modelled (rivet nuts M4, drilled to the keybed holes)
    f, h, t = Z_FLANGE, Z_H, Z_T
    zsec = [(-f / 2, h - t), (-f / 2, h), (f / 2, h), (f / 2, t), (f / 2 - t + f, t), (f / 2 - t + f, 0),
            (f / 2 - t, 0), (f / 2 - t, h - t)]                     # bottom flange towards +u
    for i, ry in enumerate(KB_HOLE_Y):
        sec = zsec if i == 0 else [(-u, v) for u, v in reversed(zsec)]   # both bottom flanges point inwards
        r = Part('riser_%d' % (i + 1), 'Keybed Z profile', ALUZ, RISER_X1 - RISER_X0, sec,
                 O=(RISER_X0, Y_KB0 + ry, Z_BASE), U=Y, V=Z, N=X,
                 note='aluminium Z 20 x 20 x 2; keybed screwed on from above, unit screwed to the base from below')
        P.append(r)

    # ------------------------------------------------------------ strip, apron, cleats (removable unit)
    sl = X_CHEEK_R - X_KEYS_IN                # 689
    sd = Y_REAR_IN - Y_STRIP0                 # 136.5
    s = jpart('strip', 'Strip behind the keys', PLY9, T_STRIP, rect(0, 0, sl, sd), None,
              {2: notches(APRON_TABS, TAB_W, T_APRON)},
              O=(X_KEYS_IN, Y_STRIP0, Z_STRIP0), cover='tolex on top, front edge and ends')
    for y in STRIP_SCREW_Y:
        for u in (CLEAT_W / 2, sl - CLEAT_W / 2):
            s.holes.append(Hole(u, y - Y_STRIP0, 4.0, csk=8.0, side='front', note='screw 3.5 x 20 into cleat'))
    P.append(s)
    a = jpart('apron', 'Apron under the strip', PLY9, T_APRON, rect(0, 0, sl, Z_STRIP0 - Z_APRON0), None,
              {2: tabs(APRON_TABS, TAB_W, T_STRIP)},
              O=(X_KEYS_IN, Y_REAR_IN, Z_APRON0), U=X, V=Z, N=NY,
              cover='black paint, glued into the strip')
    P.append(a)
    cl_len = Y_CLEAT1 - Y_CLEAT0
    cf = {2: tabs(CLEAT_TABS, CLEAT_TAB_W, T_CHEEK)}
    # lying flat (12 mm ply, 15 wide), the tabs go through the cheek
    P.append(jpart('cleat_l', 'Strip cleat', PLY12, CLEAT_H, rect(0, 0, cl_len, CLEAT_W), None, cf,
                   O=(X_KEYS_IN + CLEAT_W, Y_CLEAT0, Z_STRIP0 - CLEAT_H), U=Y, V=NX, N=Z,
                   cover='black paint'))
    P.append(jpart('cleat_r', 'Strip cleat', PLY12, CLEAT_H, rect(0, 0, cl_len, CLEAT_W), None, cf,
                   O=(X_CHEEK_R - CLEAT_W, Y_CLEAT1, Z_STRIP0 - CLEAT_H), U=NY, V=X, N=Z,
                   cover='black paint'))

    # ------------------------------------------------------------ filler behind the panel
    fd = Y_REAR_IN - Y_FILL0
    f = jpart('filler', 'Filler behind the panel', PLY9, T_FILL, rect(0, 0, PANEL_OPEN, fd), None,
              {1: tabs(FILL_SIDE, FILLER_TAB_W, T_CHEEK),
               2: tabs(FILL_REAR, FILLER_TAB_W + 6, T_WALL),
               3: tabs(FILL_SIDE, FILLER_TAB_W, T_WALL)},
              O=(X_PANEL_IN, Y_FILL0, Z_TOP - T_FILL), cover='tolex on top and front edge')
    P.append(f)

    # ------------------------------------------------------------ lid
    lt = jpart('lid_top', 'Lid top', PLY6, T_LID_TOP, rect(0, 0, W, D), None,
               {0: notches(LID_TABS_X, TAB_W, T_LID_WALL), 2: notches(LID_TABS_X, TAB_W, T_LID_WALL),
                1: notches(LID_TABS_Y, TAB_W, T_LID_WALL), 3: notches(LID_TABS_Y, TAB_W, T_LID_WALL)},
               O=(0, 0, Z_LID1), cover='tolex outside')
    P.append(lt)
    ALL3 = set(range(N_FINGER_LID))
    for key, y0 in (('lid_front', T_LID_WALL), ('lid_rear', D)):
        P.append(jpart(key, 'Lid front/rear', PLY9, T_LID_WALL, rect(0, 0, W, LID_INSIDE), None,
                       {2: tabs(LID_TABS_X, TAB_W, T_LID_TOP),
                        1: fingers(0, LID_INSIDE, N_FINGER_LID, ALL3 - LID_END_OWN, T_LID_WALL, base='outer'),
                        3: fingers(0, LID_INSIDE, N_FINGER_LID, ALL3 - LID_END_OWN, T_LID_WALL, base='outer')},
                       O=(0, y0, Z_LID0), U=X, V=Z, N=NY, cover='tolex outside and over the lower edge'))
    for key, x0 in (('lid_end_l', 0.0), ('lid_end_r', W - T_LID_WALL)):
        P.append(jpart(key, 'Lid end', PLY9, T_LID_WALL, rect(0, 0, D - 2 * T_LID_WALL, LID_INSIDE), None,
                       {2: tabs([c - T_LID_WALL for c in LID_TABS_Y], TAB_W, T_LID_TOP),
                        1: fingers(0, LID_INSIDE, N_FINGER_LID, LID_END_OWN, T_LID_WALL),
                        3: fingers(0, LID_INSIDE, N_FINGER_LID, LID_END_OWN, T_LID_WALL)},
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

# assembly order with the direction each part moves into place (case x/y/z);
# build.py checks that every part slides in without touching the parts already there
ASSEMBLY = [
    ('base', None, 'base on the bench, inside up'),
    ('riser_1', (0, 0, -1), 'Z profiles (with the keybed on them): screw from below through the base'),
    ('riser_2', (0, 0, -1), ''),
    ('cheek_l', (0, 0, -1), 'left cheek: tabs down into the slots of the base'),
    ('cheek_r', (0, 0, -1), 'right cheek: tabs down into the notches at the right edge of the base'),
    ('cleat_l', (-1, 0, 0), 'strip cleats: from the inside through the cheeks'),
    ('cleat_r', (1, 0, 0), ''),
    ('filler', (1, 0, 0), 'filler: right tab into the left cheek, hold it level'),
    ('front', (0, 1, 0), 'front wall: over the cheek tabs, tabs into the base'),
    ('rear', (0, -1, 0), 'rear wall: over the cheek tabs and the filler tabs'),
    ('end_l', (1, 0, 0), 'end walls from the sides: fingers, base tabs, filler tab'),
    ('end_r', (-1, 0, 0), ''),
]
ASSEMBLY_STRIP = [
    ('strip', None, 'strip'),
    ('apron', (0, 0, 1), 'apron tabs up into the strip notches (glue)'),
]
ASSEMBLY_LID = [
    ('lid_top', None, 'lid top'),
    ('lid_front', (0, 0, 1), 'front and rear: tabs into the lid top'),
    ('lid_rear', (0, 0, 1), ''),
    ('lid_end_l', (1, 0, 0), 'ends from the sides: fingers, tabs into the lid top'),
    ('lid_end_r', (-1, 0, 0), ''),
]
JOINTS = [('base', 'front'), ('base', 'rear'), ('base', 'end_l'), ('base', 'end_r'), ('base', 'cheek_l'),
          ('base', 'cheek_r'), ('front', 'end_l'), ('front', 'end_r'), ('rear', 'end_l'), ('rear', 'end_r'),
          ('front', 'cheek_l'), ('rear', 'cheek_l'), ('front', 'cheek_r'), ('rear', 'cheek_r'),
          ('end_r', 'cheek_r'), ('filler', 'end_l'), ('filler', 'rear'), ('filler', 'cheek_l'),
          ('cleat_l', 'cheek_l'), ('cleat_r', 'cheek_r'), ('strip', 'apron'),
          ('lid_top', 'lid_front'), ('lid_top', 'lid_rear'), ('lid_top', 'lid_end_l'), ('lid_top', 'lid_end_r'),
          ('lid_front', 'lid_end_l'), ('lid_front', 'lid_end_r'), ('lid_rear', 'lid_end_l'),
          ('lid_rear', 'lid_end_r')]
