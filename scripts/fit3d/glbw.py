# -*- coding: utf-8 -*-
"""Minimal GLB (binary glTF 2.0) writer and FreeCAD tessellation for the fit viewer, numpy only.
After the Percy viewer (Percy/gehaeuse/viewer/glb.py). Case coordinates (x right, y back, z up, mm)
become three.js coordinates (x, z, -y)."""
import json, struct
import numpy as np


def mesh(shape, tol, angle=0.2):
    """Triangles per face (sharp edges stay sharp), in three.js coordinates."""
    import MeshPart
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=tol, AngularDeflection=angle, Relative=False,
                               Segments=True)
    pts = np.array([[p.x, p.y, p.z] for p in m.Topology[0]], dtype=np.float64)
    fac = np.array(m.Topology[1], dtype=np.int64).reshape(-1, 3)
    if not len(fac):
        return pts[:0], pts[:0], np.zeros(0, dtype=np.uint32)
    segs = [list(m.getSegment(i)) for i in range(m.countSegments())] or [list(range(len(fac)))]
    P, N, I = [], [], []
    base = 0
    for s in segs:
        f = fac[s]
        u, inv = np.unique(f.reshape(-1), return_inverse=True)
        p = pts[u]
        t = inv.reshape(-1, 3)
        fn = np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
        vn = np.zeros_like(p)
        for k in range(3):
            np.add.at(vn, t[:, k], fn)
        ln = np.linalg.norm(vn, axis=1, keepdims=True)
        vn = vn / np.where(ln > 0, ln, 1)
        P.append(p); N.append(vn); I.append(t.reshape(-1) + base)
        base += len(p)
    P = np.vstack(P); N = np.vstack(N); I = np.concatenate(I).astype(np.uint32)
    P3 = np.column_stack([P[:, 0], P[:, 2], -P[:, 1]])
    N3 = np.column_stack([N[:, 0], N[:, 2], -N[:, 1]])
    return P3, N3, I


class Writer:
    def __init__(self):
        self.bin = bytearray()
        self.j = dict(asset=dict(version='2.0', generator='arp3620-woodcase fit3d'), scene=0,
                      scenes=[dict(nodes=[])], nodes=[], meshes=[], materials=[], accessors=[], bufferViews=[],
                      buffers=[])

    def _view(self, data, target):
        while len(self.bin) % 4:
            self.bin.append(0)
        off = len(self.bin)
        self.bin += data
        self.j['bufferViews'].append(dict(buffer=0, byteOffset=off, byteLength=len(data), target=target))
        return len(self.j['bufferViews']) - 1

    def _acc(self, arr, typ, ct, target, minmax=False):
        v = self._view(arr.tobytes(), target)
        a = dict(bufferView=v, componentType=ct, count=int(arr.shape[0]), type=typ)
        if minmax:
            a['min'] = [float(x) for x in arr.min(axis=0)]
            a['max'] = [float(x) for x in arr.max(axis=0)]
        self.j['accessors'].append(a)
        return len(self.j['accessors']) - 1

    def material(self, name, colour, metal=0.0, rough=0.7):
        self.j['materials'].append(dict(name=name, doubleSided=True, pbrMetallicRoughness=dict(
            baseColorFactor=[float(c) for c in colour], metallicFactor=metal, roughnessFactor=rough)))
        return len(self.j['materials']) - 1

    def node(self, name, prims, extras=None):
        ps = []
        for mat, pos, nor, idx in prims:
            if len(idx) == 0:
                continue
            pos = np.ascontiguousarray(pos, dtype=np.float32)
            nor = np.ascontiguousarray(nor, dtype=np.float32)
            at = dict(POSITION=self._acc(pos, 'VEC3', 5126, 34962, True), NORMAL=self._acc(nor, 'VEC3', 5126, 34962))
            if len(pos) < 65536:
                ia = self._acc(np.ascontiguousarray(idx, dtype=np.uint16), 'SCALAR', 5123, 34963)
            else:
                ia = self._acc(np.ascontiguousarray(idx, dtype=np.uint32), 'SCALAR', 5125, 34963)
            ps.append(dict(attributes=at, indices=ia, material=mat, mode=4))
        if not ps:
            return None
        self.j['meshes'].append(dict(name=name, primitives=ps))
        n = dict(name=name, mesh=len(self.j['meshes']) - 1)
        if extras:
            n['extras'] = extras
        self.j['nodes'].append(n)
        self.j['scenes'][0]['nodes'].append(len(self.j['nodes']) - 1)
        return len(self.j['nodes']) - 1

    def save(self, path):
        while len(self.bin) % 4:
            self.bin.append(0)
        self.j['buffers'] = [dict(byteLength=len(self.bin))]
        js = json.dumps(self.j, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        while len(js) % 4:
            js += b' '
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        with open(path, 'wb') as f:
            f.write(struct.pack('<III', 0x46546C67, 2, total))
            f.write(struct.pack('<II', len(js), 0x4E4F534A))
            f.write(js)
            f.write(struct.pack('<II', len(self.bin), 0x004E4942))
            f.write(self.bin)
        return total
