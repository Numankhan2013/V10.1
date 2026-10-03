# Search-engine exclusion

PWA packaging emits `robots.txt` with `User-agent: *` / `Disallow: /`, an HTML
robots meta tag, and a global `X-Robots-Tag` header requesting `noindex`,
`nofollow`, `noarchive`, `nosnippet` and `noimageindex`. The Pages worker adds
the same header to streamed Anatomy PDF responses, errors, and every static or
dynamic asset fallthrough. Source bytes, HTTP ranges, validators, cache rules,
offline use and account-state synchronization remain unchanged.

These are instructions for cooperating search engines, not access control or
copyright protection. Public GitHub files/history, downloadable app assets and
direct source-storage URLs remain publicly accessible; this deployment cannot
set GitHub or an upstream storage service's search policy. Removing already
indexed links may require the search engine's removal tools; blocking crawling
can prevent a crawler from discovering a new `noindex` instruction.

Before broader content rollout, keep licensed source content in private storage
and repositories, confirm the permitted personal-use scope, and use server-side
access control if downloads must be restricted. A client-side gate or obfuscated
bundle would not protect bundled content. This change deliberately introduces
no authentication architecture or false promise of content protection.

`tools/test_crawler_exclusion.py` builds isolated fixture distributions with and
without the PDF bridge and exercises real worker responses, including ranges,
conditional/HEAD requests, static assets, fallback routes and errors. Hosted
response-header verification is still required for each deployed candidate.
