# -*- coding: utf-8 -*-
"""Fit check of the whole instrument in 3D (FreeCAD, headless).

    scripts/fit3d/make_fit3d.sh

Case as the carpenter builds it (scripts/carpenter.py, butt joints, no lid since Rev0.4), the two aluminium
Z profiles, the Fatar keybed (keys at rest and pressed), and the four boards of the ARP 3620 project
as KiCad exports them (STEP with the KiCad 3D models). Parts without a 3D model get envelopes from
their footprint and a height from the datasheet; those heights are listed in ENVELOPES and marked
in the report. Writes model/fit3d/fit_report.txt, fit_check.json and the viewer data
(viewer/case.glb, viewer/fit3d.json).
"""
import os, sys, json, math, time, itertools
from pathlib import Path

HERE = Path(os.path.abspath(__file__)).parent if os.path.isabs(__file__) else (Path.cwd() / __file__).parent
SCR = HERE.parent
ROOT = SCR.parent
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import numpy as np
import FreeCAD as App, Part, Import, MeshPart
from FreeCAD import Vector as V, Placement, Rotation
from params import *
import model
import parts as P0
import glbw

OUT = ROOT / 'model' / 'fit3d'
VIEW = HERE / 'viewer'

# ------------------------------------------------------------------ case as the carpenter builds it
_src = (SCR / 'carpenter.py').read_text(encoding='utf-8')
_src = _src[:_src.rstrip().rfind('\nmain()')]
CNS = {'__file__': str(SCR / 'carpenter.py'), '__name__': 'carpenter_fit'}
exec(compile(_src, str(SCR / 'carpenter.py'), 'exec'), CNS)
CARP = CNS['PARTS']

K = json.load(open(OUT / 'kicad_parts.json', encoding='utf-8'))

# ------------------------------------------------------------------ board placement (case coordinates)
PX0, PY0 = X_PANEL_IN + GAP_PANEL, Y_PANEL0          # lower left corner of the panel PCB
Z_BOARD_B = Z_PANEL0 - BOARD_SPACER                  # board 3620: back side (controls) faces the panel
PLACE = {
    # local STEP: x right, y up from the lower left board corner, z up (B side 0, F side 1.6)
    'panel': Placement(V(PX0, PY0, Z_PANEL0), Rotation()),
    # board 3620 hangs under the panel on 12 mm standoffs, mirrored: F side (parts) down,
    # controls fitted from the back reach up to the panel. Board = panel - 5 mm all round.
    'board': Placement(V(PX0 + 5 + 160, PY0 + 5, Z_BOARD_B), Rotation(V(0, 1, 0), 180)),
    'emu': Placement(V(EMU_X0, EMU_Y0, Z_BASE + STANDOFF), Rotation()),
    'psu': Placement(V(NT_X0, NT_Y0, Z_BASE + STANDOFF), Rotation()),
}
NAMES = {'panel': 'Frontplatte (Leiterplatte) Rev0.3', 'board': 'Board 3620-007 Rev0.5',
         'emu': 'Bus-Emulator Rev0.3', 'psu': 'Netzteil Rev0.1'}


def local_origin(k):
    e = K[k]['edge']
    return e[0] + 0.05, e[3] - 0.05            # KiCad sheet x, y of the lower left board corner


def fp_local(k, p):
    """footprint box in local board coordinates (x, y up)"""
    ox, oy = local_origin(k)
    b = p['box']
    return b[0] - ox, oy - b[3], b[2] - ox, oy - b[1]


