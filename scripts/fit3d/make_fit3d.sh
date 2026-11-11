#!/bin/bash
# 3D fit check: KiCad exports of the four ARP 3620 boards, then FreeCAD check and viewer data.
# Reads the boards in ../Arp3620 (scripts/fit3d/sources.py), writes model/fit3d/ and scripts/fit3d/viewer/.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KIPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
arch -arm64 "$KIPY" -B scripts/fit3d/kicad_parts.py 2>&1 | grep -E "parts$" || true
python3 -B - <<'PY' > model/fit3d/origins.txt
import json
K = json.load(open('model/fit3d/kicad_parts.json'))
for k, v in K.items():
    e = v['edge']; print(k, round(e[0] + 0.05, 3), round(e[3] - 0.05, 3))
PY
while read -r k x y; do
  f=$(python3 -B -c "import sys; sys.path.insert(0, 'scripts/fit3d'); from sources import BOARDS; print(BOARDS['$k'])")
  for fmt in step glb; do
    "$KC" pcb export $fmt --subst-models --user-origin ${x}x${y}mm -f -o model/fit3d/$k.$fmt "$f" 2>&1 \
      | grep -E "Could not add" || true
  done
  cp model/fit3d/$k.glb scripts/fit3d/viewer/$k.glb
done < model/fit3d/origins.txt
"$FC" -c "import sys; sys.dont_write_bytecode = True; p = '$PWD/scripts/fit3d/fit3d.py'; exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, '__name__': '__main__'})" 2>&1 \
  | grep -v -E '^\*\*|^\[|Transferring|^$' | grep -v $'\x1b' || true
for f in scripts/fit3d/viewer/*.glb; do base64 -i "$f" -o "$f.txt"; done
