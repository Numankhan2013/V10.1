#!/usr/bin/env python3
"""Install additive Firebase sync, account UI, and responsive PWA metadata."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/cross_device_sync_core.js"

CSS = r'''<style id="nk-cross-device-pwa-v1">
.nk-cloud-card{display:grid;gap:13px}.nk-cloud-card label{display:grid;gap:6px;color:var(--muted);font-size:11px;font-weight:800}.nk-cloud-card input{width:100%;min-height:46px;border:1px solid var(--line);border-radius:12px;padding:0 13px;background:var(--surface);color:var(--ink);font:inherit}.nk-cloud-card input:focus{outline:3px solid rgba(63,207,232,.22);border-color:var(--primary)}.nk-cloud-actions{display:flex;gap:9px;flex-wrap:wrap}.nk-cloud-actions button{min-height:44px;border:1px solid var(--line);border-radius:12px;padding:0 16px;background:var(--surface);font-weight:800;color:var(--ink)}.nk-cloud-actions .primary-btn{background:var(--primary);border-color:var(--primary);color:#073943}.nk-cloud-user{display:flex;align-items:center;gap:10px}.nk-cloud-user div{display:grid;gap:3px}.nk-cloud-user small{color:var(--muted)}.nk-cloud-dot{width:11px;height:11px;border-radius:50%;background:#a9adba;box-shadow:0 0 0 5px rgba(169,173,186,.14)}.nk-cloud-dot.is-online{background:var(--success);box-shadow:0 0 0 5px rgba(21,154,104,.13)}.nk-cloud-dot.is-error{background:var(--error);box-shadow:0 0 0 5px rgba(214,75,88,.12)}.nk-cloud-pwa{padding-top:11px;border-top:1px solid var(--line);font-size:11px;line-height:1.5;color:var(--muted)}
@media (min-width:768px){body{background:#eef1f6}.app-shell{min-height:100vh;padding-left:88px}.topbar{left:88px!important;width:calc(100% - 88px)!important}.bottom-nav{position:fixed!important;left:0!important;right:auto!important;top:0!important;bottom:0!important;width:88px!important;height:100vh!important;display:flex!important;flex-direction:column!important;justify-content:center!important;gap:8px!important;padding:18px 8px calc(18px + env(safe-area-inset-bottom))!important;border-top:0!important;border-right:1px solid var(--line)!important}.nav-item{width:72px!important;min-height:66px!important;border-radius:15px!important;flex:none!important}.nav-item.active{background:rgba(63,207,232,.13)!important}.page{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 22px 54px!important}.dashboard-v10,.nk-app-v114{max-width:none!important}.more-card-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.nk-study-set-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.nk-module-topic-groups{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}.question-card{padding:24px}.question-text{font-size:20px;line-height:1.58}.option-text{font-size:16px}.feedback-body{font-size:15px}.source-pdf-scroll{max-width:100%}}
@media (min-width:1024px) and (orientation:landscape){.question-shell{grid-template-columns:minmax(0,1.55fr) minmax(310px,.75fr)!important;gap:20px}.navigator{position:sticky!important;top:82px!important;align-self:start}.dashboard-v10>.dashboard-section.grid-2{grid-template-columns:1.15fr .85fr}.nk-module-builder-card{padding:24px!important}}
@media (display-mode:standalone){body{overscroll-behavior:none}.topbar{padding-top:env(safe-area-inset-top)}.page{padding-bottom:calc(38px + env(safe-area-inset-bottom))!important}}
</style>'''

META = '''<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#135262">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NK QBank">
<link rel="apple-touch-icon" href="qbank-icon-192.png">
<script src="qbank-config.js"></script>
<script type="module" src="web_pdf_renderer.mjs"></script>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise SystemExit(f"{label}: expected one anchor, found {source.count(old)}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if "NK_CROSS_DEVICE_SYNC_V1_START" in source:
        print("Cross-device/PWA layer already installed")
        return source

    source = replace_once(source, "</head>", META + "\n" + CSS + "\n</head>", "head metadata")
    source = source.replace("location.protocol !== 'file:'", "location.hostname !== 'qbank.local'", 1)
    native_source = r'''    const url=seg=>`https://qbank.local/${subject}/pdf?page=${encodeURIComponent(seg.page)}&scale=4${seg.top!=null?`&top=${encodeURIComponent(seg.top)}`:''}${seg.bottom!=null?`&bottom=${encodeURIComponent(seg.bottom)}`:''}`;
    return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source solution · ${label}</div>${segments.map(seg=>`<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector('img'))"><img loading="lazy" src="${url(seg)}" data-source-page="${seg.page}" alt="Original ${label} PDF solution page ${seg.page}"></div>`).join('')}<div class="source-pdf-note">Original PDF rendering only. No explanation text is parsed or reconstructed.</div></div></div>`;'''
    adaptive_source = r'''    if(location.hostname!=='qbank.local')return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source solution · ${label}</div>${segments.map(seg=>`<div class="source-pdf-page nk-web-pdf-segment" data-subject="${subject}" data-page="${seg.page}" data-top="${seg.top??''}" data-bottom="${seg.bottom??''}"><canvas aria-label="Original ${label} PDF solution page ${seg.page}"></canvas><div class="nk-web-pdf-status">Loading original source…</div></div>`).join('')}<div class="source-pdf-note">Rendered locally from the original PDF. No explanation text is reconstructed.</div></div></div>`;
    const url=seg=>`https://qbank.local/${subject}/pdf?page=${encodeURIComponent(seg.page)}&scale=4${seg.top!=null?`&top=${encodeURIComponent(seg.top)}`:''}${seg.bottom!=null?`&bottom=${encodeURIComponent(seg.bottom)}`:''}`;
    return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source solution · ${label}</div>${segments.map(seg=>`<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector('img'))"><img loading="lazy" src="${url(seg)}" data-source-page="${seg.page}" alt="Original ${label} PDF solution page ${seg.page}"></div>`).join('')}<div class="source-pdf-note">Original PDF rendering only. No explanation text is parsed or reconstructed.</div></div></div>`;'''
    if native_source not in source:
        raise SystemExit("final source-solution renderer anchor not found")
    source = source.replace(native_source, adaptive_source, 1)
    source = replace_once(
        source,
        "    localStorage.setItem('qbank_active_subject_v1',activeSubject);",
        "    localStorage.setItem('qbank_active_subject_v1',activeSubject);\n    if(typeof nkScheduleCloudSync==='function')nkScheduleCloudSync();",
        "subject persistence hook",
    )
    source = replace_once(
        source,
        "    try { nkSyncModuleFromSession(); localStorage.setItem(LS_KEY, JSON.stringify(state)); }\n    catch (e) { showToast('Progress could not be saved on this device.', 'bad'); }",
        "    try { nkSyncModuleFromSession(); localStorage.setItem(LS_KEY, JSON.stringify(state)); if(typeof nkScheduleCloudSync==='function')nkScheduleCloudSync(); }\n    catch (e) { showToast('Progress could not be saved on this device.', 'bad'); }",
        "save hook",
    )
    source = replace_once(
        source,
        '<section class="nk-settings-group"><div class="nk-kicker">APP & SOURCE</div>',
        '${nkCloudAccountCard()}\n      <section class="nk-settings-group"><div class="nk-kicker">APP & SOURCE</div>',
        "More account card",
    )
    reset_pattern = re.compile(r"function resetProgress\(\)\{ if\(confirm\('Reset all local QBank progress,[^\n]+\}\}")
    hit = reset_pattern.search(source)
    if not hit:
        raise SystemExit("reset progress function not found")
    reset = "function resetProgress(){if(nkAuth){showToast('Sign out before resetting this device. Your cloud copy will remain safe.','bad');return;}if(confirm('Reset all local QBank progress, bookmarks, review schedules, modules, and test history on this device? The source questions will remain.')){state=defaultState();saveState();navigate('dashboard');showToast('Local progress reset.');}}"
    source = source[: hit.start()] + reset + source[hit.end() :]

    # Preserve sync metadata through module normalization and distinguish an intentional restart.
    source = source.replace(
        "resultTestId:module.resultTestId?String(module.resultTestId):null\n    };",
        "resultTestId:module.resultTestId?String(module.resultTestId):null,\n      syncEpoch:String(module.syncEpoch||`epoch_${module.createdAt||Date.now()}`),updatedAt:Number(module.updatedAt||module.lastOpenedAt||module.createdAt||Date.now())\n    };",
        1,
    )
    source = source.replace(
        "completedAt:null,isCompleted:false,resultTestId:null});",
        "completedAt:null,isCompleted:false,resultTestId:null,syncEpoch:`epoch_${now}`,updatedAt:now});",
        1,
    )
    source = source.replace(
        "module.completedQuestionIds=[];module.currentPosition=0;",
        "module.syncEpoch=`epoch_${Date.now()}_${Math.random().toString(36).slice(2)}`;module.updatedAt=Date.now();module.completedQuestionIds=[];module.currentPosition=0;",
        1,
    )

    export_match = re.search(r"window\.QB=\{([^\n]+)\};", source)
    if not export_match:
        raise SystemExit("Canonical QB export not found")
    exports = export_match.group(1)
    additions = "nkCloudAuthenticate,nkCloudSignOut,nkCloudSyncNow,"
    if "nkCloudAuthenticate" not in exports:
        exports = additions + exports
        source = source[: export_match.start(1)] + exports + source[export_match.end(1) :]

    core = CORE.read_text(encoding="utf-8")
    export_pos = source.find("  window.QB={")
    if export_pos < 0:
        raise SystemExit("QB export insertion point not found")
    source = source[:export_pos] + core + "\n" + source[export_pos:]
    source = replace_once(source, "  render();\n})();", "  render();\n  nkCloudInit();\n})();", "cloud boot")

    # Browser source visuals use same-origin generated assets; Android retains its asset URL.
    renderer = ROOT / "app/src/main/assets/source_visual_renderer.js"
    if renderer.exists():
        text = renderer.read_text(encoding="utf-8")
        old = "if(v.type==='asset'&&v.source)return 'file:///android_asset/'+String(v.source).replace(/^\\/+/, '');"
        new = "if(v.type==='asset'&&v.source)return (location.hostname==='qbank.local'?'/app/':'./')+String(v.source).replace(/^\\/+/, '');"
        if old in text:
            renderer.write_text(text.replace(old, new, 1), encoding="utf-8")

    required = ["NK_CROSS_DEVICE_SYNC_V1_START", "nkCloudAccountCard()", "qbank-config.js", "manifest.webmanifest", "nkCloudInit();", "nkCloudAuthenticate,nkCloudSignOut,nkCloudSyncNow", "syncEpoch"]
    missing = [marker for marker in required if marker not in source]
    if missing:
        raise SystemExit(f"Cross-device/PWA markers missing: {missing}")
    return source


def main() -> None:
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("CROSS_DEVICE_PWA_OK: local-first Firebase sync, safe migration, account UI, and adaptive tablet shell installed")


if __name__ == "__main__":
    main()
