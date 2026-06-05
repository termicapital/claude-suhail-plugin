---
name: proposal-html
description: Generates a single-file Arabic print-ready HTML proposal from a project brief. No animations, no JS, PDF-exportable via browser print. Use for NGO/non-profit technical proposals in Saudi Arabia when a Figma deck is not required and token budget matters.
version: 1.1.0
user-invocable: true
argument-hint: "<brief_path> [client_url_or_hex] [output.html]"
---

Transforms a project brief into a styled Arabic HTML document optimized for A4 PDF export. One pass — no browser iteration, no setup scripts, no approval gates. Token budget: ~10k total. The output is a single `.html` file with all CSS inline and zero JavaScript, so it prints to PDF identically everywhere.

## Inputs

| Param | Description | Example |
|---|---|---|
| `brief` | Path to `.docx`, `.md`, or `.txt` | `brief.docx` |
| `client` | Brand URL, hex color, or known client name | `kyan.org.sa` or `#1c7993` |
| `output` | Output filename (default: `proposal.html`) | `kyan-proposal.html` |

## Critical rule: client-only branding

The proposal represents the **client** to **their** stakeholders (board, donors, government). The producing agency (Suhail) must be **invisible** in the artifact.

- **Never** put Suhail's logo, name ("سهيل"/"Suhail"), `suhailsa.com`, or any Suhail email anywhere in the output.
- Only the **client's** brand appears: their logo, colors, name, and `client.org.sa` / `info@client...`.
- The closing/contact slide shows the **client's** contact details, not the agency's.

This is the single most common mistake — scrub every slide for agency references before saving.

## Workflow

### Step 1 — Extract brief content

Read the brief with Python (force UTF-8 on Windows):

```python
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document("path/to/brief.docx")
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
tables = [[[c.text.strip() for c in row.cells] for row in t.rows] for t in doc.tables]
```

Map content to these slots — if a slot is missing, leave it empty, **never hallucinate** scope, KPIs, pricing, dates, or deliverables:

- `cover_title`, `cover_subtitle`, `client_name`, `date`
- `exec_summary` + key points
- `context_paragraphs`, `methodology_principle` (the core quote)
- `challenges[]` — `{title, body}`
- `phases[]` — `{title, goal, activities[], deliverables[], requirements}` (from the per-phase tables)
- `deliverables[]` — `{name, description}`
- `kpis[]` — `{indicator, description, examples}`
- `timeline[]` — `{phase_name, months[]}` (boolean per month)

### Step 2 — Resolve brand and gather assets

Create an `assets/` folder next to the output file. Then:

**Brand color** — priority order, stop at first match:
1. `client` is a URL → WebFetch it; read CSS `--thm-*`/brand variables or the first non-white/black hex.
2. `client` is a hex → use directly.
3. Known client (e.g. Kyan = `#1c7993` primary, `#2c2734` dark) → use stored values.
4. None → ask the user; do not guess a palette.

