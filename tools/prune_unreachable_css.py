#!/usr/bin/env python3
"""Remove CSS rules that can never match anything in the built app.

A selector is unreachable when it requires a class or id that appears nowhere
in the app's markup, scripts or data (index.html without its styles, every JS,
MJS, JSON and HTML file in the build, vendor libraries included). Names that
scripts build at runtime are honoured: any literal ending in "-" that is joined
to a value ('nk-step-' + n, `nk-step-${n}`) keeps every name with that prefix.
Requirements inside :not(), :is(), :where() and :has() are ignored, so only
names a selector cannot match without are counted.

Each unreachable alternative of a selector list is dropped; a rule whose
alternatives are all unreachable is removed, and so is an @media/@supports
block left empty. Everything else is kept byte for byte.

  python3 tools/prune_unreachable_css.py build/web            # prune the build in place
  python3 tools/prune_unreachable_css.py build/web --report   # only report
  python3 tools/prune_unreachable_css.py build/web --files app/src/main/assets/redesign/nk-theme.css
"""
import argparse
import re
import sys
from pathlib import Path

STYLE_BLOCK = re.compile(r'(<style\b[^>]*>)(.*?)(</style>)', re.S | re.I)
SOURCE_SUFFIXES = {'.js', '.mjs', '.json', '.html', '.htm', '.svg'}
GROUPING_AT_RULES = ('@media', '@supports', '@layer', '@container', '@document')
NAME = re.compile(r'[A-Za-z0-9_-]+')
# A literal that ends in "-" and is then joined to a runtime value.
JOINED_PREFIX = re.compile(r'([A-Za-z_][A-Za-z0-9_-]*-)(?:[\'"`]\s*\+|\$\{)')
SELECTOR_NAME = re.compile(r'[.#](-?[A-Za-z_][A-Za-z0-9_-]*)(?![A-Za-z0-9_\\-])')
LOGICAL_PSEUDO = re.compile(r':(?:not|is|where|has|matches|-webkit-any|-moz-any)\(', re.I)


class Reachability:
    def __init__(self, text: str):
        self.names = set(NAME.findall(text))
        self.prefixes = tuple(sorted(set(JOINED_PREFIX.findall(text)), key=len))

    @classmethod
    def from_build(cls, root: Path) -> 'Reachability':
        parts = []
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            if path.suffix.lower() in {'.html', '.htm'}:
                text = STYLE_BLOCK.sub(' ', text)
            parts.append(text)
        return cls('\n'.join(parts))

    def reachable(self, name: str) -> bool:
        return name in self.names or name.startswith(self.prefixes)


def _skip_string(css: str, i: int) -> int:
    quote = css[i]
    i += 1
    while i < len(css) and css[i] != quote:
        i += 2 if css[i] == '\\' else 1
    return i + 1


def _matching(css: str, i: int, open_ch: str, close_ch: str) -> int:
    """Index just past the bracket that closes the one at css[i]."""
    depth = 0
    while i < len(css):
        ch = css[i]
        if ch in '"\'':
            i = _skip_string(css, i)
            continue
        if css.startswith('/*', i):
            end = css.find('*/', i + 2)
            i = len(css) if end < 0 else end + 2
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(css)


def _split_top(selector: str) -> list:
    parts, depth, start, i = [], 0, 0, 0
    while i < len(selector):
        ch = selector[i]
        if ch in '"\'':
            i = _skip_string(selector, i)
            continue
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(selector[start:i])
            start = i + 1
        i += 1
    parts.append(selector[start:])
    return parts


def _required_part(selector: str) -> str:
    """The selector without logical pseudo-classes and attribute selectors."""
    out, i = [], 0
    while i < len(selector):
        m = LOGICAL_PSEUDO.match(selector, i)
        if m:
            i = _matching(selector, m.end() - 1, '(', ')')
            continue
        if selector[i] == '[':
            i = _matching(selector, i, '[', ']')
            continue
        if selector[i] in '"\'':
            i = _skip_string(selector, i)
            continue
        out.append(selector[i])
        i += 1
    return ''.join(out)


def selector_reachable(selector: str, reach: Reachability) -> bool:
    selector = re.sub(r'/\*.*?\*/', ' ', selector, flags=re.S)
    if '\\' in selector:
        return True
    return all(reach.reachable(name) for name in SELECTOR_NAME.findall(_required_part(selector)))


