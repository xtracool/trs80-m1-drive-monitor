"""
Two-layer grid maze router.

Layer 0 = F.Cu (horizontal preference), layer 1 = B.Cu (vertical preference).
Cells are GRID apart.  A cell is blocked on a layer when copper of another
net on that layer would violate CLEARANCE against a trace centred on that
cell.  Vias have a separate, stricter mask.

Nets are routed one at a time, shortest-first, each additional terminal of a
net being connected to the copper the net already owns (multi-source
Dijkstra).  Output is a list of straight segments and vias in board mm.
"""
import heapq
import math
from typing import Dict, List, Tuple, Set, Optional
import config as C
from design import Footprint, Pad, tab_left

F, B = 0, 1
LAYER_NAME = {F: "F.Cu", B: "B.Cu"}


class RouteError(Exception):
    pass


class Router:
    def __init__(self, fps: List[Footprint], key_slot_x: float):
        self.g = C.GRID
        self.nx = int(C.BOARD_W / self.g) + 1
        self.ny = int(C.BOARD_H / self.g) + 1
        self.fps = fps
        self.pads: List[Pad] = [p for fp in fps for p in fp.pads]
        self.key_slot_x = key_slot_x
        # occupancy: (layer, ix, iy) -> net name  (traces + vias)
        self.occ: Dict[Tuple[int, int, int], str] = {}
        self.vias: Dict[Tuple[int, int], str] = {}
        self.segments: List[Tuple[str, int, float, float, float, float, float]] = []  # net, layer, x1,y1,x2,y2,w
        self.via_list: List[Tuple[str, float, float]] = []
        self.net_width: Dict[str, float] = {}
        self.terminal_cells: Dict[str, List[Tuple[int, int, int]]] = {}
        self._build_terminals()
        self.terminal_set: Dict[Tuple[int, int, int], str] = {
            c: n for n, cells in self.terminal_cells.items() for c in cells}
        self.padmask: Dict[Tuple[float, int], Dict[Tuple[int, int], Set[str]]] = {}
        self.viamask: Dict[Tuple[int, int], Set[str]] = {}
        self._build_masks()

    def _build_masks(self):
        widths = sorted({C.TRACE_W, C.POWER_W})
        for w in widths:
            for layer in (F, B):
                self.padmask[(w / 2, layer)] = {}
        for p in self.pads:
            key = p.net or f"NC:{id(p)}"
            reach = max(p.size) / 2 + C.CLEARANCE + max(widths) / 2 + C.VIA_DIA + 1.0
            ix0, iy0 = round(p.x / self.g), round(p.y / self.g)
            r = int(reach / self.g) + 1
            for ix in range(ix0 - r, ix0 + r + 1):
                for iy in range(iy0 - r, iy0 + r + 1):
                    x, y = self.to_mm(ix, iy)
                    for w in widths:
                        for layer in (F, B):
                            if self._pad_blocks(p, x, y, w / 2, layer):
                                self.padmask[(w / 2, layer)].setdefault((ix, iy), set()).add(key)
                    if math.hypot(x - p.x, y - p.y) < max(p.size) / 2 + C.CLEARANCE + C.VIA_DIA / 2 + 0.6:
                        self.viamask.setdefault((ix, iy), set()).add(key)

    # ---------------------------------------------------------------- helpers
    def to_cell(self, x: float, y: float) -> Tuple[int, int]:
        ix, iy = round(x / self.g), round(y / self.g)
        if abs(ix * self.g - x) > 0.01 or abs(iy * self.g - y) > 0.01:
            raise RouteError(f"off-grid terminal at ({x:.3f},{y:.3f})")
        return ix, iy

    def to_mm(self, ix: int, iy: int) -> Tuple[float, float]:
        return round(ix * self.g, 3), round(iy * self.g, 3)

    def pad_layers(self, p: Pad) -> Set[int]:
        s = set()
        for l in p.layers:
            if l.startswith("*") or l.startswith("F.Cu"):
                s.add(F)
            if l.startswith("*") or l.startswith("B.Cu"):
                s.add(B)
        return s

    def _build_terminals(self):
        for fp in self.fps:
            for p in fp.pads:
                if not p.net:
                    continue
                if fp.ref == "J1":
                    # connect at the inner end of the finger; fingers are centred on the
                    # 1.795 in tab so they are ~0.06 mm off the routing grid - snap inside the pad
                    ix, iy = round(p.x / self.g), round(C.J1_FINGER_LEN / self.g)
                    layer = F if "F.Cu" in p.layers else B
                    cells = [(layer, ix, iy)]
                    # reserve the exit stub directly below the finger so another
                    # net cannot run under it and seal the finger in
                    self.occ[(layer, ix, iy + 1)] = p.net
                    self.occ[(layer, ix, iy + 2)] = p.net
                else:
                    ix, iy = self.to_cell(p.x, p.y)
                    cells = [(l, ix, iy) for l in sorted(self.pad_layers(p))]
                self.terminal_cells.setdefault(p.net, []).extend(cells)

    # ---------------------------------------------------------------- masks
    def _pad_blocks(self, p: Pad, x: float, y: float, half_w: float, layer: int) -> bool:
        """True if a trace of half-width half_w centred at (x,y) on `layer`
        would violate clearance to pad p."""
        if layer not in self.pad_layers(p):
            return False
        need = C.CLEARANCE + half_w
        if p.shape == "circle":
            return math.hypot(x - p.x, y - p.y) < p.size[0] / 2 + need
        # rect / oval treated as rect
        dx = max(abs(x - p.x) - p.size[0] / 2, 0)
        dy = max(abs(y - p.y) - p.size[1] / 2, 0)
        return math.hypot(dx, dy) < need

    def blocked(self, net: str, layer: int, ix: int, iy: int, half_w: float, for_via=False) -> bool:
        x, y = self.to_mm(ix, iy)
        if not for_via and self.occ.get((layer, ix, iy)) == net:
            return False            # already this net's copper (pads, stubs, earlier traces)
        if self.terminal_set.get((layer, ix, iy)) == net and not for_via:
            o = self.occ.get((layer, ix, iy))
            return o is not None and o != net
        # board edge
        edge = C.EDGE_CLEARANCE + half_w
        if x < edge or y < edge or x > C.BOARD_W - edge or y > C.BOARD_H - edge:
            return True
        # rear edge is recessed by the tab depth everywhere; the tab itself is fingers only
        if y < C.J1_REAR_RECESS + edge:
            return True
        # key slot
        if C.J1_KEY_SLOT and abs(x - self.key_slot_x) < C.J1_KEY_SLOT_W / 2 + edge and y < C.J1_KEY_SLOT_DEPTH + edge:
            return True
        # existing copper of other nets
        o = self.occ.get((layer, ix, iy))
        if o is not None and o != net:
            return True
        if for_via:
            o2 = self.occ.get((1 - layer, ix, iy))
            if o2 is not None and o2 != net:
                return True
            v = self.vias.get((ix, iy))
            if v is not None and v != net:
                return True
        # pads
        if for_via:
            s = self.viamask.get((ix, iy))
        else:
            s = self.padmask[(half_w, layer)].get((ix, iy))
        if s and any(k != net for k in s):
            return True
        return False

    # ---------------------------------------------------------------- search
    def _dijkstra(self, net: str, sources: Set[Tuple[int, int, int]],
                  targets: Set[Tuple[int, int, int]], half_w: float) -> List[Tuple[int, int, int]]:
        INF = float("inf")
        dist: Dict[Tuple[int, int, int], float] = {}
        prev: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        pq = []
        for s in sources:
            dist[s] = 0.0
            heapq.heappush(pq, (0.0, s))
        seen = set()
        while pq:
            d, cur = heapq.heappop(pq)
            if cur in seen:
                continue
            seen.add(cur)
            if cur in targets:
                path = [cur]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return path[::-1]
            layer, ix, iy = cur
            # planar moves
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (layer, ix + dx, iy + dy)
                if nxt in seen:
                    continue
                if not (0 <= nxt[1] < self.nx and 0 <= nxt[2] < self.ny):
                    continue
                if self.blocked(net, layer, nxt[1], nxt[2], half_w):
                    continue
                cost = 1.0
                # direction preference: F horizontal, B vertical
                if (layer == F and dy != 0) or (layer == B and dx != 0):
                    cost += 1.0
                # bend penalty
                if cur in prev:
                    pl, pix, piy = prev[cur]
                    if pl == layer and (pix - ix, piy - iy) != (-dx, -dy):
                        cost += 0.6
                nd = d + cost
                if nd < dist.get(nxt, INF):
                    dist[nxt] = nd
                    prev[nxt] = cur
                    heapq.heappush(pq, (nd, nxt))
            # via
            nxt = (1 - layer, ix, iy)
            if nxt not in seen and not self.blocked(net, 1 - layer, ix, iy, half_w) \
                    and not self.blocked(net, layer, ix, iy, half_w, for_via=True):
                nd = d + 4.0
                if nd < dist.get(nxt, INF):
                    dist[nxt] = nd
                    prev[nxt] = cur
                    heapq.heappush(pq, (nd, nxt))
        raise RouteError(f"no path for net {net}")

    def route_net(self, net: str, width: float):
        self.net_width[net] = width
        half_w = width / 2
        terms = self.terminal_cells[net]
        # group cells per pad (same ix,iy on both layers = one THT pad)
        pads_xy: List[Tuple[int, int]] = []
        for l, ix, iy in terms:
            if (ix, iy) not in pads_xy:
                pads_xy.append((ix, iy))
        if len(pads_xy) < 2:
            return
        layers_at = {}
        for l, ix, iy in terms:
            layers_at.setdefault((ix, iy), set()).add(l)
        # greedy nearest-neighbour ordering
        owned: Set[Tuple[int, int, int]] = set()
        start = pads_xy[0]
        for l in layers_at[start]:
            owned.add((l, start[0], start[1]))
            self.occ[(l, start[0], start[1])] = net
        remaining = pads_xy[1:]
        while remaining:
            # nearest pad to owned copper
            best, bd = None, None
            for pxy in remaining:
                d = min(abs(pxy[0] - o[1]) + abs(pxy[1] - o[2]) for o in owned)
                if bd is None or d < bd:
                    best, bd = pxy, d
            remaining.remove(best)
            targets = {(l, best[0], best[1]) for l in layers_at[best]}
            path = self._dijkstra(net, owned, targets, half_w)
            self._commit(net, path, width, layers_at)
            for cell in path:
                owned.add(cell)
            for l in layers_at[best]:
                owned.add((l, best[0], best[1]))
                self.occ[(l, best[0], best[1])] = net

    def _commit(self, net: str, path: List[Tuple[int, int, int]], width: float, layers_at):
        for cell in path:
            self.occ[cell] = net
        # split into runs per layer, then into straight segments
        i = 0
        while i < len(path) - 1:
            a, b = path[i], path[i + 1]
            if a[0] != b[0]:
                x, y = self.to_mm(a[1], a[2])
                if (a[1], a[2]) not in self.vias:
                    # a via is not needed if this cell is a through-hole pad of the net
                    if not (a[1], a[2]) in layers_at or len(layers_at[(a[1], a[2])]) < 2:
                        self.vias[(a[1], a[2])] = net
                        self.via_list.append((net, x, y))
                    self.occ[(F, a[1], a[2])] = net
                    self.occ[(B, a[1], a[2])] = net
                i += 1
                continue
            # extend straight run
            j = i + 1
            dx, dy = b[1] - a[1], b[2] - a[2]
            while j + 1 < len(path) and path[j + 1][0] == a[0] and \
                    (path[j + 1][1] - path[j][1], path[j + 1][2] - path[j][2]) == (dx, dy):
                j += 1
            x1, y1 = self.to_mm(a[1], a[2])
            x2, y2 = self.to_mm(path[j][1], path[j][2])
            self.segments.append((net, a[0], x1, y1, x2, y2, width))
            i = j

    # ---------------------------------------------------------------- verify
    def drc(self) -> List[str]:
        """Independent geometric clearance check (does not use the grid)."""
        errs = []

        def seg_pt_dist(x1, y1, x2, y2, px, py):
            vx, vy = x2 - x1, y2 - y1
            L2 = vx * vx + vy * vy
            t = 0 if L2 == 0 else max(0, min(1, ((px - x1) * vx + (py - y1) * vy) / L2))
            return math.hypot(px - (x1 + t * vx), py - (y1 + t * vy))

        def seg_seg_dist(a, b):
            (ax1, ay1, ax2, ay2), (bx1, by1, bx2, by2) = a, b
            return min(seg_pt_dist(ax1, ay1, ax2, ay2, bx1, by1), seg_pt_dist(ax1, ay1, ax2, ay2, bx2, by2),
                       seg_pt_dist(bx1, by1, bx2, by2, ax1, ay1), seg_pt_dist(bx1, by1, bx2, by2, ax2, ay2))

        segs = self.segments
        # trace vs trace
        for i in range(len(segs)):
            n1, l1, *a, w1 = segs[i]
            for j in range(i + 1, len(segs)):
                n2, l2, *b, w2 = segs[j]
                if n1 == n2 or l1 != l2:
                    continue
                d = seg_seg_dist(a, b) - w1 / 2 - w2 / 2
                if d < C.CLEARANCE - 1e-6:
                    errs.append(f"trace/trace {n1} vs {n2} on {LAYER_NAME[l1]} gap {d:.3f}")
        # trace vs pad
        for n1, l1, x1, y1, x2, y2, w1 in segs:
            for p in self.pads:
                if p.net == n1 or l1 not in self.pad_layers(p):
                    continue
                r = max(p.size) / 2 if p.shape == "circle" else math.hypot(*p.size) / 2
                d = seg_pt_dist(x1, y1, x2, y2, p.x, p.y) - r - w1 / 2
                if d < C.CLEARANCE - 1e-6:
                    # refine for rect pads
                    if p.shape != "circle":
                        # sample along segment
                        ok = True
                        for k in range(0, 21):
                            t = k / 20
                            sx, sy = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
                            dx = max(abs(sx - p.x) - p.size[0] / 2, 0)
                            dy = max(abs(sy - p.y) - p.size[1] / 2, 0)
                            if math.hypot(dx, dy) - w1 / 2 < C.CLEARANCE - 1e-6:
                                ok = False
                        if ok:
                            continue
                    errs.append(f"trace/pad {n1} vs {p.net or 'NC'} pad near ({p.x:.2f},{p.y:.2f}) gap {d:.3f}")
        # via vs pad / trace
        for n, vx, vy in self.via_list:
            for p in self.pads:
                if p.net == n:
                    continue
                r = max(p.size) / 2
                d = math.hypot(vx - p.x, vy - p.y) - r - C.VIA_DIA / 2
                if d < C.CLEARANCE - 1e-6:
                    errs.append(f"via/pad {n} vs {p.net} at ({vx:.2f},{vy:.2f}) gap {d:.3f}")
            for n1, l1, x1, y1, x2, y2, w1 in segs:
                if n1 == n:
                    continue
                d = seg_pt_dist(x1, y1, x2, y2, vx, vy) - w1 / 2 - C.VIA_DIA / 2
                if d < C.CLEARANCE - 1e-6:
                    errs.append(f"via/trace {n} vs {n1} at ({vx:.2f},{vy:.2f}) gap {d:.3f}")
        # pad vs pad (different nets)
        for i, p in enumerate(self.pads):
            for q in self.pads[i + 1:]:
                if p.net == q.net or not (self.pad_layers(p) & self.pad_layers(q)):
                    continue
                d = math.hypot(p.x - q.x, p.y - q.y) - max(p.size) / 2 - max(q.size) / 2
                if p.shape != "circle" and q.shape != "circle":
                    d = max(abs(p.x - q.x) - p.size[0] / 2 - q.size[0] / 2,
                            abs(p.y - q.y) - p.size[1] / 2 - q.size[1] / 2)
                if d < C.CLEARANCE - 1e-6:
                    errs.append(f"pad/pad {p.net} vs {q.net} at ({p.x:.2f},{p.y:.2f}) gap {d:.3f}")
        return errs
