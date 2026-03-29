#!/usr/bin/env python3
"""
Download Google Fonts (TTF) for the CV style system.
Run once: uv run python3 download_fonts.py

Fonts are saved to fonts/<Family>/<Family>-{Regular,Bold,Italic,BoldItalic}.ttf
"""
import re
import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "fonts"

FAMILIES = {
    "Inter":             "Inter",
    "Jost":              "Jost",
    "Lato":              "Lato",
    "Cormorant+Garamond": "CormorantGaramond",
    "Source+Sans+3":     "SourceSans3",
}

# Google Fonts CSS2 API — omitting User-Agent returns TTF (not woff2)
CSS_URL = "https://fonts.googleapis.com/css2?family={family}:ital,wght@0,400;0,700;1,400;1,700"

# Order in the CSS response: italic-400, italic-700, normal-400, normal-700
VARIANTS = ["Italic", "BoldItalic", "Regular", "Bold"]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as r:
        return r.read()


def main():
    FONTS_DIR.mkdir(exist_ok=True)
    for family_param, dir_name in FAMILIES.items():
        print(f"\n{dir_name}")
        out_dir = FONTS_DIR / dir_name
        out_dir.mkdir(exist_ok=True)

        css = fetch(CSS_URL.format(family=family_param)).decode()
        ttf_urls = re.findall(r"https://fonts\.gstatic\.com[^\)]+\.ttf", css)

        if len(ttf_urls) < 4:
            print(f"  ⚠  Only {len(ttf_urls)} TTF URLs found, expected 4")
            continue

        for url, variant in zip(ttf_urls, VARIANTS):
            filename = f"{dir_name}-{variant}.ttf"
            dest = out_dir / filename
            data = fetch(url)
            dest.write_bytes(data)
            print(f"  ✓  {filename}  ({len(data)//1024} KB)")


if __name__ == "__main__":
    main()
