#!/usr/bin/env python3
"""Check an exact release artifact before the existing main-domain uploader runs."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify(root, release_sha):
    root = root.resolve()
    web = root / 'build/web'
    assert (web / 'index.html').is_file(), 'Missing verified web artifact'
    web_manifest = root / 'build/NK-QBank-web-manifest.json'
    if web_manifest.is_file():
        manifest = json.loads(web_manifest.read_text())
        assert manifest['schema'] == 1 and manifest['platform'] == 'web'
        assert manifest['git_commit'] == release_sha, 'Artifact commit mismatch'
        paths = set()
        total = 0
        for item in manifest['files']:
            path = (root / item['path']).resolve()
            assert path.is_relative_to(web.resolve()), 'Artifact path outside web directory'
            assert path not in paths, 'Duplicate artifact path'
            paths.add(path)
            assert path.is_file() and path.stat().st_size == item['bytes'], 'Artifact size mismatch'
            assert digest(path) == item['sha256'], 'Artifact hash mismatch'
            total += item['bytes']
        assert paths == {p.resolve() for p in web.rglob('*') if p.is_file()}, 'Unmanifested or missing web assets'
        assert web / 'sw.js' in paths and web / 'index.html' in paths, 'Missing PWA entry points'
        assert total == manifest['total_bytes'], 'Artifact byte count mismatch'
        return 'web'
    # Earlier approved releases used the combined Android/PWA artifact.
    manifest = json.loads((root / 'app/build/outputs/apk/debug/NK-QBank-build-manifest.json').read_text())
    assert manifest['git_commit'] == release_sha, 'Artifact commit mismatch'
    apks = [item for item in manifest['files'] if item['path'].endswith('.apk')]
    assert len(apks) == 1, 'Expected one verified APK'
    apk = root / apks[0]['path']
    assert digest(apk) == apks[0]['sha256'], 'APK hash mismatch'
    index = next(item for item in manifest['files'] if item['path'] == 'app/src/main/assets/index.html')
    with zipfile.ZipFile(apk) as archive:
        assert hashlib.sha256(archive.read('assets/index.html')).hexdigest() == index['sha256'], 'Packaged app mismatch'
    return 'android'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-sha', required=True)
    args = parser.parse_args()
    print('APPROVED_MAIN_ARTIFACT_OK', args.release_sha, verify(Path.cwd(), args.release_sha))
