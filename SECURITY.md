# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's
[private vulnerability reporting](https://github.com/Numankhan2013/V10.1/security/advisories/new)
rather than in a public issue or pull request. Include the affected page or file,
steps to reproduce, and the impact you expect.

You can expect an acknowledgement within a week.

## Scope

- The web app built from this repository and its service worker
- Cloud sync code in `app/src/main/modules/cross_device_sync.js` and `firestore.rules`
- The GitHub Actions workflows in `.github/workflows/`

## Design notes

- Each signed-in user can read and write only their own Firestore documents.
- Synced records are treated as untrusted input and validated before they reach
  app state or markup.
- Responses carry a restrictive Content-Security-Policy and related headers,
  defined in `tools/web_security_policy.py`.
- No credentials or signing keys are stored in the repository. Build-time
  configuration comes from GitHub repository variables and secrets.
