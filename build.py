#!/usr/bin/env python3
"""
Build CV PDFs from YAML data + Jinja2 LaTeX templates.

Usage:
    python3 build.py           # builds all versions (full, exec, ats)
    python3 build.py --full    # full CV only
    python3 build.py --exec    # executive CV only (3 pages max)
    python3 build.py --ats     # ATS-friendly one-page CV
    python3 build.py --style simple  # use sans-serif style variant

Requirements:
    pip3 install pyyaml jinja2 pypdf
    macOS/Linux: xelatex (MacTeX / TeX Live)
    Windows: tectonic (via Scoop: scoop install tectonic)
"""

import argparse
import datetime
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from pypdf import PdfReader, PdfWriter

ROOT       = Path(__file__).parent.resolve()
DATA_DIR   = ROOT / "data"
TMPL_DIR   = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"
FONTS_DIR  = ROOT / "fonts"

_MESES_ES = {
    "01": "enero",    "02": "febrero",   "03": "marzo",
    "04": "abril",    "05": "mayo",      "06": "junio",
    "07": "julio",    "08": "agosto",    "09": "septiembre",
    "10": "octubre",  "11": "noviembre", "12": "diciembre",
}


# ── Data ─────────────────────────────────────────────────────────────────────

def load_data() -> dict:
    data = {}
    for f in sorted(DATA_DIR.glob("*.yaml")):
        with open(f, encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
            if content is None:
                print(f"  ⚠  {f.name} está vacío, se omite", file=sys.stderr)
                continue
            data[f.stem] = content
    return data


def base_context(data: dict) -> dict:
    ctx = dict(data)
    # publicaciones.yaml is a dict {publicaciones: [], congresos: []}
    # rename to avoid collision with the key name
    ctx["pub"] = data.get("publicaciones", {})
    del ctx["publicaciones"]
    hoy = datetime.date.today()
    mes = _MESES_ES[hoy.strftime("%m")].capitalize()
    ctx["fecha_generacion"] = f"{mes} {hoy.year}"
    ctx["fonts_dir"] = str(FONTS_DIR)
    return ctx


# ── Jinja2 ───────────────────────────────────────────────────────────────────
# Use [[ ]] and [% %] so LaTeX braces { } are never ambiguous

def _latex_escape(text) -> str:
    """Escape LaTeX special characters in plain-text YAML values."""
    if not isinstance(text, str):
        return str(text)
    # backslash first, before we add more backslashes
    text = text.replace("\\", r"\textbackslash{}")
    text = text.replace("&",  r"\&")
    text = text.replace("%",  r"\%")
    text = text.replace("$",  r"\$")
    text = text.replace("#",  r"\#")
    text = text.replace("_",  r"\_")
    text = text.replace("{",  r"\{")
    text = text.replace("}",  r"\}")
    text = text.replace("~",  r"\textasciitilde{}")
    text = text.replace("^",  r"\textasciicircum{}")
    return text


def _format_date(value) -> str:
    """Convert date strings to Spanish human-readable format.

    Handles: YYYY-MM → 'mes YYYY', YYYY → 'YYYY'. Passes everything else through.
    """
    if not isinstance(value, str):
        return str(value)
    v = value.strip()
    # YYYY-MM → "mes YYYY"
    m = re.match(r"^(\d{4})-(\d{2})$", v)
    if m:
        return f"{_MESES_ES.get(m.group(2), m.group(2)).capitalize()} {m.group(1)}"
    # YYYY solo → pass through (ya es legible)
    if re.match(r"^\d{4}$", v):
        return v
    return value


def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TMPL_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        variable_start_string="[[",
        variable_end_string="]]",
        block_start_string="[%",
        block_end_string="%]",
        comment_start_string="[#",
        comment_end_string="#]",
    )
    env.filters["e"]    = _latex_escape  # [[ value | e ]]
    env.filters["date"] = _format_date   # [[ value | date ]]
    return env


# ── LaTeX compilation ─────────────────────────────────────────────────────────

