#!/usr/bin/env python3
"""Generate the Geist redesign colour/shape mapping layer (redesign/nk-theme.css).

The legacy app paints itself through ~50 versioned style layers with hard-coded
violet/indigo hex values.  Instead of editing those layers, the redesign maps
every colour, gradient, shadow, radius and font declaration they contain onto
the neutral semantic tokens in ``redesign/nk-tokens.css``.  Each generated rule
repeats the legacy selector behind ``html[data-nk-ui="geist"]`` so it always
out-ranks the rule it re-skins, and only applies when the redesign is active.

Input is a JSON dump of the generated build's CSSOM (selector, media context and
longhand declarations), produced by loading the built ``index.html`` in a
browser and walking ``document.styleSheets``.  Regenerate whenever the legacy
style layers change:

    python3 tools/redesign_generate_theme_css.py legacy_rules.json \
        app/src/main/assets/redesign/nk-theme.css

This script is a design-time generator; it is not part of the build pipeline
and never touches ``index.html``.
"""
from __future__ import annotations

import colorsys
import json
import re
import sys
from pathlib import Path

ROOT_ATTR = '[data-nk-ui="geist"]'
SCOPE = 'html' + ROOT_ATTR

# --------------------------------------------------------------------------- colour parsing
NAMED = {
    'white': (255, 255, 255, 1.0), 'black': (0, 0, 0, 1.0),
    'transparent': (0, 0, 0, 0.0),
}
COLOR_RE = re.compile(r'rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b|\b(?:white|black)\b')


def parse_color(text: str):
    text = text.strip().lower()
    if text in NAMED:
        return NAMED[text]
    if text.startswith('#'):
        h = text[1:]
        if len(h) in (3, 4):
            h = ''.join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return r, g, b, a
    m = re.match(r'rgba?\(([^)]*)\)', text)
    if not m:
        return None
    parts = [p for p in re.split(r'[\s,/]+', m.group(1).strip()) if p]
    try:
        r, g, b = (float(parts[i].rstrip('%')) for i in range(3))
        a = float(parts[3].rstrip('%')) / (100 if parts[3].endswith('%') else 1) if len(parts) > 3 else 1.0
    except (ValueError, IndexError):
        return None
    return r, g, b, a


