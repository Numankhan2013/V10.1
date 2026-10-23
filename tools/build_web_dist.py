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
from prune_unreachable_css import prune_build
from web_security_policy import HEADERS, worker_source


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
DEFAULT_OUT = ROOT / "build/web"
# The page the app ships is the one build_app_data.py filled; the source page is
# only a template with data tokens.
BUILT_PAGE = ROOT / "build/app/index.html"
PAGES_FILE_LIMIT = 25 * 1024 * 1024
ROBOTS_DIRECTIVES = "noindex, nofollow, noarchive, nosnippet, noimageindex"


# Explanations are read only once an answer is shown, yet they are three quarters
# of the question data. The web build moves them into per-subject packs that the
# app fetches on demand (modules/question_details.js). The Android shell loads
# this same build.
DETAIL_FIELDS = ("explanation", "structuredExplanation", "provenance", "sourceFidelity", "references")
PRESENTATION = ROOT / "app/src/main/modules/question_presentation.js"


class DetailPacks:
    def __init__(self, out: Path):
        self.out = out
        self.packs: dict[str, dict] = {}
        self.pack_of: dict[str, str] = {}
        # Start-up integrity checks and reviewed rewrites read these questions'
        # explanations, so any question the presentation module names stays whole.
        self.pinned = PRESENTATION.read_text(encoding="utf-8")

    def split(self, key: str, question: dict) -> None:
        qid = str(question.get("id", ""))
        if not qid or f'"{qid}"' in self.pinned or f"'{qid}'" in self.pinned:
            return
        fields = {name: question.pop(name) for name in DETAIL_FIELDS if name in question}
        if not fields:
            return
        pack = self.packs.setdefault(key, {"index": len(self.packs), "q": {}, "gold": {}})
        pack["q"][qid] = fields
        question["detailPack"] = pack["index"]
        self.pack_of[qid] = key

    def split_gold(self, gold: dict) -> None:
        for qid in [qid for qid in gold if qid in self.pack_of]:
            self.packs[self.pack_of[qid]]["gold"][qid] = gold.pop(qid)

    def write(self) -> list[str]:
        names = []
        for key, pack in self.packs.items():
            body = json.dumps({"q": pack["q"], "gold": pack["gold"]}, ensure_ascii=False, separators=(",", ":"))
            slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
            name = f"data/details/{slug}.{hashlib.sha256(body.encode()).hexdigest()[:10]}.json"
            (self.out / name).parent.mkdir(parents=True, exist_ok=True)
            (self.out / name).write_text(body, encoding="utf-8")
            names.append(name)
        return names


