#!/usr/bin/env python3
"""Create a Cloudflare Pages-ready PWA from the generated Android assets."""

from __future__ import annotations

import argparse
import hashlib
import html as html_escape
import json
import re
import shutil
from pathlib import Path
from web_security_policy import HEADERS, worker_source


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
DEFAULT_OUT = ROOT / "build/web"
PAGES_FILE_LIMIT = 25 * 1024 * 1024
ROBOTS_DIRECTIVES = "noindex, nofollow, noarchive, nosnippet, noimageindex"


def externalize_data(page: str, out: Path) -> tuple[str, list[str]]:
    """Move the large question data out of index.html into cacheable scripts.

    Inline scripts are re-parsed on every launch and never get V8's code cache;
    external ones do. Marrow literals load through JSON.parse (much faster to
    parse than an object literal). Scripts stay synchronous and ahead of the app
    script, so the app sees exactly the same globals at the same time.
    """
    files = []
    for var in ("SUBJECT_QBANK_DATA", "QBANK_DATA"):
        source = {"SUBJECT_QBANK_DATA": "subjects_qbank_data.js", "QBANK_DATA": "qbank_data.js"}[var]
        match = re.search(r'<script>(\s*window\.' + var + r'\s*=.*?)</script>', page, re.S)
        if match and match.group(1).strip() == (out / source).read_text(encoding="utf-8").strip():
            page = page[:match.start()] + f'<script src="{source}"></script>' + page[match.end():]
    loaders = []
    for const in ("MARROW_DATA", "NK_MARROW_EXPLANATION_GOLD_V1"):
        match = re.search(r'\n(\s*)const ' + const + r'\s*=\s*(\{.*?\});\n', page)
        if not match:
            continue
        literal = match.group(2)
        json.loads(literal)  # fails the build rather than shipping broken data
        body = "window.NK_DATA_" + const + "=JSON.parse(" + json.dumps(literal) + ");\n"
        name = f"data/{const.lower()}.{hashlib.sha256(body.encode()).hexdigest()[:10]}.js"
        (out / "data").mkdir(exist_ok=True)
        (out / name).write_text(body, encoding="utf-8")
        files.append(name)
        loaders.append(f'<script src="{name}"></script>')
        page = page[:match.start()] + "\n" + match.group(1) + f"const {const} = window.NK_DATA_{const};\n" + page[match.end():]
    if loaders:
        anchor = page.index("const MARROW_DATA = window.NK_DATA_MARROW_DATA;") if "NK_DATA_MARROW_DATA" in page else None
        at = page.rindex("<script", 0, anchor) if anchor else page.index("</head>")
        page = page[:at] + "\n".join(loaders) + "\n" + page[at:]
    return page, files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--version", default="dev")
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    skipped = []
    for source in ASSETS.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(ASSETS)
        if source.stat().st_size > PAGES_FILE_LIMIT:
            skipped.append(str(relative))
            continue
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    config_path=out / "qbank-config.js"
    config=json.loads(re.search(r"=\s*(\{.*\})\s*;",config_path.read_text()).group(1))
    anatomy_url=config.get("anatomyPdfUrl", "")
    if anatomy_url:
        worker=worker_source(anatomy_url)
        (out / "_worker.js").write_text(worker)
        # Pages _headers rules do not apply to Worker-generated responses.
        # Route all paths through the bridge so fallthrough/error responses
        # receive the same search-engine exclusion as static assets.
        (out / "_routes.json").write_text(json.dumps({"version":1,"include":["/*"],"exclude":[]}))
        config["anatomyPdfUrl"]="./anatomy-source.pdf"
        config_path.write_text("window.NK_QBANK_FIREBASE_CONFIG = "+json.dumps(config)+";\n")
    html = out / "index.html"
    html.write_text(html.read_text(encoding="utf-8").replace('src="assets/physiology_image_pages.js"', 'src="physiology_image_pages.js"').replace('href="assets/Biochemistry_QBank_Source.pdf"', 'href="Biochemistry_QBank_Source.pdf"'), encoding="utf-8")
    html.write_text(html.read_text(encoding="utf-8").replace('</head>', '<meta name="nk-qbank-build" content="'+html_escape.escape(args.version, quote=True)+'">\n</head>', 1), encoding="utf-8")
    page = html.read_text(encoding="utf-8")
    page = re.sub(r'<meta\b[^>]*\bname\s*=\s*[\"\']robots[\"\'][^>]*>', '', page, flags=re.IGNORECASE)
    page, data_files = externalize_data(page, out)
    html.write_text(page.replace('</head>', '<meta name="robots" content="'+ROBOTS_DIRECTIVES+'">\n</head>', 1), encoding="utf-8")
    sw = out / "sw.js"
    sw_text=sw.read_text(encoding="utf-8").replace("const BUILD_VERSION='dev';", f"const BUILD_VERSION={args.version!r};", 1)
    image_shell=(
        ['./marrow_visual_metadata.js','./marrow_visual_renderer.js','./source_visual_inventory.json']
        + ['./'+name for name in data_files]
        + ['./'+p.relative_to(out).as_posix() for p in sorted((out/'marrow_visuals').glob('*'))]
        + ['./'+p.relative_to(out).as_posix() for p in sorted((out/'source_visuals').rglob('*')) if p.is_file() and p.suffix != '.webp']
    )
    sw_text=sw_text.replace("const SHELL=[",'const SHELL='+json.dumps(image_shell)[:-1]+',',1)
    sw.write_text(sw_text, encoding="utf-8")
    (out / "_headers").write_text(
        "/*\n  X-Robots-Tag: "+ROBOTS_DIRECTIVES+"\n"+
        ''.join('  '+name+': '+value+'\n' for name,value in HEADERS.items())+
        "/sw.js\n  Cache-Control: no-cache\n/index.html\n  Cache-Control: no-cache\n/qbank-config.js\n  Cache-Control: no-cache\n/source_visuals/*\n  Cache-Control: public, max-age=31536000, immutable\n/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n",
        encoding="utf-8",
    )
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "_redirects").write_text("/* /index.html 200\n", encoding="utf-8")
    if "Anatomy_QBank_Source.pdf" not in skipped:
        raise SystemExit("Expected oversized Anatomy PDF to be excluded from Pages output")
    print(f"WEB_DIST_OK files={sum(1 for p in out.rglob('*') if p.is_file())} skipped_oversize={','.join(skipped)}")


if __name__ == "__main__":
    main()
