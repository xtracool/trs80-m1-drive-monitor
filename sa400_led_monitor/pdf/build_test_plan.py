"""
build_test_plan.py — docs/TEST_PLAN.md -> trs80-m1-drive-monitor_test_plan_v<ver>.pdf (LuaLaTeX via pandoc).

The board drawing in the plan is the FROZEN docs/img/board_populated_v<BOARD_REV>.pdf of the boards in hand
(BOARD_REV below). gen/render_populated.py draws the current design (config.VERSION), which may be a newer
revision; it is only re-run here when --render is given and config.VERSION == BOARD_REV.

Steps:
  1. (--render only) gen/render_populated.py -> docs/img/board_populated_v<ver>.png/.pdf
  1b. lualatex pdf/schematic.tex and pdf/fixtures.tex -> docs/img/*.pdf (+ .png via pdftoppm for the Markdown)
  2. pandoc TEST_PLAN.md -> standalone .tex (DejaVu Sans, footer on every page:
     document name, version, created/updated date, Page X of Y); color_spans.lua turns the
     Markdown <span style="color:#rrggbb"> markup into \textcolor (red = caution / correction,
     blue = new in this revision)
  3. patch the .tex: vector PDF figures instead of the PNGs; Appendix A (board), B (schematic) and
     C (parts list) and D (fixtures) each start on a right-hand page (twoside + cleardoublepage, blank
     versos say so) so A.1, A.2, B and C have nothing on their backs; E (cable, landscape) is the back of D;
     the record sheets become full grids (boxed cells, tall rows) for writing readings in by hand
  4. lualatex x3 (LastPage needs the extra passes)

Usage (from the project root, needs pandoc + LuaLaTeX with fontspec/fancyhdr/lastpage):
    python pdf/build_test_plan.py              -> pdf/trs80-m1-drive-monitor_test_plan_v<VERSION>.pdf
    python pdf/build_test_plan.py --keep-tex   -> also leaves the .tex beside it
    python pdf/build_test_plan.py --render     -> re-draw the board first (only if the design is still BOARD_REV)

Exit codes: 0 ok, 1 error, 130 interrupted (Ctrl-C).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

VERSION = "1.8"
BOARD_REV = "0.2.3"      # the boards the plan is written for; the frozen drawing docs/img/board_populated_v0.2.3.*
CREATED = "2026-10-19"
UPDATED = "2026-10-19"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
NAME = f"trs80-m1-drive-monitor_test_plan_v{VERSION}"

HEADER = r"""
\usepackage{xcolor}
\usepackage{float}
\floatplacement{figure}{H}
\usepackage{pdflscape}
% blank verso pages (double-sided printing) carry a note instead of nothing
\makeatletter
\renewcommand{\cleardoublepage}{\clearpage\if@twoside\ifodd\c@page\else
  \null\vfill{\centering\small\textit{This page is intentionally blank (double-sided printing).}\par}\vfill\newpage\fi\fi}