# ------------------------------------------------------------------ envelopes for parts without a 3D model
# heights in mm above the board surface on the side the part sits on. 'back' = fitted from the back
# (board 3620 controls, towards the panel). Every height names its source; 'assumed' marks the values
# that no datasheet gives (checked 11.11.2026). Kinds: 'fp' footprint box, 'box' (w, d) centred,
# 'cyl' diameter, 'slot' (across, along): a box along the longer footprint axis, for actuators
# that slide (the whole travel is the envelope). Names starting with 'plug' are mated cable plugs:
# they are added even when KiCad has a model, because the model shows the header only.
PANEL_TOP_LOCAL = BOARD_SPACER + PANEL_T                 # panel top above the board's back side (13.6)
LEAD_CUT = 2.0                                           # leads cut this long on the solder side
IN = 25.4
ENVELOPES = {
    # footprint: list of (name, side, kind, size, z0, z1, source)
    'Thonk_PJ301BM': [
        ('body', 'back', 'fp', None, 0, 11.5, 'Thonk PJ301BM: body 11.5 (dealer data WQP518MA-BM, '
                                             'Arp2600 pcb/bauteile/buchse-switchcraft.md 3)'),
        ('bush', 'back', 'cyl', 6.0, 11.5, 17.0, 'PJ301BM: bushing M6, 5.5 long (4.5 thread), same source')],
    'Bourns_PTL45_LED': [
        ('body', 'back', 'fp', None, 0, 7.5, 'Bourns PTL45: body 7.0 +-0.5 to the mounting surface (PTL.pdf p. 2)'),
        ('lever', 'back', 'slot', (2.05, 45.0 + 6.0), 7.5, 7.0 + 15.0 + 0.5,
         'PTL45-15: lever L 15 above the mounting surface, 2.05 thick, swept over 45 travel (PTL.pdf p. 2, 4); '
         'no slider caps (Arp3620 bestellung/README.md)')],
    'Switchcraft_46206': [
        ('body', 'back', 'fp', None, 0, 0.295 * IN, 'Switchcraft 46206LRX: housing 0.295 below the flange '
                                                   '(Arp2600 Switchcraft_46200LRX_SERIES_CD.pdf)'),
        ('flange', 'back', 'slot', (0.53 * IN, 1.38 * IN), 0.295 * IN - 0.5, 0.295 * IN, '46206: flange 1.38 x 0.53'),
        ('actuator', 'back', 'slot', (0.23 * IN, (0.28 + 0.19) * IN), 0.295 * IN, (0.295 + 0.34) * IN,
         '46206: knob 0.28 x 0.23, 0.34 above the flange, throw 0.19')],
    'Switchcraft_46313': [
        ('body', 'back', 'fp', None, 0, 0.34 * IN, 'Switchcraft 46313LDRX: housing 0.34 below the flange '
                                                  '(Arp3620 doku/datenblatt/Switchcraft_46300LDRX_SERIES_CD.pdf)'),
        ('flange', 'back', 'slot', (0.53 * IN, 1.66 * IN), 0.34 * IN - 0.5, 0.34 * IN, '46313: flange 1.66 x 0.53'),
        ('actuator', 'back', 'slot', (0.23 * IN, (0.28 + 2 * 0.25) * IN), 0.34 * IN, 0.68 * IN,
         '46313: knob 0.28 x 0.23, 0.34 above the flange, throw 0.25 either direction')],
    'NKK_SB4011': [
        ('body', 'back', 'fp', None, 0, 11.5, 'NKK SB4011NCHC-RO: body (assumed; nkkswitches.com not reachable, '
                                              'Digi-Key: rear panel mount, solder lugs, cut-out 12.5)'),
        ('plunger', 'back', 'cyl', 12.5, 11.5, 23.0, 'SB4011: bushing and red plunger dia 12.5 to 23 (assumed)')],
    'Alps_RK09D': [
        ('body', 'back', 'fp', None, 0, 6.8, 'Alps RK09D vertical: body 6.8 above the mounting surface '
                                             '(Alps_RK09K_RK09D.pdf drawing 12)'),
        ('bush', 'back', 'cyl', 7.0, 6.8, 11.8, 'RK09D: collar 5 long (dia from the drawing, about 6.5)'),
        ('shaft', 'back', 'cyl', 6.0, 11.8, 25.0, 'RK09D113BF25: shaft dia 6, LM1 25 above the mounting surface'),
        ('knob', 'back', 'cyl', 20.0, PANEL_TOP_LOCAL + 1.0, 25.0 + 1.5,
         'knob dia 20 (bestellung/README.md), top 1.5 above the shaft end (assumed, knob not chosen)')],
    'Bourns_3266_P_W_Y': [('body', 'front', 'fp', None, 0, 6.7, 'Bourns 3266W, 6.7 (Bourns_3266.pdf)')],
    '2N3958_Klon': [('body', 'front', 'fp', None, 0, 5.3, 'TO-71 can 5.3')],
    # emulator
    'TE_MTA-100_640456-5_1x05_P2.54mm_Vertical': [
        ('body', 'front', 'fp', None, 0, 0.100 * IN + 0.305 * IN,
         'TE 640456 header: base 0.100, polarizing wall 0.305 (ENG_CD_640456_W3)'),
        ('plug', 'front', 'fp', None, 0.100 * IN, 0.100 * IN + 0.520 * IN,
         'MTA-100 IDC plug 0.520 high on the header base (TE catalog 82056 p. 14)')],
    'RaspberryPi_Pico_Common_THT': [
        ('plug Pico', 'front', 'fp', None, 0, 20.0 + 1.0 + 3.3,
         'Pico 2 on long pin headers 15-20 (emulator session, 12.11.2026), board 1.0, USB socket 3.3'),
        ('plug USB', 'front', 'out_y', (13.0, 32.0), 8.0, 20.0 + 1.0 + 3.3 + 2.0,
         'Micro-B plug of the panel-mount cable Adafruit 3258 over the board: socket 15 in front of the rear edge, '
         'plug and strain relief 10-12 above the board (emulator session, 13.11.2026), cable bend 15 behind the edge; '
         'height also covers the Pico on headers 15-20')],
    'TE_Micro-MaTch_2-215079-0_2x10_P1.27mm_Vertical': [
        ('body', 'front', 'fp', None, 0, 4.0, 'TE Micro-MaTch 215079 female on board: insulator height 4.00 '
                                              '(Digi-Key 8-215079-0)'),
        ('plug', 'front', 'fp', None, 4.0, 18.0, 'Micro-MaTch ribbon plug, to 18 (assumed; TE drawing not reachable)')],
    # power supply
    'MeanWell_SI06W8': [('body', 'front', 'fp', None, 0, 10.7, 'Mean Well SI06W8: 25.4 x 25.4 x 10.2 +-0.5 '
                                                               '(MeanWell_SI06W8_DI06W8.pdf)')],
    'Heatsink_Fischer_SK104-STC-STIC_35x13mm_2xDrill2.5mm': [('body', 'front', 'fp', None, 0, 35.0,
                                                               'Fischer SK104 35 mm, upright')],
}
# KiCad models that the export could not find (file missing in the library): envelope instead
MISSING_MODELS = {'emu': {'J1', 'J2', 'J7'}, 'psu': {'HS1', 'HS2'}}
ENVELOPES['TE_MTA-100_640456-7_1x07_P2.54mm_Vertical'] = ENVELOPES['TE_MTA-100_640456-5_1x05_P2.54mm_Vertical']
ENVELOPES['TE_Micro-MaTch_1-215079-6_2x08_P1.27mm_Vertical'] = ENVELOPES['TE_Micro-MaTch_2-215079-0_2x10_P1.27mm_Vertical']
# Measured by Patrick on board 3620 (11.11.2026): tallest parts 18 mm on the part side, the WIMA
# capacitors C2/C4 and the KK headers with their crimp housings plugged in. Taken from the board
# surface (if the 18 included the board, this is 1.6 mm on the safe side). 'measured' and 'plug'
# entries are added even where KiCad has a model (the model is smaller or shows the header only).
MEASURED_H = 18.0
MEASURED_SRC = 'measured on board 3620 by Patrick, 11.11.2026: 18 on the part side'
ENVELOPES['C_Rect_P22.50mm_P5.00mm_Halteglied'] = [
    ('measured', 'front', 'fp', None, 0, MEASURED_H, 'WIMA C2/C4 ' + MEASURED_SRC)]
