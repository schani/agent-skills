"""Renderer regressions. Fixtures contain only local, explicitly authored HTML."""

import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

SKILL = Path(__file__).resolve().parents[1] / 'skill'
RENDER = SKILL / 'scripts' / 'render.sh'
TEMPLATE = SKILL / 'assets' / 'template.html'
FIT = TEMPLATE.read_text().split('<script>', 1)[1].split('</script>', 1)[0]
CSS = '''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
.page { position: relative; width: 210mm; height: 297mm;
  padding: 9mm 15mm 0 16mm; overflow: hidden; background: white;
  break-inside: avoid; break-after: page; }
.foot { position: absolute; bottom: 8mm; left: 16mm; right: 15mm; height: 12mm; }
p { margin: 0; }
'''
MARKER = '''<defs><marker id="arrow" viewBox="0 0 6 4" refX="5.6" refY="2"
 markerWidth="2.4" markerHeight="1.3" markerUnits="userSpaceOnUse" orient="auto"
 preserveAspectRatio="none"><path d="M0,0 L6,2 L0,4 Z"/></marker></defs>'''


def page(content='<p>Normal page.</p>', footer=True):
    return '<div class="page">' + content + ('<footer class="foot">Footer</footer>' if footer else '') + '</div>'


def document(body, css='', fit=True, extra=''):
    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + CSS + css +
            '</style></head><body>' + body + ('<script>' + FIT + '</script>' if fit else '') + extra + '</body></html>')


def png_info(path):
    data = path.read_bytes()
    width, height, depth, color = struct.unpack('>IIBB', data[16:26])
    compressed = b''
    offset = 8
    while offset < len(data):
        size = struct.unpack('>I', data[offset:offset + 4])[0]
        if data[offset + 4:offset + 8] == b'IDAT':
            compressed += data[offset + 8:offset + 8 + size]
        offset += size + 12
    # All PNG filters have a zero predictor for the first pixel of row one.
    first = zlib.decompress(compressed)[1:4] if depth == 8 and color in (2, 6) else None
    return width, height, first


