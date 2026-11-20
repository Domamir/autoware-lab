#!/usr/bin/env python3
"""Instrukcja w Markdownie -> fragment HTML do wklejenia na stronę Moodle.

Moodle (HTML Purifier) wycina <style> i <script>, ale zostawia atrybuty class i style.
Dlatego formatowanie to klasy Bootstrapa z motywu Boost (tabele) i style w atrybutach
(bloki kodu z kolorowaniem składni). Tytuł "# ..." jest pomijany: to nazwa strony w Moodle.
Linki względne prowadzą do pliku w repozytorium na GitHubie.

Wymaga: python3-markdown, python3-pygments (apt) albo `pip install markdown pygments`.
Użycie:
  ./scripts/md_to_moodle.py projekty/01-panel-kierowcy.md     # -> projekty/01-panel-kierowcy.moodle.html
W Moodle: edytor -> kod źródłowy (TinyMCE: Narzędzia -> Kod źródłowy, Atto: przycisk HTML),
wklej całą zawartość pliku.
"""

import argparse
import posixpath
import re
from pathlib import Path

import markdown

REPO = 'https://github.com/PanHassan/Carla-Autoware-Bridge/blob/autoware-1.9-carla-0.9.16'
ROOT = Path(__file__).resolve().parent.parent

PRE = ('<pre style="background-color: #f6f8fa; border: 1px solid #d1d9e0; padding: 12px 14px; '
       'line-height: 1.45; font-size: 0.9em; color: #1f2328;"><code>')


def github_links(md, src):
    """[tekst](plik.md#kotwica) względem pliku źródłowego -> pełny adres na GitHubie."""
    folder = src.resolve().parent.relative_to(ROOT).as_posix()

    def fix(m):
        text, target = m.group(1), m.group(2)
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            return m.group(0)
        path = posixpath.normpath(posixpath.join(folder, target))
        return f'[{text}]({REPO}/{path})'

    return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', fix, md)


def convert(src):
    md = github_links(src.read_text(encoding='utf-8'), src)
    md = re.sub(r'^# .*\n', '', md, count=1)

    h = markdown.markdown(md, extensions=['tables', 'fenced_code', 'codehilite'], extension_configs={
        'codehilite': {'noclasses': True, 'pygments_style': 'default', 'guess_lang': False}})

    h = re.sub(r'<div class="codehilite" style="[^"]*"><pre style="[^"]*"><span></span><code>', PRE, h)
    h = h.replace('</code></pre></div>', '</code></pre>')
    h = re.sub(r'(?<!</code>)<pre><code[^>]*>', PRE, h)       # bloki bez języka bez codehilite
    h = re.sub(r'<h2>(.*?)</h2>', r'<h3 style="margin-top: 1.6em;">\1</h3>', h)
    h = re.sub(r'<h3>(.*?)</h3>', r'<h4 style="margin-top: 1.2em;">\1</h4>', h)
    h = h.replace('<table>', '<div class="table-responsive"><table class="table table-bordered table-sm">')
    h = h.replace('</table>', '</table></div>')
    h = h.replace('<thead>', '<thead class="thead-light">')
    h = re.sub(r'<strong>Sprawdź(:?)</strong>', r'<strong style="color: #1a7f37;">✔ Sprawdź\1</strong>', h)
    h = h.replace('<a href="https://', '<a target="_blank" rel="noopener" href="https://')
    return h + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('src', type=Path, help='plik .md')
    p.add_argument('-o', '--out', type=Path, help='plik wynikowy (domyślnie <src>.moodle.html)')
    a = p.parse_args()
    out = a.out or a.src.with_suffix('.moodle.html')
    out.write_text(convert(a.src), encoding='utf-8')
    print(f'zapisano {out}')


if __name__ == '__main__':
    main()
