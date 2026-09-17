# Klip — Feature Backlog

A roadmap for [klip](src/klip), organized by how much of a reaction each feature earns.
Klip today: JWT auth with refresh-token rotation, snippets with `public`/`unlisted`/`private`
visibility, optional expiry, cursor pagination, and role-gated delete.

Legend: **S** = a sitting, **M** = a weekend, **L** = a real project.

---

## 1. Table Stakes
*The tutorial layer. Nobody says "wow" — but people absolutely notice when it's missing.*

| Feature | Why | Size |
|---|---|---|
| **Unique constraint on `User.email`** | `register_user` guards duplicates with a `SELECT` first, but nothing at the DB level enforces it. Two concurrent signups both win. | S |
| **Empty list ≠ 404** | `/snippet/snippetlist` raises `SnippetNotFound` when you simply have no snippets. An empty page is not an error; return `{snippets: [], cursor: null}`. | S |
| **A test suite** | There is currently none. `pytest` + `httpx.AsyncClient` + a transactional fixture. Nothing else on this page is safe to build without it. | M |
| **Edit / update a snippet** | Create, read, and delete exist. Update does not. | S |
| **Rate limiting** | `/auth/login` and `/auth/register` are unauthenticated and unthrottled — free credential stuffing. Per-IP and per-account buckets. | M |
| **Structured logging + request IDs** | One `X-Request-ID` per request, threaded through logs, echoed in error bodies. The difference between debugging and guessing. | S |
| **Size limits on `body`** | `body` is an unbounded `Text` column. A 2GB POST is currently a valid POST. | S |
| **Pagination on the way in, too** | `limit` is capped by `max_page_size`; `title` and `body` have no length validation in [schemas](src/klip/schemas/snippet.py). | S |
| **Soft delete** | Deletes are hard and immediate. A `deleted_at` column plus a 30-day grace window turns a support ticket into a checkbox. | S |
| **Health check that checks something** | `/health` returns a literal. Make it probe the DB and report migration revision. | S |
| **Docker Compose for the app itself** | Compose runs Postgres only; the API is a manual `uvicorn`. One `docker compose up` should boot the whole thing. | S |
| **CI** | Ruff is configured and currently failing on ~30 findings. Wire it to a GitHub Action so it stays at zero. | S |

---

## 2. Genuinely Great
*Unglamorous to describe, but they're why someone picks Klip over the other paste tool.*

| Feature | Why | Size |
|---|---|---|
| **Syntax highlighting with language auto-detect** | The single biggest perceived-quality jump for a code-sharing tool. Detect on the server at write time, store the language, let the user override. | M |
| **Burn after reading** | One-view snippets that self-destruct on first fetch. The canonical use case for sharing a credential, and it composes perfectly with your existing `expires_at`. | S |
| **Password-protected snippets** | Visibility is currently binary-ish. A per-snippet passphrase (Argon2, same as passwords) adds a tier that doesn't require a Klip account to open. | M |
| **Snippet versions** | Every edit writes a new revision instead of overwriting. Diff any two. Restore any one. | M |
| **Multi-file snippets** | Real bug reports are a config file *and* a stack trace *and* the command. One snippet, several named files, tabbed. | M |
| **Full-text search** | Postgres `tsvector` over `title` + `body` with a GIN index. Your own snippets become a searchable notebook rather than a pile. | M |
| **Folders and tags** | At 200 snippets, a flat reverse-chronological list stops working. | M |
| **Raw endpoint** | `GET /raw/{public_id}` returning `text/plain`. Makes `curl klip.sh/raw/abc \| bash` possible, which is how these tools actually get used. | S |
| **CLI client** | `cat error.log \| klip --expires 1h` copying the URL to the clipboard. The terminal is where snippets are born. | M |
| **API tokens** | Long-lived scoped tokens, separate from the login JWT, so scripts don't need your password. | M |
| **Webhooks** | Fire on create/view/expire. Turns Klip into something other systems can build on. | M |

---

## 3. No Way It Does This
*Demo features. The reaction you're aiming for is a double-take.*