Derive: `--primary` (brand), `--dark` (brand's dark or primary darkened ~30%), `--surface` (very light tint of primary), `--accent-light` (light tint for table rows).

**Client logo** — download from the site to `assets/`:
```python
import urllib.request
for fname, url in {
    'logo-header.png': 'https://CLIENT/assets/images/logo-header.png',  # horizontal wordmark
    'logo-full.png':   'https://CLIENT/assets/images/full-logo.png',    # stacked/full color
}.items():
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    open(f'assets/{fname}','wb').write(urllib.request.urlopen(req, timeout=10).read())
```

**Imagery** — abstract, brand-colored conceptual images carry the design.
- **Reuse first**: if a prior deliverable folder for this client already has generated imagery (`img-cover`, `img-innovation`, `img-journey`, `img-vision`, `img-closing`), copy those into `assets/`. They are token-free and already on-brand.
- Else generate with an efficient image model (e.g. Higgsfield `z_image` / GPT Image 2) in the client's palette. Save to `assets/`.
- **Motif → slide mapping** (themes that read well for an "idea → product → scale" narrative):
  - abstract waves/particles (dark) → cover background
  - lightbulb + network / concept diagram → context (الابتكار) band
  - winding glowing path / road → methodology journey band
  - ascending glass stairs → phases overview band + closing background

### Step 3 — Generate HTML

Single file, all CSS in `<style>`, **zero JavaScript, zero animation** (no `transition`, `@keyframes`, or `animation` — it must freeze identically into PDF).

**Page setup**
```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;600;700;900&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&display=swap');
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
body { direction:rtl; font-family:'IBM Plex Sans Arabic',sans-serif; font-size:13px; line-height:1.8; color:var(--ink); background:#d4d4d4; }
section.slide { width:210mm; min-height:297mm; height:297mm; margin:0 auto 10px; background:var(--white); overflow:hidden; position:relative; display:flex; flex-direction:column; }
.slide-inner { padding:9mm 13mm; flex:1; display:flex; flex-direction:column; }
@media print { body{background:transparent;margin:0;} section.slide{margin:0;page-break-after:always;break-after:page;} }
```

**Client logo on every slide** — top-left, no white box. One CSS rule covers all content slides:
```css
section.slide:not(.slide-cover)::after {
  content:""; position:absolute; top:7mm; left:13mm;
  width:105px; height:24px;
  background:url(assets/logo-header.png) left center / contain no-repeat;
  z-index:6; opacity:0.95; pointer-events:none;
}
```
On **dark** backgrounds (cover, dark contact box) place the logo as a real `<img>` and invert it to white: `filter: brightness(0) invert(1)`. Never wrap the logo in a white box — sit it directly on the slide; invert only when contrast demands it.

**Typography** — display/headings in `Noto Kufi Arabic`, body in `IBM Plex Sans Arabic`. Scale with ≥1.25 weight/size contrast. Numerals in mixed strings: wrap in `<span dir="ltr">`.

**Fill rules — every slide must fill A4 with neither large empty bands nor oversized boxes holding tiny content.** This is the hardest part; pick the tactic per slide:
- **Grids of many short items** (challenges, phase cards): fixed equal rows `grid-template-rows: repeat(n, 1fr)` + `flex:1`, and **center each card's content** (`align-items:center` / `justify-content:center`). Cards read as solid feature tiles and the grid fills the page.
- **Stacks of rich cards** (phase details): cards `flex:1`; inside, pin the secondary row (e.g. requirements) to the card bottom and keep the lists at the top — the card reads as content + footer, not an empty box.
- **Tables** (KPIs, timeline): set the `<table>` to `flex:1` and `td { vertical-align:middle }` → rows distribute to fill the height.
- **Content-light slides** (executive summary): anchor the bottom with a **full-width image band that grows** (`flex:1; min-height:0`) so there is no gap — content on top, hero band fills the rest.
- **Simple lists** (deliverables): `flex:1; justify-content:space-between` (or `space-evenly`).
- **Avoid** `align-content:space-between` when content is far smaller than the container — it produces huge gaps between rows. Prefer equal `1fr` rows with centered content.

**Images = full-width horizontal bands**, bled to the slide edges with negative margins, never awkward side panels:
```html
<div style="width:calc(100% + 26mm); margin:12px -13mm; height:90px; overflow:hidden;">
  <img src="assets/img-journey.png" style="width:100%;height:100%;object-fit:cover;object-position:center 45%;display:block;">
</div>
```

**Slide structure** (adapt count to the brief; typical 13):
1. Cover — dark image bg, client logo (inverted, top-left), title, subtitle, client name + date.
2. Table of contents — 2-col numbered grid.
3. Executive summary — lead quote + key points + hero image band.
4. Strategic context — paragraphs + concept image band + pull-quote.
5. Challenges — equal-row grid, alternate some tiles in `--primary` for rhythm.
6. Methodology / journey — intro + path image band + numbered step flow + principle callout.
7. Phases overview — equal-row grid of phase tiles + stairs image band.
8–10. Phase details — stacked cards, 3 phases/slide (activities, deliverables, requirements footer).
11. Deliverables — distributed numbered list.
12. KPIs — full table, `--primary` header, zebra rows, fills height.
13. Timeline — Gantt table (months as columns, `--primary` cells) + client contact box (dark image bg).

**Banned patterns**: gradient text, side-stripe-only cards, all-caps body, glassmorphism, shadow on everything, decorative empty circles, identical-everywhere spacing, numbered eyebrows on every heading, and (most important here) any agency/Suhail reference.

### Step 4 — Save and confirm

Write the HTML, then print:
```
✓ Saved: <path>   (<n> slides, A4)
  Brand: <--primary> / <--dark>   Assets: assets/ (<count> files)
PDF: open in Chrome → Ctrl/Cmd+P → A4, margins None, Background graphics ON.
```

## Quality checklist (run before saving)

- [ ] **No agency branding anywhere** — no Suhail logo/name/url/email; only the client's.
- [ ] Client logo on every slide (inverted on dark backgrounds, no white box).
- [ ] Every slide fills A4 — no large empty bands, no oversized boxes with tiny centered content.
- [ ] All text RTL; numerals wrapped in `<span dir="ltr">`.
- [ ] Table headers/text meet contrast (white on `--primary`).
- [ ] No `transition`/`animation` anywhere; no JavaScript.
- [ ] Brief content is verbatim — no invented KPIs, dates, scope, or pricing.
- [ ] Images are full-width bands, well-cropped (`object-position` tuned), not stretched or clipping faces/logos.
