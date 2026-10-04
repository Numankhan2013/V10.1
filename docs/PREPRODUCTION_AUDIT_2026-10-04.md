# Preproduction audit and main-domain release

The user explicitly requests an app-wide UI/UX/function/security audit, confirmed
repairs and production promotion through `https://nk-qbank.pages.dev`.
The accepted appearance, source-native presenters, scoring, FSRS, stored state,
cloud account isolation, navigation and haptics remain protected.

## Evidence and findings

A fresh running capture covers122 states at320/390/820px, including simulated
larger phone text. Seven contact sheets were inspected before changes. The
Ophthalmology/source browser suite separately covers390/820/1194/1440px.
This is a bounded audit of the main surfaces and security-sensitive code,
with behavioral checks beyond screenshots. It is not a claim of exhaustive
penetration testing, WCAG certification or physical-device acceptance.

| Area | Evidence | Finding and resulting behavior |
|---|---|---|
| Home, banks, modules, topics | Fresh Home/module/topic captures | Preserve hierarchy, stable deep-topic selection and full-width reading. At320px, Topic index extends beyond the viewport and filter labels crowd. Header title now yields space to all44px controls; filters retain readable labels, selected position, keyboard focus and pressed-state semantics. |
| Account creation | Synthetic-config phone/tablet/desktop forms; all APIs blocked | Back from password previously returned to sign-in, losing the email step. It now returns to the email step with the address retained, focuses that input, and clears password fields. Back from email still returns to sign-in. Dark account-action text on purple is corrected to white. |
| Practice, CBT, Review, Revision, FSRS | Fresh question/answer/grids/analysis and existing behavioral suites | Preserve immediate answering, scoring, Pause/Finish and continuous Revision. Dedicated FSRS previously offered an enabled zero-card action; it now clearly disables unavailable work, distinguishes a completed daily limit and keeps available work labeled Review due. Scheduling/admission rules are unchanged. |
| Notes, Search, Insights, source figures | Fresh captures plus stored-HTML browser probe | Preserve source-faithful reading, image zoom, Search and analytics. A harmless HTML/event-handler payload saved as a learner note renders as literal text across Practice and My notes, without executing. No broad explanation or visual redesign is introduced. |
| Cloud/auth/source serving | Owner-rule review; live unauthenticated Firestore read rejected HTTP403; source/credential review | Owner-scoped rules and account-switch journals remain intact. No private-key/GitHub-token/AWS-key pattern was found in the scanned tracked source/config files. Packaged PDF.js reports6.3.289. Authentication passwords are not retained by the Back flow. No live account is created or signed into during the audit. |
| Hosted responses | Existing preview has no frame restrictions; Worker/static response tests | One shared policy adds CSP frame-ancestors none, X-Frame-Options DENY, nosniff and strict-origin-when-cross-origin. It applies to static assets, streamed PDF ranges, redirects/errors and Worker fallthrough without changing bodies, source URLs, validators or cache/offline behavior. |
| Android WebView | Native Activity/build-owner review and real emulator assertions | Completed starts previously still registered the migration bridge and allowed file access; private asset failures could fall through to networking. Migration now owns those capabilities only until completion. Missing/rejected private assets return local404. Native haptics remain present; initial/repeated emulator launches verify bridge removal and the local failure boundary. |

Account control contrast is a release finding; the remaining confirmed issues
are usability/security hardening findings. There is no unsupported assertion
that a live account was compromised. The final browser confirmation covers
320/390/820/1440px, correct Back/focus/labels, disabled empty review, password
clearing and inert learner text.

## Verification and release

All 103 local checks and focused browser checks pass before publication. The
Ophthalmology candidate4b23940 passes full37188960243, including Android
phone/tablet emulators, and Engineering37188960230/37188962652. The initial37187979431 run was cancelled after a
stale eight-bank test expectation; the corrected check derives the count from
the registry and verifies each UWorld collection explicitly.

Final main product `315cfcccc2a0d830aa851fbd136f3e8d14e215e8` passes
Engineering [37191000202](https://github.com/Numankhan2013/V10.1/actions/runs/37191000202)
and complete [37191000207](https://github.com/Numankhan2013/V10.1/actions/runs/37191000207),
including production APK identity, package/media/offline checks, the focused audit
browser suite and Android phone/tablet emulators. PR98 is merged.

The automatic workflow-run upload did not start. The user-authorized recovery
branch `release/approved-production-20261004` pins the successful main SHA and
artifact run; it makes no product change or rebuild. Approved production [release 37192960486](https://github.com/Numankhan2013/V10.1/actions/runs/37192960486)
verifies current main, manifest commit, APK hash and packaged HTML identity, then
reuses the exact successful artifact without rebuilding. It sets the Pages
production branch to main and uploads successfully. The live primary domain is
**https://nk-qbank.pages.dev**. The historical `main.nk-qbank.pages.dev`
preview alias remains on an older build and is not the production URL. The immutable
upload is https://92774e98.nk-qbank.pages.dev.

Actual root HTML equals the hash measured by the final CI browser suite:
`086b04f41fcf610af844b76652b7c6368392dc26d9bd8f609b258b2a6e77897b`.
Root HTML/configuration/service worker/UWorld inventory/robots bytes equal the
immutable upload from the verified artifact. All 283 UWorld images are downloaded
from the root and match their packaged inventory hashes and offline paths;
all 206 prior media identities remain unchanged. Streamed Anatomy PDF byte ranges,
security/crawler headers and SPA fallback policy pass. A real foreign-origin
iframe attempt is rejected by the browser's frame policy.

Fresh Android contexts use the driver's existing one-retry reattachment path;
completed-start bridge removal, native haptics and local missing-asset checks pass.
The first migration document is not claimed to have no JavaScript bridge symbol
before a new document is loaded. No physical cold-start timing is measured.

The actual root passes four-width UWorld source/read/answer/statistics/zoom/table/
CBT/Review/Pause/Continue/module/Search flows, four-width audit repairs and phone/
tablet Search and reference-focus checks. Browser contexts use isolated local
state; account checks use synthetic configuration with API calls blocked.
The local environment cannot download the 893 MB artifact through its network
proxy, and the connector's 512 MB ceiling also rejects it. Artifact identity is
therefore established by the release workflow's exact-artifact checks, the CI
HTML hash and byte comparison against that same immutable upload; no local APK
archive download is claimed.

Authenticated live-account and physical-device testing require user usage;
server access conclusions are limited to the inspected rules and observed
anonymous denial. Source-review limits remain in the UWorld collection reports.
Search exclusion continues to be indexing guidance, not access control.
