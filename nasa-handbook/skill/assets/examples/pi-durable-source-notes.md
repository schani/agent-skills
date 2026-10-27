# Pi-Durable report — source notes

## Scope

- Package: `@earendil-works/pi-durable`, repository [earendil-works/pi](https://github.com/earendil-works/pi), `packages/durable`.
- Inspected source: commit [`479d6e5e298821088cfd77566a139097e73a888b`](https://github.com/earendil-works/pi/commit/479d6e5e298821088cfd77566a139097e73a888b), a main-branch snapshot, 27 October 2026, 08:16:49 PDT.
- Source manifest version: **1.4.0**. README marks the API **experimental**. This report does not establish that the published npm tarball contains this commit.
- Report Date is this report's preparation date. Change Date identifies the source snapshot date, not the package's first release or first commit. Dates use America/Los_Angeles.
- Code and documentation were inspected; package tests were not run. No performance measurements are claimed.

## Checked claims

Paths below are relative to `packages/durable/` at the pinned commit. The report author read these code ranges directly, with the factfinder's dossier as a cross-check.

| Report claim | Checked source |
|---|---|
| Package identity and source version | `package.json:2–4`; experimental status `README.md:3` |
| Harness/Session boundary; scheduler receives guarded storage, model access, registry and environment | `src/harness/harness.ts:215–257` |
| Normal commits settle writes, call Storage and publish during adoption | `src/session/session.ts:831–899`, especially `879–899` |
| SQLite batches entries/documents/task writes in a transaction, then adopts after COMMIT | `src/storage/sqlite/storage.ts:187–211` |
| Live progress may be observed before storage | `src/session/session.ts:929–960`; `src/harness/types.ts:531–546` |
| Progress persistence default is 1000 ms; nominal window, not hard latency/loss guarantee | `src/harness/agent.ts:34–38`; `src/harness/types.ts:531–546` |
| Tool validates and stores intent, final arguments and default unsafe policy before execution | `src/harness/tool.ts:136–179`, especially `169–179` |
| Recovery reruns only when stored and current tool policies both say safe; otherwise reports interrupted/may have partially run | `src/harness/tool.ts:181–198` |
| Six durable task states | `src/types.ts:605–649`: pending, running, waiting, sleeping, completing, terminal |
| Five terminal outcome kinds | `src/types.ts:568–602`: completed, failed, aborted, orphaned, faulted |
| Generation retry budget 3; base delay 2000 ms | `src/harness/agent.ts:20–25` |
| Default restart parking threshold 5 cutoffs without changed state | `src/harness/agent.ts:57–62`; `src/harness/scheduler.ts:379–408,1982–1995` |
| Reopen changes running to pending while preserving checkpoint; dispatch starts separately | `src/harness/scheduler.ts:379–434`; `src/harness/harness.ts:295–302,562–585` |
| Registry must restore built-in task definitions | `src/harness/harness.ts:569–575` |
| Persistent backends, MemoryStorage exception, exclusive ownership responsibility | `README.md:770–782,801` |
| Nested-call receipt reuse is distinct from interrupted-call replay | `src/harness/tool.ts:742–799` (background check; not diagrammed) |

Pinned source URL prefix:
`https://github.com/earendil-works/pi/blob/479d6e5e298821088cfd77566a139097e73a888b/packages/durable/`

## Deliberate simplifications

- Figure 2.1-1 groups the scheduler, generation, tool tasks and extension registry into one Harness tier. Session is a kernel abstraction, not a separate process. Boxes show responsibilities, not deployment units.
- Storage means the Storage abstraction and its backend together. The three named persistent families are examples, not an exhaustive adapter list; Cloudflare uses SQLite. MemoryStorage is intentionally absent from the recovery path.
- The numbered write/adopt/publish path concerns durable entries and task decisions. The nearby progress note and paragraph explicitly identify the deferred-progress exception; no claim is made that all UI output is durable before display.
- Figure 2.1-2 selects loss after execute intent but before a result receipt. It is an ordinal sequence, not a measured timeline. A tool may have produced an external effect; the runtime cannot infer its extent.
- Tool replay starts the implementation again, not a suspended JavaScript stack. Safe replay is a host/implementation declaration, not an automatically proven property. External effects and local result commits are not one transaction.
- Recovery's read-only mode, missing/migrated definitions, abandonment flags, task joins, sleeping/wake alarms, nested receipts, compaction, request IDs and cancellation details are omitted.
- Retry defaults refer to durable generation retries, not a universal HTTP-attempt count. Provider/SDK retries are separate.
- Restart parking counts process cutoffs without durable progress; ordinary close does not count. Parking is derived, not a seventh TaskState.
- Progress persistence is configurable and timer-dependent. The 1000 ms row is a default target, not a hard real-time upper bound.
- Persistence remains backend-dependent. SQLite NORMAL can lose newest commits on power/host failure; JSONL fsync is optional. Exclusive ownership is enforced by the host, not a cross-process lease in the package.
- Document number, section numbers and figure art codes are report furniture, not package identifiers or agency authorship.

## Reproduction and checks

- Based on the nasa-handbook template, shared SVG definitions and structured print-media fit contract. Font sizes match the template. The standalone HTML has a sibling `fonts/`; the repository example uses `../fonts/`.
- Figures use black linework only. No quantitative chart is appropriate: no measured series exists.
- Render: `sh nasa-handbook/skill/scripts/render.sh <out>/pi-durable.html`. Keep the sibling `fonts/` directory; set `CHROME=/path/to/chrome` if needed.
- Check (Python with PyMuPDF): `python3 nasa-handbook/skill/scripts/check.py <out>/pi-durable.pdf --out <out>/review`.
- Results: one A4 page, 6.8 mm clear above the footer, pure black/white, expected body/drawing/checklist fonts. All eight detail tiles inspected; no text/line crossings or clipping found.
- Checklist order excludes other writers before reopening and reconciles external effects before enabling scheduling.