def split_script_data(path: Path, packs: DetailPacks) -> None:
    """Split a `window.X = {...};` data script in place."""
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"\s*(window\.\w+)\s*=\s*(\{.*\})\s*;?\s*", text, re.S)
    if not match:
        raise SystemExit(f"{path.name}: unexpected data script shape")
    data = json.loads(match.group(2))
    if "questions" in data:  # Biochemistry PrepLadder
        for question in data["questions"]:
            packs.split("prepladder-biochemistry", question)
    for record in data.get("subjects", []):
        for question in record.get("questions", []):
            packs.split(f"{question.get('bank') or 'PrepLadder'}-{record.get('subject', '')}", question)
    path.write_text(match.group(1) + "=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def externalize_data(page: str, out: Path, packs: DetailPacks | None = None) -> tuple[str, list[str]]:
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
            if packs:
                split_script_data(out / source, packs)
    loaders = []
    for const in ("MARROW_DATA", "NK_MARROW_EXPLANATION_GOLD_V1"):
        match = re.search(r'\n(\s*)const ' + const + r'\s*=\s*(\{.*?\});\n', page)
        if not match:
            continue
        literal = match.group(2)
        data = json.loads(literal)  # fails the build rather than shipping broken data
        if packs and const == "MARROW_DATA":
            for record in data.get("records", [data]):
                for question in record.get("questions", []):
                    packs.split(f"{record.get('bank') or 'Marrow'}-{record.get('subject', '')}", question)
            literal = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        elif packs:
            packs.split_gold(data)
            literal = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
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
    parser.add_argument("--page", type=Path, default=None,
                        help="the filled app page to ship; defaults to build/app/index.html when it exists")
    args = parser.parse_args()
    page_source = args.page if args.page else (BUILT_PAGE if BUILT_PAGE.is_file() else ASSETS / "index.html")
    if not Path(page_source).is_file():
        raise SystemExit(f"the app page to ship is missing: {page_source}")
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    skipped = []
    for source in ASSETS.rglob("*"):
        if not source.is_file():
            continue
        if source == ASSETS / "index.html":
            # The filled page ships instead of the source template.
            continue
        relative = source.relative_to(ASSETS)
        if source.stat().st_size > PAGES_FILE_LIMIT:
            skipped.append(str(relative))
            continue
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # The filled page carries the inline question data until externalize_data
    # moves it out; the output check below covers what it leaves behind.
    shutil.copy2(page_source, out / "index.html")
    config_path=out / "qbank-config.js"
    config=json.loads(re.search(r"=\s*(\{.*\})\s*;",config_path.read_text()).group(1))
    anatomy_url=config.get("anatomyPdfUrl", "")
    if anatomy_url:
        worker=worker_source(anatomy_url)
        (out / "_worker.js").write_text(worker)
        # Only the PDF bridge runs the Worker. Every other request is a free static
        # asset hit, so a script hammering the site cannot spend the Workers quota.
        (out / "_routes.json").write_text(json.dumps({"version":1,"include":["/anatomy-source.pdf"],"exclude":[]}))
        config["anatomyPdfUrl"]="./anatomy-source.pdf"
        config_path.write_text("window.NK_QBANK_FIREBASE_CONFIG = "+json.dumps(config)+";\n")
    html = out / "index.html"
    html.write_text(html.read_text(encoding="utf-8").replace('src="assets/physiology_image_pages.js"', 'src="physiology_image_pages.js"').replace('href="assets/Biochemistry_QBank_Source.pdf"', 'href="Biochemistry_QBank_Source.pdf"'), encoding="utf-8")
    html.write_text(html.read_text(encoding="utf-8").replace('</head>', '<meta name="nk-qbank-build" content="'+html_escape.escape(args.version, quote=True)+'">\n</head>', 1), encoding="utf-8")
    page = html.read_text(encoding="utf-8")
    page = re.sub(r'<meta\b[^>]*\bname\s*=\s*[\"\']robots[\"\'][^>]*>', '', page, flags=re.IGNORECASE)
    packs = DetailPacks(out)
    page, data_files = externalize_data(page, out, packs)
    page = page.replace('</head>', '<script>window.NK_DETAIL_PACKS='+json.dumps(packs.write())+';</script>\n</head>', 1)
    html.write_text(page.replace('</head>', '<meta name="robots" content="'+ROBOTS_DIRECTIVES+'">\n</head>', 1), encoding="utf-8")
    sw = out / "sw.js"
    sw_text=sw.read_text(encoding="utf-8").replace("const BUILD_VERSION='dev';", f"const BUILD_VERSION={args.version!r};", 1)
    data_shell=(
        ['./marrow_visual_metadata.js','./microbiology_visual_metadata.js','./prepladder_microbiology_visual_metadata.js','./prepladder_pathology_visual_metadata.js','./prepladder_pharmacology_visual_metadata.js','./prepladder_biochemistry_visual_metadata.js','./prepladder_physiology_visual_metadata.js','./marrow_visual_renderer.js','./source_visual_inventory.json']
        + ['./'+name for name in data_files]
    )
    # Figures are content-hashed: the worker fills them into a persistent cache
    # in the background instead of blocking installation on every deploy.
    media=(
        ['./'+p.relative_to(out).as_posix() for p in sorted((out/'marrow_visuals').glob('*'))]
        + ['./'+p.relative_to(out).as_posix() for p in sorted((out/'source_visuals').rglob('*')) if p.is_file() and p.suffix != '.webp']
    )
    sw_text=sw_text.replace("const SHELL=[",'const SHELL='+json.dumps(data_shell)[:-1]+',',1)
    sw_text=sw_text.replace("const MEDIA=[];",'const MEDIA='+json.dumps(media)+';',1)
    sw.write_text(sw_text, encoding="utf-8")
    (out / "_headers").write_text(
        "/*\n  X-Robots-Tag: "+ROBOTS_DIRECTIVES+"\n"+
        ''.join('  '+name+': '+value+'\n' for name,value in HEADERS.items())+
        # Pages adds a wildcard CORS header to static assets; nothing here is meant for other origins.
        "  ! Access-Control-Allow-Origin\n"+
        "/sw.js\n  Cache-Control: no-cache\n/index.html\n  Cache-Control: no-cache\n/qbank-config.js\n  Cache-Control: no-cache\n/source_visuals/*\n  Cache-Control: public, max-age=31536000, immutable\n/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        # Content-hashed file names: a new build never reuses a URL.
        "/data/*\n  Cache-Control: public, max-age=31536000, immutable\n/marrow_visuals/*\n  Cache-Control: public, max-age=31536000, immutable\n",
        encoding="utf-8",
    )
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    # Routes live in the URL hash, so there is no SPA fallback: a missing file is
    # a real 404 instead of index.html, which the service worker would cache as that file.
    (out / "404.html").write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="'+ROBOTS_DIRECTIVES+'"><title>Not found</title><p>Not found. <a href="/">Open NK QBank</a></p>\n', encoding="utf-8")
    # Drop CSS that no markup, script or data in the build can ever match, such
    # as rules for legacy screens Geist replaced. The browser suite runs on this output.
    pruned = prune_build(out)
    print(f"UNREACHABLE_CSS_PRUNED rules={pruned.removed_rules} trimmed={pruned.trimmed_rules} kb={pruned.removed_bytes / 1024:.1f}")
    required = ("biochemistry_source_solution_map.js", "subject_source_solution_maps.js")
    missing = [name for name in required if not (out / name).is_file()]
    if missing:
        raise SystemExit(f"Required generated web assets are missing: {', '.join(missing)}")
    if "Anatomy_QBank_Source.pdf" not in skipped:
        raise SystemExit("Expected oversized Anatomy PDF to be excluded from Pages output")
    oversize = [p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file() and p.stat().st_size > PAGES_FILE_LIMIT]
    if oversize:
        raise SystemExit(f"Files over the Cloudflare Pages 25 MiB limit: {oversize}")
    print(f"WEB_DIST_OK files={sum(1 for p in out.rglob('*') if p.is_file())} skipped_oversize={','.join(skipped)}")


if __name__ == "__main__":
    main()
