#!/usr/bin/env python3
"""Contract checks for the Android shell, the service worker and the web build.

The Android side cannot be compiled in this environment, so the Java shell is
checked against its source contract; the service worker is driven for real.

- the manifest must not allow the app's data directory to be backed up, and
  must name data-extraction rules that exclude every domain from both cloud
  backup and device-to-device transfer;
- the WebView must only hand http, https, mailto and tel links to the system,
  and the native bridges must only answer while the app origin is in front;
- the WebChromeClient must answer confirm() and prompt() with a native dialog,
  declared as members of the class rather than inside another method;
- a cached PDF byte range must keep the cached response's headers;
- the web build must fail when a required generated asset is missing.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
RULES = ROOT / "app/src/main/res/xml/nk_data_extraction_rules.xml"
ACTIVITY = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
SW = ROOT / "app/src/main/assets/sw.js"
WEB_BUILD = ROOT / "tools/build_web_dist.py"

DOMAINS = (
    "root",
    "file",
    "database",
    "sharedpref",
    "external",
    "device_root",
    "device_file",
    "device_database",
    "device_sharedpref",
)

RANGE_RUNTIME = r"""
const assert=require('assert'),fs=require('fs');
const SOURCE=fs.readFileSync(process.argv[2],'utf8');
// Take the shipped range responder out of the service worker.
const start=SOURCE.indexOf('async function rangeResponse(request){');
assert(start>=0,'the service worker must have a range responder');
let depth=0,i=SOURCE.indexOf('{',start),j=i;
for(;j<SOURCE.length;j++){if(SOURCE[j]==='{')depth++;else if(SOURCE[j]==='}'){depth--;if(depth===0)break;}}
const rangeResponse=eval('('+SOURCE.slice(start,SOURCE.indexOf('}',j)+1)+')');

// A cached full PDF that carries the security headers of the hosted response.
const cachedHeaders=new Headers({
  'Content-Type':'application/pdf',
  'Content-Security-Policy':"default-src 'none'",
  'X-Content-Type-Options':'nosniff',
  'X-Frame-Options':'DENY',
  'Referrer-Policy':'no-referrer',
  'Cache-Control':'public, max-age=31536000',
});
global.caches={match:async()=>({status:200,headers:cachedHeaders,blob:async()=>new Blob([new Uint8Array(1000)])})};
global.fetch=async()=>{throw new Error('the cache must answer the range request');};
global.Response=Response;
global.Headers=Headers;

