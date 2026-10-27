"""Run: python -m unittest discover -s nasa-handbook/tests -v"""

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pymupdf

SKILL = Path(__file__).resolve().parents[1] / "skill"
spec = importlib.util.spec_from_file_location("handbook_check", SKILL / "scripts/check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def document(size=(210, 297), checklist=True):
    doc = pymupdf.open()
    page = doc.new_page(width=size[0] * check.MM, height=size[1] * check.MM)
    page.insert_text((30, 40), "BODY TEXT", fontname="tiro")
    page.insert_font(fontname="drawing", fontfile=str(SKILL / "assets/fonts/routed-gothic.ttf"))
    page.insert_text((30, 60), "DRAWING", fontname="drawing")
    if checklist:
        page.insert_font(fontname="checklist", fontfile=str(SKILL / "assets/fonts/LetterGothicCode-R.ttf"))
        page.insert_text((30, 80), "CHECKLIST", fontname="checklist")
    return doc


def image(page, colour=(0, 0, 0), alpha=None):
    pix = pymupdf.Pixmap(pymupdf.csRGB, (0, 0, 4, 4), alpha is not None)
    for y in range(4):
        for x in range(4):
            pix.set_pixel(x, y, colour + ((alpha,) if alpha is not None else ()))
    page.insert_image(pymupdf.Rect(20, 100, 100, 180), pixmap=pix)


def state(page, content):
    doc = page.parent
    resources = int(doc.xref_get_key(page.xref, "Resources")[1].split()[0])
    doc.xref_set_key(resources, "ExtGState", f"<</GS << /Type /ExtGState {content} >>>>")
    xref = page.get_contents()[-1]
    doc.update_stream(xref, b"/GS gs\n" + doc.xref_stream(xref))


class CheckTests(unittest.TestCase):
    def validate(self, doc, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return check.check_document(doc, **kwargs)

    def test_valid_three_roles(self):
        with document() as doc:
            self.assertEqual(self.validate(doc), [])

    def test_colour_raster(self):
        with document() as doc:
            image(doc[0], (255, 0, 0))
            self.assertTrue(any("raster image" in p for p in self.validate(doc)))

    def test_grey_raster(self):
        with document() as doc:
            image(doc[0], (128, 128, 128))
            self.assertTrue(any("source pixels" in p for p in self.validate(doc)))

    def test_bw_raster_and_binary_mask(self):
        with document() as doc:
            image(doc[0])
            image(doc[0], (255, 255, 255), alpha=255)
            image(doc[0], alpha=0)
            self.assertEqual(self.validate(doc), [])

    def test_raster_soft_mask(self):
        with document() as doc:
            image(doc[0], alpha=128)
            self.assertTrue(any("fractional transparency" in p for p in self.validate(doc)))

    def test_raster_paint_opacity(self):
        with document() as doc:
            image(doc[0])
            state(doc[0], "/ca 0.5")
            self.assertEqual(doc[0].get_drawings(extended=True), [])
            self.assertTrue(any("fractional opacity" in p for p in self.validate(doc)))

    def test_raster_paint_opacity_indirect_state(self):
        with document() as doc:
            image(doc[0])
            page = doc[0]
            gs = doc.get_new_xref()
            doc.update_object(gs, "<</Type/ExtGState/ca .5>>")
            resources = int(doc.xref_get_key(page.xref, "Resources")[1].split()[0])
            states = doc.get_new_xref()
            doc.update_object(states, f"<</GS {gs} 0 R>>")
            doc.xref_set_key(resources, "ExtGState", f"{states} 0 R")
            xref = page.get_contents()[-1]
            doc.update_stream(xref, b"/GS gs\n" + doc.xref_stream(xref))
            self.assertTrue(any("fractional opacity" in p for p in self.validate(doc)))

    def test_inherited_page_resources(self):
        with document() as doc:
            image(doc[0])
            state(doc[0], "/ca .5")
            page = doc[0]
            parent = int(doc.xref_get_key(page.xref, "Parent")[1].split()[0])
            resources = doc.xref_get_key(page.xref, "Resources")[1]
            doc.xref_set_key(parent, "Resources", resources)
            doc.xref_set_key(page.xref, "Resources", "null")
            self.assertTrue(any("fractional opacity" in p for p in self.validate(doc)))

    def test_nested_form_image_opacity(self):
        with document() as doc, pymupdf.open() as source:
            source.new_page()
            image(source[0])
            state(source[0], "/ca .5")
            doc[0].show_pdf_page(pymupdf.Rect(100, 200, 300, 500), source, 0)
            self.assertTrue(any("fractional opacity" in p for p in self.validate(doc)))

    def test_non_normal_blend_mode(self):
        with document() as doc:
            image(doc[0])
            state(doc[0], "/BM /Screen")
            self.assertTrue(any("blend mode" in p for p in self.validate(doc)))

    def test_translucent_black_vector(self):
        with document() as doc:
            doc[0].draw_rect(pymupdf.Rect(100, 100, 200, 200), fill=(0, 0, 0), fill_opacity=.5)
            self.assertTrue(any("fractional opacity" in p for p in self.validate(doc)))

    def test_translucent_black_text(self):
        with document() as doc:
            doc[0].insert_text((30, 100), "TEXT", fontname="tiro", fill_opacity=.5)
            self.assertTrue(any("fractional opacity" in p for p in self.validate(doc)))

    def test_tinted_vector_and_text(self):
        with document() as doc:
            doc[0].draw_rect(pymupdf.Rect(100, 100, 200, 200), fill=(1, 0, 0))
            doc[0].insert_text((30, 100), "TEXT", fontname="tiro", color=(0.5, 0.5, 0.5))
            problems = self.validate(doc)
            self.assertTrue(any("vector ink" in p for p in problems))
            self.assertTrue(any("text ink" in p for p in problems))

    def test_faint_tint_not_rounded_to_white(self):
        self.assertFalse(check.is_bw((.9999, .9999, .9999)))

    def test_antialiasing_is_not_source_tint(self):
        with document() as doc:
            doc[0].draw_line((100, 100), (200, 103), color=(0, 0, 0), width=.2)
            pixels = doc[0].get_pixmap(colorspace=pymupdf.csGRAY).samples
            self.assertTrue(any(v not in (0, 255) for v in pixels))
            self.assertEqual(self.validate(doc), [])

    def test_wrong_size_and_letter_option(self):
        with document(size=check.SIZES["Letter"]) as doc:
            self.assertTrue(any("expected 210 x 297" in p for p in self.validate(doc)))
            self.assertEqual(self.validate(doc, size=check.page_size("letter")), [])

    def test_custom_size_and_rotation(self):
        with document(size=(180, 240)) as doc:
            self.assertEqual(self.validate(doc, size=check.page_size("180x240")), [])
            doc[0].set_rotation(90)
            self.assertTrue(any("expected 180 x 240" in p for p in self.validate(doc, size=(180, 240))))

    def test_missing_checklist_and_explicit_variant(self):
        with document(checklist=False) as doc:
            self.assertTrue(any("missing checklist" in p for p in self.validate(doc)))
            expected = {k: v for k, v in check.FONT_DEFAULTS.items() if k != "checklist"}
            self.assertEqual(self.validate(doc, expectations=expected), [])

    def test_unexpected_fallback_font(self):
        with document() as doc:
            doc[0].insert_text((30, 100), "FALLBACK", fontname="helv")
            self.assertTrue(any("unexpected font" in p for p in self.validate(doc)))

    def test_missing_body_and_drawing_fonts(self):
        with pymupdf.open() as doc:
            doc.new_page().insert_text((30, 100), "FALLBACK", fontname="helv")
            problems = self.validate(doc)
            self.assertTrue(any("missing body" in p for p in problems))
            self.assertTrue(any("missing drawing" in p for p in problems))

    def test_unused_font_resources_do_not_count(self):
        with document() as doc:
            doc[0].insert_font(fontname="cour")
            self.assertEqual(self.validate(doc), [])

    def test_flagged_one_fallback(self):
        with document() as doc:
            doc[0].insert_text((30, 100), "1", fontname="helv")
            self.assertEqual(self.validate(doc), [])

    def test_documented_symbol_fallback(self):
        path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        if not path.exists():
            self.skipTest("DejaVu Sans not installed")
        with document() as doc:
            doc[0].insert_font(fontname="symbols", fontfile=str(path))
            doc[0].insert_text((30, 100), "≤−≈", fontname="symbols")
            self.assertEqual(self.validate(doc), [])
            doc[0].insert_text((30, 120), "WRONG", fontname="symbols")
            self.assertTrue(any("unexpected font" in p for p in self.validate(doc)))

    def test_font_family_normalization(self):
        for name in ("ABCDEF+LetterGothicCode-R", "Letter Gothic Code Bold", "LetterGothicCode-B"):
            self.assertEqual(check.font_family(name), "lettergothiccode")
        self.assertEqual(check.font_family("ABCDEF+DejaVuSerif-BoldItalic"), "dejavuserif")
        self.assertNotEqual(check.font_family("DejaVuSansMono"), check.font_family("DejaVuSans"))

    def test_page_count(self):
        with document() as doc:
            doc.new_page()
            self.assertTrue(any("expected 1 page" in p for p in self.validate(doc)))
            self.assertEqual(self.validate(doc, pages=2), [])

    def test_cli_overrides(self):
        with tempfile.TemporaryDirectory() as tmp, pymupdf.open() as doc:
            doc.new_page(width=180 * check.MM, height=240 * check.MM).insert_text((30, 40), "BODY", fontname="cour")
            pdf = Path(tmp) / "page.pdf"
            doc.save(pdf)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check.main([str(pdf), "--no-tiles", "--size", "180x240", "--roles", "body", "--body-font", "Courier"]), 0)
                self.assertEqual(check.main([str(pdf), "--no-tiles"]), 1)

    def test_cli_bad_inputs(self):
        for args in (["--size", "any"], ["--dpi", "0"], ["--pages", "-1"], ["--roles", "invalid"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    check.main(["missing.pdf", *args])
                self.assertEqual(result.exception.code, 2)

    def test_valid_template_pdf(self):
        chrome = os.environ.get("CHROME") or shutil.which("chromium") or shutil.which("google-chrome")
        if not chrome:
            self.skipTest("Chrome/Chromium not installed")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            shutil.copy(SKILL / "assets/template.html", out / "page.html")
            shutil.copytree(SKILL / "assets/fonts", out / "fonts")
            subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--virtual-time-budget=4000", "--no-pdf-header-footer", f"--print-to-pdf={out / 'page.pdf'}", (out / "page.html").as_uri()], capture_output=True, check=True, timeout=45)
            with pymupdf.open(out / "page.pdf") as doc:
                self.assertEqual(self.validate(doc), [])
                check.write_tiles(doc, out / "tiles", 36)
                self.assertEqual(len(list((out / "tiles").glob("*.png"))), 9)


if __name__ == "__main__":
    unittest.main()