| Feature | Why | Size |
|---|---|---|
| **Runnable snippets** | A sandboxed "Run" button — gVisor or Firecracker, hard CPU/memory/network caps — that executes the snippet and shows stdout inline. Nobody expects a pastebin to *run* the paste. | L |
| **Live collaborative editing** | Two cursors in one snippet over WebSockets with CRDT merge. A pastebin that is quietly also a shared scratchpad. | L |
| **Zero-knowledge encryption** | Encrypt in the browser; the key lives in the URL fragment (`#key=…`), which browsers never transmit. The server stores ciphertext it genuinely cannot read — and you can *prove* it. | M |
| **Self-destruct on screenshot attempt** | Detect devtools-open / PrintScreen / focus-loss heuristics and blur the body. Defeatable in principle, startling in practice. | M |
| **Time-travel share links** | A link that renders the snippet *as it was* at a timestamp, on top of the versions feature. | S |
| **Instant preview rendering** | Detect Markdown, Mermaid, SVG, HTML, CSV, JSON and render it live beside the source. Paste a Mermaid graph, get a diagram. | M |
| **QR for every snippet** | One click puts the snippet on a phone across the room. Trivially cheap, disproportionately impressive. | S |
| **"Explode to gist"** | One button that mirrors a snippet to a real GitHub Gist and keeps them in sync. | M |

---

## 4. Rare Air
*Uncommon in pastebin-class software. Not hard — just almost nobody bothers, which is precisely the opportunity.*

| Feature | Why | Size |
|---|---|---|
| **Secret scanning on paste** | Regex + entropy scan for AWS keys, JWTs, private keys, DB URLs. Warn before publishing, offer one-click redaction. People paste credentials constantly and every pastebin cheerfully accepts them. | M |
| **View receipts** | The owner sees *when* and *from where* their snippet was opened. Standard in DocSend, essentially absent in pastebins — yet you obviously want it when you share a credential. | M |
| **Expiry by view count, not just time** | `expires_at` is a timestamp. `max_views` is a different and often more useful axis. Support both, whichever trips first. | S |
| **Postgres row-level security** | Push the ownership check from [snippet_service](src/klip/services/snippet_service.py) into the database itself, so a bug in the service layer still can't leak another user's rows. Defense in depth almost no app at this scale implements. | M |
| **Signed audit log** | Hash-chained append-only log of every create/view/delete. Tamper-evident by construction. | M |
| **Content-addressed storage** | Key the body by its SHA-256. Ten people pasting the same stack trace store it once. Dedup plus free integrity checking. | M |
| **Deterministic export** | `GET /export` producing a reproducible tarball of everything you own, byte-identical across runs. Real data portability rather than a JSON dump. | M |
| **Abuse-resistant public feed** | A public firehose of `public` snippets with heuristic spam filtering. Every pastebin that has tried this drowned in phishing kits; doing it *well* is genuinely differentiating. | L |
| **Snippet TTL negotiation** | Let the *recipient* request an extension, and the owner approve from a notification. Expiry becomes a conversation instead of a cliff. | M |
| **Offline-first PWA** | Compose and queue snippets with no connection; sync on reconnect. | M |

---

## 5. AI Features
*Ordered by ratio of usefulness to hype. The first three earn their inference cost; the rest are worth prototyping.*

| Feature | Why | Size |
|---|---|---|
| **Auto-title and auto-tag** | Users leave titles blank or type "test". Generate a real title, language tag, and one-line summary at write time. Highest-value, lowest-risk use of a model here. | S |
| **Explain this snippet** | A plain-English walkthrough beside the code. The person receiving a snippet often understands it less well than the sender. | S |
| **Stack-trace triage** | Detect that a paste is an exception; extract the failing frame, likely cause, and a suggested fix. Most pastes of this kind *are* stack traces. | M |
| **Semantic search over your snippets** | Embed each body, store as `pgvector`, search by meaning. "That nginx thing I saved in March" finds it without the keyword. | M |
| **Smarter secret detection** | A model catches what regex misses — a credential in an unusual format, a private hostname, a customer name in a log. Pairs with §4's scanner. | M |
| **Auto-redaction with a diff** | Propose a redacted version alongside the original and let the user accept per-hunk. | M |
| **Diff summarization** | On top of versions: "this revision switches the retry from linear to exponential backoff." | S |
| **Natural-language expiry** | "expire this end of the week" → a real timestamp. Small, but removes the most annoying widget in the form. | S |
| **Snippet Q&A** | Ask a question about a snippet and get an answer grounded in that snippet only. | M |
| **Duplicate detection** | Flag semantically near-identical snippets you already own — an embedding-distance check at write time. | S |
| **Language-to-code** | Describe what you want; get a starting snippet. Well-trodden, and the least differentiated idea on this page — worth listing, worth building last. | M |

---

## Suggested Order

1. **Unblock:** tests, CI, `User.email` unique constraint, empty-list-≠-404.
2. **Earn the name:** syntax highlighting, raw endpoint, edit, burn-after-reading.
3. **Differentiate:** secret scanning, view receipts, zero-knowledge encryption.
4. **Then AI:** auto-title, explain, semantic search — on top of a codebase that has tests.