(async()=>{
  const response=await rangeResponse(new Request('https://x.test/a.pdf',{headers:{range:'bytes=0-99'}}));
  assert.equal(response.status,206,'a cached range must answer 206');
  assert.equal(response.headers.get('content-security-policy'),"default-src 'none'",'the cached CSP must survive');
  assert.equal(response.headers.get('x-content-type-options'),'nosniff','the cached MIME protection must survive');
  assert.equal(response.headers.get('x-frame-options'),'DENY','the cached frame protection must survive');
  assert.equal(response.headers.get('referrer-policy'),'no-referrer','the cached referrer policy must survive');
  assert.equal(response.headers.get('content-type'),'application/pdf','the content type must survive');
  assert.equal(response.headers.get('content-range'),'bytes 0-99/1000','the range must be correct');
  assert.equal(response.headers.get('content-length'),'100','the length must be correct');
  console.log('SW_RANGE_HEADERS_OK security_headers=preserved');
})().catch(error=>{console.error('SW_RANGE_HEADERS_FAIL:',error&&error.message);process.exit(1);});
"""


def check_manifest() -> None:
    manifest = MANIFEST.read_text(encoding="utf-8")
    assert 'android:allowBackup="false"' in manifest, "the app must not be eligible for backup"
    assert 'android:allowBackup="true"' not in manifest, "the app must not be eligible for backup"
    assert "android:dataExtractionRules=" in manifest, "the app must name its data-extraction rules"
    match = re.search(r'android:dataExtractionRules="([^"]+)"', manifest)
    assert match, "the app must name its data-extraction rules"
    assert RULES.is_file(), f"the data-extraction rules are missing: {match.group(1)}"

    rules = RULES.read_text(encoding="utf-8")
    assert "<data-extraction-rules>" in rules, "the rules file must be a data-extraction-rules document"
    for section in ("cloud-backup", "device-transfer"):
        assert f"<{section}>" in rules, f"the rules must cover {section}"
        assert f"</{section}>" in rules, f"the rules must cover {section}"
        body = rules.split(f"<{section}>", 1)[1].split(f"</{section}>", 1)[0]
        for domain in DOMAINS:
            assert f'<exclude domain="{domain}" path="."/>' in body, (
                f"{section} must exclude the {domain} domain"
            )


def check_activity() -> None:
    source = ACTIVITY.read_text(encoding="utf-8")

    # Only the schemes the app means to open may leave the WebView, and the
    # check must run before the intent is fired.
    should = source.split("shouldOverrideUrlLoading", 1)[1].split("onPageCommitVisible", 1)[0]
    assert "String scheme = url.getScheme();" in should, "the shell must check the link scheme"
    for scheme in ("http", "https", "mailto", "tel"):
        assert f'scheme.equals("{scheme}")' in should, f"the shell must allow the {scheme} scheme"
    assert should.index("String scheme = url.getScheme();") < should.index("startActivity("), (
        "the scheme check must run before the link is handed to the system"
    )

    # The native bridges must only answer on the app origin.
    assert "private boolean onAppOrigin()" in source, "the shell must know whether the app origin is in front"
    lines = source.split("\n")
    for method in ("platform()", "theme(boolean isDark)", "toast(String message)", "play(String kind)"):
        index = [n for n, l in enumerate(lines) if method in l and "@JavascriptInterface" in l]
        assert index, f"the bridge method {method} must exist"
        body = "\n".join(lines[index[0]:index[0] + 3])
        assert "onAppOrigin()" in body, f"the bridge method {method} must check the origin"

    # confirm() and prompt() must be answered, and they must be members of the
    # WebChromeClient class rather than nested inside another method.
    for method in ("onJsConfirm", "onJsPrompt"):
        assert f"public boolean {method}(" in source, f"the shell must answer {method}()"
    class_body = source.split("private final class NoteFileChooserClient extends WebChromeClient {", 1)[1]
    chooser = [l for l in class_body.split("\n") if "public boolean onShowFileChooser(" in l]
    confirm = [l for l in class_body.split("\n") if "public boolean onJsConfirm(" in l]
    assert chooser and confirm, "the WebChromeClient must declare both dialog handlers"
    assert chooser[0][: len(chooser[0]) - len(chooser[0].lstrip())] == confirm[0][
        : len(confirm[0]) - len(confirm[0].lstrip())
    ], "the dialog handlers must be class members, not nested inside another method"

    # The Java must still be balanced.
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', source)
    stripped = re.sub(r"//[^\n]*", "", stripped)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.S)
    assert stripped.count("{") == stripped.count("}"), "the Java braces must balance"
    assert stripped.count("(") == stripped.count(")"), "the Java parentheses must balance"


def check_web_build() -> None:
    source = WEB_BUILD.read_text(encoding="utf-8")
    assert "Required generated web assets are missing" in source, (
        "the web build must fail when a required asset is missing"
    )
    assert "biochemistry_source_solution_map.js" in source, (
        "the web build must check the source-solution maps the page loads"
    )


def check_service_worker() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(RANGE_RUNTIME)
        script = Path(handle.name)
    try:
        subprocess.run(["node", str(script), str(SW)], check=True, cwd=ROOT)
    finally:
        script.unlink(missing_ok=True)


def main() -> None:
    check_manifest()
    check_activity()
    check_web_build()
    check_service_worker()
    print("ANDROID_SHELL_CONTRACT_OK backup=excluded schemes=allowlist bridges=origin_gated dialogs=answered")


if __name__ == "__main__":
    main()
