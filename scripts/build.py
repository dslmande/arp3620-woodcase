# -*- coding: utf-8 -*-
"""Build the 3D model, check it, export STEP and FCStd.

    freecadcmd build.py          (output goes to ../production and ../model)
"""
import os, sys, itertools, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import FreeCAD as App, Part, Import
from params import *
from parts import PARTS, ASSEMBLY, ASSEMBLY_STRIP, ASSEMBLY_LID, JOINTS
import model

ROOT = os.path.dirname(HERE)
PROD = os.path.join(ROOT, 'production'); os.makedirs(PROD, exist_ok=True)
MOD = os.path.join(ROOT, 'model'); os.makedirs(MOD, exist_ok=True)

case = model.case_solids()
refs = model.references()

# ------------------------------------------------------------------ checks
report = []
bad = 0
for k in model.check_orientation():
    report.append('ORIENTATION: %s has N != U x V' % k); bad += 1
for k, s in case.items():
    if not s.isValid() or len(s.Solids) != 1:
        report.append('INVALID solid: %s (%d solids)' % (k, len(s.Solids))); bad += 1

shapes = dict(case)
shapes.update({k: v[0] for k, v in refs.items()})
# reference bodies that belong together may touch or overlap
same = [{'ref_keybed_frame', 'ref_keys_white', 'ref_keys_black'},
        {'ref_board3620', 'ref_board3620_parts', 'ref_panel_jacks'},
        {'ref_emulator', 'ref_emulator_parts', 'ref_emulator_standoffs'},
        {'ref_psu', 'ref_psu_parts', 'ref_psu_standoffs'}]
allowed = {
    # the standoffs pass through the board envelope? no -> nothing allowed by default
}
pairs = 0
for a, b in itertools.combinations(sorted(shapes), 2):
    if any(a in g and b in g for g in same):
        continue
    sa, sb = shapes[a], shapes[b]
    if not sa.BoundBox.intersect(sb.BoundBox):
        continue
    pairs += 1
    v = sa.common(sb).Volume
    if v > 0.5:
        report.append('COLLISION %-24s %-24s %.1f mm3' % (a, b, v)); bad += 1


def gap(a, b):
    return shapes[a].distToShape(shapes[b])[0]


checks = [
    ('keybed -> left cheek', 'ref_keybed_frame', 'cheek_l', GAP_KB_SIDE),
    ('keybed -> right cheek', 'ref_keybed_frame', 'cheek_r', GAP_KB_SIDE),
    ('white keys -> front wall', 'ref_keys_white', 'front', GAP_KB_FRONT),
    ('keybed frame -> strip', 'ref_keybed_frame', 'strip', 3.0),
    ('black keys -> strip', 'ref_keys_black', 'strip', 3.0),
    ('panel -> left end wall', 'ref_panel', 'end_l', GAP_PANEL),
    ('panel -> left cheek', 'ref_panel', 'cheek_l', GAP_PANEL),
    ('panel -> front wall', 'ref_panel', 'front', GAP_PANEL),
    ('panel -> filler', 'ref_panel', 'filler', GAP_PANEL),
    ('lid top -> strip', 'lid_top', 'strip', 5.0),
    ('lid top -> panel', 'lid_top', 'ref_panel', 25.0),
    ('lid rear -> apron', 'lid_rear', 'apron', 2.5),
    ('lid end right -> right cheek', 'lid_end_r', 'cheek_r', 2.5),
    ('lid front -> keys', 'lid_front', 'ref_keys_white', 2.5),
    ('board parts -> base', 'ref_board3620_parts', 'base', 3.0),
    ('panel jacks -> base', 'ref_panel_jacks', 'base', 3.0),
    ('emulator parts -> strip', 'ref_emulator_parts', 'strip', 10.0),
    ('emulator parts -> apron', 'ref_emulator_parts', 'apron', 2.0),
    ('psu parts -> strip', 'ref_psu_parts', 'strip', 10.0),
    ('psu -> apron', 'ref_psu_parts', 'apron', 2.0),
    ('emulator -> left cheek', 'ref_emulator', 'cheek_l', 3.0),
    ('emulator -> psu', 'ref_emulator_parts', 'ref_psu_parts', 3.0),
    ('emulator -> keybed', 'ref_emulator', 'ref_keybed_frame', 1.0),
    ('rear plate parts -> rear wall', 'ref_plate_parts', 'rear', 0.5),
    ('rear plate parts -> emulator', 'ref_plate_parts', 'ref_emulator_parts', 2.0),
    ('rear plate parts -> apron', 'ref_plate_parts', 'apron', 2.0),
]
report.append('')
report.append('%-34s %8s %8s' % ('clearance', 'mm', 'min'))
for label, a, b, need in checks:
    g = gap(a, b)
    flag = '' if g >= need - 1e-6 else '  <-- too small'
    if flag: bad += 1
    report.append('%-34s %8.2f %8.2f%s' % (label, g, need, flag))

