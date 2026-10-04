"""A web build must hash every shipped asset and refuse missing core files."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
import write_build_manifest as manifest
from approved_release_artifact import verify


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        web = root/'build/web'
        web.mkdir(parents=True)
        files = {'index.html':b'<html>Reviewed content</html>', 'sw.js':b'// worker',
                 'source_visuals/uworld/plot.png':b'source pixels'}
        for name, raw in files.items():
            path = web/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        with patch.object(manifest,'ROOT',root), patch('sys.argv',['manifest','--web-only']), patch.dict(os.environ,{'GITHUB_SHA':'a'*40}):
            with contextlib.redirect_stdout(io.StringIO()):
                manifest.main()
            actual = json.loads((root/'build/NK-QBank-web-manifest.json').read_text())
            assert actual['platform'] == 'web' and actual['git_commit'] == 'a'*40
            assert actual['total_bytes'] == sum(len(b) for b in files.values())
            assert {f['path']:f['sha256'] for f in actual['files']} == {
                'build/web/'+n:hashlib.sha256(b).hexdigest() for n,b in files.items()}
            assert verify(root, 'a'*40) == 'web'
            def rejected(label):
                try:
                    verify(root, 'a'*40)
                except AssertionError:
                    return
                raise AssertionError(label + ' accepted for production')
            (web/'source_visuals/uworld/plot.png').write_bytes(b'changed pixels')
            rejected('Modified media')
            (web/'source_visuals/uworld/plot.png').write_bytes(files['source_visuals/uworld/plot.png'])
            (web/'extra.js').write_bytes(b'unverified')
            rejected('Unverified extra file')
            (web/'extra.js').unlink()
            for key, value in [('git_commit','b'*40), ('total_bytes',0)]:
                bad = {**actual, key:value}
                (root/'build/NK-QBank-web-manifest.json').write_text(json.dumps(bad))
                rejected('Incorrect '+key)
            bad = {**actual, 'files':[{**actual['files'][0], 'path':'../outside.html'}]}
            (root/'build/NK-QBank-web-manifest.json').write_text(json.dumps(bad))
            rejected('Out-of-directory file')
            (root/'build/NK-QBank-web-manifest.json').write_text(json.dumps(actual))
            (web/'sw.js').unlink()
            rejected('Missing service worker')
            try:
                manifest.main()
            except SystemExit as error:
                assert 'missing' in str(error)
            else:
                raise AssertionError('Incomplete PWA accepted')
    print('WEB_BUILD_MANIFEST_OK assets=all production_hash_commit_paths=verified missing_worker=rejected apk_required=false')


if __name__ == '__main__':
    main()
