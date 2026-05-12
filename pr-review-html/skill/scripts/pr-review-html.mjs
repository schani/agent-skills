#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

function usage() {
  console.error(`Usage:
  pr-review-html scaffold --repo <repo> --base <base> --head <head> --out <spec.json> [--spec <existing.json>]
  pr-review-html render   --repo <repo> --base <base> --head <head> --spec <spec.json> --out <review.html>
  pr-review-html extract  --html <review.html> --out <spec.json>`);
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const opts = { command };
  for (let i = 0; i < rest.length; i++) {
    const arg = rest[i];
    if (!arg.startsWith("--")) throw new Error(`Unexpected argument: ${arg}`);
    const key = arg.slice(2);
    const value = rest[i + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for --${key}`);
    opts[key] = value;
    i++;
  }
  return opts;
}

function requireOpt(opts, name) {
  if (!opts[name]) throw new Error(`Missing required option --${name}`);
  return opts[name];
}

function ensureParent(path) {
  mkdirSync(dirname(resolve(path)), { recursive: true });
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf-8"));
}

function writeJson(path, value) {
  ensureParent(path);
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function git(repo, args) {
  const result = spawnSync("git", args, {
    cwd: repo,
    encoding: "utf-8",
    maxBuffer: 1024 * 1024 * 200,
  });
  if (result.status !== 0) {
    throw new Error(`git ${args.join(" ")} failed\n${result.stderr || result.stdout}`);
  }
  return result.stdout;
}

function getDiff(repo, base, head) {
  return git(repo, [
    "diff",
    "--no-ext-diff",
    "--find-renames",
    "--src-prefix=a/",
    "--dst-prefix=b/",
    `${base}...${head}`,
    "--",
    ".",
    ":(exclude).beads/issues.jsonl",
  ]);
}

function shortHash(value) {
  return createHash("sha1").update(value).digest("hex").slice(0, 8);
}

function parseRange(text) {
  const [startText, lenText] = text.split(",");
  return {
    start: Number(startText),
    len: lenText === undefined ? 1 : Number(lenText),
  };
}

function parseHunkHeader(line) {
  const match = /^@@ -(\d+(?:,\d+)?) \+(\d+(?:,\d+)?) @@(.*)$/.exec(line);
  if (!match) return null;
  return {
    old: parseRange(match[1]),
    new: parseRange(match[2]),
    section: match[3]?.trim() ?? "",
  };
}

function pathFromDiffToken(token) {
  if (token === "/dev/null") return null;
  return token.replace(/^[ab]\//, "");
}

function parseDiff(diffText) {
  const files = [];
  let file = null;
  let hunk = null;

  function finishHunk() {
    if (!file || !hunk) return;
    const hash = shortHash(hunk.lines.join("\n"));
    hunk.id = `${file.path}@@${hunk.oldStart},${hunk.oldLen}:${hunk.newStart},${hunk.newLen}|${hash}`;
    file.hunks.push(hunk);
    hunk = null;
  }

  function finishFile() {
    finishHunk();
    if (!file) return;
    if (file.isNew) {
      const added = file.hunks.flatMap((candidate) => candidate.lines)
        .filter((line) => line.startsWith("+") && !line.startsWith("+++"))
        .map((line) => line.slice(1))
        .join("\n");
      file.fileItem = {
        kind: "file",
        id: `newfile:${file.path}|${shortHash(added)}`,
        path: file.path,
        preview: previewText(added.split("\n")),
        content: added,
      };
    }
    files.push(file);
    file = null;
  }

  for (const line of diffText.split("\n")) {
    if (line.startsWith("diff --git ")) {
      finishFile();
      const match = /^diff --git a\/(.*) b\/(.*)$/.exec(line);
      file = {
        oldPath: match?.[1] ?? "",
        path: match?.[2] ?? "",
        isNew: false,
        isDeleted: false,
        hunks: [],
        fileItem: null,
      };
      continue;
    }

    if (!file) continue;

    if (line.startsWith("new file mode ")) {
      file.isNew = true;
      continue;
    }
    if (line.startsWith("deleted file mode ")) {
      file.isDeleted = true;
      continue;
    }
    if (line.startsWith("--- ")) {
      const oldPath = pathFromDiffToken(line.slice(4).trim());
      if (oldPath) file.oldPath = oldPath;
      continue;
    }
    if (line.startsWith("+++ ")) {
      const newPath = pathFromDiffToken(line.slice(4).trim());
      if (newPath) file.path = newPath;
      continue;
    }

    const parsedHeader = parseHunkHeader(line);
    if (parsedHeader) {
      finishHunk();
      hunk = {
        kind: "hunk",
        id: "",
        path: file.path,
        header: line,
        oldStart: parsedHeader.old.start,
        oldLen: parsedHeader.old.len,
        newStart: parsedHeader.new.start,
        newLen: parsedHeader.new.len,
        section: parsedHeader.section,
        preview: "",
        lines: [],
      };
      continue;
    }

    if (hunk) {
      hunk.lines.push(line);
      if (!hunk.preview) hunk.preview = previewText([line]);
    }
  }

  finishFile();
  return files;
}

function currentItems(files) {
  const items = [];
  for (const file of files) {
    if (file.isNew && file.fileItem) {
      items.push({
        kind: "file",
        id: file.fileItem.id,
        path: file.path,
        preview: file.fileItem.preview,
      });
    } else {
      for (const hunk of file.hunks) {
        items.push({
          kind: "hunk",
          id: hunk.id,
          path: hunk.path,
          header: hunk.header,
          preview: hunk.preview,
        });
      }
    }
  }
  return items;
}

function previewText(lines) {
  for (const line of lines) {
    const text = line.replace(/^[ +\-]/, "").trim();
    if (text) return text.slice(0, 160);
  }
  return "";
}

function makePlaceholderSpec(current, repo) {
  return {
    schemaVersion: 1,
    title: "PR review walkthrough",
    prUrl: detectPrUrl(repo),
    overview: {
      summary: ["TODO: summarize the PR and the review narrative."],
      reviewFocus: ["TODO: list the highest-value review concerns."],
    },
    chapters: [
      {
        id: "unassigned",
        title: "Unassigned hunks",
        subtitle: "Move these into real chapters before rendering.",
        body: ["These hunks were discovered by scaffold and still need chapter placement."],
        reviewFocus: ["Assign every item to a real chapter and fill in each description."],
        items: current.map((item) => ({ ...item, description: "" })),
      },
    ],
  };
}

function detectPrUrl(repo) {
  const result = spawnSync("gh", ["pr", "view", "--json", "url", "--jq", ".url"], {
    cwd: repo,
    encoding: "utf-8",
  });
  return result.status === 0 ? result.stdout.trim() : "";
}

function collectSpecItems(spec) {
  const records = [];
  for (const chapter of spec.chapters ?? []) {
    for (const item of chapter.items ?? []) {
      records.push({ chapter, item });
    }
  }
  return records;
}

function scaffold(opts) {
  const repo = requireOpt(opts, "repo");
  const base = requireOpt(opts, "base");
  const head = requireOpt(opts, "head");
  const out = requireOpt(opts, "out");
  const files = parseDiff(getDiff(repo, base, head));
  const current = currentItems(files);

  if (!opts.spec || !existsSync(opts.spec)) {
    writeJson(out, makePlaceholderSpec(current, repo));
    console.log(`Wrote ${out} with ${current.length} unassigned item(s).`);
    return;
  }

  const spec = readJson(opts.spec);
  const currentById = new Map(current.map((item) => [item.id, item]));
  const seenCurrent = new Set();
  const staleItems = [];

  for (const chapter of spec.chapters ?? []) {
    const kept = [];
    for (const item of chapter.items ?? []) {
      if (currentById.has(item.id)) {
        kept.push({ ...currentById.get(item.id), ...item });
        seenCurrent.add(item.id);
      } else {
        staleItems.push({ chapterId: chapter.id, ...item });
      }
    }
    chapter.items = kept;
  }

  let unassigned = spec.chapters.find((chapter) => chapter.id === "unassigned");
  if (!unassigned) {
    unassigned = {
      id: "unassigned",
      title: "Unassigned hunks",
      subtitle: "Move these into real chapters before rendering.",
      body: ["These hunks were discovered by scaffold and still need chapter placement."],
      reviewFocus: ["Assign every item to a real chapter and fill in each description."],
      items: [],
    };
    spec.chapters.push(unassigned);
  }

  const added = [];
  for (const item of current) {
    if (!seenCurrent.has(item.id)) {
      const next = { ...item, description: "" };
      unassigned.items.push(next);
      added.push(next);
    }
  }

  if (staleItems.length > 0) spec.staleItems = staleItems;
  else delete spec.staleItems;

  writeJson(out, spec);
  console.log(`Wrote ${out}. Added ${added.length} new item(s); stale ${staleItems.length}.`);
}

function validateSpec(spec, liveItems) {
  const errors = [];
  const liveById = new Map(liveItems.map((item) => [item.id, item]));
  const assigned = new Map();

  if (spec.schemaVersion !== 1) errors.push("schemaVersion must be 1.");
  if (!spec.title) errors.push("Missing title.");
  if (!spec.overview?.summary?.length) errors.push("Missing overview.summary.");
  if (!spec.overview?.reviewFocus?.length) errors.push("Missing overview.reviewFocus.");
  if (!Array.isArray(spec.chapters) || spec.chapters.length === 0) errors.push("Missing chapters.");
  if (Array.isArray(spec.staleItems) && spec.staleItems.length > 0) {
    errors.push(`Spec has ${spec.staleItems.length} stale item(s). Run scaffold and resolve/remove staleItems.`);
  }

  const chapterIds = new Set();
  for (const chapter of spec.chapters ?? []) {
    if (!chapter.id) errors.push("Chapter missing id.");
    else if (chapterIds.has(chapter.id)) errors.push(`Duplicate chapter id: ${chapter.id}`);
    else chapterIds.add(chapter.id);

    if (!chapter.body?.length) errors.push(`Chapter ${chapter.id} has no body.`);
    if (!chapter.reviewFocus?.length) errors.push(`Chapter ${chapter.id} has no reviewFocus.`);

    for (const item of chapter.items ?? []) {
      if (chapter.id === "unassigned") errors.push(`Item remains in unassigned: ${item.id}`);
      if (!item.description?.trim()) errors.push(`Item has empty description: ${item.id}`);
      if (!liveById.has(item.id)) errors.push(`Spec references stale item: ${item.id}`);
      if (assigned.has(item.id)) errors.push(`Item assigned more than once: ${item.id}`);
      assigned.set(item.id, chapter.id);
    }
  }

  for (const live of liveItems) {
    if (!assigned.has(live.id)) {
      errors.push(`Current diff item is not assigned: ${live.id}\n  Preview: ${live.preview}`);
    }
  }

  return errors;
}

function render(opts) {
  const repo = requireOpt(opts, "repo");
  const base = requireOpt(opts, "base");
  const head = requireOpt(opts, "head");
  const specPath = requireOpt(opts, "spec");
  const out = requireOpt(opts, "out");
  const spec = readJson(specPath);
  const files = parseDiff(getDiff(repo, base, head));
  const liveItems = currentItems(files);
  const errors = validateSpec(spec, liveItems);
  if (errors.length > 0) {
    throw new Error(`Review spec is invalid:\n${errors.map((error) => `- ${error}`).join("\n")}`);
  }

  const hunksById = new Map();
  const filesById = new Map();
  for (const file of files) {
    if (file.isNew && file.fileItem) filesById.set(file.fileItem.id, file.fileItem);
    for (const hunk of file.hunks) hunksById.set(hunk.id, hunk);
  }

  const html = renderHtml(spec, hunksById, filesById, diffStats(files));
  ensureParent(out);
  writeFileSync(out, html);
  console.log(`Wrote ${out}`);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"]/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
  }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/'/g, "&#39;");
}

function scriptJson(value) {
  return JSON.stringify(value).replaceAll("</script", "<\\/script");
}

function renderMarkdownish(blocks) {
  return (blocks ?? []).map((text) => `<p>${escapeHtml(text)}</p>`).join("\n");
}

function slugForId(value) {
  return String(value).replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 120);
}

function fileLanguage(path) {
  const ext = path.split(".").pop()?.toLowerCase() ?? "";
  const byExt = {
    js: "javascript",
    mjs: "javascript",
    cjs: "javascript",
    jsx: "jsx",
    ts: "typescript",
    tsx: "tsx",
    json: "json",
    jsonl: "json",
    yml: "yaml",
    yaml: "yaml",
    toml: "toml",
    md: "markdown",
    html: "html",
    css: "css",
    sh: "bash",
    bash: "bash",
    sql: "sql",
  };
  return byExt[ext] ?? "text";
}

function isMarkdownFile(path) {
  return /\.mdx?$/i.test(path);
}

function diffStats(files) {
  let additions = 0;
  let deletions = 0;
  for (const file of files) {
    for (const hunk of file.hunks) {
      for (const line of hunk.lines) {
        if (line.startsWith("+") && !line.startsWith("+++")) additions++;
        else if (line.startsWith("-") && !line.startsWith("---")) deletions++;
      }
    }
  }
  return { files: files.length, additions, deletions, changedLines: additions + deletions };
}

function renderHtml(spec, hunksById, filesById, stats) {
  const embeddedSpec = scriptJson(spec);
  const sourceScripts = [];
  const chapters = spec.chapters.map((chapter, index) => renderChapter(chapter, index, hunksById, filesById, sourceScripts)).join("\n");
  const toc = spec.chapters.map((chapter, index) => `<a href="#${escapeAttr(chapter.id)}">${index + 1}. ${escapeHtml(chapter.title)}</a>`).join("\n");
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(spec.title)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown-light.css">
<style>
:root { --bg:#f6f8fa; --panel:#fff; --border:#d0d7de; --text:#24292f; --muted:#57606a; --blue:#0969da; --add:#dafbe1; --del:#ffebe9; --head:#ddf4ff; --shadow:0 8px 28px rgba(27,31,36,.08); --toolbar-height:46px; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
a { color:var(--blue); text-decoration:none; } a:hover { text-decoration:underline; }
.layout { display:grid; grid-template-columns:270px minmax(0,1fr); gap:22px; width:100%; max-width:none; margin:0; padding:18px; }
.sidebar { position:sticky; top:calc(var(--toolbar-height) + 12px); align-self:start; background:var(--panel); border:1px solid var(--border); border-radius:12px; box-shadow:var(--shadow); padding:14px; max-height:calc(100vh - var(--toolbar-height) - 24px); overflow:auto; }
.sidebar h2 { font-size:14px; margin:0 0 10px; } .sidebar nav { display:flex; flex-direction:column; gap:6px; } .sidebar a { padding:7px 8px; border-radius:7px; color:var(--text); } .sidebar a:hover { background:#f6f8fa; text-decoration:none; }
main { min-width:0; } .hero,.chapter { background:var(--panel); border:1px solid var(--border); border-radius:14px; box-shadow:var(--shadow); padding:22px; margin-bottom:20px; }
.hero h1 { font-size:30px; margin:8px 0; } .subtitle,.muted,.count { color:var(--muted); } .eyebrow { color:var(--blue); font-weight:700; text-transform:uppercase; letter-spacing:.06em; margin:0; font-size:12px; }
.pills { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; } .pill { border:1px solid var(--border); border-radius:999px; padding:6px 10px; background:#f6f8fa; color:var(--text); } .pill.primary { background:#ddf4ff; border-color:#54aeff; } .pill.additions { background:#dafbe1; border-color:#4ac26b; color:#116329; font-weight:600; } .pill.deletions { background:#ffebe9; border-color:#ff8182; color:#82071e; font-weight:600; }
.focus { border-left:4px solid var(--blue); background:#f6f8fa; padding:12px 14px; margin:16px 0; border-radius:8px; }
.toolbar { position:sticky; top:0; z-index:50; display:flex; justify-content:flex-end; align-items:center; gap:8px; padding:8px 18px; background:rgba(246,248,250,.92); backdrop-filter:blur(8px); border-bottom:1px solid rgba(208,215,222,.75); }
.toolbar button { border:1px solid var(--border); border-radius:8px; background:#fff; padding:8px 10px; cursor:pointer; box-shadow:var(--shadow); } .toolbar .count { margin-right:auto; } .toolbar-status { color:var(--muted); min-width:110px; }
.unit { border:1px solid var(--border); border-radius:10px; margin:14px 0; overflow:visible; background:#fff; }
.unit > summary { position:sticky; top:var(--toolbar-height); z-index:30; display:flex; flex-direction:column; gap:2px; cursor:pointer; padding:10px 12px; background:#f6f8fa; border-bottom:1px solid var(--border); font-weight:600; border-radius:10px 10px 0 0; }
.unit:not([open]) > summary { border-bottom:0; border-radius:10px; } .unit > summary small { color:var(--muted); font-weight:400; }
.item-desc { margin:12px; color:var(--muted); }
.diff-table { width:100%; table-layout:fixed; border-collapse:collapse; font-family:ui-monospace,SFMono-Regular,SFMono,Consolas,"Liberation Mono",monospace; font-size:12px; line-height:1.38; } .col-old,.col-new { width:48px; } .col-mark { width:26px; }
.diff-table td { border-top:0; vertical-align:top; } .ln { color:#6e7781; text-align:right; padding:2px 8px; user-select:none; } .mark { text-align:center; padding:2px 4px; color:#57606a; } .code { white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; min-width:0; padding:2px 8px; }
.diff-line.add { background:var(--add); } .diff-line.del { background:var(--del); } .diff-line.ctx { background:#fff; } .hunk-head td { background:var(--head); color:#0969da; padding:5px 10px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }
.commentable { cursor:pointer; } .commentable:hover .code,.commentable:hover .source-code,.commentable:hover.markdown-body > *, .markdown-body .commentable:hover { outline:2px solid rgba(84,174,255,.55); outline-offset:-2px; background:#ddf4ff44; }
.commentable.has-comment .code,.commentable.has-comment .source-code,.markdown-body .commentable.has-comment { box-shadow: inset 4px 0 0 #bf8700; background:#fff8c5 !important; }
.source-view { font-family:ui-monospace,SFMono-Regular,SFMono,Consolas,"Liberation Mono",monospace; font-size:12px; line-height:1.42; background:#fff; } .source-line { display:grid; grid-template-columns:64px minmax(0,1fr); }
.source-ln { color:#6e7781; text-align:right; padding:2px 10px; user-select:none; background:#f6f8fa; } .source-code { white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; padding:2px 8px; min-width:0; }
.source-view .shiki { background:transparent !important; margin:0; padding:0; } .source-view .shiki code { white-space:pre-wrap; }
.rendered-md { padding:18px 24px; }
.markdown-body .commentable { border-radius:6px; padding:2px 4px; margin-left:-4px; margin-right:-4px; }
.dialog { position:fixed; inset:0; background:rgba(27,31,36,.35); display:none; align-items:center; justify-content:center; z-index:100; } .dialog.open { display:flex; } .modal { width:min(760px,calc(100vw - 32px)); background:#fff; border-radius:12px; border:1px solid var(--border); box-shadow:var(--shadow); padding:16px; } .modal textarea { width:100%; min-height:140px; font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; } .modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:10px; }
.comment-preview { margin:0 0 10px; padding:10px; background:#f6f8fa; border:1px solid var(--border); border-radius:8px; font:12px ui-monospace,SFMono-Regular,Consolas,monospace; white-space:pre-wrap; overflow-wrap:anywhere; }
@media (max-width:900px) { .layout { grid-template-columns:1fr; padding:10px; } .sidebar { position:relative; top:auto; max-height:none; } .unit > summary { top:var(--toolbar-height); } .hero h1 { font-size:24px; } .toolbar { padding:8px 10px; flex-wrap:wrap; } }
</style>
<script type="application/json" id="pr-review-spec">${embeddedSpec}</script>
${sourceScripts.join("\n")}
</head>
<body>
<div class="toolbar" id="comment-toolbar"><span class="count" id="comment-count">0 comments</span><span class="toolbar-status" id="toolbar-status" aria-live="polite"></span><button id="copy-comments" type="button">Copy comments to clipboard</button><button id="clear-comments" type="button">Clear local comments</button></div>
<div class="layout">
<aside class="sidebar"><h2>Chapters</h2><nav><a href="#overview">Overview</a>${toc}</nav></aside>
<main>
<section class="hero" id="overview">
<h1>${escapeHtml(spec.title)}</h1>
<div class="pills">${spec.prUrl ? `<a class="pill primary" href="${escapeAttr(spec.prUrl)}">GitHub PR</a>` : ""}<span class="pill">${stats.files} files</span><span class="pill additions">+${stats.additions}</span><span class="pill deletions">-${stats.deletions}</span><a class="pill" href="https://hostr.flingit.run/s/pr-review-html/SKILL.md">Generated with the pr-review-html skill</a></div>
${renderMarkdownish(spec.overview.summary)}
<div class="focus"><strong>Review focus</strong><ul>${spec.overview.reviewFocus.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>
</section>
${chapters}
</main>
</div>
<div id="comment-modal" class="dialog" role="dialog" aria-modal="true" aria-labelledby="comment-title">
  <div class="modal">
    <h3 id="comment-title">Review comment</h3>
    <pre id="comment-preview" class="comment-preview"></pre>
    <textarea id="comment-text" placeholder="Write a PR review comment... Auto-saves as you type. Cmd/Ctrl+Enter or Escape closes."></textarea>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js"></script>
<script type="module">
const pageId = location.pathname + ':' + document.title;
const collapseKey = 'pr-review-collapse:' + pageId;
const commentsKey = 'pr-review-comments:' + pageId;
const readJson = (key, fallback) => { try { return JSON.parse(localStorage.getItem(key) || '') ?? fallback; } catch { return fallback; } };
const writeJson = (key, value) => localStorage.setItem(key, JSON.stringify(value));
const escapeHtmlClient = (value) => String(value).replace(/[&<>\"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[char]));

const toolbar = document.getElementById('comment-toolbar');
const updateToolbarHeight = () => document.documentElement.style.setProperty('--toolbar-height', toolbar.offsetHeight + 'px');
updateToolbarHeight();
new ResizeObserver(updateToolbarHeight).observe(toolbar);

const collapsed = readJson(collapseKey, {});
document.querySelectorAll('details.unit[data-collapse-id]').forEach((details) => {
  const id = details.dataset.collapseId;
  if (Object.prototype.hasOwnProperty.call(collapsed, id)) details.open = !collapsed[id];
  else if (details.dataset.defaultCollapsed === 'true') details.open = false;
  details.addEventListener('toggle', () => {
    const next = readJson(collapseKey, {});
    next[id] = !details.open;
    writeJson(collapseKey, next);
  });
});

function setupMarkdown() {
  if (!window.markdownit || !window.DOMPurify) return;
  document.querySelectorAll('[data-markdown-source]').forEach((target) => {
    const source = document.getElementById(target.dataset.markdownSource);
    if (!source) return;
    const file = target.dataset.file;
    const raw = JSON.parse(source.textContent);
    const lines = raw.split('\\n');
    const md = window.markdownit({ html:false, linkify:true, typographer:true });
    md.core.ruler.push('commentable_blocks', (state) => {
      const blockTypes = new Set(['heading_open','paragraph_open','list_item_open','blockquote_open','tr_open','th_open','td_open','fence','code_block']);
      for (const token of state.tokens) {
        if (!token.map || !blockTypes.has(token.type)) continue;
        const start = token.map[0] + 1;
        const end = token.map[1];
        const range = start === end ? String(start) : start + '-' + end;
        token.attrJoin('class', 'commentable md-block');
        token.attrSet('data-comment-id', file + '|new|' + range);
        token.attrSet('data-file', file);
        token.attrSet('data-side', 'new');
        token.attrSet('data-line-range', range);
        token.attrSet('data-code', lines.slice(start - 1, end).join('\\n'));
      }
    });
    target.innerHTML = window.DOMPurify.sanitize(md.render(raw), { ADD_ATTR: ['data-comment-id','data-file','data-side','data-line-range','data-code'] });
  });
}

function highlightedLinesFor(code, lang, highlighter) {
  const doc = new DOMParser().parseFromString(highlighter.codeToHtml(code || ' ', { lang, theme: 'github-light' }), 'text/html');
  return Array.from(doc.querySelectorAll('code .line')).map((line) => line.innerHTML);
}

async function setupSourceHighlighting() {
  try {
    const shiki = await import('https://esm.sh/shiki@1.29.2');
    const highlighter = await shiki.createHighlighter({ themes: ['github-light'], langs: ['javascript','jsx','typescript','tsx','json','yaml','toml','markdown','html','css','bash','sql'] });
    const loaded = highlighter.getLoadedLanguages();
    for (const target of document.querySelectorAll('[data-source-code]')) {
      const source = document.getElementById(target.dataset.sourceCode);
      if (!source) continue;
      const code = JSON.parse(source.textContent);
      const lang = loaded.includes(target.dataset.language) ? target.dataset.language : 'text';
      const lines = code.split('\\n');
      const highlightedLines = highlightedLinesFor(code, lang, highlighter);
      target.innerHTML = lines.map((line, index) => {
        const lineNo = index + 1;
        const highlighted = highlightedLines[index] || escapeHtmlClient(line || ' ');
        return '<div class="source-line commentable" data-comment-id="' + escapeHtmlClient(target.dataset.file + '|new|' + lineNo) + '" data-file="' + escapeHtmlClient(target.dataset.file) + '" data-side="new" data-line="' + lineNo + '" data-code="' + escapeHtmlClient(line) + '"><span class="source-ln">' + lineNo + '</span><span class="source-code">' + highlighted + '</span></div>';
      }).join('');
      target.classList.add('highlighted');
    }
  } catch (error) {
    console.warn('Syntax highlighting failed; using escaped source fallback.', error);
  }
}

setupMarkdown();
await setupSourceHighlighting();

let comments = readJson(commentsKey, {});
let activeId = null;
const modal = document.getElementById('comment-modal');
const textarea = document.getElementById('comment-text');
const preview = document.getElementById('comment-preview');
const count = document.getElementById('comment-count');
const toolbarStatus = document.getElementById('toolbar-status');
let toolbarStatusTimer = null;
function setToolbarStatus(message) {
  toolbarStatus.textContent = message;
  clearTimeout(toolbarStatusTimer);
  if (message) toolbarStatusTimer = setTimeout(() => { toolbarStatus.textContent = ''; }, 2500);
}
function allCommentables() { return Array.from(document.querySelectorAll('.commentable[data-comment-id]')); }
function updateCommentMarkers() {
  const total = Object.values(comments).filter((comment) => comment.text?.trim()).length;
  count.textContent = total + (total === 1 ? ' comment' : ' comments');
  for (const el of allCommentables()) el.classList.toggle('has-comment', Boolean(comments[el.dataset.commentId]?.text));
}
function openComment(el) {
  activeId = el.dataset.commentId;
  const existing = comments[activeId]?.text || '';
  textarea.value = existing;
  const lineLabel = el.dataset.lineRange ? 'lines ' + el.dataset.lineRange : 'line ' + (el.dataset.line || el.dataset.newLine || el.dataset.oldLine || '');
  preview.textContent = (el.dataset.file || '') + ' — ' + (el.dataset.side || 'new') + ' ' + lineLabel + '\\n' + (el.dataset.code || '');
  modal.classList.add('open');
  textarea.focus();
}
document.addEventListener('click', (event) => {
  const el = event.target.closest('.commentable[data-comment-id]');
  if (!el) return;
  const selection = window.getSelection();
  if (selection && !selection.isCollapsed) return;
  event.preventDefault();
  openComment(el);
});
let autosaveTimer = null;
function persistActiveComment() {
  if (!activeId) return;
  const el = document.querySelector('[data-comment-id="' + CSS.escape(activeId) + '"]');
  comments[activeId] = {
    text: textarea.value,
    file: el?.dataset.file || '',
    side: el?.dataset.side || '',
    line: el?.dataset.line || el?.dataset.newLine || el?.dataset.oldLine || '',
    lineRange: el?.dataset.lineRange || '',
    oldLine: el?.dataset.oldLine || '',
    newLine: el?.dataset.newLine || '',
    code: el?.dataset.code || '',
  };
  if (!comments[activeId].text.trim()) delete comments[activeId];
  writeJson(commentsKey, comments);
  updateCommentMarkers();
}
function scheduleAutosave() {
  clearTimeout(autosaveTimer);
  autosaveTimer = setTimeout(persistActiveComment, 300);
}
function closeCommentEditor() {
  clearTimeout(autosaveTimer);
  persistActiveComment();
  modal.classList.remove('open');
}
textarea.addEventListener('input', scheduleAutosave);
textarea.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    event.preventDefault();
    closeCommentEditor();
  } else if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
    event.preventDefault();
    closeCommentEditor();
  }
});
modal.addEventListener('click', (event) => { if (event.target === modal) closeCommentEditor(); });
document.getElementById('clear-comments').addEventListener('click', () => {
  if (!confirm('Clear all local comments for this review?')) return;
  comments = {};
  writeJson(commentsKey, comments);
  updateCommentMarkers();
});
updateCommentMarkers();

document.getElementById('copy-comments').addEventListener('click', async () => {
  comments = readJson(commentsKey, {});
  const entries = Object.values(comments).filter((comment) => comment.text?.trim());
  const grouped = new Map();
  for (const comment of entries) {
    if (!grouped.has(comment.file)) grouped.set(comment.file, []);
    grouped.get(comment.file).push(comment);
  }
  const sections = ['# PR review comments', '', 'Generated from ' + location.href, ${JSON.stringify(spec.prUrl)} ? 'GitHub PR: ' + ${JSON.stringify(spec.prUrl)} : ''];
  for (const [file, fileComments] of grouped) {
    sections.push('', '## ' + file, '');
    for (const comment of fileComments) {
      const lineLabel = comment.lineRange ? 'lines ' + comment.lineRange : (comment.side + ' line ' + comment.line + (comment.oldLine && comment.newLine ? ' (old ' + comment.oldLine + ', new ' + comment.newLine + ')' : ''));
      sections.push('- ' + lineLabel, '  Code: ' + comment.code, '  Comment:', '  ' + comment.text.replace(/\\n/g, '\\n  '), '');
    }
  }
  await navigator.clipboard.writeText(sections.filter((line, i) => line !== '' || sections[i - 1] !== '').join('\\n'));
  setToolbarStatus('Copied ' + entries.length + ' comment(s).');
});
</script>
</body>
</html>`;
}

function renderChapter(chapter, index, hunksById, filesById, sourceScripts) {
  const items = chapter.items.map((item) => renderItem(item, hunksById, filesById, sourceScripts)).join("\n");
  return `<section class="chapter" id="${escapeAttr(chapter.id)}">
<p class="eyebrow">Chapter ${index + 1}</p>
<h2>${index + 1}. ${escapeHtml(chapter.title)}</h2>
${chapter.subtitle ? `<p class="subtitle">${escapeHtml(chapter.subtitle)}</p>` : ""}
${renderMarkdownish(chapter.body)}
<div class="focus"><strong>Review focus</strong><ul>${chapter.reviewFocus.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>
${items}
</section>`;
}

function lineCount(text) {
  if (!text) return 0;
  return text.split("\n").length;
}

function renderSourceFallback(path, content) {
  return content.split("\n").map((line, index) => {
    const lineNo = index + 1;
    const commentId = `${path}|new|${lineNo}`;
    return `<div class="source-line commentable" data-comment-id="${escapeAttr(commentId)}" data-file="${escapeAttr(path)}" data-side="new" data-line="${lineNo}" data-code="${escapeAttr(line)}"><span class="source-ln">${lineNo}</span><span class="source-code">${escapeHtml(line || " ")}</span></div>`;
  }).join("\n");
}

function renderItem(item, hunksById, filesById, sourceScripts) {
  const collapseId = slugForId(item.id);
  if (item.kind === "file") {
    const file = filesById.get(item.id);
    const sourceId = `source-${sourceScripts.length + 1}`;
    sourceScripts.push(`<script type="application/json" id="${sourceId}">${scriptJson(file.content)}</script>`);
    const count = lineCount(file.content);
    const body = isMarkdownFile(file.path)
      ? `<div class="rendered-md markdown-body" data-markdown-source="${sourceId}" data-file="${escapeAttr(file.path)}"><p>Rendering Markdown…</p></div>`
      : `<div class="source-view" data-source-code="${sourceId}" data-file="${escapeAttr(file.path)}" data-language="${escapeAttr(fileLanguage(file.path))}">${renderSourceFallback(file.path, file.content)}</div>`;
    const defaultCollapsed = file.path.endsWith(".test.ts") ? " data-default-collapsed=\"true\"" : "";
    return `<details class="unit" open data-collapse-id="${escapeAttr(collapseId)}"${defaultCollapsed}><summary><span>${escapeHtml(item.path)} <span class="pill">new file</span> <small>${count} lines</small></span><small>${escapeHtml(item.description)}</small></summary>${body}</details>`;
  }
  const hunk = hunksById.get(item.id);
  const count = hunk.lines.length;
  const defaultCollapsed = hunk.path.endsWith(".test.ts") ? " data-default-collapsed=\"true\"" : "";
  return `<details class="unit" open data-collapse-id="${escapeAttr(collapseId)}"${defaultCollapsed}><summary><span>${escapeHtml(hunk.path)} <span class="pill">hunk</span> <small>${count} lines</small></span><small>${escapeHtml(item.description)}</small></summary>${renderHunkTable(hunk, item.id)}</details>`;
}

function renderHunkTable(hunk, hunkId) {
  let oldLine = hunk.oldStart;
  let newLine = hunk.newStart;
  const rows = [`<tr class="hunk-head"><td colspan="4">${escapeHtml(hunk.header)}</td></tr>`];
  for (const raw of hunk.lines) {
    const marker = raw[0] === "+" || raw[0] === "-" ? raw[0] : " ";
    const code = raw.length > 0 ? raw.slice(1) : "";
    const cls = marker === "+" ? "add" : marker === "-" ? "del" : "ctx";
    const oldText = marker === "+" ? "" : oldLine++;
    const newText = marker === "-" ? "" : newLine++;
    const side = marker === "-" ? "old" : "new";
    const line = marker === "-" ? oldText : newText;
    const commentId = `${hunkId}|${side}|${line}`;
    const data = line === "" ? "" : ` data-comment-id="${escapeAttr(commentId)}" data-file="${escapeAttr(hunk.path)}" data-side="${side}" data-old-line="${oldText}" data-new-line="${newText}" data-line="${line}" data-code="${escapeAttr(code)}"`;
    const commentable = line === "" ? "" : " commentable";
    rows.push(`<tr class="diff-line ${cls}${commentable}"${data}><td class="ln">${oldText}</td><td class="ln">${newText}</td><td class="mark">${marker === " " ? "" : marker}</td><td class="code">${escapeHtml(code)}</td></tr>`);
  }
  return `<table class="diff-table"><colgroup><col class="col-old"><col class="col-new"><col class="col-mark"><col class="col-code"></colgroup><tbody>${rows.join("\n")}</tbody></table>`;
}

function extract(opts) {
  const html = readFileSync(requireOpt(opts, "html"), "utf-8");
  const out = requireOpt(opts, "out");
  const match = /<script[^>]+id=["']pr-review-spec["'][^>]*>([\s\S]*?)<\/script>/.exec(html);
  if (!match) throw new Error("No embedded pr-review-spec script found.");
  const spec = JSON.parse(match[1]);
  writeJson(out, spec);
  console.log(`Wrote ${out}`);
}

try {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.command === "scaffold") scaffold(opts);
  else if (opts.command === "render") render(opts);
  else if (opts.command === "extract") extract(opts);
  else {
    usage();
    process.exit(1);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
