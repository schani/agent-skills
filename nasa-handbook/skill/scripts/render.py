#!/usr/bin/env python3
"""Chrome DevTools pipe client; no browser driver or third-party packages."""

import argparse
import base64
import json
import math
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import time


class RenderError(Exception):
    pass


class Chrome:
    def __init__(self, executable, timeout, profile, stderr):
        # Chrome's pipe protocol uses fd 3/4. The shell maps ordinary Popen
        # pipes there and keeps Chrome's stdout out of the protocol stream.
        self.process = subprocess.Popen(
            ['/bin/sh', '-c',
             'exec 3<&0 4>&1; exec </dev/null >/dev/null; exec "$@"',
             'chrome', executable, '--headless=new', '--disable-gpu',
             '--remote-debugging-pipe', '--allow-file-access-from-files',
             '--no-first-run', '--no-default-browser-check',
             f'--user-data-dir={profile}'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
        )
        self.deadline = time.monotonic() + timeout
        self.buffer = b''
        self.sequence = 0
        self.session = None

    def call(self, method, **params):
        self.sequence += 1
        request = dict(id=self.sequence, method=method, params=params)
        if self.session:
            request['sessionId'] = self.session
        try:
            self.process.stdin.write(json.dumps(request).encode() + b'\0')
            self.process.stdin.flush()
        except BrokenPipeError as exc:
            raise RenderError('Chrome closed its DevTools pipe') from exc
        while True:
            while b'\0' not in self.buffer:
                remaining = self.deadline - time.monotonic()
                if remaining <= 0 or not select.select([self.process.stdout], [], [], remaining)[0]:
                    raise RenderError(f'timed out waiting for Chrome ({method}); try --timeout 90')
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    raise RenderError(f'Chrome exited during {method} (exit {self.process.poll()})')
                self.buffer += chunk
            raw, self.buffer = self.buffer.split(b'\0', 1)
            response = json.loads(raw)
            if response.get('id') != self.sequence:
                continue
            if 'error' in response:
                raise RenderError(f'{method}: {response["error"]}')
            return response.get('result', {})

    def evaluate(self, expression):
        response = self.call('Runtime.evaluate', expression=expression,
                             awaitPromise=True, returnByValue=True)
        if 'exceptionDetails' in response:
            detail = response['exceptionDetails']
            raise RenderError(detail.get('exception', {}).get('description', detail.get('text', str(detail))))
        return response.get('result', {}).get('value')

    def close(self):
        if self.process.poll() is None:
            self.deadline = time.monotonic() + 3
            self.session = None
            try:
                self.call('Browser.close')
            except (RenderError, OSError, ValueError):
                self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdin.close()
        self.process.stdout.close()


FIT = """(async () => {
  if (document.readyState !== 'complete')
    await new Promise(resolve => addEventListener('load', resolve, {once: true}));
  await document.fonts.ready;
  await Promise.all([...document.images].map(image => image.decode()));
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  if (typeof window.nasaHandbookFit !== 'function')
    throw new Error('Missing nasaHandbookFit; copy the fit script from assets/template.html');
  return {fit: window.nasaHandbookFit(), count: document.querySelectorAll('.page').length};
})()"""


def validate(result):
    """Reject missing, stale or malformed fit data, not just explicit overflow."""
    if not isinstance(result, dict) or not isinstance(result.get('fit'), dict):
        raise RenderError('missing or invalid fit data')
    fit = result['fit']
    pages = fit.get('pages')
    if (type(fit.get('version')) is not int or fit['version'] != 1 or
            type(result.get('count')) is not int or fit.get('media') != 'print' or
            not isinstance(pages, list) or not pages or len(pages) != result.get('count')):
        raise RenderError('invalid fit data: need print-media results for every .page')
    for number, page in enumerate(pages, 1):
        if (not isinstance(page, dict) or type(page.get('page')) is not int or page['page'] != number or
                page.get('status') not in ('ok', 'overflow', 'invalid') or
                not isinstance(page.get('issues'), list) or
                any(not isinstance(issue, str) for issue in page['issues'])):
            raise RenderError(f'invalid fit data for page {number}')
        for key in ('x', 'y', 'width', 'height', 'freeMm'):
            value = page.get(key)
            if (isinstance(value, bool) or not isinstance(value, (int, float)) or
                    not math.isfinite(value) or (key in ('width', 'height') and value <= 0)):
                raise RenderError(f'invalid fit data for page {number}: {key}')
        if page['status'] == 'ok' and (page['issues'] or page['freeMm'] < -0.5 * 25.4 / 96):
            raise RenderError(f'inconsistent fit data for page {number}')
    return pages


def chrome_path():
    configured = os.environ.get('CHROME')
    if configured:
        path = shutil.which(configured)
        if not path:
            raise RenderError(f'CHROME is not executable: {configured}')
        return path
    mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if os.access(mac, os.X_OK):
        return mac
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        path = shutil.which(name)
        if path:
            return path
    raise RenderError('Chrome or Chromium not found; set CHROME=/path/to/chrome')


def render(chrome, source):
    target = chrome.call('Target.createTarget', url='about:blank')['targetId']
    chrome.session = chrome.call('Target.attachToTarget', targetId=target, flatten=True)['sessionId']
    chrome.call('Page.enable')
    chrome.call('Emulation.setDeviceMetricsOverride', width=794, height=1123,
                deviceScaleFactor=2, mobile=False)
    chrome.call('Emulation.setEmulatedMedia', media='print')
    response = chrome.call('Page.navigate', url=source.as_uri())
    if response.get('errorText'):
        raise RenderError(f'cannot load {source}: {response["errorText"]}')
    pages = validate(chrome.evaluate(FIT))
    # Use the paper's viewport for print-media width/height queries as well.
    chrome.call('Emulation.setDeviceMetricsOverride', width=round(pages[0]['width']),
                height=round(pages[0]['height']), deviceScaleFactor=2, mobile=False)
    pages = validate(chrome.evaluate(FIT))
    failed = False
    for page in pages:
        detail = '; '.join(page['issues']) if page['issues'] else f'{page["freeMm"]:.1f} mm free above footer'
        print(f'fit: page {page["page"]}: {page["status"]}: {detail}', flush=True)
        failed |= page['status'] != 'ok'
    if failed:
        raise RenderError('page fit failed; fix clipping or cut content, do not shrink type')
    # Build all artifacts before publishing any. PNGs use the same print media,
    # font state and page bounds as the fit check, not a screen-only screenshot.
    pdf = chrome.call('Page.printToPDF', printBackground=True, preferCSSPageSize=True,
                      displayHeaderFooter=False, marginTop=0, marginBottom=0,
                      marginLeft=0, marginRight=0)
    artifacts = {source.with_suffix('.pdf'): base64.b64decode(pdf['data'], validate=True)}
    for page in pages:
        clip = {key: page[key] for key in ('x', 'y', 'width', 'height')}
        clip['scale'] = 1
        png = chrome.call('Page.captureScreenshot', format='png', captureBeyondViewport=True, clip=clip)
        suffix = '' if len(pages) == 1 else f'-{page["page"]}'
        path = source.with_name(source.stem + suffix + '.png')
        artifacts[path] = base64.b64decode(png['data'], validate=True)
    for path, data in artifacts.items():
        path.write_bytes(data)
        print(f'{path.suffix[1:]}: {path}')


def main():
    parser = argparse.ArgumentParser(description='Check print-media fit, render PDF and 2x PNG(s) with Chrome.')
    parser.add_argument('html', type=Path)
    parser.add_argument('--timeout', type=float, default=45, metavar='SECONDS', help='total Chrome time budget (default: 45)')
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be positive and finite')
    source = args.html.resolve()
    if not source.is_file() or source.suffix.lower() not in ('.html', '.htm'):
        parser.error('input must be an existing .html or .htm file')
    chrome = None
    failed = True
    with tempfile.TemporaryDirectory(prefix='nasa-render-') as profile, tempfile.TemporaryFile() as stderr:
        try:
            chrome = Chrome(chrome_path(), args.timeout, profile, stderr)
            render(chrome, source)
            failed = False
            return 0
        except (RenderError, OSError, ValueError, KeyError) as exc:
            print(f'render: {exc}', file=sys.stderr)
            return 3
        finally:
            if chrome:
                chrome.close()
            # Success diagnostics are noisy; preserve Chrome's own explanation
            # on failure, including sandbox, loading and startup errors.
            stderr.seek(0)
            diagnostics = stderr.read().decode(errors='replace')
            if failed and diagnostics:
                print(diagnostics, file=sys.stderr, end='')


if __name__ == '__main__':
    sys.exit(main())