for _n in (2, 3, 4, 5, 6):
    ENVELOPES['Molex_KK-254_AE-6410-%02dA_1x%02d_P2.54mm_Vertical' % (_n, _n)] = [
        ('plug', 'front', 'fp', None, 0, MEASURED_H, 'Molex KK header with crimp housing plugged in, ' + MEASURED_SRC)]


def envelope_shapes(k):
    """name -> (shape in local board coordinates, source note)"""
    out = {}
    t = K[k]['thickness']
    for p in K[k]['parts']:
        env = ENVELOPES.get(p['fp'])
        if not env:
            continue
        modelled = p['models'] and p['ref'] not in MISSING_MODELS.get(k, ())
        x0, y0, x1, y1 = fp_local(k, p)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for name, side, kind, size, z0, z1, src in env:
            if modelled and not name.startswith(('plug', 'measured')):
                continue
            # local z: front (F) side above 1.6, back (B) side below 0
            za, zb = (t + z0, t + z1) if side == 'front' else (-z1, -z0)
            if kind == 'fp':
                s = Part.makeBox(x1 - x0, y1 - y0, zb - za, V(x0, y0, za))
            elif kind == 'out_y':
                w, d = size                          # leaves the board towards local +y (rear), from the courtyard edge
                s = Part.makeBox(w, d, zb - za, V(cx - w / 2, y1 - 2.0, za))
            elif kind in ('box', 'slot'):
                w, d = size
                if kind == 'slot' and (x1 - x0) > (y1 - y0):
                    w, d = d, w                       # along the longer footprint axis
                s = Part.makeBox(w, d, zb - za, V(cx - w / 2, cy - d / 2, za))
            else:
                s = Part.makeCylinder(size / 2, zb - za, V(cx, cy, za), V(0, 0, 1))
            out['%s %s' % (p['ref'], name)] = (s, src)
    return out


