"""Validate a handbook PDF, then cut overlapping tiles for visual review.

uv run --no-project --with pymupdf python check.py page.pdf [--help]

Checks source ink and image samples, not rendered pixels: ordinary vector/text
antialiasing is not a tint. Raster images must themselves be bilevel; fractional
alpha, tinted ink and shading are rejected. Fit is checked by render.sh.
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path

import pymupdf

MM = 72 / 25.4
SIZES = {"A4": (210, 297), "Letter": (215.9, 279.4)}
FONT_DEFAULTS = {
    "body": ("Iowan Old Style", "Iowan", "Georgia", "DejaVu Serif", "Liberation Serif", "Times New Roman", "Times"),
    "drawing": ("Routed Gothic", "Routed Gothic Narrow"),
    "checklist": ("Letter Gothic Code",),
}
SYMBOL_FONTS = ("Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans")
FALLBACK_CHARS = set("1≤−≈")


def font_family(name):
    """Ignore PDF subset tags, separators and style suffixes, not family names."""
    name = re.sub(r"^[A-Z]{6}\+", "", name)
    name = re.sub(r"[-_ ](?:R|B|I|BI)$", "", name)
    name = re.sub(r"[^a-z0-9]", "", name.lower())
    return re.sub(r"(?:(?:regular|roman|bold|italic|oblique|psmt|mt))+$", "", name)


def page_size(value):
    for name, size in SIZES.items():
        if value.lower() == name.lower():
            return size
    match = re.fullmatch(r"(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)", value.lower())
    if match and all(float(v) > 0 for v in match.groups()):
        return tuple(float(v) for v in match.groups())
    raise argparse.ArgumentTypeError("use A4, Letter or WIDTHxHEIGHT in mm (e.g. 180x240)")


def positive_int(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def is_bw(colour):
    return colour is None or tuple(colour) in (
        (0.0,), (1.0,), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
    )


def image_problems(block):
    pix = pymupdf.Pixmap(block["image"])
    alpha = pix.samples[pix.n - 1::pix.n] if pix.alpha else None
    if block.get("mask"):
        mask = pymupdf.Pixmap(block["mask"])
        alpha = mask.samples
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    if pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    samples = pix.samples
    problems = []
    if alpha and any(v not in (0, 255) for v in alpha):
        problems.append("raster image has fractional transparency")
    for i in range(0, len(samples), 3):
        if alpha is not None and alpha[i // 3] == 0:
            continue
        if samples[i:i + 3] not in (b"\x00\x00\x00", b"\xff\xff\xff"):
            problems.append("raster image uses non-black/white source pixels")
            break
    return problems


def pdf_key(doc, xref, path):
    """Read a nested dictionary key, following indirect dictionaries."""
    prefix = []
    for part in path.split("/"):
        prefix.append(part)
        kind, value = doc.xref_get_key(xref, "/".join(prefix))
        if kind == "xref":
            xref = int(value.split()[0])
            prefix = []
    return ("xref", f"{xref} 0 R") if not prefix else (kind, value)


def transparency_problems(page):
    # Image paint opacity is not exposed by get_drawings/get_image_info.
    # Conservatively inspect graphics-state resources, including nested forms.
    doc = page.parent
    objects = [page.xref] + [item[0] for item in page.get_xobjects()]
    problems = []
    for xref in objects:
        while pdf_key(doc, xref, "Resources")[0] == "null":
            kind, parent = doc.xref_get_key(xref, "Parent")
            if kind != "xref":
                break
            xref = int(parent.split()[0])
        kind, value = pdf_key(doc, xref, "Resources/ExtGState")
        pending = [value] if kind != "null" else []
        seen = set()
        while pending:
            source = pending.pop()
            for ref in re.findall(r"(\d+)\s+\d+\s+R\b", source):
                ref = int(ref)
                if ref not in seen:
                    seen.add(ref)
                    pending.append(doc.xref_object(ref))
            if any(float(v) not in (0, 1) for v in re.findall(r"/(?:ca|CA)\s+([+-]?(?:\d*\.\d+|\d+))", source)):
                problems.append("graphics state has fractional opacity (including image paint)")
            if re.search(r"/SMask\s+(?!/None\b)", source):
                problems.append("graphics state uses a soft mask")
            for mode in re.findall(r"/BM\s*(/\w+|\[[^]]*\])", source):
                if mode not in ("/Normal", "[/Normal]", "[ /Normal ]"):
                    problems.append("graphics state uses a non-Normal blend mode")
    return problems


def page_ink_problems(page):
    problems = transparency_problems(page)
    for drawing in page.get_drawings(extended=True):
        if drawing["type"] == "group":
            if drawing.get("opacity", 1) not in (0, 1):
                problems.append("transparency group has fractional opacity")
            if drawing.get("blendmode", "Normal") != "Normal":
                problems.append("transparency group uses a non-Normal blend mode")
        for key, opacity_key in (("fill", "fill_opacity"), ("color", "stroke_opacity")):
            colour = drawing.get(key)
            if colour is None:
                continue
            opacity = drawing.get(opacity_key, 1)
            if opacity == 0:
                continue
            if not is_bw(colour):
                problems.append(f"vector ink uses non-black/white colour {colour}")
            if opacity != 1:
                problems.append(f"vector ink has fractional opacity {opacity:g}")
    for span in page.get_texttrace():
        if span["type"] == 3 or span["opacity"] == 0:  # invisible text
            continue
        if not is_bw(span["color"]):
            problems.append(f"text ink uses non-black/white colour {span['color']}")
        if span["opacity"] != 1:
            problems.append(f"text ink has fractional opacity {span['opacity']:g}")
    for block in page.get_text("dict")["blocks"]:
        if block["type"] == 1:
            problems.extend(image_problems(block))
    if any(kind == "fill-shade" for kind, *_ in page.get_bboxlog()):
        problems.append("shading cannot be certified black/white; replace it with solid ink")
    if list(page.annots() or []):
        problems.append("annotations must be flattened before checking print ink")
    return sorted(set(problems))


def font_problems(doc, expectations):
    """Check fonts actually used for visible text, including text in form XObjects."""
    families = {role: {font_family(n) for n in names} for role, names in expectations.items()}
    symbol_fonts = {font_family(n) for n in SYMBOL_FONTS}
    found = set()
    used = set()
    problems = []
    for page in doc:
        for span in page.get_texttrace():
            if span["type"] == 3 or span["opacity"] == 0:
                continue
            text = "".join(chr(c[0]) for c in span["chars"]).strip()
            if not text:
                continue
            name = span["font"]
            used.add(name)
            family = font_family(name)
            matched = {role for role, names in families.items() if family in names}
            found.update(matched)
            if not matched and not (family in symbol_fonts and set(text) <= FALLBACK_CHARS):
                problems.append(f"unexpected font {name!r} on page {page.number + 1} ({text[:32]!r})")
    for role in expectations.keys() - found:
        problems.append(f"missing {role} font; expected one of: {', '.join(expectations[role])}")
    return sorted(used), sorted(set(problems))


def check_document(doc, *, pages=1, size=SIZES["A4"], expectations=None):
    if expectations is None:
        expectations = FONT_DEFAULTS
    problems = []
    print(f"pages: {doc.page_count}")
    if doc.page_count != pages:
        problems.append(f"expected {pages} page(s), got {doc.page_count}")
    for i, page in enumerate(doc):
        w, h = page.rect.width / MM, page.rect.height / MM
        print(f"page {i + 1}: {w:.1f} x {h:.1f} mm")
        if abs(w - size[0]) > 0.5 or abs(h - size[1]) > 0.5:
            problems.append(f"page {i + 1}: expected {size[0]:g} x {size[1]:g} mm, got {w:.1f} x {h:.1f}")
        ink = page_ink_problems(page)
        print(f"  ink: {'PROBLEMS' if ink else 'black and white only'}")
        problems.extend(f"page {i + 1}: {p}" for p in ink)
    fonts, font_errors = font_problems(doc, expectations)
    print(f"fonts used: {', '.join(fonts) or '(none)'}")
    for role, names in expectations.items():
        print(f"  expected {role}: {', '.join(names)}")
    problems.extend(font_errors)
    return problems


def write_tiles(doc, out, dpi):
    out.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(doc):
        w, h = page.rect.width / MM, page.rect.height / MM
        page.get_pixmap(dpi=110).save(out / f"p{i + 1}-overview.png")
        step = h / 4
        for j in range(4):
            top, bottom = max(0, j * step - 10), min(h, (j + 1) * step + 10)
            for side, (left, right) in (("left", (0, min(w, w / 2 + 10))), ("right", (max(0, w / 2 - 10), w))):
                clip = pymupdf.Rect(left * MM, top * MM, right * MM, bottom * MM)
                page.get_pixmap(dpi=dpi, clip=clip).save(out / f"p{i + 1}-band{j + 1}-{side}-{top:.0f}-{bottom:.0f}mm.png")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--pages", type=positive_int, default=1, help="expected page count (default: 1)")
    ap.add_argument("--size", type=page_size, default=SIZES["A4"], help="expected A4 (default), Letter or WIDTHxHEIGHT in mm; tolerance 0.5 mm")
    ap.add_argument("--roles", default="body,drawing,checklist", help="required font roles, comma-separated (default: body,drawing,checklist); select only roles present in your variant")
    for role in FONT_DEFAULTS:
        ap.add_argument(f"--{role}-font", action="append", metavar="NAME", help=f"accepted {role} family; repeat for alternatives, replaces defaults")
    ap.add_argument("--out", help="tile folder (default: a new temp folder)")
    ap.add_argument("--dpi", type=positive_int, default=300, help="tile resolution (default: 300)")
    ap.add_argument("--no-tiles", action="store_true", help="validate only; skip visual-review images")
    args = ap.parse_args(argv)
    roles = args.roles.split(",")
    if not roles or any(role not in FONT_DEFAULTS for role in roles):
        ap.error("--roles must list body, drawing and/or checklist")
    expectations = {role: getattr(args, f"{role}_font") or FONT_DEFAULTS[role] for role in roles}
    try:
        with pymupdf.open(args.pdf) as doc:
            if not doc.is_pdf or doc.needs_pass:
                ap.error("input must be an unencrypted PDF")
            problems = check_document(doc, pages=args.pages, size=args.size, expectations=expectations)
            if not args.no_tiles:
                out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="nasa-handbook-check-"))
                write_tiles(doc, out, args.dpi)
                print(f"tiles: {out}")
                for path in sorted(out.iterdir()):
                    print(f"  {path}")
    except (OSError, RuntimeError, ValueError) as error:
        print(f"check failed: {error}", file=sys.stderr)
        return 1
    if problems:
        print("PROBLEMS:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
