# -*- coding: utf-8 -*-
"""3D solids for the case parts and simplified reference bodies (FreeCAD)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import FreeCAD as App, Part
from FreeCAD import Vector as Vec
from params import *
from parts import PARTS, kb_holes_xy
from geom2d import fillet_poly


def _wire(part, pts, radii):
    P = lambda q: Vec(*part.to3d(q[0], q[1]))
    edges = []
    for s in fillet_poly(pts, radii):
        if s[0] == 'L':
            edges.append(Part.makeLine(P(s[1]), P(s[2])))
        else:
            edges.append(Part.Arc(P(s[1]), P(s[2]), P(s[3])).toShape())
    return Part.Wire(edges)


def part_solid(part, render=False):
    n = Vec(*part.N) * part.t
    face = Part.Face(_wire(part, part.outline, part.radii))
    solid = face.extrude(n)
    cuts = []
    for pts, rad in part.cutouts:
        cuts.append(Part.Face(_wire(part, pts, rad)).extrude(n))
    for h in part.holes:
        if h.kind != 'drill' or (render and h.covered):
            continue
        c = Vec(*part.to3d(h.u, h.v, -1.0))
        cuts.append(Part.makeCylinder(h.d / 2, part.t + 2, c, Vec(*part.N)))
        if h.csk:
            depth = (h.csk - h.d) / 2
            if h.side == 'front':
                apex = Vec(*part.to3d(h.u, h.v, part.t - depth))
                cuts.append(Part.makeCone(h.d / 2, h.csk / 2 + 0.5, depth + 0.5, apex, Vec(*part.N)))
            else:
                base = Vec(*part.to3d(h.u, h.v, -0.5))
                cuts.append(Part.makeCone(h.csk / 2 + 0.5, h.d / 2, depth + 0.5, base, Vec(*part.N)))
    if cuts:
        solid = solid.cut(Part.makeCompound(cuts) if len(cuts) > 1 else cuts[0])
    return solid


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vec(x0, y0, z0))


def cylz(x, y, z0, z1, d):
    return Part.makeCylinder(d / 2, z1 - z0, Vec(x, y, z0), Vec(0, 0, 1))


def cyly(x, z, y0, y1, d):
    return Part.makeCylinder(d / 2, y1 - y0, Vec(x, y0, z), Vec(0, 1, 0))


# ------------------------------------------------------------------ references
def keybed():
    """Fatar TP/9S 49 as frame, 29 white and 20 black keys (simplified)."""
    x0 = X_KEYS_IN + GAP_KB_SIDE
    y0, z0 = Y_KB0, Z_KB
    zw = z0 + KB_WHITE
    frame = box(x0, y0 + 12, z0, x0 + KB_W, Y_KB1, zw - 9)
    rear = box(x0, Y_KB1 - KB_REAR_FRAME, z0, x0 + KB_W, Y_KB1, zw)
    p = KB_W / 29.0
    whites = []
    for i in range(29):
        whites.append(box(x0 + i * p + 0.5, y0, z0 + KB_LIP, x0 + (i + 1) * p - 0.5,
                          Y_KB1 - KB_REAR_FRAME, zw))
    blacks = []
    shift = {1: -0.12, 2: 0.12, 4: -0.15, 5: 0.0, 6: 0.15}   # black key after white n of an octave
    for octv in range(4):
        for n, s in shift.items():
            xc = x0 + (octv * 7 + n + s) * p
            blacks.append(box(xc - 5.6, y0 + KB_BLACK_Y[0], zw, xc + 5.6, y0 + KB_BLACK_Y[1], z0 + KB_BLACK))
    return frame.fuse(rear), Part.makeCompound(whites), Part.makeCompound(blacks)


def panel():
    x0, y0 = X_PANEL_IN + GAP_PANEL, Y_PANEL0
    s = box(x0, y0, Z_PANEL0, x0 + PANEL_W, y0 + PANEL_D, Z_TOP)
    for hx, hy in PANEL_HOLES:
        s = s.cut(cylz(x0 + hx, y0 + hy, Z_PANEL0 - 1, Z_TOP + 1, PANEL_HOLE_D))
    return s


def board3620():
    """3620 board as a simplified envelope: 160 x 220 with the four corners clear
    for the panel standoffs, plus the space taken by the parts underneath."""
    x0, y0 = X_PANEL_IN + GAP_PANEL + 5, Y_PANEL0 + 5
    zt = Z_PANEL0 - BOARD_SPACER
    zb = zt - PCB_T
    c = 23.0
    def body(z0, z1):
        b = box(x0, y0, z0, x0 + 160, y0 + 220, z1)
        for cx, cy in ((x0, y0), (x0 + 160 - c, y0), (x0, y0 + 220 - c), (x0 + 160 - c, y0 + 220 - c)):
            b = b.cut(box(cx, cy, z0 - 1, cx + c, cy + c, z1 + 1))
        return b
    return body(zb, zt), body(zb - BOARD_PARTS_BELOW, zb)


def panel_jacks():
    """Parts hanging from the panel only: GX16 and the two 6.3 mm jacks (envelope)."""
    x0, y0 = X_PANEL_IN + GAP_PANEL, Y_PANEL0
    out = []
    for px, py, d, depth in ((148.0, 205.0, 22.0, 32.0), (25.0, 210.0, 16.0, 30.0), (25.0, 182.5, 16.0, 30.0)):
        out.append(cylz(x0 + px, y0 + py, Z_PANEL0 - depth, Z_PANEL0, d))
    return Part.makeCompound(out)


def pcb(x0, y0, w, d, holes, parts_h):
    zb = Z_BASE + STANDOFF
    board = box(x0, y0, zb, x0 + w, y0 + d, zb + PCB_T)
    parts = box(x0 + 3, y0 + 3, zb + PCB_T, x0 + w - 3, y0 + d - 3, zb + PCB_T + parts_h)
    stand = Part.makeCompound([cylz(x0 + hx, y0 + hy, Z_BASE, zb, 5.5) for hx, hy in holes])
    return board, parts, stand


def panel_standoffs():
    x0, y0 = X_PANEL_IN + GAP_PANEL, Y_PANEL0
    return Part.makeCompound([cylz(x0 + hx, y0 + hy, Z_BASE, Z_PANEL0, 5.5) for hx, hy in PANEL_HOLES])


def feet():
    return Part.makeCompound([cylz(x, y, -FOOT_H, 0, FOOT_D) for x, y in FEET])


def latches():
    w, d, h = LATCH
    out = []
    for x in LATCH_FRONT_X:
        out.append(box(x - w / 2, -d, Z_TOP - h / 2, x + w / 2, -TOLEX, Z_TOP + h / 2))
    for x in LATCH_REAR_X:
        out.append(box(x - w / 2, D + TOLEX, Z_TOP - h / 2, x + w / 2, D + d, Z_TOP + h / 2))
    return Part.makeCompound(out)


def plate_parts():
    """Bodies of the rear plate parts behind the plate (envelopes)."""
    out = []
    yi = D + TOLEX                                  # inner face of the plate
    for u, v, top, bot, holes in PLATE_ITEMS:
        x = PLATE_X_RIGHT - u
        z = PLATE_Z0 + v
        d0 = holes[0][2]
        if d0 >= 15:
            dd, depth = (20.0, 20.0) if d0 < 20 else (24.0, 30.0)
            out.append(cyly(x, z, yi - depth, yi, dd))
        elif d0 >= 10:
            out.append(cyly(x, z, yi - 20.0, yi, 12.0))
        else:
            out.append(box(x - 6.5, yi - 18.0, z - 4.0, x + 6.5, yi, z + 4.0))
    return Part.makeCompound(out)


def references():
    """name -> (shape, colour key)"""
    frame, whites, blacks = keybed()
    bt, bp = board3620()
    eb, ep, es = pcb(EMU_X0, EMU_Y0, EMU_W, EMU_D, EMU_HOLES, EMU_PARTS)
    nb, np_, ns = pcb(NT_X0, NT_Y0, NT_W, NT_D, NT_HOLES, NT_PARTS)
    return {
        'ref_keybed_frame': (frame, 'frame'),
        'ref_keys_white': (whites, 'white'),
        'ref_keys_black': (blacks, 'black'),
        'ref_panel': (panel(), 'panel'),
        'ref_panel_standoffs': (panel_standoffs(), 'metal'),
        'ref_board3620': (bt, 'pcb'),
        'ref_board3620_parts': (bp, 'parts'),
        'ref_panel_jacks': (panel_jacks(), 'metal'),
        'ref_emulator': (eb, 'pcb'),
        'ref_emulator_parts': (ep, 'parts'),
        'ref_emulator_standoffs': (es, 'metal'),
        'ref_psu': (nb, 'pcb'),
        'ref_psu_parts': (np_, 'parts'),
        'ref_psu_standoffs': (ns, 'metal'),
        'ref_plate_parts': (plate_parts(), 'metal'),
        'ref_feet': (feet(), 'rubber'),
        'ref_latches': (latches(), 'metal'),
    }


def case_solids(render=False):
    return {p.key: part_solid(p, render) for p in PARTS}


def check_orientation():
    bad = []
    for p in PARTS:
        U, V, N = p.U, p.V, p.N
        c = (U[1] * V[2] - U[2] * V[1], U[2] * V[0] - U[0] * V[2], U[0] * V[1] - U[1] * V[0])
        if any(abs(c[i] - N[i]) > 1e-9 for i in range(3)):
            bad.append(p.key)
    return bad
