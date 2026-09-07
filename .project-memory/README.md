# Project Memory Schema

This directory is the canonical, harness-neutral memory for NK QBank.
Start at the repository-root `AGENTS.md`; harness-specific instruction files
must only point there and to `STATE.md`.

## File roles

- `STATE.md` — concise current handoff: branch lineage, verification status,
  working state, known issues, and immediate next action. Replace stale facts;
  do not append history indefinitely.
- `PRODUCT.md` — stable product intent, protected behavior, design principles,
  and non-goals.
- `ARCHITECTURE.md` — verified implementation shape, integration points, and
  build/runtime contracts.
- `DECISIONS.md` — durable decisions and their reasoning.
- `ROADMAP.md` — future work and completed milestones that affect priority.
- `SESSION_LOG.md` — append-only factual history of substantial sessions.

## Truth and conflict order

1. The checked-out repository and live Git/GitHub state.
2. `STATE.md` for the latest written handoff.
3. The other role-specific files above.
4. Legacy `memory.md` and historical documentation.

When written memory disagrees with executable reality, verify the repository
and correct memory in the same change. Never infer device verification from CI.

## Update protocol

- At session start, resolve the live branch and HEAD with Git. Do not hardcode
  a field claiming to be the current HEAD: committing that field changes HEAD.
- Use explicit labels: implemented, build-verified, device-verified, accepted.
- Update only files whose role changed; always refresh `STATE.md` after
  substantial work and append a short `SESSION_LOG.md` entry.
- Keep adapters thin and knowledge-free.
- Run `python3 tools/verify_project_memory.py` before committing memory changes.

No documentation scheme can force every possible tool to load repository
instructions. The committed adapters cover the common harness conventions;
the integrity check protects placement, links, role separation, and drift-prone
patterns once the repository is loaded.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

