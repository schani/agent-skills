# pr-review-html Generator Plan

## Goal

Build a data-driven generator for hosted PR review walkthroughs. The generator should separate:

1. the live git diff, parsed directly from the repository; and
2. a human-authored review spec that explains the overview, chapters, and every hunk.

Rendering must fail when the spec is stale or incomplete. The review input itself should be embedded in the generated HTML so it can later be extracted and edited after the PR changes.

## Commands

### `scaffold`

Create or update a review spec from the current diff.

```bash
pr-review-html scaffold \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --out pr-review.json
```

Update an existing spec while preserving existing prose and hunk descriptions:

```bash
pr-review-html scaffold \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --spec pr-review.json \
  --out pr-review.json
```

Behavior:

- Parse the live diff.
- Preserve existing overview, chapters, item order, descriptions, and prose where exact hunk IDs still match.
- Add newly discovered hunks/files to an `unassigned` chapter.
- Report stale spec items whose hunk IDs no longer exist in the live diff.
- Do not silently fuzzy-match changed hunks. Fuzzy suggestions may be printed later, but exact matching is the default.

### `render`

Render standalone HTML and validate the spec as part of rendering.

```bash
pr-review-html render \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --spec pr-review.json \
  --out /tmp/pr-review.html
```

No separate `validate` command is needed. `render` fails if validation fails.

### `extract`

Extract the embedded review spec from generated HTML.

```bash
pr-review-html extract \
  --html /tmp/pr-review.html \
  --out pr-review.json
```

For hosted reviews:

```bash
curl -s https://hostr.flingit.run/s/some-review > /tmp/review.html
pr-review-html extract --html /tmp/review.html --out pr-review.json
```

## Review spec shape

Use JSON first because it can be embedded and extracted exactly. JSONC/YAML can be considered later.

```json
{
  "schemaVersion": 1,
  "title": "Fling PR #131 — Google OAuth auth overview",
  "prUrl": "https://github.com/glideapps/fling/pull/131",
  "overview": {
    "summary": [
      "This PR adds Google OAuth support for Fling apps.",
      "It also adds fake-provider integration tests and private platform route handling."
    ],
    "reviewFocus": [
      "Confirm the auth route contract is consistent.",
      "Check private platform path-mode behavior."
    ]
  },
  "chapters": [
    {
      "id": "route-contract",
      "title": "Route contract and app-facing API",
      "subtitle": "The app auth surface lives under /api/auth.",
      "body": [
        "This chapter defines the routes developers use from frontend and worker code."
      ],
      "reviewFocus": [
        "Verify docs and runtime agree on /api/auth/*.",
        "Check private path routing keeps the project slug."
      ],
      "items": [
        {
          "kind": "hunk",
          "id": "src/worker-runtime/auth.ts@@224,30:228,31|a1b2c3d4",
          "description": "Changes deployed auth route matching to /api/auth/* and updates provider extraction for the new path depth."
        },
        {
          "kind": "file",
          "id": "newfile:templates/default/src/react-app/paths.ts|9f00abcd",
          "description": "Adds a helper for Vite base-aware frontend URLs."
        }
      ]
    }
  ]
}
```

Scaffolded items may include authoring aids that render can ignore or softly check:

```json
{
  "kind": "hunk",
  "id": "src/runtime/auth.ts@@248,7:248,7|b8349a1c",
  "path": "src/runtime/auth.ts",
  "header": "@@ -248,7 +248,7 @@",
  "preview": "if (url.pathname.startsWith(\"/api/auth/signin/\")) {",
  "description": ""
}
```

## Hunk IDs

No separate manifest file is needed. The script computes the live hunk list internally on every run and compares it with item IDs in the spec.

Hunk IDs:

```text
path@@oldStart,oldLen:newStart,newLen|contentHash
```

New-file IDs:

```text
newfile:path|contentHash
```

The ID intentionally includes line information and a content hash. If a hunk moves or changes, render should fail and scaffold should add the changed hunk to `unassigned` rather than guessing.

## Validation during `render`

`render` must fail if:

- a current diff hunk/new-file item is not mentioned in the spec;
- a spec item references a hunk/file not in the current diff;
- a hunk/file is mentioned more than once;
- any item remains in chapter `unassigned`;
- any item has an empty description;
- required top-level fields are missing;
- chapter IDs are duplicated;
- a chapter has no body text or no review focus.

Failures should be actionable, for example:

```text
Unassigned current hunk:
  src/runtime/auth.ts@@248,7:248,7|b8349a1c
  Preview: if (url.pathname.startsWith("/api/auth/signin/")) {

Spec references stale hunk:
  src/runtime/auth.ts@@120,3:120,4|deadbeef
```

## Embedding the spec in HTML

Generated HTML embeds the exact review spec as machine-readable metadata:

```html
<script type="application/json" id="pr-review-spec">
{ ...original pr-review.json... }
</script>
```

No visible buttons are needed. The embedded spec is for the script only. `extract` recovers it later.

## Renderer responsibilities

The spec does not contain raw diff text. The renderer owns:

- parsing unified diff output;
- rendering review-style diff tables;
- rendering net-new files as complete files, not all-green diffs;
- rendering net-new Markdown as Markdown;
- syntax-highlighting net-new source/config files;
- comment IDs and localStorage-backed line comments;
- collapse state;
- responsive layout and wrapped long lines.

## Scaffold details

First run:

- create placeholder title/overview;
- create one `unassigned` chapter;
- include every current hunk/new-file item;
- set item descriptions to `""`;
- include path/header/preview authoring aids.

Subsequent run:

- preserve exact item matches and all authored text;
- append new items to `unassigned`;
- report stale items;
- do not silently remove stale items unless explicitly requested later.

## Demo PR

Use a local Fling checkout PR #131 as the initial demo input:

```bash
pr-review-html scaffold \
  --repo /path/to/fling \
  --base origin/main \
  --head HEAD \
  --out examples/fling-pr-131.review.json
```

The first scaffold should intentionally render as incomplete because every hunk starts unassigned/undescribed. A fully authored demo can be created later by moving items into chapters and filling descriptions.

## Future considerations

- JSON Schema or Zod-style validation error quality. Start without dependencies; add a schema library only if worth it.
- Fuzzy hunk suggestions for stale IDs, but never automatic silent matching.
- A `publish` wrapper for Hostr can come later; rendering and hosting should initially stay separate.
- CI can run `render` against the spec to guarantee the writeup is current.
- Comment migration/orphan handling can be layered on after stable rendering exists.
