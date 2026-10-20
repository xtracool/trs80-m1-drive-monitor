#!/usr/bin/env python3
"""
Build the design PDF from pdf/template.tex.

Single sources of truth pulled in at build time:
  * gen/config.py     -> VERSION (document name, footer, title)
  * docs/CHANGELOG.md -> Changelog section
  * docs/TODO.md      -> To-do section
Images are copied from output/.  Run:  python3 pdf/build_pdf.py
Exit: 0 ok, 1 LaTeX failure, 130 interrupted.
"""
import datetime, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import config as C  # noqa: E402

PDFDIR = os.path.join(ROOT, "pdf")
OUT = os.path.join(ROOT, "output")
IMAGES = ["placement.png", "cable.png", "board_top_kicad.png", "render_top.png", "render_bottom.png",
          "copper_top.png", "copper_bottom.png", "net_gnd.png", "net_5v.png", "net_5v_in.png",
          "j1_vs_photo.png", "j1_root_holes.png", "j2_labels.png", "sa400_led_monitor_schematic.pdf"]


def esc(s: str) -> str:
    """Markdown inline -> LaTeX."""
    s = s.replace("\\", "\\textbackslash{}")
    for a, b in (("&", "\\&"), ("%", "\\%"), ("#", "\\#"), ("$", "\\$")):
        s = s.replace(a, b)
    s = re.sub(r"`([^`]*)`", lambda m: "\\texttt{" + m.group(1).replace("_", "\\_") + "}", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", s)
    s = re.sub(r"(?<!\\)_", "\\_", s)   # underscores outside \texttt
    s = s.replace("\\texttt{", "\\texttt{").replace("\\_\\_", "\\_")
    for a, b in (("→", "$\\to$"), ("≤", "$\\le$"), ("≥", "$\\ge$"), ("×", "$\\times$"), ("Ω", "$\\Omega$"),
                 ("µ", "$\\mu$"), ("≈", "$\\approx$"), ("°", "$^\\circ$"), ("↔", "$\\leftrightarrow$")):
        s = s.replace(a, b)
    return s


def changelog_tex(md: str) -> str:
    """'## heading' -> paragraph; free text stays prose; '- ' lines become an itemize."""
    out, in_list = [], False

    def close():
        nonlocal in_list
        if in_list:
            out.append("\\end{itemize}"); in_list = False
    for line in md.splitlines():
        if line.startswith("## "):
            close(); out.append("\\paragraph{" + esc(line[3:].strip()) + "}")
        elif line.startswith("- "):
            if not in_list:
                out.append("\\begin{itemize}[leftmargin=8mm]"); in_list = True
            out.append("\\item " + esc(line[2:].strip()))
        elif line.startswith("  ") and in_list and out[-1].startswith("\\item"):
            out[-1] += " " + esc(line.strip())
        elif line.strip() and not line.startswith("#"):
            close(); out.append(esc(line.strip()) + "\n")
    close()
    return "\n".join(out)


def todo_tex(md: str) -> str:
    out = []
    open_list = False
    for line in md.splitlines():
        if line.startswith("## "):
            if open_list:
                out.append("\\end{itemize}"); open_list = False
            out.append("\\subsection*{" + esc(line[3:].strip()) + "}")
        elif line.startswith("- ["):
            if not open_list:
                out.append("\\begin{itemize}[leftmargin=8mm]"); open_list = True
            box = "$\\boxtimes$" if line[3].lower() == "x" else "$\\square$"
            out.append("\\item[" + box + "] " + esc(line[5:].strip()))
    if open_list:
        out.append("\\end{itemize}")
    return "\n".join(out)


def main() -> int:
    ver = C.VERSION
    name = f"sa400_led_monitor_design_v{ver}"
    tpl = open(os.path.join(PDFDIR, "template.tex")).read()
    changelog = open(os.path.join(ROOT, "docs", "CHANGELOG.md")).read()
    m = re.search(r"^## v\S+ — (\d{4}-\d{2}-\d{2})", changelog, re.M)
    updated = m.group(1) if m else datetime.date.today().isoformat()   # "Updated" = newest changelog entry
    tex = (tpl.replace("%%VERSION%%", ver).replace("%%DATE%%", updated)
              .replace("%%CHANGELOG%%", changelog_tex(open(os.path.join(ROOT, "docs", "CHANGELOG.md")).read()))
              .replace("%%TODO%%", todo_tex(open(os.path.join(ROOT, "docs", "TODO.md")).read())))
    for old in os.listdir(PDFDIR):
        if old.startswith("sa400_led_monitor_design_v") and old.endswith((".tex", ".pdf")):
            os.remove(os.path.join(PDFDIR, old))
    open(os.path.join(PDFDIR, name + ".tex"), "w").write(tex)
    for img in IMAGES:
        src = os.path.join(OUT, img)
        if os.path.exists(src):
            shutil.copy(src, PDFDIR)
    for _ in range(3):
        r = subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"],
                           cwd=PDFDIR, capture_output=True, text=True)
        if r.returncode != 0:
            log = r.stdout
            i = log.find("\n! ")
            print(log[i:i + 800] if i >= 0 else log[-800:])
            return 1
    for ext in (".aux", ".log", ".out", ".toc"):
        p = os.path.join(PDFDIR, name + ext)
        if os.path.exists(p):
            os.remove(p)
    print(f"[pdf] {name}.pdf")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
