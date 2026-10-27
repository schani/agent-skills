---
name: nasa-handbook
description: Make printable technical documents in the style of Apollo-era NASA paperwork. The model is an Apollo Operations Handbook "Systems Data" page with a typed running head, numbered paragraphs, Leroy-lettered line drawings and schematics, a performance data table, NOTE/CAUTION/WARNING notices, a Flight Data File checklist card, a black thumb tab and a dated footer, rendered to an A4 or US Letter PDF. Use this whenever someone asks for NASA-style, Apollo-style, retro aerospace or "mission manual" documentation. Also use it for a technical explainer, spec sheet or one-pager that should look like vintage engineering paperwork, for a handbook page explaining a product, codebase, system or fictional gadget, or for "another one of those NASA pages", even if they never say Apollo or handbook.
compatibility: opencode
metadata:
  opencode/slash: "true"
---

# NASA handbook page

This skill makes one-page (or few-page) technical documents that read like a
1969 Apollo Operations Handbook page. A typed running head sits over numbered
paragraphs, followed by a hero line drawing, a second figure, a data table, a
caution and a crew checklist. The thumb tab and the dated footer finish the
page. It suits real subjects (a codebase, a product, a protocol) and fictional
ones (a portal gun). For real subjects, the page should leave the reader
understanding the technical idea. For fiction, it should be convincing.

Finished pages ship with the skill. Look at the PNGs before you start;
they are the bar:
- `assets/examples/portal-gun-device.png` (+ `.html`): a fictional device. It
  has a general arrangement drawing with callouts, dimensions and a section
  view, an electrical schematic, and a deadpan WARNING.
- `assets/examples/espresso-fluid-system.png` (+ `.html`): a fictional machine
  built on real physics (brewing at lunar-habitat cabin pressure). It has a
  general arrangement with a section view, a fluid and electrical schematic
  with station tags, and a computed chart. A fresh agent made it from this
  skill alone in six render passes.
- `assets/examples/pi-durable.png` (+ `.html`): a ten-page software handbook
  covering APIs, task states, replay and operations. `pi-durable-overview.png`
  shows all sheets; `pi-durable-source-notes.md` pins sources and assumptions.

## Resource paths

Paths here are relative to this skill's directory (the base directory reported
when the skill loads):

- `assets/template.html`: the page with all CSS, shared SVG markers,
  a skeleton of every block and a fit check. Start every page from it.
- `assets/fonts/`: Routed Gothic (Leroy lettering), Letter Gothic and their
  licences. Copy the folder next to the page.
- `scripts/render.sh`: renders a PDF and 2x PNG previews in headless Chrome's
  print media. Checks every `.page` before writing; exits 3 on overflow or
  missing/invalid fit data. Uses the standard-library `scripts/render.py`.
- `scripts/check.py`: enforces the expected page count, size, black/white
  source ink and font families. It cuts 300 dpi review tiles (`--out DIR`).
  It can't see overflow; `render.sh` catches that.
- `references/style-guide.md`: anatomy, space budget, typography, writing
  voice, which figures to draw, drawing taste, pitfalls and variants. Read it
  in full for your first page in a session.
- `references/svg-parts.md`: copy-paste drawing parts (boxes, drums, wires,
  breakers, switches, talkbacks, callouts, dimensions, section views,
  timelines, sequence and parts strips, valves, pumps, gauges, sensors,
  station tags, charts).
- `references/sources.md`: the scanned originals and what each taught.

## Workflow

1. **Understand the subject and find its one idea.** This is the sentence the
   reader must leave with ("the coffee brews at sea-level pressure in a sealed circuit"). For a real
   system, read its spec or README and the code. Grep every number you intend
   to print (limits, sizes, intervals, retries, key bindings, UI strings) and
   prefer the code when docs disagree. For fiction, invent a consistent
   specification first: name, what it does, five to eight numbers with units,
   its controls and its one dangerous failure mode.

2. **Plan the page on paper before drawing.** Decide the blocks in the order
   they appear: intro (3 lines), hero figure, functional description
   (4 lines), one underlined mechanism (2 lines), secondary figure (with
   optional DETAIL insets), data table (6–8 rows), one notice, a checklist
   (6–7 steps). Pick figure types from the table in style guide §5. Write the
   text now; it is short, and writing it shows what the figures must explain.

3. **Set up the folder.** Use the folder the user names. Otherwise use a new
   folder in the current project or working directory.
   ```sh
   mkdir -p <out> && cp <skill>/assets/template.html <out>/<name>.html && cp -R <skill>/assets/fonts <out>/fonts
   ```

4. **Fill the template.** Replace every `[BRACKETED]` placeholder. Draw the
   figures from `svg-parts.md` parts in millimetre coordinates. Keep the shared
   `nh-*` marker defs. Draw hatching and stipple as explicit vector strokes
   and circles (`svg-parts.md`); clip them to curved faces. Don't add colours,
   logos or paper texture.

