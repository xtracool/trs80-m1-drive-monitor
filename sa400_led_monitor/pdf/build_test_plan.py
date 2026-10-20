"""
build_test_plan.py — docs/TEST_PLAN.md -> sa400_led_monitor_test_plan_v<ver>.pdf (LuaLaTeX via pandoc).

Steps:
  1. gen/render_populated.py  -> docs/img/board_populated.png/.pdf (wireframe board drawing)
  1b. lualatex pdf/schematic.tex and pdf/fixtures.tex -> docs/img/*.pdf (+ .png via pdftoppm for the Markdown)
  2. pandoc TEST_PLAN.md -> standalone .tex (DejaVu Sans, footer on every page:
     document name, version, created/updated date, Page X of Y); color_spans.lua turns the
     Markdown <span style="color:#rrggbb"> markup into \textcolor (red = caution / correction,
     blue = new in this revision)
  3. patch the .tex: vector PDF figures instead of the PNGs; Appendix A (board), B (schematic) and
     C (parts list), D (fixtures) and E (cable, landscape page) each start on a right-hand page
     (twoside + cleardoublepage, blank versos say so); taller rows on the record sheets
  4. lualatex x3 (LastPage needs the extra passes)

Usage (from the project root, needs pandoc + LuaLaTeX with fontspec/fancyhdr/lastpage):
    python pdf/build_test_plan.py              -> pdf/sa400_led_monitor_test_plan_v1.1.pdf
    python pdf/build_test_plan.py --keep-tex   -> also leaves the .tex beside it

Exit codes: 0 ok, 1 error, 130 interrupted (Ctrl-C).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

VERSION = "1.4"
CREATED = "2026-10-19"
UPDATED = "2026-10-19"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
NAME = f"sa400_led_monitor_test_plan_v{VERSION}"

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
\fancyfoot[L]{\footnotesize TEST\_PLAN --- SA400 LED Monitor Test Plan · Version VER}%
\fancyfoot[R]{\footnotesize Created CRE · Updated UPD · Page \thepage\ of \pageref*{LastPage}}}
\pagestyle{fancy}\tpfoot
\fancypagestyle{plain}{\tpfoot}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{Shaded}{\footnotesize}
\setlength{\LTpre}{6pt}\setlength{\LTpost}{6pt}
\renewcommand{\arraystretch}{1.25}
""".replace("VER", VERSION).replace("CRE", CREATED).replace("UPD", UPDATED)


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-tex", action="store_true")
    args = ap.parse_args()

    run([sys.executable, os.path.join(ROOT, "gen", "render_populated.py"), "--out", os.path.join(DOCS, "img")], ROOT)
    img = os.path.join(DOCS, "img")
    os.makedirs(img, exist_ok=True)
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
    s = s.replace("img/board_populated.png", "img/board_populated.pdf")
    s = s.replace("img/schematic.png", "img/schematic.pdf")
    s = s.replace("img/fixtures.png", "img/fixtures.pdf")
    s = re.sub(r"\\includegraphics\[[^\]]*\]\{(img/board_populated\.pdf)\}",
               r"\\includegraphics[width=\\textwidth,height=0.84\\textheight,keepaspectratio]{\1}", s)
    s = re.sub(r"\\includegraphics\[[^\]]*\]\{(img/(?:schematic|fixtures)\.pdf)\}",
               r"\\includegraphics[width=\\textwidth,height=0.885\\textheight,keepaspectratio]{\1}", s)

    def before_heading(text, title, insert):
        k = text.index(title)
        k = text.rfind("\\hypertarget", 0, k)
        return text[:k] + insert + "\n" + text[k:]

    s = before_heading(s, "0.7 Design-review findings", "\\clearpage")
    s = before_heading(s, "Phase 1 --- Unpowered", "\\clearpage")
    s = before_heading(s, "5. Record sheets", "\\clearpage\\renewcommand{\\arraystretch}{2.1}")
    s = before_heading(s, "6. TODO", "\\renewcommand{\\arraystretch}{1.25}")
    s = before_heading(s, "Appendix A ---", "\\cleardoublepage")
    s = before_heading(s, "A.2 Legend for", "\\cleardoublepage")
    s = before_heading(s, "Appendix B ---", "\\cleardoublepage")
    s = before_heading(s, "Appendix C ---", "\\cleardoublepage")
    s = before_heading(s, "Appendix D ---", "\\cleardoublepage")
    s = before_heading(s, "Appendix E ---", "\\cleardoublepage\\begin{landscape}")   # wide, short drawing
    s = s.replace("\\end{document}", "\\end{landscape}\n\\end{document}")
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
