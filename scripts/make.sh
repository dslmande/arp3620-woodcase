#!/bin/bash
# Regenerate everything from params.py: 3D model + checks, DXF, renders, drawing.
set -e
cd "$(dirname "$0")"
FC=${FREECADCMD:-/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd}
PY=${PYTHON:-/usr/bin/python3}
export PYTHONDONTWRITEBYTECODE=1
"$FC" build.py   | grep -v '^\*\*\|^\[' || true
grep -q 'problems: 0' ../model/check.txt || { echo "model check failed, see model/check.txt"; exit 1; }
"$PY" dxf_out.py
"$PY" dxf_preview.py
"$FC" render.py  | grep wrote
"$FC" drawing.py | grep wrote
