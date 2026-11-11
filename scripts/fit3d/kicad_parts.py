#!/usr/bin/env python3
"""Read outline, footprints and holes of the four ARP 3620 boards (KiCad python, read only).

    arch -arm64 <KiCad python> scripts/fit3d/kicad_parts.py

Writes model/fit3d/kicad_parts.json: per board the edge bounding box (KiCad sheet coordinates, mm, y down) and per
footprint reference, value, footprint, side, position, rotation, courtyard/bounding box and model count.
"""
import json, sys
from pathlib import Path
import pcbnew

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from sources import BOARDS                              # noqa: E402

T = pcbnew.ToMM


def read(path):
    b = pcbnew.LoadBoard(str(path))
    bb = b.GetBoardEdgesBoundingBox()
    parts = []
    for fp in b.GetFootprints():
        p = fp.GetPosition()
        cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
        if cy.OutlineCount():
            r = cy.BBox()
            box = [T(r.GetLeft()), T(r.GetTop()), T(r.GetRight()), T(r.GetBottom())]
        else:
            r = fp.GetBoundingBox(False)
            box = [T(r.GetLeft()), T(r.GetTop()), T(r.GetRight()), T(r.GetBottom())]
        holes = []
        for pad in fp.Pads():
            if pad.GetDrillSize().x > 0:
                q = pad.GetPosition()
                holes.append([round(T(q.x), 3), round(T(q.y), 3), round(T(pad.GetDrillSize().x), 3)])
        parts.append(dict(ref=fp.GetReference(), value=fp.GetValue(), fp=fp.GetFPID().GetLibItemName().wx_str(),
                          side='B' if fp.IsFlipped() else 'F', x=round(T(p.x), 3), y=round(T(p.y), 3),
                          rot=round(fp.GetOrientationDegrees() % 360, 2), box=[round(v, 3) for v in box],
                          models=len(fp.Models()), holes=holes))
    return dict(file=str(path.relative_to(path.parents[2])), edge=[T(bb.GetLeft()), T(bb.GetTop()),
                T(bb.GetRight()), T(bb.GetBottom())], thickness=T(b.GetDesignSettings().GetBoardThickness()),
                parts=parts)


out = {k: read(v) for k, v in BOARDS.items()}
dst = ROOT / 'model' / 'fit3d'
dst.mkdir(parents=True, exist_ok=True)
json.dump(out, open(dst / 'kicad_parts.json', 'w', encoding='utf-8'), indent=1)
for k, v in out.items():
    e = v['edge']
    print('%-8s %s  %.2f x %.2f  t %.2f  %d parts' % (k, v['file'], e[2] - e[0], e[3] - e[1], v['thickness'],
                                                     len(v['parts'])))
