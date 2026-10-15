#!/usr/bin/env python3
"""Project launcher. Python 3.10+, no external dependency needed for setup."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / '.agents' / 'skills' / 'aules-chrome'
ENV = ROOT / '.venv'
PYTHON = ENV / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')

def main():
    if sys.version_info < (3, 10):
        raise SystemExit('Cal Python 3.10 o posterior.')
    if sys.argv[1:] == ['setup']:
        venv.EnvBuilder(with_pip=True).create(ENV)
        subprocess.run([str(PYTHON), '-m', 'pip', 'install', '-r',
                        str(ROOT / 'requirements.txt')], check=True)
        print('Preparat. Executa: python3 aules.py start --url URL_DEL_CURS')
        return
    script = SKILL / 'scripts' / 'aules_chrome.py'
    if PYTHON.exists() and Path(sys.prefix).resolve() != ENV.resolve():
        raise SystemExit(subprocess.call([str(PYTHON), str(script), *sys.argv[1:]]))
    spec = importlib.util.spec_from_file_location('aules_chrome', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()

if __name__ == '__main__':
    main()