\makeatother
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage{etoolbox}
\newcommand{\tpfoot}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0.4pt}%
\fancyfoot[L]{\scriptsize trs80-m1-drive-monitor · TEST\_PLAN · Version VER}%
\fancyfoot[R]{\scriptsize Created CRE · Updated UPD · Page \thepage\ of \pageref*{LastPage}}}
\pagestyle{fancy}\tpfoot
\fancypagestyle{plain}{\tpfoot}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{Shaded}{\footnotesize}
\setlength{\LTpre}{6pt}\setlength{\LTpost}{6pt}
\renewcommand{\arraystretch}{1.25}
""".replace("VER", VERSION).replace("CRE", CREATED).replace("UPD", UPDATED)


def grid_record_sheets(s):
    """Section 5 tables -> full grids (every cell boxed) so readings can be written in by hand.
    pandoc emits booktabs longtables; here, between '5. Record sheets' and '6. TODO', the column spec
    becomes |p|c|c|c|c|c| and every row gets a \\hline."""
    a = s.index("5. Record sheets")
    b = s.index("6. TODO", a)
    region = s[a:b]
    spec = ("\\begin{longtable}[]{|>{\\raggedright\\arraybackslash}p{0.40\\linewidth}|"
            "*{5}{>{\\centering\\arraybackslash}p{0.085\\linewidth}|}}")
    region = re.sub(r"\\begin\{longtable\}\[\]\{@\{\}.*?@\{\}\}", lambda m: spec, region, flags=re.S)
    region = re.sub(r"\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright\n(.*?)\n\\end\{minipage\}",
                    lambda m: "\\textbf{" + m.group(1) + "}", region, flags=re.S)
    region = region.replace("\\toprule\\noalign{}", "\\hline").replace("\\midrule\\noalign{}", "\\hline")
    region = region.replace("\\bottomrule\\noalign{}", "")
    out = []
    for table in region.split("\\endlastfoot"):
        if "\\end{longtable}" in table:
            body, rest = table.split("\\end{longtable}", 1)
            body = re.sub(r"\\\\\n", lambda m: "\\\\ \\hline\n", body)
            table = body + "\\end{longtable}" + rest
        out.append(table)
    region = "\\endlastfoot".join(out)
    return s[:a] + region + s[b:]


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-tex", action="store_true")
    ap.add_argument("--render", action="store_true", help="re-draw the board with gen/render_populated.py")
    args = ap.parse_args()

    img = os.path.join(DOCS, "img")
    os.makedirs(img, exist_ok=True)
    frozen = os.path.join(img, f"board_populated_v{BOARD_REV}.pdf")
    if args.render:
        sys.path.insert(0, os.path.join(ROOT, "gen"))
        import config  # noqa: E402  (the design's single source of truth)
        if config.VERSION != BOARD_REV:
            raise RuntimeError(f"design is v{config.VERSION}, the plan covers the v{BOARD_REV} boards: "
                               f"keeping the frozen drawing {os.path.basename(frozen)} (drop --render)")
        run([sys.executable, os.path.join(ROOT, "gen", "render_populated.py"), "--out", img], ROOT)
    if not os.path.exists(frozen):
        raise RuntimeError(f"missing {frozen}; run with --render on a v{BOARD_REV} checkout")
    for drawing in ("schematic", "fixtures"):
        run(["lualatex", "-interaction=nonstopmode", drawing + ".tex"], HERE)
        shutil.move(os.path.join(HERE, drawing + ".pdf"), os.path.join(img, drawing + ".pdf"))
        for ext in (".aux", ".log"):
            f = os.path.join(HERE, drawing + ext)
            if os.path.exists(f):
                os.remove(f)
        if shutil.which("pdftoppm"):   # PNG for the Markdown view; optional
            subprocess.run(["pdftoppm", "-r", "200", "-png", "-singlefile", os.path.join(img, drawing + ".pdf"),
                            os.path.join(img, drawing)], capture_output=True)

    hdr = os.path.join(HERE, "_test_plan_hdr.tex")
    open(hdr, "w", encoding="utf-8").write(HEADER)
    tex = os.path.join(DOCS, NAME + ".tex")
    run(["pandoc", "TEST_PLAN.md", "-s", "-o", tex, "--pdf-engine=lualatex", "-H", hdr,
         "--lua-filter", os.path.join(HERE, "color_spans.lua"),
         "-V", "classoption=twoside", "-V", "geometry:margin=0.7in", "-V", "geometry:footskip=0.4in",
         "-V", "mainfont=DejaVu Sans", "-V", "sansfont=DejaVu Sans", "-V", "monofont=DejaVu Sans Mono",
         "-V", "fontsize=10pt", "-V", "colorlinks=true", "-V", "linkcolor=blue", "-V", "urlcolor=blue",
         "--columns=60"], DOCS)

    s = open(tex, encoding="utf-8").read()
    s = s.replace(f"img/board_populated_v{BOARD_REV}.png", f"img/board_populated_v{BOARD_REV}.pdf")
    s = s.replace("img/schematic.png", "img/schematic.pdf")
    s = s.replace("img/fixtures.png", "img/fixtures.pdf")
    s = re.sub(r"\\includegraphics\[[^\]]*\]\{(img/board_populated_v[\d.]+\.pdf)\}",
               r"\\includegraphics[width=\\textwidth,height=0.84\\textheight,keepaspectratio]{\1}", s)
    s = re.sub(r"\\includegraphics\[[^\]]*\]\{(img/(?:schematic|fixtures)\.pdf)\}",
               r"\\includegraphics[width=\\textwidth,height=0.885\\textheight,keepaspectratio]{\1}", s)

    def before_heading(text, title, insert):
        k = text.index(title)
        k = text.rfind("\\hypertarget", 0, k)
        return text[:k] + insert + "\n" + text[k:]

    s = before_heading(s, "0.7 Design-review findings", "\\clearpage")
    s = before_heading(s, "Phase 1 --- Unpowered", "\\clearpage")
    s = before_heading(s, "5. Record sheets", "\\clearpage\\renewcommand{\\arraystretch}{2.3}")
    s = grid_record_sheets(s)
    s = before_heading(s, "6. TODO", "\\renewcommand{\\arraystretch}{1.25}")
    s = before_heading(s, "Appendix A ---", "\\cleardoublepage")
    s = before_heading(s, "A.2 Legend for", "\\cleardoublepage")
    s = before_heading(s, "Appendix B ---", "\\cleardoublepage")
    s = before_heading(s, "Appendix C ---", "\\cleardoublepage")
    s = before_heading(s, "Appendix D ---", "\\cleardoublepage")
    s = before_heading(s, "Appendix E ---", "\\clearpage\\begin{landscape}")   # wide, short drawing; shares D's sheet
    s = before_heading(s, "Appendix F ---", "\\end{landscape}\\clearpage")           # E's landscape ends before F
    s = re.sub(r"\\includegraphics\[[^\]]*\]\{(\.\./output/cable\.png)\}",
               r"\\includegraphics[width=\\linewidth]{\1}", s)
    open(tex, "w", encoding="utf-8").write(s)

    for _ in range(3):
        subprocess.run(["lualatex", "-interaction=nonstopmode", os.path.basename(tex)], cwd=DOCS,
                       capture_output=True, text=True)
    pdf = os.path.join(DOCS, NAME + ".pdf")
    if not os.path.exists(pdf):
        raise RuntimeError(f"no PDF produced, see {NAME}.log")
    errs = [l for l in open(os.path.join(DOCS, NAME + ".log"), encoding="utf-8", errors="replace") if l.startswith("!")]
    if errs:
        raise RuntimeError("LaTeX errors:\n" + "".join(errs[:10]))

    out = os.path.join(HERE, NAME + ".pdf")
    shutil.move(pdf, out)
    keep = {".tex"} if args.keep_tex else set()
    for ext in (".aux", ".log", ".out", ".tex"):
        f = os.path.join(DOCS, NAME + ext)
        if os.path.exists(f):
            if ext in keep:
                shutil.move(f, os.path.join(HERE, NAME + ext))
            else:
                os.remove(f)
    os.remove(hdr)
    print(f"[build_test_plan] wrote {out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[build_test_plan] interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[build_test_plan] FAILED: {e}", file=sys.stderr)
        sys.exit(1)
