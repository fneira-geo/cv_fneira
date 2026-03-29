#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Remove generated PDF files from output/.

Usage:
    uv run python3 clean.py
"""
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"

def main():
    pdfs = sorted(OUTPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print("output/ already clean.")
        return
    for pdf in pdfs:
        pdf.unlink()
        print(f"  deleted  {pdf.name}")
    print(f"\n{len(pdfs)} file(s) removed.")

if __name__ == "__main__":
    main()