def compile_latex(tex: str, output_pdf: Path):
    OUTPUT_DIR.mkdir(exist_ok=True)
    is_windows = platform.system() == "Windows"

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "cv.tex"
        src.write_text(tex, encoding="utf-8")

        if is_windows:
            # Windows: use Tectonic (handles passes automatically)
            cmd = ["tectonic", str(src), "--outdir", tmp]
            r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if r.returncode != 0:
                print("\n❌ Tectonic error:", r.stderr, file=sys.stderr)
                sys.exit(1)
        else:
            # macOS/Linux: use xelatex (2 passes)
            cmd = [
                "xelatex", "-interaction=nonstopmode",
                "-output-directory", tmp, str(src),
            ]
            for _ in range(2):
                r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                errors = [l for l in r.stdout.splitlines() if l.startswith("!")]
                print("\n".join(errors) or r.stdout[-3000:], file=sys.stderr)
                sys.exit(1)

        shutil.copy(Path(tmp) / "cv.pdf", output_pdf)
    print(f"  ✓  {output_pdf.name}")


def enforce_page_limit(pdf_path: Path, max_pages: int):
    """Trim pdf_path in-place to at most max_pages pages. Warns if trimmed."""
    reader = PdfReader(str(pdf_path))
    total = len(reader.pages)
    if total <= max_pages:
        return
    print(
        f"  ⚠  {pdf_path.name} has {total} pages — trimming to {max_pages} "
        f"(remove content or reduce font size to fit naturally).",
        file=sys.stderr,
    )
    writer = PdfWriter()
    for page in reader.pages[:max_pages]:
        writer.add_page(page)
    with open(pdf_path, "wb") as fh:
        writer.write(fh)
    print(f"  ✓  {pdf_path.name} trimmed to {max_pages} pages.")


# ── Builders ──────────────────────────────────────────────────────────────────

def _style_suffix(style: str) -> str:
    """Returns filename suffix for non-default styles: '' or '-deedy' etc."""
    return "" if style == "default" else f"-{style}"


def build_full(data: dict, style: str = "default"):
    suffix = _style_suffix(style)
    print(f"Building cv-full{suffix}.pdf … (style: {style})")
    ctx = base_context(data)
    ctx["style"] = style
    tex = make_env().get_template("cv-full.tex.j2").render(**ctx)
    compile_latex(tex, OUTPUT_DIR / f"cv-full{suffix}.pdf")


def build_exec(data: dict, style: str = "default"):
    suffix = _style_suffix(style)
    print(f"Building cv-exec{suffix}.pdf … (style: {style})")
    ctx = base_context(data)
    ctx["style"] = style
    exp = ctx.get("experiencia", [])
    ctx["exp_reciente"]  = [e for e in exp if e.get("incluir_exec")]
    ctx["exp_anterior"]  = [e for e in exp if not e.get("incluir_exec")]
    ctx["cursos_exec"]   = [c for c in ctx.get("cursos", []) if c.get("incluir_exec")]
    tex = make_env().get_template("cv-exec.tex.j2").render(**ctx)
    out = OUTPUT_DIR / f"cv-exec{suffix}.pdf"
    compile_latex(tex, out)
    enforce_page_limit(out, max_pages=3)




def build_ats(data: dict, style: str = "simple"):
    """Build ATS-friendly one-page CV (single column, plain text separators, full URLs).

    Uses simple style by default for maximum ATS compatibility (no colors or special styling).
    """
    # Force simple style for ATS (adaptive's tcolorbox breaks ATS parsing)
    style_arg = style if style in ["simple", "default", "jake"] else "simple"
    suffix = _style_suffix(style_arg)
    print(f"Building cv-ats{suffix}.pdf … (style: {style_arg})")
    ctx = base_context(data)
    ctx["style"] = style_arg
    exp = ctx.get("experiencia", [])
    ctx["exp_reciente"]  = [e for e in exp if e.get("incluir_exec")]
    ctx["exp_anterior"]  = [e for e in exp if not e.get("incluir_exec")]
    tex = make_env().get_template("cv-ats.tex.j2").render(**ctx)
    compile_latex(tex, OUTPUT_DIR / f"cv-ats{suffix}.pdf")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full",    action="store_true")
    ap.add_argument("--exec",    action="store_true")
    ap.add_argument("--ats",     action="store_true",
                    help="ATS-friendly one-page layout (single column, plain text)")
    ap.add_argument(
        "--style",
        default="default",
        choices=["default", "simple"],
        help="Visual style variant (default: serif, simple: sans-serif). "
             "Output filenames: cv-full.pdf (default), cv-full-simple.pdf, etc.",
    )
    args = ap.parse_args()
    if not args.full and not args.exec and not args.ats:
        args.full = args.exec = args.ats = True

    data = load_data()
    if args.full: build_full(data, args.style)
    if args.exec: build_exec(data, args.style)
    if args.ats:  build_ats(data, args.style)
    print("Done.")

if __name__ == "__main__":
    main()
