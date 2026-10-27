# NASA handbook

A skill for printable, Apollo-era technical explainers: one idea, two diagrams, verified data and an operational checklist. Start with [`skill/SKILL.md`](skill/SKILL.md).

## Provenance

Adapted from [R44VC0RP/skills — nasa-handbook](https://github.com/R44VC0RP/skills/tree/e6f8682d10458ba4f42f925a4c099f4ceb68a961/skills/nasa-handbook), commit `e6f8682d10458ba4f42f925a4c099f4ceb68a961`.

## Install

This repository keeps installable skills under `<name>/skill/`. Copy that directory, not its parent, into your agent's configured skills directory:

```sh
# Set SKILLS_DIR to your agent's skills directory; destination must not exist.
mkdir -p "$SKILLS_DIR"
cp -R nasa-handbook/skill "$SKILLS_DIR/nasa-handbook"
```

Keep the scripts, references, assets and fonts beside `SKILL.md`.

## Requirements and use

- POSIX shell and Chrome/Chromium; set `CHROME` if automatic discovery fails.
- Python 3; rendering uses a standard-library CDP helper, without a browser driver.
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF checks and tests.
- A serif body font; drawing and checklist fonts are bundled.

From the repository root:

```sh
python3 -m venv /tmp/nasa-handbook-venv
. /tmp/nasa-handbook-venv/bin/activate
python3 -m pip install pymupdf

mkdir -p /tmp/handbook
cp nasa-handbook/skill/assets/template.html /tmp/handbook/page.html
cp -R nasa-handbook/skill/assets/fonts /tmp/handbook/fonts
# Replace the template content before rendering.
sh nasa-handbook/skill/scripts/render.sh /tmp/handbook/page.html
python3 nasa-handbook/skill/scripts/check.py /tmp/handbook/page.pdf \
  --out /tmp/handbook/review
```

Rendering writes PDF and PNG files beside the HTML and checks layout fit. The PDF check validates page count, dimensions, ink and fonts; inspect its tiles for drawing collisions. Run either script with `--help` for options.

## Tests

From the repository root, in the environment above:

```sh
python3 -m unittest discover -s nasa-handbook/tests
```

## Font licenses

- **Routed Gothic:** [SIL Open Font License 1.1](skill/assets/fonts/LICENSE-routed-gothic.md), copyright Darren Embry; “Routed Gothic” is a reserved font name.
- **Letter Gothic Code:** [Aladdin Free Public License 9](skill/assets/fonts/LICENSE-letter-gothic-code.txt), not the SIL OFL. Its redistribution and sale restrictions require separate review.

Retain both bundled license files when copying the fonts.
