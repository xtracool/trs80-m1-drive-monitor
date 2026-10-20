"""
Post-process the generated board with KiCad's own tools (run with the KiCad Python):

  * flip every footprint that design.py placed on B.Cu (written front-side, mirrored)
  * fill the copper zones so the shipped file is complete
  * write the per-footprint metadata KiCad 10's "Update PCB from Schematic" would otherwise
    add on first run: sheetname, sheetfile and the unit/pin list, taken from KiCad's own
    netlist export so they compare equal in the updater
  * save in the running KiCad's native format

    <kicad>/bin/python3 gen/postprocess.py kicad/sa400_led_monitor.kicad_pcb
"""
import os, re, subprocess, sys, tempfile
import pcbnew

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from design import build   # noqa: E402

PCB = sys.argv[1]
SCH = PCB.replace(".kicad_pcb", ".kicad_sch")
SHEETFILE = os.path.basename(SCH)


# ---------------------------------------------------------------- tiny s-expression reader
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


def units_from_netlist():
    """ref -> [(unit name, [pin numbers in netlist order]), ...] via kicad-cli sch export netlist."""
    cli = os.path.join(os.path.dirname(sys.executable), "kicad-cli")
    with tempfile.TemporaryDirectory() as td:
        net = os.path.join(td, "n.kicad_net")
        subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr", "--output", net, SCH],
                       check=True, capture_output=True)
        tree = parse(open(net).read())
    out = {}
    comps = next(x for x in tree if isinstance(x, list) and x and x[0] == "components")
    for comp in comps[1:]:
        ref = next(x[1] for x in comp if isinstance(x, list) and x[0] == "ref")
        units = next((x for x in comp if isinstance(x, list) and x[0] == "units"), None)
        lst = []
        if units:
            for u in units[1:]:
                name = next(x[1] for x in u if isinstance(x, list) and x[0] == "name")
                pins = next((x for x in u if isinstance(x, list) and x[0] == "pins"), ["pins"])
                nums = []
                for pin in pins[1:]:
                    if isinstance(pin, list) and pin[0] == "pin":
                        nums.append(next(x[1] for x in pin if isinstance(x, list) and x[0] == "num"))
                lst.append((name, nums))
        out[ref] = lst
    return out


board = pcbnew.LoadBoard(PCB)
back = {fp.ref for fp in build()[0] if fp.layer == "B.Cu"}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in back and not fp.IsFlipped():
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        print(f"[post] {ref} -> {fp.GetLayerName()}")
    fp.SetSheetname("/")            # root sheet, as the updater names it
    fp.SetSheetfile(SHEETFILE)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
print(f"[post] filled {len(board.Zones())} zone(s)")
pcbnew.SaveBoard(PCB, board)

# unit info is not settable through the Python API: patch the saved text in KiCad's own syntax
units = units_from_netlist()
text = open(PCB).read()
count = 0
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def add_units(m):
    global count
    ref = m.group("ref")
    lst = units.get(ref) or []
    if not lst:
        return m.group(0)
    blk = "(units" + "".join(f' (unit (name {q(n)}) (pins {" ".join(q(x) for x in pins)}))' for n, pins in lst) + ")"
    count += 1
    return m.group(0) + "\n\t\t" + blk
# within each footprint the Reference property precedes the sheetfile line; insert the units block after it
pattern = re.compile(r'\(property "Reference" "(?P<ref>[^"]+)"(?:(?!\(footprint ).)*?\(sheetfile "[^"]*"\)', re.S)
text = pattern.sub(add_units, text)
open(PCB, "w").write(text)
print(f"[post] unit metadata written for {count} footprints")

# prove it loads and that KiCad preserves the block on its own save (i.e. it parsed into FP_UNIT_INFO)
b2 = pcbnew.LoadBoard(PCB)
pcbnew.SaveBoard(PCB, b2)
kept = len(re.findall(r'\(units\s*\(unit', open(PCB).read()))
if kept != count:
    raise SystemExit(f"[post] FAILED: KiCad kept unit info for {kept}/{count} footprints")
print(f"[post] reload + resave OK: {kept} footprints carry unit info, sheetname={b2.GetFootprints()[0].GetSheetname()!r}")
print("[post] saved", PCB)