class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.environ.get('CHROME') or any(shutil.which(c) for c in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable')) or
                Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').is_file()):
            raise unittest.SkipTest('Chrome/Chromium not installed')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nasa-render-test-')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def run_html(self, html, expected=0, name='page.html', env=None, options=()):
        source = self.root / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(html)
        result = subprocess.run(['sh', str(RENDER), str(source), *options], capture_output=True,
                                text=True, timeout=60, env=env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected:
            self.assertFalse(source.with_suffix('.pdf').exists())
            self.assertFalse(source.with_suffix('.png').exists())
        return result, source

    def test_normal_page_and_print_preview(self):
        result, source = self.run_html(document(page(), css='@media screen {.page {background:red}}'))
        self.assertIn('page 1: ok', result.stdout)
        self.assertTrue(source.with_suffix('.pdf').read_bytes().startswith(b'%PDF'))
        width, height, first = png_info(source.with_suffix('.png'))
        self.assertAlmostEqual(width, 210 / 25.4 * 192, delta=2)
        self.assertAlmostEqual(height, 297 / 25.4 * 192, delta=2)
        self.assertEqual(first, b'\xff\xff\xff', 'preview must use print, not red screen background')

    def test_horizontal_descendant_overflow(self):
        result, _ = self.run_html(document(page('<div><span style="display:block;width:1000px">Wide</span></div>')), 3)
        self.assertIn('horizontal overflow', result.stdout)

    def test_nowrap_text_overflow(self):
        result, _ = self.run_html(document(page('<p style="width:10px;white-space:nowrap">' + 'W' * 150 + '</p>')), 3)
        self.assertIn('horizontal overflow', result.stdout)

    def test_vertical_overflow_on_second_page(self):
        result, _ = self.run_html(document(page() + page('<div style="height:1200px">Too tall</div>')), 3)
        self.assertIn('page 1: ok', result.stdout)
        self.assertIn('page 2: overflow', result.stdout)

    def test_svg_text_clipping(self):
        svg = '<svg width="300" height="150" viewBox="0 0 100 50"><text x="95" y="20">CLIPPED</text></svg>'
        result, _ = self.run_html(document(page(svg)), 3)
        self.assertIn('SVG viewBox overflow', result.stdout)

    def test_svg_transformed_geometry_clipping(self):
        svg = '<svg width="300" height="150" viewBox="0 0 100 50"><g transform="translate(95 0)"><rect y="10" width="20" height="10"/></g></svg>'
        result, _ = self.run_html(document(page(svg)), 3)
        self.assertIn('SVG viewBox overflow', result.stdout)

    def test_svg_stroke_clipping(self):
        svg = '<svg width="300" height="150" viewBox="0 0 100 50"><line x1="10" y1="0" x2="90" y2="0" stroke="black" stroke-width="2"/></svg>'
        result, _ = self.run_html(document(page(svg)), 3)
        self.assertIn('SVG viewBox overflow', result.stdout)

    def test_svg_marker_clipping(self):
        svg = '<svg width="300" height="150" viewBox="0 0 100 50">' + MARKER + '<line x1="20" y1="0.2" x2="50" y2="0.2" stroke="black" marker-end="url(#arrow)"/></svg>'
        result, _ = self.run_html(document(page(svg)), 3)
        self.assertIn('SVG viewBox overflow', result.stdout)

    def test_hidden_defs_and_valid_marker(self):
        svg = ('<svg width="300" height="150" viewBox="0 0 100 50">' + MARKER +
               '<defs><pattern id="unused"><rect width="1000" height="1000"/></pattern></defs>'
               '<rect display="none" width="1000" height="1000"/>'
               '<line x1="20" y1="20" x2="50" y2="20" stroke="black" marker-end="url(#arrow)"/></svg>')
        self.run_html(document(page(svg)))

    def test_unsupported_marker_fails_closed(self):
        svg = '<svg width="300" height="150" viewBox="0 0 100 50">' + MARKER.replace('preserveAspectRatio="none"', '') + '<line x1="20" y1="20" x2="50" y2="20" marker-end="url(#arrow)"/></svg>'
        result, _ = self.run_html(document(page(svg)), 3)
        self.assertIn('unsupported marker configuration', result.stdout)

    def test_missing_fit_script_fails_closed(self):
        result, _ = self.run_html(document(page(), fit=False), 3)
        self.assertIn('Missing nasaHandbookFit', result.stderr)

    def test_invalid_fit_data_fails_closed(self):
        result, _ = self.run_html(document(page(), extra='<script>window.nasaHandbookFit = () => ({version:1,media:"print",pages:[]})</script>'), 3)
        self.assertIn('invalid fit data', result.stderr)

    def test_missing_footer_fails_closed(self):
        result, _ = self.run_html(document(page(footer=False)), 3)
        self.assertIn('missing or hidden .foot', result.stdout)

    def test_print_only_overflow(self):
        result, _ = self.run_html(document(page('<p id="wide">Print is wider</p>'), css='@media print {#wide {width:1200px}}'), 3)
        self.assertIn('horizontal overflow', result.stdout)

    def test_screen_only_overflow_does_not_fail_print(self):
        self.run_html(document(page('<p id="wide">Screen is wider</p>'), css='@media screen {#wide {width:1200px}}'))

    def test_two_page_pdf_and_individual_pngs(self):
        _, source = self.run_html(document(page() + page('<p>Second page</p>')))
        pdf = source.with_suffix('.pdf').read_bytes()
        self.assertEqual(len(re.findall(rb'/Type\s*/Page\b', pdf)), 2)
        self.assertFalse(source.with_suffix('.png').exists())
        for number in (1, 2):
            self.assertTrue(source.with_name(f'page-{number}.png').is_file())

    def test_chrome_failure_preserves_stderr(self):
        fake = self.root / 'fake-chrome'
        fake.write_text('#!/bin/sh\necho "Chrome startup sentinel" >&2\nexit 1\n')
        fake.chmod(0o755)
        result, _ = self.run_html(document(page()), 3, env={**os.environ, 'CHROME': str(fake)})
        self.assertIn('Chrome startup sentinel', result.stderr)

    def test_timeout_is_actionable(self):
        fake = self.root / 'fake-chrome'
        fake.write_text('#!/bin/sh\nexec sleep 30\n')
        fake.chmod(0o755)
        result, _ = self.run_html(document(page()), 3, env={**os.environ, 'CHROME': str(fake)}, options=('--timeout', '0.1'))
        self.assertIn('timed out waiting for Chrome', result.stderr)

    def test_shipped_fit_scripts_match_template(self):
        for example in (SKILL / 'assets' / 'examples').glob('*.html'):
            with self.subTest(example=example.name):
                script = example.read_text().rsplit('<script>', 1)[1].split('</script>', 1)[0]
                self.assertEqual(script, FIT)

    def test_shipped_pi_durable_ten_page_report(self):
        (self.root / 'fonts').symlink_to(SKILL / 'assets' / 'fonts', target_is_directory=True)
        _, source = self.run_html((SKILL / 'assets/examples/pi-durable.html').read_text(),
                                  name='examples/pi-durable.html')
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/check.py'),
                                 str(source.with_suffix('.pdf')), '--pages', '10', '--no-tiles'],
                                capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(source.with_suffix('.png').exists())
        previews = set(source.parent.glob('pi-durable-*.png'))
        self.assertEqual(previews, {source.with_name(f'pi-durable-{n}.png') for n in range(1, 11)})
        for preview in previews:
            with self.subTest(preview=preview.name):
                width, height, _ = png_info(preview)
                self.assertAlmostEqual(width, 210 / 25.4 * 192, delta=2)
                self.assertAlmostEqual(height, 297 / 25.4 * 192, delta=2)

    def test_template_and_original_examples(self):
        (self.root / 'fonts').symlink_to(SKILL / 'assets' / 'fonts', target_is_directory=True)
        for name in ('template.html', 'examples/portal-gun-device.html', 'examples/espresso-fluid-system.html'):
            with self.subTest(name=name):
                _, source = self.run_html((SKILL / 'assets' / name).read_text(), name=name)
                result = subprocess.run([sys.executable, str(SKILL / 'scripts' / 'check.py'),
                                         str(source.with_suffix('.pdf')), '--no-tiles'],
                                        capture_output=True, text=True, timeout=45)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
