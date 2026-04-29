# CV Fneira Project

CV generation tool for creating multiple variants (full, executive, ATS) in PDF and DOCX formats.

## Local Environment

This project uses **uv** for dependency management. All Python code must run through the uv environment.

**Requirements:**
- Python 3.12+
- uv (installed and available in PATH)

**Dependencies:**
- `jinja2` - template rendering
- `pypdf` - PDF manipulation
- `python-docx` - DOCX file generation
- `pyyaml` - YAML parsing
- `watchfiles` - (dev) file watching

## Commands

Use `make` or `uv run` directly:

```bash
# Build all CV variants (full, exec, ats)
make all

# Build individual variants
make full    # Full CV
make exec    # Executive summary
make ats     # ATS-optimized

# Build sans-serif variants
make simple

# Build DOCX templates
make template-docx

# Run scripts directly with uv
uv run python build.py --full
uv run python build.py --exec
uv run python build.py --ats
```

## Instructions for Claude

1. **Always use `uv run` for Python scripts**: Never run `python build.py` directly. Use `uv run python build.py [args]`.
2. **Use `make` for common tasks**: When running standard CV builds, prefer `make [target]` over individual commands.
3. **Run in this directory**: All commands assume execution in the project root (`h:\PORTFOLIO\cv_fneira`).
4. **Output directory**: Generated PDFs/DOCXs go to `output/`.

## Project Structure

```
.
├── build.py                 # Main CV builder script
├── build_template_docx.py   # DOCX template builder
├── build_template_docx_bonito.py
├── Makefile                 # Make targets for common builds
├── pyproject.toml           # Project metadata & dependencies
├── uv.lock                  # Locked dependency versions
├── output/                  # Generated CV files
├── template_ciren/          # CV templates
└── data/                    # CV content data
```

## Notes

- All builds generate both simple (sans-serif) and standard variants
- Output files follow naming pattern: `cv-{type}-{simple|standard}.pdf`
- Keep uv.lock in sync when adding dependencies

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
