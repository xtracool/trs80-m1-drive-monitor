"""
Emulates the comparisons KiCad 10's BOARD_NETLIST_UPDATER makes in dry-run (the F8 dialog list):
footprint id, value, sheetname, sheetfile and per-unit pin lists, for every component.
Runs with plain Python; needs kicad-cli for the netlist export.
"""
import os, re, subprocess, tempfile


def parse(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    pos = 0

    def node():
        nonlocal pos
        t = tokens[pos]; pos += 1
        if t == "(":
            lst = []
            while tokens[pos] != ")":
                lst.append(node())
            pos += 1
            return lst
        return t[1:-1] if t.startswith('"') else t
    return node()


def child(lst, key, default=None):
    return next((x for x in lst if isinstance(x, list) and x and x[0] == key), default)


def netlist_components(cli, env, sch):
    with tempfile.TemporaryDirectory() as td:
        net = os.path.join(td, "n.kicad_net")
        subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr", "--output", net, sch],
                       check=True, capture_output=True, env=env)
        tree = parse(open(net).read())
    out = {}
    for comp in child(tree, "components")[1:]:
        ref = child(comp, "ref")[1]
        props = {p[1][1] if isinstance(p[1], list) else None: (child(p, "value") or ["", ""])[1]
                 for p in comp if isinstance(p, list) and p[0] == "property"}
        units = []
        for u in (child(comp, "units") or ["units"])[1:]:
            pins = [child(pin, "num")[1] for pin in (child(u, "pins") or ["pins"])[1:] if isinstance(pin, list)]
            units.append((child(u, "name")[1], pins))
        out[ref] = {"footprint": (child(comp, "footprint") or ["", ""])[1], "value": child(comp, "value")[1],
                    "sheetfile": props.get("Sheetfile", ""), "units": units}
    return out


def board_footprints(pcb):
    tree = parse(open(pcb).read())
    out = {}
    for fp in tree:
        if not (isinstance(fp, list) and fp and fp[0] == "footprint"):
            continue
        ref = next(p[2] for p in fp if isinstance(p, list) and p[0] == "property" and p[1] == "Reference")
        val = next(p[2] for p in fp if isinstance(p, list) and p[0] == "property" and p[1] == "Value")
        units = []
        for u in (child(fp, "units") or ["units"])[1:]:
            units.append((child(u, "name")[1], list((child(u, "pins") or ["pins"])[1:])))
        out[ref] = {"footprint": fp[1], "value": val, "sheetname": (child(fp, "sheetname") or ["", ""])[1],
                    "sheetfile": (child(fp, "sheetfile") or ["", ""])[1], "units": units}
    return out


def compare_with_netlist(cli, env, sch, pcb):
    net = netlist_components(cli, env, sch)
    brd = board_footprints(pcb)
    problems = []
    for ref, c in net.items():
        f = brd.get(ref)
        if f is None:
            problems.append(f"{ref}: no footprint on board"); continue
        if f["footprint"] != c["footprint"]: problems.append(f"{ref}: footprint {f['footprint']} != {c['footprint']}")
        if f["value"] != c["value"]: problems.append(f"{ref}: value {f['value']!r} != {c['value']!r}")
        if f["sheetname"] != "/": problems.append(f"{ref}: sheetname {f['sheetname']!r} != '/'")
        if f["sheetfile"] != c["sheetfile"]: problems.append(f"{ref}: sheetfile {f['sheetfile']!r} != {c['sheetfile']!r}")
        if f["units"] != c["units"]: problems.append(f"{ref}: units {f['units']} != {c['units']}")
    for ref in brd:
        if ref not in net:
            problems.append(f"{ref}: on board but not in schematic")
    return problems