def special_shapes():
    """Envelopes in case coordinates: rocker S1 (snaps into the panel, hangs through the board cut-out),
    GX16 and the two 6.3 mm foot switch jacks on the panel (from model.panel_jacks)."""
    out = {}
    p = next(q for q in K['board']['parts'] if q['ref'] == 'S1')
    x0, y0, x1, y1 = fp_local('board', p)
    c = PLACE['board'].multVec(V((x0 + x1) / 2, (y0 + y1) / 2, 0))
    # E-Switch 300DP6R7BLKM3QEBLK, drawing T331003: housing 12.70 x 11.43 down to 16.4 below the panel top,
    # terminals to 23.0; bezel 19.85 x 15.80 x 2.3, rocker 13.8 above the panel
    hw, hd = 12.70, 11.43
    out['S1 Wippe (Gehäuse)'] = (Part.makeBox(hw, hd, 16.4 - PANEL_T, V(c.x - hw / 2, c.y - hd / 2, Z_TOP - 16.4)),
                                  'E-Switch 300DP6 housing 12.70 x 11.43, 16.4 below the panel top (datasheet)')
    out['S1 Wippe (Fahnen)'] = (Part.makeBox(10.0, 5.0, 23.0 - 16.4, V(c.x - 5.0, c.y - 2.5, Z_TOP - 23.0)),
                                 'E-Switch 300DP6 terminals to 23 below the panel top (datasheet)')
    out['S1 Wippe (oben)'] = (Part.makeBox(19.85, 15.80, 13.8, V(c.x - 19.85 / 2, c.y - 7.9, Z_TOP)),
                              'E-Switch 300DP6 bezel 19.85 x 15.80, rocker 13.8 above the panel (datasheet)')
    jacks = model.panel_jacks().Solids
    for s, n in zip(jacks, ('GX16 Interface', 'ACJS Fußschalter oben', 'ACJS Fußschalter unten')):
        out[n] = (s, 'envelope as in model.py (GX16 dia 22 x 32, ACJS dia 16 x 30)')
    return out


# ------------------------------------------------------------------ import the KiCad STEP files
def board_solids(k):
    """[(ref or label, shape in case coordinates, kind)] from the KiCad STEP export"""
    doc = App.newDocument('b_' + k)
    Import.insert(str(OUT / ('%s.step' % k)), doc.Name)
    ox, oy = local_origin(k)
    fps = []
    for p in K[k]['parts']:
        fps.append((p['ref'], fp_local(k, p)))
    out = []
    t = K[k]['thickness']
    # leads: KiCad models keep them uncut; after soldering they stand LEAD_CUT below the board
    keep = Part.makeBox(400, 400, 200, V(-100, -100, -LEAD_CUT))
    for o in doc.Objects:
        if o.TypeId != 'Part::Feature' or not o.Shape.Solids:
            continue
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        b = s.BoundBox
        if 'PCB' in o.Label or (b.XLength > 60 and b.YLength > 60):
            out.append(('Leiterplatte', s, 'pcb'))
            continue
        if b.ZMin < -LEAD_CUT:
            c = s.common(keep)
            if c.Volume > 1e-6:
                s = c
        cx, cy = b.Center.x, b.Center.y
        best, area = None, 1e9
        for ref, (x0, y0, x1, y1) in fps:
            if x0 - 0.5 <= cx <= x1 + 0.5 and y0 - 0.5 <= cy <= y1 + 0.5:
                a = (x1 - x0) * (y1 - y0)
                if a < area:
                    best, area = ref, a
        out.append((best or o.Label, s, 'part'))
    App.closeDocument(doc.Name)
    res = []
    for ref, s, kind in out:
        s2 = s.copy()
        s2.Placement = PLACE[k].multiply(s.Placement)
        res.append((ref, s2, kind))
    for name, (s, src) in envelope_shapes(k).items():
        s2 = s.copy()
        s2.Placement = PLACE[k].multiply(s.Placement)
        res.append((name, s2, 'envelope:' + src))
    return res


# ------------------------------------------------------------------ keybed
def keybed_bodies():
    frame, whites, blacks = model.keybed()
    # keys pressed: white and black keys turned about the pivot at the rear frame, front 10 mm down
    piv_y, piv_z = Y_KB1 - KB_REAR_FRAME, Z_KB + KB_WHITE
    ang = math.degrees(math.atan2(KB_TRAVEL, piv_y - Y_KB0))
    rot = Placement(V(0, 0, 0), Rotation(V(1, 0, 0), ang), V(0, piv_y, piv_z))
    wp = whites.copy(); wp.Placement = rot.multiply(wp.Placement)
    bp = blacks.copy(); bp.Placement = rot.multiply(bp.Placement)
    return {'Keybed Rahmen': frame, 'Tasten weiß': whites, 'Tasten schwarz': blacks,
            'Tasten weiß gedrückt': wp, 'Tasten schwarz gedrückt': bp}


