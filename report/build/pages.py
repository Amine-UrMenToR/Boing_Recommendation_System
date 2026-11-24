"""Render the pages of a PDF to PNG files so they can be looked at.

    py pages.py REPORT.pdf OUTDIR [--dpi 110] [--pages 1-3,6] [--sheet]

Writes OUTDIR/page-01.png, page-02.png, ... and, with --sheet, OUTDIR/sheet.png (all pages side by side,
small, with page numbers) for a quick overview. Prints the page count.
"""
import argparse
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


def parse_pages(spec, n):
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            a, b = int(a or 1), int(b or n)
        else:
            a = b = int(part)
        for i in range(a, b + 1):
            if 1 <= i <= n and i - 1 not in out:
                out.append(i - 1)
    return out


def contact_sheet(images, numbers, cols=4, width=420):
    thumbs = []
    for im in images:
        h = round(im.height * width / im.width)
        thumbs.append(im.resize((width, h), Image.LANCZOS))
    rows = (len(thumbs) + cols - 1) // cols
    cell_h = max(t.height for t in thumbs) + 28
    sheet = Image.new('RGB', (cols * (width + 16) + 16, rows * cell_h + 16), (200, 200, 200))
    draw = ImageDraw.Draw(sheet)
    for k, (t, num) in enumerate(zip(thumbs, numbers)):
        x = 16 + (k % cols) * (width + 16)
        y = 16 + (k // cols) * cell_h
        sheet.paste(t, (x, y))
        draw.text((x + 4, y + t.height + 4), f'page {num}', fill=(0, 0, 0))
    return sheet


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf')
    ap.add_argument('outdir')
    ap.add_argument('--dpi', type=float, default=110, help='resolution (default 110)')
    ap.add_argument('--pages', default='', help='pages to render, e.g. 1-3,6 (default: all)')
    ap.add_argument('--sheet', action='store_true', help='also write sheet.png with every rendered page')
    a = ap.parse_args()

    src = Path(a.pdf)
    if not src.is_file():
        sys.exit(f'pages: no such file: {src}')
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    pdf = pdfium.PdfDocument(str(src))
    try:
        n = len(pdf)
        chosen = parse_pages(a.pages, n)
        images = []
        for i in chosen:
            page = pdf[i]
            try:
                bitmap = page.render(scale=a.dpi / 72)
                im = bitmap.to_pil().convert('RGB')
            finally:
                page.close()
            path = out / f'page-{i + 1:02d}.png'
            im.save(path)
            images.append(im)
            print('wrote', path)
        if a.sheet and images:
            sp = out / 'sheet.png'
            contact_sheet(images, [i + 1 for i in chosen]).save(sp)
            print('wrote', sp)
    finally:
        pdf.close()
    print(f'pages: {n}')


if __name__ == '__main__':
    main()