5. **Render and fit.** Run `sh <skill>/scripts/render.sh <out>/<name>.html`.
   Each `fit:` line reports one page's clearance above the footer; aim for
   4–10 mm. Checks use print media after fonts and images load, including
   horizontal descendants, text ranges and SVG geometry/viewBox bounds.
   Missing fit scripts, invalid data and clipping exit 3 without new outputs.
   Cut words or a table row, not type size. In the lower band, trim whichever
   column is taller (style guide §2). `--timeout 90` raises the 45-second budget.

   One page writes `<name>.pdf` and `<name>.png`; multiple pages write one PDF
   and `<name>-1.png`, `<name>-2.png`, etc. Previews use print media, not the
   screen paper tint. Existing outputs are not removed on failure or when
   page counts change; deliver only files listed by a successful run.

   Fit checks are conservative, not a collision detector. SVG strokes and
   template start/end markers are bounded; marker-mid, external markers and
   unsupported marker configurations fail closed. Filters, masks, complex
   stroke joins, CSS effects and arbitrary clip paths still need visual review.

6. **Check and look.** Run
   `uv run --no-project --with pymupdf python <skill>/scripts/check.py <out>/<name>.pdf`.
   It must exit zero: one A4 page, black/white ink and all three font families.
   For Letter use `--size Letter`; custom sizes use `--size 180x240` (mm,
   width first, 0.5 mm tolerance). Use `--pages N` for multi-page PDFs.

   Fonts are checked on visible text, not unused PDF resources. Body defaults
   accept Iowan Old Style/Iowan, Georgia, DejaVu Serif, Liberation Serif,
   Times New Roman or Times; drawings require Routed Gothic/Narrow and
   checklists Letter Gothic Code. Other fonts fail, except sans-serif
   fallbacks for `1 ≤ − ≈`. This checks family presence, not text placement.
   Intentional variants can select `--roles body,drawing` or replace a role's
   allowed families with `--body-font "Helvetica"` (repeat for alternatives;
   likewise `--drawing-font` and `--checklist-font`).

   Ink checks inspect source colours, raster pixels and opacity, so normal
   text/vector antialiasing passes. Raster sources must be bilevel; grey
   pixels and fractional transparency fail. Graphics-state resources are
   checked conservatively, even if unused. Flatten annotations and replace
   shading/soft masks before checking. `--no-tiles` validates without images.

   Then open every tile it lists and look for:
   - a line or leader crossing or touching text (keep 0.6 mm clear)
   - labels touching each other or a box edge
   - a dimension value sitting on its line
   - a clipped word
   - a pattern used with two meanings
   - an arrow pointing at the wrong thing

   Fix them, then repeat steps 5 and 6. Most of the quality comes from this
   loop; expect three to six passes.

7. **Deliver.** Give the PDF as the print file and each PNG as a page preview,
   and show them if you have a preview tool. Say what the page explains. For real
   subjects, list the files you checked the numbers against. Mention anything
   deliberately simplified.

## What makes it look right

These are the calls that separate a convincing page from a costume.
`style-guide.md` has the full reasoning.

- **Structure over texture.** The genre is carried by the running head,
  numbered paragraphs, figure codes, change bar, thumb tab and dated footer.
  Leave out coffee stains, noise, rotated stamps and NASA insignia.
- **Three typefaces, three jobs.** Letter-spaced serif typewriter text for
  prose. Leroy caps for everything inside a drawing. Letter Gothic only on the
  checklist card. All caps is the genre here, not a style mistake.
- **One idea, two figures.** The hero figure draws the one idea; the secondary
  shows how it behaves over time or in detail. Everything else supports them.
- **Flat, exact voice.** Third person, present tense, numbers with units,
  controls in caps as placarded, UI strings quoted exactly.
- **Text is never crossed by a line.** Leaders start just outside their label
  and end on the part. Move a label rather than shrink it.
- **Drafting-sized details.** Line weights from 0.16 to 0.5 mm, arrowheads
  about 2 mm long, labels 2.05 to 2.5 mm. The template's classes and markers
  already encode this; use them instead of ad-hoc strokes.
- **Pure black on pure white.** Differentiate with hatching and dotted
  outlines. Printers turn any tint or grey into dots.
- **Truth first on real subjects.** A precise-looking page with a wrong number
  is worse than one row fewer.

## Variants

US Letter, multi-page sections, controls-and-displays pages, engineering
drawing sheets, Technical Note covers and the 1975 Helvetica look are all
covered in style guide §9. The page structure, the drawing rules and the check
loop stay the same.

## Requirements

- Google Chrome or Chromium, for `render.sh` (set `CHROME=/path` if it isn't
  found).
- Python 3, for `render.sh`; no Python packages or browser driver required.
- `uv` (or a Python with `pymupdf`), for `check.py`.
- Iowan Old Style ships with macOS. Elsewhere the body falls back to Georgia,
  which is acceptable. Helvetica Neue (or Arial) supplies the flagged "1" in
  drawing labels.