# ------------------------------------------------------------------ joints
report.append('')
report.append('joints: parts in contact (distance 0)')
for a, b in JOINTS:
    g = gap(a, b)
    if g > 0.01:
        report.append('  NO CONTACT %s - %s: %.2f' % (a, b, g)); bad += 1
report.append('  %d joints checked' % len(JOINTS))

# outer shell of the case body: everything in it should be wood except the rear
# window, holes, dogbones and the joint play. A notch or slot without its tab
# would leave a void of at least one tab volume (smallest: 2.6 cm3).
shell = model.box(0, 0, 0, W, D, Z_TOP).cut(model.box(T_WALL, T_WALL, T_BASE, W - T_WALL, D - T_WALL, Z_TOP + 1))
body = [case[k] for k in case if not k.startswith('lid') and k != 'plate']
voids = sorted(shell.cut(Part.makeCompound(body)).Solids, key=lambda v: -v.Volume)
u0, u1, h, r = WINDOW
window = ((u1 - u0) * h - (4 - math.pi) * r * r) * T_WALL
report.append('outer shell: %d voids, largest %s cm3 (rear window %.1f)'
              % (len(voids), ', '.join('%.2f' % (v.Volume / 1e3) for v in voids[:4]), window / 1e3))
for v in voids[1:]:
    if v.Volume > 2e3:
        bb = v.BoundBox
        report.append('  <-- void %.1f cm3 at x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f'
                      % (v.Volume / 1e3, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)); bad += 1

# assembly: every part slides into place along its direction without touching
# the parts already in place
report.append('')
report.append('assembly order (each part moved 40 mm back along its direction, 1 mm steps)')
for seq in (ASSEMBLY, ASSEMBLY_STRIP, ASSEMBLY_LID):
    placed = []
    for key, d, note in seq:
        if d is not None:
            worst = 0.0
            for t in range(1, 41):
                s = case[key].copy(); s.translate(App.Vector(*d) * (-t))
                for k in placed:
                    if s.BoundBox.intersect(case[k].BoundBox):
                        worst = max(worst, s.common(case[k]).Volume)
            flag = '' if worst < 0.5 else '  <-- blocked (%.1f mm3)' % worst
            if flag: bad += 1
            report.append('  %-10s %-12s %s%s' % (key, d, note, flag))
        else:
            report.append('  %-10s %-12s %s' % (key, '', note))
        placed.append(key)

# ------------------------------------------------------------------ mass, sizes
mass = 0.0
report.append('')
for p in PARTS:
    dens = DENSITY_ALU if p.material.startswith('alu') else DENSITY_PLY
    m = case[p.key].Volume * dens
    mass += m
lid = sum(case[p.key].Volume * DENSITY_PLY for p in PARTS if p.key.startswith('lid'))
report.append('mass wood + plate: %.2f kg (lid %.2f kg), without tolex, keybed, electronics' % (mass / 1000, lid / 1000))
report.append('outside: %.0f x %.0f x %.0f mm (with lid, without feet)' % (W, D, H_TOTAL))
report.append('checked pairs: %d, problems: %d' % (pairs, bad))
txt = '\n'.join(report)
print(txt)
open(os.path.join(MOD, 'check.txt'), 'w').write(txt + '\n')

# ------------------------------------------------------------------ export
doc = App.newDocument('ARP3620_Woodcase')
objs_case, objs_all = [], []
for p in PARTS:
    o = doc.addObject('Part::Feature', p.key); o.Shape = case[p.key]; o.Label = p.name
    objs_case.append(o); objs_all.append(o)
for k, (s, col) in refs.items():
    o = doc.addObject('Part::Feature', k); o.Shape = s; o.Label = k.replace('ref_', 'REF ')
    objs_all.append(o)
doc.recompute()
doc.saveAs(os.path.join(MOD, NAME + '.FCStd'))
Import.export(objs_case, os.path.join(PROD, NAME + '.step'))
Import.export(objs_all, os.path.join(MOD, NAME + '_assembly.step'))
print('exported', NAME)
sys.exit(1 if bad else 0)