def standoffs():
    out = {}
    out['Bolzen Frontplatte (4 x M3, %s)' % CNS['fmt'](Z_PANEL0 - Z_BASE)] = model.panel_standoffs()
    holes = [p for p in K['board']['parts'] if p['ref'].startswith('H') and p['fp'].startswith('MountingHole')]
    cs = []
    for p in holes:
        x0, y0, x1, y1 = fp_local('board', p)
        c = PLACE['board'].multVec(V((x0 + x1) / 2, (y0 + y1) / 2, 0))
        cs.append(Part.makeCylinder(5.5 / 2, BOARD_SPACER, V(c.x, c.y, Z_BOARD_B), V(0, 0, 1)))
    out['Bolzen Board (8 x M3 x 12)'] = Part.makeCompound(cs)
    _, _, es = model.pcb(EMU_X0, EMU_Y0, EMU_W, EMU_D, EMU_HOLES, EMU_PARTS)
    _, _, ns = model.pcb(NT_X0, NT_Y0, NT_W, NT_D, NT_HOLES, NT_PARTS)
    out['Bolzen Emulator (6 x M3 x 6)'] = es
    out['Bolzen Netzteil (4 x M3 x 6)'] = ns
    return out


# ------------------------------------------------------------------ checks
def common_vol(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def bbox_gap(a, b):
    dx = max(0.0, max(a.XMin, b.XMin) - min(a.XMax, b.XMax))
    dy = max(0.0, max(a.YMin, b.YMin) - min(a.YMax, b.YMax))
    dz = max(0.0, max(a.ZMin, b.ZMin) - min(a.ZMax, b.ZMax))
    return math.sqrt(dx * dx + dy * dy + dz * dz)


_pts = {}


def _points(s):
    k = id(s)
    if k not in _pts:
        P, _, _ = glbw.mesh(s, 0.1)
        _pts[k] = np.column_stack([P[:, 0], -P[:, 2], P[:, 1]])        # back to case coordinates
    return _pts[k]


def _pt_to_shape(pts, shape, n=400):
    if not len(pts):
        return 1e9
    step = max(1, len(pts) // n)
    best = 1e9
    for p in pts[::step]:
        try:
            d = shape.distToShape(Part.Vertex(V(*p)))[0]
        except Exception:
            continue
        best = min(best, d)
    return best


def distance(a, b):
    """Shortest distance. Some KiCad models make BRepExtrema return 0 for parts far apart:
    then, if the solids do not overlap, measure from the mesh points of each body to the other body
    and take the larger result (the one against a well-formed body); if both read 0, use the
    distance between the two point sets."""
    try:
        d = a.distToShape(b)[0]
    except Exception:
        d = 0.0
    if d > 1e-6 or common_vol(a, b) > 0.05:
        return d
    pa, pb = _points(a), _points(b)
    d = max(_pt_to_shape(pa, b), _pt_to_shape(pb, a))
    if d > 1e-6 or not len(pa) or not len(pb):
        return d
    best = 1e9
    ch = max(1, int(2e6 // max(1, len(pb))))
    for i in range(0, len(pa), ch):
        q = pa[i:i + ch]
        best = min(best, float(np.sqrt(((q[:, None, :] - pb[None, :, :]) ** 2).sum(-1)).min()))
    return best


def main():
    t0 = time.time()
    bodies = []          # (group, name, shape, note)
    for p in CARP:
        bodies.append(('Holz' if p.group != CNS['G4'] else 'Z-Profil', '%d %s' % (p.pos, p.name), p.solid, ''))
    plate = next(q for q in P0.PARTS if q.key == 'plate')
    bodies.append(('Rückplatte', 'Alu-Rückplatte', model.part_solid(plate), ''))
    bodies.append(('Rückplatte', 'Teile an der Rückplatte (Hüllen)', model.plate_parts(), 'envelope'))
    for n, s in keybed_bodies().items():
        bodies.append(('Keybed', n, s, 'simplified (model.keybed)'))
    for n, s in standoffs().items():
        bodies.append(('Bolzen', n, s, ''))
    for n, (s, src) in special_shapes().items():
        bodies.append(('Frontplatte Teile', n, s, 'envelope: ' + src))
    boards = {}
    for k in ('panel', 'board', 'emu', 'psu'):
        boards[k] = board_solids(k)
        for ref, s, kind in boards[k]:
            bodies.append((NAMES[k], ref, s, kind))
        print('%-8s %d solids' % (k, len(boards[k])), flush=True)

    # ---- collisions
    G = lambda g: [b for b in bodies if b[0] == g]
    pressed = lambda b: 'gedrückt' in b[1]
    findings = []

    def test(A, B, label, allow=lambda a, b: False):
        n = 0
        for a in A:
            for b in B:
                if a is b or allow(a, b):
                    continue
                v = common_vol(a[2], b[2])
                n += 1
                if v > 0.05 or v < 0:
                    findings.append(dict(check=label, a='%s: %s' % (a[0], a[1]), b='%s: %s' % (b[0], b[1]),
                                         vol=round(v, 2), note=(a[3] + ' ' + b[3]).strip()))
        return n

    wood = G('Holz') + G('Z-Profil')
    pcbs = [b for k in boards for b in bodies if b[0] == NAMES[k]]
    keyb = G('Keybed')
    others = G('Rückplatte') + G('Bolzen') + G('Frontplatte Teile')
    counts = {}
    counts['Platinen/Bauteile gegen Holz und Z-Profile'] = test(pcbs, wood, 'Platine gegen Gehäuse')
    counts['Keybed gegen Holz, Z-Profile, Platinen'] = test(keyb, wood + pcbs, 'Keybed')
    # boards against each other and against standoffs, plate parts, panel parts
    def same_board(a, b):
        return a[0] == b[0]
    def through_panel(a, b):
        # controls pass through their panel holes: bush, shaft, lever, actuator, plunger, knob,
        # rocker against the panel PCB are intended
        names = ('bush', 'shaft', 'lever', 'actuator', 'plunger', 'knob', 'Wippe', 'GX16', 'ACJS')
        pa = a[0] == NAMES['panel'] or b[0] == NAMES['panel']
        return pa and any(n in a[1] or n in b[1] for n in names)
    def standoff_ok(a, b):
        # board standoffs sit on the board and under the panel by design
        sa = 'Bolzen Board' in a[1] or 'Bolzen Board' in b[1]
        ok = sa and ('Leiterplatte' in (a[1], b[1])) and (NAMES['board'] in (a[0], b[0]) or NAMES['panel'] in (a[0], b[0]))
        sp = 'Bolzen Frontplatte' in a[1] or 'Bolzen Frontplatte' in b[1]
        ok2 = sp and (a[1] == 'Leiterplatte' or b[1] == 'Leiterplatte') and NAMES['panel'] in (a[0], b[0])
        se = ('Bolzen Emulator' in a[1] or 'Bolzen Emulator' in b[1]) and NAMES['emu'] in (a[0], b[0]) and 'Leiterplatte' in (a[1], b[1])
        sn = ('Bolzen Netzteil' in a[1] or 'Bolzen Netzteil' in b[1]) and NAMES['psu'] in (a[0], b[0]) and 'Leiterplatte' in (a[1], b[1])
        return ok or ok2 or se or sn
    counts['Platinen untereinander'] = test(pcbs, pcbs, 'Platinen untereinander',
                                            allow=lambda a, b: same_board(a, b) or through_panel(a, b) or id(a) > id(b))
    counts['Platinen gegen Bolzen, Rückplatte, Frontplattenteile'] = test(
        pcbs, others, 'Platine gegen Bolzen/Teile', allow=lambda a, b: through_panel(a, b) or standoff_ok(a, b))
    counts['Bolzen, Rückplatte, Frontplattenteile gegen Holz'] = test(
        others, wood, 'Teile gegen Gehäuse',
        allow=lambda a, b: ('Bolzen' in a[1] and b[1].startswith('1 ')) or
                           (a[0] == 'Rückplatte' and a[1] == 'Alu-Rückplatte' and False))
    # the panel standoffs stand on the base (1 Boden) by design: allowed above

    # ---- clearances
    def dmin(A, B):
        best = (1e9, None, None)
        for a in A:
            for b in B:
                if a is b:
                    continue
                d = bbox_gap(a[2].BoundBox, b[2].BoundBox)
                if d >= best[0]:
                    continue                      # true distance >= box gap: cannot be closer
                d = distance(a[2], b[2])
                if d < best[0]:
                    best = (d, a, b)
        return best

    def by(group, pred=lambda b: True):
        return [b for b in bodies if b[0] == group and pred(b)]
    base = [b for b in G('Holz') if b[1].startswith('1 ')]
    strip = [b for b in G('Holz') if b[1].startswith(('11 ', '12 '))]
    rear = [b for b in G('Holz') if b[1].startswith('3 ')]
    walls = [b for b in G('Holz') if b[1].startswith(('2 ', '3 ', '4 ', '5 ', '6 ', '8 ', '9 '))]
    board_parts = by(NAMES['board'], lambda b: b[1] != 'Leiterplatte')
    emu = by(NAMES['emu']); psu = by(NAMES['psu'])
    gaps = [
        ('Board 3620 Bauteile unten -> Boden', board_parts, base, 2.0),
        ('Board 3620 + Bauteile -> Wände, Wange, Füllstück', by(NAMES['board']), walls, 1.0),
        ('Frontplatten-Teile (GX16, ACJS, Wippe) -> Boden', G('Frontplatte Teile'), base, 2.0),
        ('Frontplatten-Teile -> Board 3620', G('Frontplatte Teile'), by(NAMES['board']), 0.5),
        ('Emulator -> Abdeckleiste/Blende', emu, strip, 2.0),
        ('Netzteil -> Abdeckleiste/Blende', psu, strip, 2.0),
        ('Emulator -> Rückwand', emu, rear, 1.0),
        ('Netzteil -> Rückwand', psu, rear, 1.0),
        ('Emulator -> Netzteil', emu, psu, 2.0),
        ('Emulator/Netzteil -> Rückplatten-Teile', emu + psu, G('Rückplatte'), 1.0),
        ('Pico-USB-Stecker -> Rückwand, Rückplatten-Teile', [b for b in emu if 'plug USB' in b[1]],
         rear + G('Rückplatte'), 2.0),
        ('Emulator -> Keybed', emu, keyb, 1.0),
        ('Keybed in Ruhe -> Abdeckleiste', [b for b in keyb if not pressed(b)], strip, 2.0),
        ('Tasten gedrückt -> Vorderwand / Z-Profil', [b for b in keyb if pressed(b)],
         [b for b in G('Holz') if b[1].startswith('2 ')] + G('Z-Profil'), 1.0),
        ('Keybed -> Wangen', keyb, [b for b in G('Holz') if b[1].startswith(('5 ', '6 '))], 2.0),
    ]
    gap_res = []
    for label, A, B, need in gaps:
        d, a, b = dmin(A, B)
        gap_res.append(dict(check=label, d=round(d, 2), need=need, ok=d >= need - 1e-6,
                            a='%s: %s' % (a[0], a[1]) if a else '', b='%s: %s' % (b[0], b[1]) if b else ''))
        print('  %-48s %7.2f  (min %s)  %s / %s' % (label, d, need, a[1] if a else '', b[1] if b else ''), flush=True)

    # ---- report
    OUT.mkdir(parents=True, exist_ok=True)
    env = sorted({(b[0], b[1], b[3]) for b in bodies if b[3].startswith('envelope')})
    lines = ['ARP 3620 - Passprobe in 3D (Gehäuse %s, Ausführung Tischler)' % CNS['DOC_REV'],
             'Platinen: ' + ', '.join('%s (%s)' % (NAMES[k], Path(K[k]['file']).name) for k in NAMES),
             'Körper: %d (davon %d aus KiCad, %d Hüllen ohne 3D-Modell)' % (
                 len(bodies), sum(len(v) for v in boards.values()), len(env)), '',
             '1. Kollisionen (Volumen > 0,05 mm³)']
    for label, n in counts.items():
        lines.append('   %-58s %5d Paare geprüft' % (label, n))
    if findings:
        for f in findings:
            lines.append('   !! %s: %s  <->  %s  %.2f mm³  %s' % (f['check'], f['a'], f['b'], f['vol'], f['note']))
    else:
        lines.append('   keine')
    lines += ['', '2. Abstände (mm)                                      Ist    Soll']
    for g in gap_res:
        lines.append('   %-48s %7.2f %6.1f  %s   %s / %s' % (g['check'], g['d'], g['need'], 'ok' if g['ok'] else 'ZU KNAPP',
                                                           g['a'], g['b']))
    lines += ['', '3. Hüllen statt 3D-Modell (Quelle je Höhe; "assumed" = kein Datenblattwert)']
    seen = set()
    for g, n, note in env:
        key = (g, note)
        if key in seen:
            continue
        seen.add(key)
        lines.append('   %-34s %s' % (g, note.replace('envelope:', '').strip()))
    lines += ['', 'Einbaulage: Frontplatte bündig mit den Wänden (Oberkante %s), Board 3620 %s darunter an 8 Bolzen,'
              % (CNS['fmt'](Z_TOP), CNS['fmt'](BOARD_SPACER)),
              'gespiegelt (Bauteile nach unten, Bedienteile von der Rückseite nach oben); Emulator und Netzteil auf',
              '%s-mm-Bolzen am Boden; Keybed auf den Z-Profilen, Auflage %s über Unterkante Boden.'
              % (CNS['fmt'](STANDOFF), CNS['fmt'](Z_KB)),
              'Gedrückte Tasten: um die Achse über dem hinteren Rahmen gedreht, vorn %s mm tiefer.' % CNS['fmt'](KB_TRAVEL)]
    rep = '\n'.join(lines) + '\n'
    (OUT / 'fit_report.txt').write_text(rep, encoding='utf-8')
    json.dump(dict(findings=findings, gaps=gap_res, counts=counts), open(OUT / 'fit_check.json', 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False)
    print(rep)

    # ---- viewer data
    VIEW.mkdir(parents=True, exist_ok=True)
    w = glbw.Writer()
    col = {'Holz': ([0.13, 0.065, 0.03, 1], 0.0, 0.75), 'Z-Profil': ([0.75, 0.77, 0.80, 1], 0.6, 0.4),
           'Rückplatte': ([0.72, 0.74, 0.78, 1], 0.6, 0.4), 'Bolzen': ([0.80, 0.80, 0.82, 1], 0.7, 0.35),
           'Frontplatte Teile': ([0.35, 0.37, 0.42, 1], 0.4, 0.5), 'Keybed': ([0.45, 0.45, 0.48, 1], 0.3, 0.6),
           'Hülle': ([0.95, 0.55, 0.20, 1], 0.0, 0.7)}
    mats = {k: w.material(k, *v) for k, v in col.items()}
    mats['weiß'] = w.material('Tasten weiß', [0.96, 0.95, 0.92, 1], 0.0, 0.5)
    mats['schwarz'] = w.material('Tasten schwarz', [0.08, 0.08, 0.09, 1], 0.0, 0.4)
    meta = []
    hit = {f['a'] for f in findings} | {f['b'] for f in findings}
    for g, n, s, note in bodies:
        if g in NAMES.values() and not note.startswith('envelope'):
            continue                                   # boards come from the KiCad GLB
        m = mats.get(g, mats['Hülle'])
        if g == 'Keybed':
            m = mats['weiß'] if 'weiß' in n else mats['schwarz'] if 'schwarz' in n else mats['Keybed']
        if note.startswith('envelope'):
            m = mats['Hülle']
        tol = 0.4 if g in ('Holz', 'Keybed') else 0.15
        P, N, I = glbw.mesh(s, tol)
        grp = g if not note.startswith('envelope') or g in ('Frontplatte Teile', 'Rückplatte') else g + ' (Hüllen)'
        idx = w.node(n, [(m, P, N, I)], extras=dict(group=grp, name=n))
        if idx is not None:
            meta.append(dict(name=n, group=grp, hit=('%s: %s' % (g, n)) in hit))
    size = w.save(str(VIEW / 'case.glb'))
    boards_meta = {}
    for k, pl in PLACE.items():
        m = pl.toMatrix()
        # case (x, y, z) -> three (x, z, -y); KiCad GLB: metres, three axes (x, z_local, -y_local)
        A = np.array([[m.A11, m.A12, m.A13, m.A14], [m.A21, m.A22, m.A23, m.A24],
                      [m.A31, m.A32, m.A33, m.A34], [0, 0, 0, 1]])
        T = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float)   # case -> three
        S = np.diag([1000.0, 1000.0, 1000.0, 1.0])
        Tinv = np.linalg.inv(T)
        M = T @ A @ Tinv @ S                              # local three (m) -> case three (mm)
        boards_meta[k] = dict(name=NAMES[k], file=k + '.glb', matrix=[float(v) for v in M.T.reshape(-1)])
    hits_by_ref = {}
    for f in findings:
        for side in ('a', 'b'):
            g, _, ref = f[side].partition(': ')
            hits_by_ref.setdefault(g, []).append(ref)
    json.dump(dict(title='ARP 3620 Passprobe', date=time.strftime('%d.%m.%Y'), rev=CNS['DOC_REV'], boards=boards_meta,
                   parts=meta, findings=findings, gaps=gap_res, counts=counts, hits=hits_by_ref,
                   heights=dict(Z_BASE=Z_BASE, Z_KB=Z_KB, Z_TOP=Z_TOP, Z_STRIP=Z_STRIP, H_TOTAL=H_TOTAL),
                   size=[W, D, H_TOTAL]),
              open(VIEW / 'fit3d.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote case.glb %.2f MB, %d nodes, %.0f s' % (size / 1e6, len(meta), time.time() - t0))


main()
