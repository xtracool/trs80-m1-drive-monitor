#!/usr/bin/env python3
"""
Release gate: every check that KiCad itself can run, in order, failing on the first nonzero.

    python3 gen/verify.py [--kicad-bin DIR]     # DIR holds kicad-cli and python3 (KiCad 10)

Steps: build -> postprocess (KiCad flips J2, fills zones) -> DRC with schematic parity -> ERC
       -> footprint/symbol UUID link check -> gerber + drill plot.
Exit: 0 all clean, 1 a check failed, 130 interrupted.
Not covered (GUI only): 'Update PCB from Schematic' (F8) - run it once by hand after opening the project.
"""
import json, os, re, subprocess, sys


def C_VERSION():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import config
    return config.VERSION


def C_PROJECT():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import config
    return config.PROJECT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(ROOT, "kicad"); O = os.path.join(ROOT, "output")
PCB = os.path.join(K, "sa400_led_monitor.kicad_pcb"); SCH = os.path.join(K, "sa400_led_monitor.kicad_sch")


def run(cmd, env=None):
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(f"[verify] FAILED: {' '.join(cmd)}")
    return r.stdout


def main():
    kbin = None
    if "--kicad-bin" in sys.argv:
        kbin = sys.argv[sys.argv.index("--kicad-bin") + 1]
    cli = os.path.join(kbin, "kicad-cli") if kbin else "kicad-cli"
    kpy = os.path.join(kbin, "python3") if kbin else "python3"
    env = dict(os.environ)
    if kbin:
        env["APPDIR"] = os.path.dirname(kbin)

    print("[1/6] build"); run([sys.executable, os.path.join(ROOT, "gen", "build.py")])
    print("[2/6] postprocess"); run([kpy, os.path.join(ROOT, "gen", "postprocess.py"), PCB], env)
    for f in os.listdir(K):
        if f.endswith(".kicad_prl"): os.remove(os.path.join(K, f))
    print("[3/6] DRC + parity")
    run([cli, "pcb", "drc", "--schematic-parity", "--severity-all", "--format", "json", "--output", os.path.join(O, "drc.json"), PCB], env)
    d = json.load(open(os.path.join(O, "drc.json")))
    n = (len(d["violations"]), len(d["unconnected_items"]), len(d["schematic_parity"]))
    print("      violations/unconnected/parity =", n)
    if any(n): raise SystemExit("[verify] FAILED: DRC not clean")
    print("[4/6] ERC")
    run([cli, "sch", "erc", "--severity-all", "--format", "json", "--output", os.path.join(O, "erc.json"), SCH], env)
    e = sum(len(s["violations"]) for s in json.load(open(os.path.join(O, "erc.json")))["sheets"])
    print("      violations =", e)
    if e: raise SystemExit("[verify] FAILED: ERC not clean")
    print("[5/6] symbol <-> footprint links")
    sch = open(SCH).read(); pcb = open(PCB).read()
    sym = {m.group(2): m.group(1) for m in re.finditer(r'\(uuid ([0-9a-f-]+)\)\n\s+\(property "Reference" "([A-Z0-9]+)"', sch)}
    paths = set(re.findall(r'\(path "/([0-9a-f-]+)"\)', pcb))   # root-sheet form: "/<symbol uuid>"
    unlinked = [r for r, u in sym.items() if u not in paths]
    print(f"      {len(sym) - len(unlinked)}/{len(sym)} linked")
    if unlinked or not sym: raise SystemExit(f"[verify] FAILED: unlinked {unlinked}")
    print("[5b] F8 metadata emulation (sheetname / sheetfile / unit pins vs KiCad's netlist)")
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    from postprocess_check import compare_with_netlist
    problems = compare_with_netlist(cli, env, SCH, PCB)
    if problems:
        for p in problems[:10]: print("      ", p)
        raise SystemExit("[verify] FAILED: board metadata differs from schematic netlist")
    print("      all footprints match the netlist (sheetname, sheetfile, unit pin lists, footprint id, value)")
    print("[5c] documentation present")
    docs = [os.path.join(ROOT, "README.md")] + [os.path.join(ROOT, "docs", f) for f in os.listdir(os.path.join(ROOT, "docs")) if f.endswith(".md")]
    small = [d for d in docs if os.path.getsize(d) < 800]
    if small: raise SystemExit(f"[verify] FAILED: truncated/empty docs: {[os.path.basename(s) for s in small]}")
    print(f"      {len(docs)} markdown docs, none empty")
    print("[5d] version consistency across docs")
    ver = C_VERSION()
    stale = []
    for fn in ["README.md"] + [os.path.join("docs", f) for f in os.listdir(os.path.join(ROOT, "docs")) if f.endswith(".md") and f != "CHANGELOG.md"]:
        txt = open(os.path.join(ROOT, fn)).read()
        for m in set(re.findall(r"v0\.\d+\.\d+", txt)):
            if m != "v" + ver and fn not in ("docs/ASSEMBLY.md", "docs/TEST_PLAN.md"):   # those name older hardware on purpose
                stale.append(f"{fn}: {m}")
    if stale: raise SystemExit(f"[verify] FAILED: stale version strings {stale}")
    cl = open(os.path.join(ROOT, "docs", "CHANGELOG.md")).read()
    first = next((l for l in cl.splitlines() if l.startswith("## ")), "")
    if not first.startswith("## v" + ver):
        raise SystemExit(f"[verify] FAILED: CHANGELOG.md has no entry for v{ver} at the top")
    print(f"      all docs at v{ver}, changelog entry present")
    print("[6/6] gerbers + drill")
    g = os.path.join(O, "gerbers"); os.makedirs(g, exist_ok=True)
    run([cli, "pcb", "export", "gerbers", "--output", g + "/", "--layers", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts", "--subtract-soldermask", PCB], env)
    run([cli, "pcb", "export", "drill", "--output", g + "/", "--format", "excellon", "--excellon-separate-th", "--generate-map", "--map-format", "gerberx2", PCB], env)
    print("[7/7] position file -> JLCPCB CPL")
    pos = os.path.join(O, "assembly", "kicad_pos.csv")
    run([cli, "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--output", pos, PCB], env)
    import csv
    n = 0
    sockets = []                                   # U1A/U2A/U3A: same place as the IC (build.py SOCKET row)
    with open(os.path.join(O, "assembly", "CPL_jlcpcb.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in csv.DictReader(open(pos)):
            if r["Ref"] == "J1" or r["Ref"].startswith("H"):
                continue
            row = [r["Ref"], f'{float(r["PosX"]):.3f}mm', f'{float(r["PosY"]):.3f}mm',
                   "Top" if r["Side"] == "top" else "Bottom", f'{float(r["Rot"]):.0f}']
            w.writerow(row); n += 1
            if r["Ref"] in ("U1", "U2", "U3"):
                sockets.append([r["Ref"] + "A"] + row[1:])
        for row in sockets:
            w.writerow(row); n += 1
    bom_refs = set()
    for r in csv.DictReader(open(os.path.join(O, "assembly", "BOM_jlcpcb.csv"))):
        bom_refs |= set(r["Designator"].split(","))
        if not r["LCSC Part #"]:
            print(f"      note: no LCSC number for {r['Comment']} ({r['Designator']}) - JLCPCB will ask")
    cpl_refs = {r["Designator"] for r in csv.DictReader(open(os.path.join(O, "assembly", "CPL_jlcpcb.csv")))}
    if bom_refs != cpl_refs:
        raise SystemExit(f"[verify] FAILED: BOM/CPL designators differ: {bom_refs ^ cpl_refs}")
    print(f"      {n} placements (incl. 3 socket rows); BOM and CPL designators agree")
    import zipfile
    zpath = os.path.join(O, f"{C_PROJECT()}_v{C_VERSION()}_gerbers_JLCPCB.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(g)):
            z.write(os.path.join(g, fn), fn)
    print(f"      JLCPCB upload zip: {os.path.relpath(zpath, ROOT)} ({len(os.listdir(g))} files)")
    print("[verify] OK - F8 comparisons emulated from the netlist; run F8 once in the GUI to confirm")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
