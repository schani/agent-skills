---
name: pr-review-html
description: Generate, render, update, extract, and host chaptered HTML PR review walkthroughs from a git diff plus a JSON review spec. Use when the user asks for an HTML PR review, annotated diff walkthrough, generated PR explainer, or hosted review document.
---

# pr-review-html

This tool creates hosted, chaptered HTML PR review walkthroughs. It separates the live git diff from the human-authored review narrative:

- `scaffold` parses the current diff and creates/updates a JSON review spec.
- You edit the spec: overview, chapter text, hunk assignment, hunk descriptions.
- `render` validates that every current hunk/file is mentioned exactly once, then writes standalone HTML.
- `extract` recovers the embedded review spec from a generated HTML file.

Rendered HTML supports:

- sticky chapter sidebar
- conceptual chapters
- collapsible hunk/file sections
- sticky hunk/file headers
- line comments saved in `localStorage`
- click-to-comment on diff lines, source lines, and rendered Markdown blocks
- automatic comment autosave while typing
- Cmd/Ctrl+Enter or Escape to close the comment editor
- copy-to-clipboard review export
- net-new Markdown rendered as Markdown
- net-new source/config/test files rendered as full syntax-highlighted files

## Location

Run commands from the skill directory unless otherwise noted.

CLI script:

```bash
./scripts/pr-review-html.mjs
```

## Workflow

### 1. Scaffold a spec

For a PR in another repo:

```bash
node ./scripts/pr-review-html.mjs scaffold \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --out examples/my-pr.review.json
```

For the Fling PR #131 demo:

```bash
npm run scaffold:demo
```

The first scaffold creates one `unassigned` chapter with every current diff hunk/new file item.

### 2. Edit the spec

Open the generated JSON file and fill in:

- top-level `title`
- `prUrl`
- `overview.summary`
- `overview.reviewFocus`
- chapter list
- chapter body/review focus
- item assignment
- every item `description`

Move every item out of `unassigned`. `render` fails if any item remains there.

A spec item looks like:

```json
{
  "kind": "hunk",
  "id": "src/runtime/auth.ts@@248,7:248,7|b8349a1c",
  "path": "src/runtime/auth.ts",
  "header": "@@ -248,7 +248,7 @@",
  "preview": "if (url.pathname.startsWith(\"/api/auth/signin/\")) {",
  "description": "Moves local auth route matching under /api/auth."
}
```

A net-new file item looks like:

```json
{
  "kind": "file",
  "id": "newfile:templates/default/src/react-app/paths.ts|9f00abcd",
  "path": "templates/default/src/react-app/paths.ts",
  "preview": "export function appPath",
  "description": "Adds a helper for Vite base-aware frontend URLs."
}
```

## Commands

### `scaffold`

Create or update a review spec from the live diff.

```bash
node ./scripts/pr-review-html.mjs scaffold \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --out pr-review.json
```

Update an existing spec after the PR changes:

```bash
node ./scripts/pr-review-html.mjs scaffold \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --spec pr-review.json \
  --out pr-review.json
```

Behavior:

- preserves exact hunk/file matches and their descriptions
- appends new hunks/files to `unassigned`
- records stale items in `staleItems`
- does not silently fuzzy-match changed hunks

After scaffolding an updated PR, resolve all `unassigned` and `staleItems` before rendering.

### `render`

Validate the spec and render standalone HTML:

```bash
node ./scripts/pr-review-html.mjs render \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --spec pr-review.json \
  --out /tmp/pr-review.html
```

For the demo:

```bash
npm run render:demo
```

`render` fails if:

- a current diff hunk/new file is missing from the spec
- a spec item references a stale hunk/file
- an item is assigned more than once
- an item remains in `unassigned`
- any item has an empty description
- required overview/chapter fields are missing
- duplicate chapter IDs exist

### `extract`

Recover the embedded review spec from a rendered HTML file:

```bash
node ./scripts/pr-review-html.mjs extract \
  --html /tmp/pr-review.html \
  --out pr-review.json
```

For a hosted review:

```bash
curl -s https://hostr.flingit.run/s/some-review > /tmp/review.html
node ./scripts/pr-review-html.mjs extract --html /tmp/review.html --out pr-review.json
```

The embedded spec should round-trip exactly.

## Hosting with hostr

Render first:

```bash
node ./scripts/pr-review-html.mjs render \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --spec pr-review.json \
  --out /tmp/pr-review.html
```

Upload to Hostr:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer AxCMmhBQ0MRAR0Io6D3p" \
  -H "Content-Type: text/html" \
  --data-binary @/tmp/pr-review.html \
  "https://hostr.flingit.run/s/<path>" \
  -w "\nHTTP %{http_code}\n"
```

Then browser-verify the URL.

## Browser verification checklist

Use `agent-browser` after hosting:

```bash
agent-browser open https://hostr.flingit.run/s/<path>
agent-browser wait 12000
agent-browser eval "({
  title: document.title,
  chapters: document.querySelectorAll('.chapter').length,
  units: document.querySelectorAll('details.unit').length,
  markdownBlocks: document.querySelectorAll('.markdown-body .commentable[data-comment-id]').length,
  sourceLines: document.querySelectorAll('.source-line.commentable[data-comment-id]').length,
  diffLines: document.querySelectorAll('tr.diff-line.commentable[data-comment-id]').length,
  highlighted: document.querySelectorAll('.source-view.highlighted').length,
  sticky: getComputedStyle(document.querySelector('details.unit > summary')).position,
  embeddedSpec: !!document.querySelector('#pr-review-spec')
})"
```

Expected:

- `embeddedSpec: true`
- `sticky: "sticky"`
- source/config files highlighted
- Markdown blocks commentable
- diff lines commentable
- no visible `+` comment buttons

Also verify comment behavior:

- click a diff line, source line, and Markdown block
- type a comment
- wait briefly; it should autosave
- Escape closes
- Cmd/Ctrl+Enter closes
- comment count updates
- copy comments updates toolbar status, not `alert()`

## Hunk IDs and collapse state

Hunk IDs include a content hash:

```text
path@@oldStart,oldLen:newStart,newLen|contentHash
```

New-file IDs include a content hash:

```text
newfile:path|contentHash
```

The rendered collapse IDs derive from these IDs, so changed hunks/files get new localStorage keys. That means changed non-test hunks default back to expanded. `*.test.ts` hunks/files default collapsed when there is no saved localStorage state.

## Demo PR

Current demo spec:

```bash
./examples/fling-pr-131.authored.review.json
```

Current hosted demo:

```text
https://hostr.flingit.run/s/pr-review-html-fling-pr-131-demo
```

Regenerate the demo after PR #131 changes:

```bash
node ./scripts/pr-review-html.mjs scaffold \
  --repo /path/to/fling \
  --base origin/main \
  --head HEAD \
  --spec examples/fling-pr-131.authored.review.json \
  --out examples/fling-pr-131.authored.review.json
```

Then resolve `unassigned` and `staleItems`, render, upload, and verify.

## Important notes

- Do not commit generated HTML unless explicitly requested.
- Keep the review spec JSON if it is part of the demo/tooling state.
- Rendering is intentionally strict; stale reviews should fail loudly.
- Hosting is separate from rendering; use Hostr only after `render` succeeds.
- If the PR changes, always run `scaffold` again before `render`.