def family(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hue = h * 360
    if s < 0.14 or l < 0.10 or l > 0.975:
        fam = 'neutral'
    elif 80 <= hue < 175:
        fam = 'green'
    elif hue >= 335 or hue < 14:
        fam = 'red'
    elif 14 <= hue < 34 and s > 0.45:
        fam = 'orange'
    elif 34 <= hue < 62:
        fam = 'amber'
    else:  # blue, teal, indigo, violet, magenta: decorative identity -> neutral
        fam = 'neutral'
    # Desaturated status hues used as text/ink are really neutrals.
    if fam != 'neutral' and s < 0.28 and 0.15 < l < 0.85:
        fam = 'neutral'
    return fam, l, s


def alpha_wrap(token: str, a: float) -> str:
    if a >= 0.995:
        return f'var({token})'
    if a <= 0.005:
        return 'transparent'
    return f'color-mix(in srgb, var({token}) {round(a * 100)}%, transparent)'


def map_color(text: str, role: str) -> str:
    c = parse_color(text)
    if c is None:
        return text
    r, g, b, a = c
    if a <= 0.005:
        return 'transparent'
    fam, l, s = family(r, g, b)
    if fam != 'neutral':
        status = 'amber' if fam == 'orange' and role in ('bg', 'border') else fam
        if role in ('text', 'icon'):
            tok = f'--nkg-{status}' if l < 0.80 else f'--nkg-{status}-border'
        elif role == 'bg':
            tok = (f'--nkg-{status}-bg' if l >= 0.86 else
                   f'--nkg-{status}-border' if l >= 0.72 else f'--nkg-{status}')
        else:  # border / shadow ring
            tok = f'--nkg-{status}-border' if l >= 0.70 else f'--nkg-{status}'
        return alpha_wrap(tok, a)
    # Neutral (includes every violet/indigo/blue identity colour).
    if role in ('text',):
        if l >= 0.80:
            tok = '--nkg-inverse-fg'
        elif l < 0.30:
            tok = '--nkg-fg'
        elif l < 0.47:
            tok = '--nkg-fg-2'
        else:
            tok = '--nkg-fg-3'
        # Saturated mid-tone identity colours (violet links, indigo labels) read as ink.
        if s > 0.35 and 0.30 <= l < 0.62:
            tok = '--nkg-fg'
        return alpha_wrap(tok, a)
    if role == 'icon':
        if l >= 0.93:
            tok = '--nkg-surface'
        elif l >= 0.80:
            tok = '--nkg-border'
        elif l < 0.30 or (s > 0.35 and l < 0.62):
            tok = '--nkg-fg'
        elif l < 0.55:
            tok = '--nkg-fg-2'
        else:
            tok = '--nkg-fg-3'
        return alpha_wrap(tok, a)
    if role == 'bg':
        if a < 0.5 and l >= 0.9:
            # Translucent white washes sit on dark (inverse) panels.
            return alpha_wrap('--nkg-inverse-fg', a)
        if l >= 0.985:
            tok = '--nkg-surface'
        elif l >= 0.955:
            tok = '--nkg-bg-subtle'
        elif l >= 0.90:
            tok = '--nkg-surface-2'
        elif l >= 0.80:
            tok = '--nkg-active'
        elif l >= 0.58 and s < 0.5:
            tok = '--nkg-border-strong'
        else:
            tok = '--nkg-inverse-bg'
        return alpha_wrap(tok, a)
    # border
    if l >= 0.80:
        tok = '--nkg-border'
    elif l >= 0.55 and s < 0.45:
        tok = '--nkg-border-strong'
    else:
        tok = '--nkg-fg'
    return alpha_wrap(tok, a)


def map_colors_in(value: str, role: str) -> str:
    return COLOR_RE.sub(lambda m: map_color(m.group(0), role), value)


# --------------------------------------------------------------------------- declaration mapping
ROLE = {
    'color': 'text', '-webkit-text-fill-color': 'text', 'caret-color': 'text',
    'text-decoration-color': 'text', 'accent-color': 'text',
    'background-color': 'bg', 'fill': 'icon', 'stroke': 'icon', 'stop-color': 'icon',
    'outline-color': 'border', 'column-rule-color': 'border',
    'border-top-color': 'border', 'border-right-color': 'border',
    'border-bottom-color': 'border', 'border-left-color': 'border',
}
# Shorthands are only captured when they hold var(...) with literal fallbacks
# (CSSOM leaves their longhands empty); only the fallbacks are remapped.
SHORTHAND_ROLE = {
    'background': 'bg', 'border': 'border', 'border-top': 'border', 'border-right': 'border',
    'border-bottom': 'border', 'border-left': 'border', 'border-color': 'border', 'outline': 'border',
}
ROLE.update({k: v for k, v in SHORTHAND_ROLE.items()})
ELEVATED = re.compile(r'modal|sheet|toast|dialog|popover|menu|dropdown|navigator|overlay|drawer|picker', re.I)


def split_top(value: str, sep=','):
    out, depth, cur = [], 0, ''
    for ch in value:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    out.append(cur)
    return [p.strip() for p in out if p.strip()]


def map_shadow(value: str, selector: str) -> str:
    if value in ('none', 'initial', 'inherit', 'unset') or 'var(' in value:
        return value
    keep = []
    for part in split_top(value):
        inset = 'inset' in part
        nums = re.findall(r'(-?[\d.]+)px', COLOR_RE.sub('', part))
        nums = [float(n) for n in nums] + [0.0] * 4
        ox, oy, blur = nums[0], nums[1], nums[2]
        if inset or (ox == 0 and oy == 0 and blur == 0):
            keep.append(map_colors_in(part, 'border'))
    if keep:
        return ', '.join(keep)
    return 'var(--nkg-shadow-lg)' if ELEVATED.search(selector) else 'none'


GRADIENT = re.compile(r'(repeating-)?(linear|radial|conic)-gradient\(')


def map_background_image(value: str):
    """Returns (background-image, background-color or None)."""
    if not GRADIENT.search(value):
        return value, None
    if 'url(' in value:
        return map_colors_in(value, 'bg'), None
    structural = ('transparent' in value or 'repeating-' in value or 'conic-' in value
                  or re.search(r'rgba\([^)]*,\s*0\)', value))
    if structural:
        return map_colors_in(value, 'bg'), None
    if value.lstrip().startswith('radial-gradient') and value.count('gradient(') == 1:
        return 'none', None  # decorative glow
    first = COLOR_RE.search(value)
    return 'none', (map_color(first.group(0), 'bg') if first else None)


def map_radius(value: str) -> str:
    def one(m):
        n = float(m.group(1))
        if n >= 500:
            return m.group(0)
        if n > 24:
            return '16px'
        if n > 12:
            return '12px'
        return m.group(0)
    return re.sub(r'([\d.]+)px', one, value)


def custom_role(name: str, value: str):
    n = name.lower()
    if re.search(r'shadow|halo|glow|spread', n):
        return 'shadow'
    if re.search(r'line|border|divider|rail|stroke|outline', n):
        return 'border'
    if re.search(r'paper|canvas|surface|bg|selection|fill|track|heat0|soft', n):
        return 'bg'
    if re.search(r'muted|secondary|ink|text|fg|label', n):
        return 'text'
    if re.search(r'success|green|danger|red|warning|amber|good|bad|error', n):
        return 'icon'
    if re.search(r'primary|action|indigo|violet|brand|accent|blue|magenta|purple', n):
        return 'accent'
    return None


def map_custom(name: str, value: str):
    if not COLOR_RE.search(value):
        return None
    role = custom_role(name, value)
    if re.search(r'tone-bg|tone-paper', name):
        return 'var(--nkg-surface-2)'  # subject tone tiles stay neutral; the glyph carries identity
    if re.search(r'tone-line|tone-border', name):
        return 'var(--nkg-border)'
    if 'var(' in value:
        return map_colors_in(value, {'shadow': 'border', 'accent': 'icon', None: 'icon'}.get(role, role))
    if role == 'shadow':
        return 'none' if re.search(r'\dpx', value) else 'transparent'
    if GRADIENT.search(value):
        img, color = map_background_image(value)
        return color or img
    if role == 'accent':
        c = parse_color(value)
        if c and len(COLOR_RE.findall(value)) == 1 and value.strip() == COLOR_RE.search(value).group(0):
            fam, l, s = family(*c[:3])
            if fam == 'neutral':
                if l >= 0.9:
                    return alpha_wrap('--nkg-surface-2', c[3])
                return alpha_wrap('--nkg-fg', c[3])
            return map_color(value, 'icon')
        return map_colors_in(value, 'icon')
    if role is None:
        c = parse_color(COLOR_RE.search(value).group(0))
        role = 'bg' if c and colorsys.rgb_to_hls(*(x / 255 for x in c[:3]))[1] > 0.7 else 'text'
    return map_colors_in(value, role)


def map_decl(prop: str, value: str, selector: str):
    v = value.strip()
    if v in ('initial', 'inherit', 'unset', 'currentcolor', 'currentColor', 'revert'):
        return None
    if prop.startswith('--'):
        return map_custom(prop, v)
    if 'var(' in v and prop in ROLE:
        out = map_colors_in(v, ROLE[prop])  # only var() fallbacks change
        return out if out != v else None
    if 'var(' in v and prop not in ('box-shadow',):
        return None  # resolved through the remapped custom properties
    if prop in ROLE:
        out = map_colors_in(v, ROLE[prop])
        return out if out != v else None
    if prop == '-webkit-tap-highlight-color':
        return 'transparent'
    if prop == 'scrollbar-color':
        return 'var(--nkg-border-strong) transparent'
    if prop == 'box-shadow':
        if 'var(' in v:
            return None
        out = map_shadow(v, selector)
        return out if out != v else None
    if prop == 'text-shadow':
        return 'none' if v != 'none' else None
    if prop == 'background-image':
        img, _ = map_background_image(v)
        return img if img != v else None
    if prop.endswith('radius'):
        out = map_radius(v)
        return out if out != v else None
    if prop == 'font-family':
        if 'mono' in v.lower():
            return 'var(--nkg-font-mono)'
        if v == 'inherit':
            return None
        return 'var(--nkg-font-sans)'
    if prop == 'font-weight':
        # Geist reads best at 400-600: heavy legacy weights settle to semibold.
        try:
            return '600' if int(v) > 600 else None
        except ValueError:
            return '600' if v in ('bold', 'bolder') else None
    if prop in ('filter',) and 'drop-shadow' in v:
        return re.sub(r'drop-shadow\([^()]*(\([^()]*\)[^()]*)*\)', '', v).strip() or 'none'
    return None


# --------------------------------------------------------------------------- selectors
def scope_selector(sel: str) -> str:
    out = []
    for s in split_top(sel):
        if s.startswith(':root'):
            out.append(':root' + ROOT_ATTR + s[5:])
        elif re.match(r'html(?![\w-])', s):
            out.append('html' + ROOT_ATTR + s[4:])
        else:
            out.append(SCOPE + ' ' + s)
    return ', '.join(out)


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else 'legacy_rules.json')
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else 'app/src/main/assets/redesign/nk-theme.css')
    rules = json.loads(src.read_text())
    blocks: list[tuple[tuple, str]] = []
    count = 0
    for rule in rules:
        sel = rule['sel']
        decls = {}
        bg_color = None
        changed = False
        for prop, value, prio in rule['d']:
            mapped = map_decl(prop, value, sel)
            if prop == 'font-weight' and mapped is None:
                continue  # weights are only emitted where they change
            if prop == 'background-image' and GRADIENT.search(value) and 'var(' not in value:
                _, bg_color = map_background_image(value)
            if mapped is None:
                # Re-emit unchanged so the scoped copies keep the legacy cascade order.
                mapped = value
            else:
                changed = True
            decls[prop] = (mapped, prio)
        if bg_color and decls.get('background-color', ('initial',))[0] in ('initial', 'transparent', 'rgba(0, 0, 0, 0)'):
            prio = next((p for pr, v, p in rule['d'] if pr == 'background-image'), '')
            decls['background-color'] = (bg_color, prio)
        # Every colour/shape rule is emitted (even unchanged ones) so specificity
        # ties resolve exactly as they did between the legacy layers.
        if not decls:
            continue
        body = ';'.join(f'{p}:{v}{" !important" if pr == "important" else ""}' for p, (v, pr) in decls.items())
        blocks.append((tuple(rule['ctx']), f'{scope_selector(sel)}{{{body}}}'))
        count += 1
    lines = ['/* GENERATED by tools/redesign_generate_theme_css.py — do not edit by hand.',
             '   Maps every legacy colour/shape declaration onto the Geist tokens (redesign/nk-tokens.css).',
             '   Active only while <html data-nk-ui="geist">. */']
    cur: tuple = ()
    for ctx, css in blocks:
        if ctx != cur:
            lines.extend('}' for _ in cur)
            lines.extend(c + '{' for c in ctx)
            cur = ctx
        lines.append(css)
    lines.extend('}' for _ in cur)
    dst.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'REDESIGN_THEME_CSS_OK rules={count} bytes={dst.stat().st_size}')


if __name__ == '__main__':
    main()
