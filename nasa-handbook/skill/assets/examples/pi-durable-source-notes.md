# Pi-Durable — source notes

## Scope

- Subject: `@earendil-works/pi-durable`, `packages/durable` in [earendil-works/pi](https://github.com/earendil-works/pi).
- Exact inspected main snapshot: [`479d6e5e298821088cfd77566a139097e73a888b`](https://github.com/earendil-works/pi/commit/479d6e5e298821088cfd77566a139097e73a888b), 27 October 2026, 08:16:49 PDT. Manifest version: **1.4.0**. README labels the API **experimental**.
- Report prepared **27 October 2026**, America/Los_Angeles. Source Date identifies the snapshot, not a release or project-origin date.
- The source snapshot defines the report. The published npm tarball was not verified. Source and selected tests were read; package tests, code samples and benchmarks were not run.
- Ten substantive A4 sheets cover architecture, integration, transactions, task states, recovery, replay, nested calls, conversation admission, observability and operations. Snippets are host compositions of verified APIs, not standalone executed examples.

## Per-sheet evidence map

| Sheet | Subject | Reference IDs |
|---|---|---|
| 1 | Scope, architecture, durable/provisional paths | A1–A3, B1, B7 |
| 2 | Open/submit/wait/close; cancellation | A1, A4, B1–B2 |
| 3 | Entries, documents, commit and storage contracts | A2, A5, B1, B3 |
| 4 | States, outcomes, phase progress and owned work | A6, B4–B5 |
| 5 | Recovery, parking, clocks and host wake | A4, A7, B5–B6 |
| 6 | Tool intent, interrupted execution and replay | A8, B7 |
| 7 | Nested receipts, registry and environment | A8–A10, B7–B8 |
| 8 | Busy admission, deduplication, reset and fork | A4, A11–A13, B2, B9 |
| 9 | Deferred progress, compaction, retries, usage and telemetry | A1, A5, A14–A16, B10–B12 |
| 10 | Backends, diagnosis and runbook | A17, B1–B3, B5–B8 |

## Pinned reference legend

All links pin the same commit. Paths are relative to `packages/durable/` unless they begin `packages/`.

### A1 — Package identity; experimental API; minimal integration; Context and telemetry

[`package.json:2–4`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/package.json#L2-L4); [`README.md:1–97`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L1-L97).

### A2 — Concepts, entry/document/task distinctions and atomic commits

[`README.md:99–117`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L99-L117); [`src/types.ts:403–449`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/types.ts#L403-L449).

### A3 — Harness extends Session; guarded storage and scheduler dependencies

[`src/harness/harness.ts:205–269`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/harness.ts#L205-L269).

### A4 — Persistence, requestId, sleep and recovery entry points

[`README.md:119–137`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L119-L137); [`src/harness/harness.ts:299–306`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/harness.ts#L299-L306); [`src/harness/submissions.ts:95–118`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/submissions.ts#L95-L118).

### A5 — Application documents, deferral and usage

[`README.md:732–766`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L732-L766); [`src/documents.ts:136–188`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/documents.ts#L136-L188).

### A6 — Six task states and five outcomes

[`src/types.ts:568–649`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/types.ts#L568-L649).

### A7 — Sleep, clock injection, alarms, parking and failed-run queues

[`README.md:139–222`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L139-L222).

### A8 — Tool intent, result channels, nested calls and callers

[`README.md:245–367`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L245-L367); [`src/harness/tool.ts:136–198`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/tool.ts#L136-L198).

### A9 — Registry installation and live code replacement

[`README.md:225–243`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L225-L243); [`README.md:462–470`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L462-L470).

### A10 — Execution environment and identity/path serialization

[`README.md:427–460`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L427-L460).

### A11 — Busy policy, writes and transcript placement

[`README.md:499–530`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L499-L530).

### A12 — Reset and handoff

[`README.md:532–545`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L532-L545); [`src/harness/harness.ts:135–142`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/harness.ts#L135-L142).

### A13 — New conversations and forks

[`README.md:622–631`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L622-L631).

### A14 — Structural watches, observers, folding and progress

[`README.md:472–497`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L472-L497).

### A15 — Manual and automatic compaction

[`README.md:547–585`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L547-L585).

### A16 — Derived agent events, telemetry and usage

[`README.md:80–95`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L80-L95); [`README.md:587–602`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L587-L602); [`README.md:760–766`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L760-L766).

### A17 — Backend tradeoffs, ownership and shared SQLite queue

[`README.md:768–813`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L768-L813).

### B1 — Commit staging, settlement, storage adoption and read-error boundary

[`src/session/session.ts:831–966`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/session/session.ts#L831-L966); [`src/types.ts:1223–1244`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/types.ts#L1223-L1244); [`src/session/transaction.ts:725–773`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/session/transaction.ts#L725-L773).

### B2 — Submission admission/deduplication, wait/abort and cancellation

[`src/harness/submissions.ts:68–134`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/submissions.ts#L68-L134); [`src/harness/submissions.ts:185–276`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/submissions.ts#L185-L276); [`src/harness/types.ts:775–801`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/types.ts#L775-L801).

### B3 — SQLite adoption, WAL/NORMAL and JSONL sidecar/marker durability

[`src/storage/sqlite/storage.ts:187–211`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/storage/sqlite/storage.ts#L187-L211); [`packages/chord/src/sqlite/node.ts:196–209`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/chord/src/sqlite/node.ts#L196-L209); [`src/storage/jsonl/storage.ts:278–308`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/storage/jsonl/storage.ts#L278-L308); [`src/storage/jsonl/storage.ts:788–805`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/storage/jsonl/storage.ts#L788-L805).

### B4 — Task definition/runtime contract and phase progress

[`src/types.ts:244–363`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/types.ts#L244-L363); [`src/harness/scheduler.ts:1838–1887`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/scheduler.ts#L1838-L1887).

### B5 — Recovery running→pending, parking, retry, ownership drain and abort/orphan handling

[`src/harness/scheduler.ts:377–453`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/scheduler.ts#L377-L453); [`src/harness/scheduler.ts:794–897`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/scheduler.ts#L794-L897); [`src/harness/scheduler.ts:1554–1578`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/scheduler.ts#L1554-L1578); [`src/harness/scheduler.ts:1970–1995`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/scheduler.ts#L1970-L1995).

### B6 — Clock/timer/wake/read-only contract; inspection and retry signatures

[`src/harness/types.ts:650–730`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/types.ts#L650-L730); [`src/harness/types.ts:816–857`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/types.ts#L816-L857); [`src/harness/harness.ts:299–358`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/harness.ts#L299-L358).

### B7 — Final intent; both replay policies; nested call identity and receipts

[`src/harness/tool.ts:136–224`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/tool.ts#L136-L224); [`src/harness/tool.ts:395–422`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/tool.ts#L395-L422); [`src/harness/tool.ts:655–677`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/tool.ts#L655-L677); [`src/harness/tool.ts:709–799`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/tool.ts#L709-L799).

### B8 — Registry resolution, built-ins, selected names and current environment

[`src/harness/agent.ts:184–335`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/agent.ts#L184-L335); [`src/harness/harness.ts:562–585`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/harness.ts#L562-L585); [`src/harness/types.ts:623–648`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/types.ts#L623-L648); [`src/harness/tool.ts:315–320`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/tool.ts#L315-L320).

### B9 — Fork history and agent state; reset admission; provider identity

[`src/session/forks.ts:25–94`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/session/forks.ts#L25-L94); [`src/harness/agent.ts:43–52`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/agent.ts#L43-L52); [`src/harness/harness.ts:135–142`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/harness.ts#L135-L142); [`src/harness/provider.ts:6–24`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/provider.ts#L6-L24).

### B10 — Deferred publication and default intervals; watch delivery limits

[`src/harness/agent.ts:34–38`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/agent.ts#L34-L38); [`src/harness/types.ts:531–546`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/types.ts#L531-L546); [`src/session/session.ts:929–966`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/session/session.ts#L929-L966); [`README.md:491–497`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L491-L497); [`README.md:587–602`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L587-L602).

### B11 — Compaction/retry defaults and overflow route

[`src/harness/agent.ts:20–32`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/agent.ts#L20-L32); [`src/harness/generation.ts:563–602`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/generation.ts#L563-L602); [`README.md:547–585`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L547-L585).

### B12 — Telemetry attributes/diagnostics and usage accounting

[`README.md:80–95`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L80-L95); [`src/harness/telemetry.ts:103–116`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/telemetry.ts#L103-L116); [`src/harness/scheduler.ts:1815–1828`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/src/harness/scheduler.ts#L1815-L1828); [`README.md:760–766`](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/README.md#L760-L766).

## Verified constants and boundaries

| Report fact | Evidence | Interpretation |
|---|---|---|
| Source manifest 1.4.0 | A1 | Not proof of npm contents. |
| Six task states | A6 | pending, running, waiting, sleeping, completing, terminal. |
| Five outcomes | A6 | completed, failed, aborted, orphaned, faulted. Terminality does not promise unlimited retention. |
| Restart limit 5 | B5; `src/harness/agent.ts:57–62` | Cutoffs without changed task state; progress-only writes do not reset it; clean close does not count. |
| Generation maxRetries 3; base delay 2000 ms | B11 | Durable model retries, not total HTTP attempts. |
| Partial/output intervals 100 ms; persistence target 1000 ms | B10 | Minimum publication pauses/nominal storage target, not guaranteed cadence or hard loss bound. |
| Compaction reserve 16384, recent 20000, background 32768 tokens | B11 | Defaults; provider/model overrides exist; recent count is approximate. |
| Structural watch replacement beyond 10,000 pending operations | A14, B10 | Slow consumers receive newest state, not every historical callback. |
| Event adapter snapshot beyond 100 pending batches | A16, B10 | Derived state stream, not a durable event ledger. |
| Error diagnostic cap 500 characters | A16, B12 | Diagnostic text may contain caller content despite payload-free normal attributes. |
| Unsafe replay default; saved AND current policy must be safe | B7 | Re-executes implementation with saved final arguments; not a restored stack or proven external idempotency. |

## Interpretation and deliberate abstraction

- Architecture boxes show responsibilities, not deployment units. Harness extends Session; the drawing does not assert separate processes. Model/tool I/O occurs outside the atomic storage batch.
- Normal stored commit order is stage/settle → storage → adopt → publish. Eligible deferred document progress is memory-first. Durable decisions must not depend on unflushed progress outside a commit that reads it.
- State diagram selects transitions rather than enumerating every edge. Waiting/sleeping reserve directly into running when eligible. Completing holds an outcome while ordinary owned work drains and runs no more task code.
- Missing definitions normally block live work. Explicit abort with unavailable definition/migration can orphan it. Parking is a derived blocked reason, not a seventh TaskState.
- `watchTaskGraph` includes blocked reasons in current code. README's sentence claiming otherwise is stale; inspected [test/harness-blocked.test.ts:156–167](https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/test/harness-blocked.test.ts#L156-L167) confirms restart-limit blocking on graph nodes.
- Tool crash trace is ordinal, not a measured timeline. Local intent/effect/result are not one transaction. Suggested operation keys and compare-and-set are host/tool design techniques, not built-in remote guarantees.
- Completed nested receipts can be reused even when the child tool is unsafe. Unfinished children follow their own saved/current replay policies. Full nested results live in the parent's documents until it settles; no perpetual-result retention is claimed.
- API snippets assume supplied `context`, `models`, registry, modelRef and handles as described. `modelRef` denotes a host-selected available pi-ai model. Sheet 5 assumes a fresh open storage adapter, not reuse of one already closed. `render` and `send` on sheet 9 are host functions.
- `harness.inspect(context)` reads diagnostics without scheduling; waits and submit can start the scheduler. `harness.submission(id, context)` reacquires an existing admission. `reset()` resolves on admission, not necessarily placement of a queued reset.
- Request IDs deduplicate within one conversation before busy policy, even if repeated input content differs; they are not external-effect keys. Do not recycle IDs for new work. Fork signature takes an options object containing ownership.
- Conversation abort covers ordinary work by default; background roots require explicit inclusion. Close signals and joins code, so an implementation ignoring cancellation can delay close. Neither abort nor close proves external rollback.
- JSONL optional fsync flushes sidecars before marker append; source does not explicitly flush every marker immediately. It flushes main before sidecar reclamation. No blanket power-loss guarantee is inferred.
- SQLite NORMAL supports process-crash recovery but may lose newest commits after host/power loss. Browser retention, backend media durability and exclusive ownership remain host responsibilities.
- One owner is an application contract, not a lease. Read-only mode prevents Harness writes/recovery; it is not an OS immutable connection or automatic replication of another writer.
- Overflow compaction and one retry require enabled compaction and a valid cut. Ordinary retry policy does not retry a context-overflow error. Failed blocking compaction can fail generation before another model request.
- Page/section/table/figure numbers, document number and art codes are handbook furniture, not package versions or agency authorship. No performance or exactly-once guarantee is claimed.

## Reproduction and validation

- Authoring: `pi-durable.html`; fonts resolve through `../fonts/` in the skill assets. Original template CSS, font declarations, shared marker definitions and canonical standalone fit script are retained unchanged; a separate report-layout style block sets prose/code/table spacing. Body and code remain 8 pt; SVG labels are at least 2.05 mm. Code inherits the body serif family with zero letter spacing. Letter Gothic appears only on the operating checklist.
- With Chrome/Chromium available, render: `sh <skill>/scripts/render.sh <out>/pi-durable.html --timeout 90`. Set `CHROME=/path/to/chrome` only if discovery needs it.
- With PyMuPDF available, check: `python3 <skill>/scripts/check.py <out>/pi-durable.pdf --pages 10 --out <out>/review`. Here `<skill>` is the nasa-handbook skill directory and `<out>` contains the report.
- Content: approximately 4750 words excluding repeated page furniture, including snippets, tables and figure labels.
- Outputs: `pi-durable.pdf`; `pi-durable-1.png` through `pi-durable-10.png`; separate `pi-durable-overview.png`; `pi-durable.png` is the first-page preview. The contact sheet is not included in the PDF.
- Automated validation: exactly ten A4 pages (209.9 × 297.0 mm as measured), pure source black/white ink, expected body/drawing/checklist font families, no reported overflow. Content/footer clearances by sheet: 7.3, 7.0, 8.8, 9.4, 8.6, 6.3, 7.4, 8.6, 9.6, 6.6 mm.
- Visual review: all eighty 300 dpi detail tiles inspected; no blocking findings. Page overviews and the separate contact sheet were reviewed. Diagram arrowheads, alternate-case labels, table wrapping, code, running furniture and footer clearance are clear.
