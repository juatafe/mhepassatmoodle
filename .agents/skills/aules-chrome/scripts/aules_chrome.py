"""Local Chrome CDP connection; reusable Session.page for native Moodle edits."""
import argparse
from contextlib import AbstractContextManager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.request import build_opener, ProxyHandler

SENSITIVE = ('sesskey', 'token', 'password', 'secret', 'cookie', 'authorization')

def course_url(value):
    u = urlsplit(value)
    if (u.scheme not in ('http', 'https') or not u.hostname
            or u.username or u.password or (u.port is not None and u.port < 1)
            or not u.path.endswith('/course/view.php')
            or not dict(parse_qsl(u.query)).get('id', '').isdigit()):
        raise ValueError('Cal la URL HTTP(S) completa del curs Moodle (course/view.php?id=...).')
    if any(any(s in k.lower() for s in SENSITIVE) for k, _ in parse_qsl(u.query)):
        raise ValueError('Usa un enllaç al curs sense claus de sessió.')
    return value

def endpoint(port):
    if not 1024 <= int(port) <= 65535:
        raise ValueError('El port ha d’estar entre 1024 i 65535.')
    return f'http://127.0.0.1:{int(port)}'

def clean_url(value):
    u = urlsplit(value)
    # Only retain structural Moodle identifiers, never session or SSO queries.
    query = [(k, v) for k, v in parse_qsl(u.query) if k in ('id', 'update', 'section')]
    host = u.hostname or ''
    if ':' in host:
        host = f'[{host}]'
    authority = f'{host}:{u.port}' if u.port else host
    return urlunsplit((u.scheme, authority, u.path, urlencode(query), ''))

def cache_dir():
    if sys.platform == 'win32':
        root = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
    elif sys.platform == 'darwin':
        root = Path.home() / 'Library/Caches'
    else:
        root = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
    return root / 'aules-chrome'

def chrome_path(explicit=None):
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return str(path)
        raise ValueError('No existeix el navegador indicat amb --chrome.')
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        found = shutil.which(name)
        if found:
            return found
    candidates = [Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')]
    if sys.platform == 'win32':
        candidates += [Path(os.environ[key]) / 'Google/Chrome/Application/chrome.exe'
                       for key in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA')
                       if key in os.environ]
    for path in candidates:
        if path.is_file():
            return str(path)
    raise RuntimeError('Instal·la Google Chrome o indica la ruta amb --chrome.')

def cdp_ready(port):
    try:
        opener = build_opener(ProxyHandler({}))
        with opener.open(endpoint(port) + '/json/version', timeout=2) as response:
            data = json.load(response)
        return bool(data.get('webSocketDebuggerUrl'))
    except (OSError, ValueError):
        return False

def start(url, port=9222, chrome=None):
    course_url(url)
    endpoint(port)
    if cdp_ready(port):
        # Keep a course tab open for the user's login; do not touch existing tabs.
        with Session(url, port) as session:
            session.page.goto(url, wait_until='domcontentloaded')
            session.keep_page = True
        print('Chrome ja està connectat. Curs obert en una pestanya nova.')
        return
    executable = chrome_path(chrome)
    state = cache_dir()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    profile = state / f'profile-{port}'
    command = [executable, f'--remote-debugging-port={port}',
               '--remote-debugging-address=127.0.0.1', f'--user-data-dir={profile}',
               '--no-first-run', '--no-default-browser-check', '--new-window', url]
    options = {'start_new_session': True} if sys.platform != 'win32' else {
        'creationflags': subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
    subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, **options)
    for _ in range(40):
        if cdp_ready(port):
            print('Chrome preparat. Inicia sessió en Moodle en la finestra oberta, si ho demana.')
            return
        time.sleep(0.25)
    raise RuntimeError('Chrome no exposa CDP. Comprova la finestra, el port i la instal·lació de Chrome.')

class Session(AbstractContextManager):
    """Attach without closing the user's browser. Only this worker tab is closed."""
    def __init__(self, url, port=9222):
        self.url = course_url(url)
        self.base = self.url.split('/course/view.php', 1)[0] + '/'
        self.endpoint = endpoint(port)
        self.pw = None
        self.page = None
        self.keep_page = False

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError('Executa primer: python3 aules.py setup') from None
        try:
            self.pw = sync_playwright().start()
            self.browser = self.pw.chromium.connect_over_cdp(self.endpoint, timeout=10000)
            self.context = self.browser.contexts[0]
            self.page = self.context.new_page()
            self.page.set_default_timeout(20000)
            return self
        except Exception:
            self.__exit__(None, None, None)
            raise RuntimeError('No s’ha pogut connectar amb Chrome. Executa start i comprova el port.') from None

    def open_course(self):
        response = self.page.goto(self.url, wait_until='domcontentloaded')
        if not response or response.status >= 400:
            raise RuntimeError('Moodle no ha retornat el curs correctament.')
        if (not self.page.url.startswith(self.base) or '/login/' in self.page.url
                or self.page.locator('input[type=password]').count()):
            raise RuntimeError('Inicia sessió en el Moodle de destinació en Chrome i torna a comprovar la connexió.')
        expected = dict(parse_qsl(urlsplit(self.url).query))['id']
        actual = self.page.evaluate('() => window.M?.cfg?.courseId ?? null')
        if str(actual) != expected:
            raise RuntimeError('No s’ha confirmat l’accés al curs sol·licitat; revisa la sessió i els permisos.')
        if not self.page.locator('a[href*="logout.php"]').count():
            raise RuntimeError('No s’ha confirmat una sessió identificada en Moodle; revisa la identificació o els controls del tema.')
        return self.page

    def __exit__(self, *args):
        try:
            if self.page and not self.keep_page:
                self.page.close()
        finally:
            if self.pw:
                self.pw.stop()
        # Never call browser.close(): Chrome belongs to the user.

def main():
    parser = argparse.ArgumentParser(description='Connexió local Chrome–Moodle (inclou Aules)')
    parser.add_argument('command', choices=('start', 'status', 'inspect'))
    parser.add_argument('--url', required=True, help='URL completa del curs Moodle, en qualsevol domini')
    parser.add_argument('--port', type=int, default=9222)
    parser.add_argument('--chrome', help='Ruta opcional a Chrome')
    args = parser.parse_args()
    try:
        if args.command == 'start':
            start(args.url, args.port, args.chrome)
            return
        with Session(args.url, args.port) as session:
            page = session.open_course()
            result = {'connected': True, 'course': clean_url(page.url), 'title': page.title()}
            if args.command == 'inspect':
                # Only course activity names/URLs, no user menu, cookies or full HTML.
                result['activities'] = page.locator('.activityinstance a[href], .activityname a[href]').evaluate_all(
                    '(els) => els.map(a => ({name: a.innerText.trim(), url: a.href}))')
                for item in result['activities']:
                    item['url'] = clean_url(item['url'])
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (RuntimeError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')
    except Exception:
        # Playwright errors may contain session-bearing URLs. Do not print raw traces.
        parser.exit(1, 'Error de navegador. Comprova Chrome, la sessió i l’accés al curs; no s’ha confirmat l’operació.\n')

if __name__ == '__main__':
    main()
