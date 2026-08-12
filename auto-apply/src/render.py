"""Render resume.md -> resume.pdf via HTML + WeasyPrint.

Usage: python -m src.render --md applications/prosper/resume.md
"""
import argparse
from pathlib import Path

import markdown

CSS = """
@page { size: letter; margin: 0.6in 0.7in; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #1a1a1a; line-height: 1.35; }
h1 { font-size: 17pt; margin: 0 0 2pt 0; }
h2 { font-size: 11.5pt; border-bottom: 1px solid #444; margin: 12pt 0 4pt 0; text-transform: uppercase; letter-spacing: 0.5px; }
h3 { font-size: 10.5pt; margin: 8pt 0 1pt 0; }
ul { margin: 2pt 0 6pt 0; padding-left: 14pt; }
li { margin-bottom: 2pt; }
p { margin: 2pt 0; }
"""

def render(md_path: str) -> str:
    from weasyprint import HTML
    md_file = Path(md_path)
    html_body = markdown.markdown(md_file.read_text(), extensions=["tables"])
    html = f"<html><head><style>{CSS}</style></head><body>{html_body}</body></html>"
    pdf_path = md_file.with_suffix(".pdf")
    HTML(string=html).write_pdf(str(pdf_path))
    return str(pdf_path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--md", required=True)
    print("Wrote", render(p.parse_args().md))