class Pruner:
    def __init__(self, reach: Reachability):
        self.reach = reach
        self.removed_bytes = 0
        self.removed_rules = 0
        self.trimmed_rules = 0
        self.removed_selectors = []

    def prune(self, css: str) -> str:
        out, i, n = [], 0, len(css)
        while i < n:
            ch = css[i]
            if css.startswith('/*', i):
                end = css.find('*/', i + 2)
                end = n if end < 0 else end + 2
                out.append(css[i:end])
                i = end
                continue
            if ch.isspace() or ch in ';}':
                out.append(ch)
                i += 1
                continue
            # A statement runs to the first top-level "{" or ";".
            j, depth = i, 0
            while j < n:
                c = css[j]
                if c in '"\'':
                    j = _skip_string(css, j)
                    continue
                if css.startswith('/*', j):
                    end = css.find('*/', j + 2)
                    j = n if end < 0 else end + 2
                    continue
                if c in '([':
                    depth += 1
                elif c in ')]':
                    depth -= 1
                elif depth == 0 and c in '{;':
                    break
                j += 1
            if j >= n or css[j] == ';':
                out.append(css[i:j + 1])
                i = j + 1
                continue
            head = css[i:j]
            end = _matching(css, j, '{', '}')
            body = css[j + 1:end - 1]
            stripped = head.strip()
            if stripped.startswith('@'):
                if stripped.lower().startswith(GROUPING_AT_RULES):
                    inner = self.prune(body)
                    if inner.strip():
                        out.append(head + '{' + inner + '}')
                    else:
                        self.removed_bytes += end - i - len(body)  # inner rules already counted
                else:
                    out.append(css[i:end])  # @keyframes, @font-face, @page ...
                i = end
                continue
            alternatives = _split_top(head)
            keep = [alt for alt in alternatives if selector_reachable(alt, self.reach)]
            self.removed_selectors += [alt.strip() for alt in alternatives if alt not in keep]
            if not keep:
                self.removed_rules += 1
                self.removed_bytes += end - i
            elif len(keep) < len(alternatives):
                self.trimmed_rules += 1
                new_head = ','.join(keep)
                lead = len(head) - len(head.lstrip())
                new_head = head[:lead] + new_head.strip() + (' ' if head.endswith(' ') else '')
                self.removed_bytes += len(head) - len(new_head)
                out.append(new_head + '{' + body + '}')
            else:
                out.append(css[i:end])
            i = end
        return ''.join(out)

    def prune_html(self, html: str) -> str:
        return STYLE_BLOCK.sub(lambda m: m.group(1) + self.prune(m.group(2)) + m.group(3), html)


def prune_build(root: Path, files=None, report_only=False) -> Pruner:
    pruner = Pruner(Reachability.from_build(root))
    targets = [Path(f) for f in files] if files else [root / 'index.html', *sorted((root / 'redesign').glob('*.css'))]
    for path in targets:
        text = path.read_text(encoding='utf-8')
        before = pruner.removed_bytes
        pruned = pruner.prune_html(text) if path.suffix.lower() in {'.html', '.htm'} else pruner.prune(text)
        if pruned != text and not report_only:
            path.write_text(pruned, encoding='utf-8')
        print(f'{path}: -{(pruner.removed_bytes - before) / 1024:.1f} KB')
    return pruner


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('build', type=Path, help='built web root whose sources decide what is reachable')
    parser.add_argument('--files', nargs='*', help='CSS or HTML files to prune (default: the build index.html and redesign/*.css)')
    parser.add_argument('--report', action='store_true', help='report without writing')
    parser.add_argument('--list', type=Path, help='write the removed selectors to this file, one per line')
    args = parser.parse_args()
    if not (args.build / 'index.html').is_file():
        sys.exit(f'{args.build}/index.html not found')
    pruner = prune_build(args.build, args.files, args.report)
    if args.list:
        args.list.write_text('\n'.join(dict.fromkeys(pruner.removed_selectors)) + '\n', encoding='utf-8')
    print(f'UNREACHABLE_CSS_{"FOUND" if args.report else "PRUNED"} rules={pruner.removed_rules} '
          f'trimmed={pruner.trimmed_rules} kb={pruner.removed_bytes / 1024:.1f}')


if __name__ == '__main__':
    main()
