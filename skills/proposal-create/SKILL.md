---
name: proposal-create
description: Fill a duplicated Mord-style Arabic (RTL) proposal deck in Figma Slides with content from a brief and brand assets from the NGO's website. Use when the user says "create a proposal", "make a proposal", "proposal for <client>", "Suhail proposal", or uses Arabic "عرض", "عرض فني", "مقترح", especially when paired with a Figma URL + NGO website URL + brief.
version: 1.0.0
---

# proposal-create

Populates a duplicated copy of the Suhail Mord master template with client-specific content. The skill does **not** create files or copy templates — the designer duplicates the master template in Figma UI (one click), and this skill fills in the duplicate.

## The workflow at a glance

1. **Designer prepares (manual, one minute):**
   - Open the Mord master template in Figma (fileKey `JtzNUXrAHFupkajwfPz952`)
   - Right-click the file or use File menu → **Duplicate**
   - Open the duplicate, copy its URL
2. **Designer invokes the skill:**
   ```
   /proposal-create
     figma_url=https://www.figma.com/slides/<NEW_KEY>/...
     client_url=https://kyan.org.sa
     brief=path/to/brief.docx
   ```
3. **Skill runs:** fetches the NGO logo + brand color, reads the brief, walks the duplicated Figma file, substitutes every `{{placeholder}}` with the right Arabic content, swaps the logo image, and applies the NGO's primary color to brand-accent elements.
4. **Designer reviews:** opens the populated file, proofreads, polishes anything that didn't fit.

## Prerequisites (per-user setup)

Each teammate needs:

1. **Figma MCP connector** in their Claude Code, signed in to a Figma plan that allows the connector. The MCP prefix is environment-specific — the skill locates it at runtime.
2. **Access to the Mord master template** (`JtzNUXrAHFupkajwfPz952`) — shared by Guillermo via Figma.
3. **The Suhail custom fonts** (`Droid Arabic Kufi`, `IBM Plex Sans Arabic`) uploaded to their Figma team. Guillermo did this once for the team; new teammates inherit it automatically.
4. **Python 3** with `beautifulsoup4`, `Pillow`, `python-docx`, `requests` (for the brand-extraction and brief-parsing helpers — `pip install -r requirements.txt`).

No FIGMA_TOKEN or REST API access is required. The skill uses the Figma MCP plugin API.

## Required inputs

- `figma_url` — URL of the **duplicated Mord file** the designer created. The skill writes into this file.
- `client_url` — the NGO's website. Source of logo, primary hex, official Arabic name.
- `brief` — the project brief. Either a file path (`.docx` / `.md` / `.txt`) or inline text.

## Optional inputs

- `primary_hex`, `logo_path` — manual overrides if the website scrape is wrong.
- `client_name` — Arabic NGO name override (defaults to what's extracted from the website).

If `figma_url`, `client_url`, or `brief` is missing, ask **once** with a single combined question. Don't loop.

## Workflow steps

### 0. Locate the Figma MCP tools

The MCP prefix is environment-specific (UUID per user). At session start, identify the prefix via ToolSearch (query: `figma whoami`) or by inspecting loaded tool names. Find any tool with `whoami`, `use_figma`, `get_screenshot`, `upload_assets` in its name and use the `mcp__<prefix>__` portion. If no Figma MCP is connected, stop and tell the user.

### 1. Extract brand assets from the NGO website

Call `fetch_brand.py --url <client_url> --out <tempdir>`. Returns JSON `{logo_url, primary_hex, secondary_hex, org_name_ar, mission_ar}`. If `logo_url` or `primary_hex` is null, fall back to `WebFetch` of the homepage. If still null, use `assets/suhail-default-palette.json` and tell the user the logo wasn't found.

See `references/brand-extraction.md` for edge cases.

### 2. Parse the brief

Call `parse_brief.py <path>` if `brief` is a file path. Otherwise read inline text. The script returns the full brief text grouped by section heading (the Arabic headings from the example: `الملخص التنفيذي`, `ارتباط المشروع باستراتيجية الجمعية`, `السياق العام`, etc.).

If the brief is missing entire sections (no `الجدول الزمني` for example), do not invent content. The corresponding placeholders stay as `{{token}}` and surface as visible gaps in the deck.

### 3. Map brief content to placeholders

This is the heart of the skill. Read `references/content-sections.md` to know which placeholder lives on which slide. Then, **reading the brief and the schema together**, build a mapping `{placeholder_token: arabic_content}` covering every `{{token}}` in the Mord layout.

The full list of placeholder tokens is in `references/content-sections.md`. Examples:

- `{{project_title}}` ← brief's project title (first heading or cover line)
- `{{exec_intro}}` ← top paragraph of `الملخص التنفيذي`
- `{{exec_point_1}}` … `{{exec_point_3}}` ← the three numbered or bulleted points
- `{{strategy_vision}}` ← the "vision" item in the strategy section
- `{{phase_3_objective}}`, `{{phase_3_activities}}`, `{{phase_3_deliverables}}`, `{{phase_3_requirements}}` ← phase 3 ("فهم التحدي") fields
- …

**Use Arabic comprehension, not regex.** The brief's structure is a guide; the placeholder schema is the target. Match by meaning. If a brief paragraph clearly maps to one placeholder, use it. If a paragraph could fit multiple, choose the closest. If a placeholder has no brief content, leave it as `{{token}}` and log a warning.

**Hard rule:** never invent commercial commitments. If the brief lacks `methodology`, `timeline`, `KPIs`, or `deliverables`, leave those placeholders visible. Designer fills them in by hand.

### 4. Walk the Figma file and substitute

For each slide (1..18) in the duplicated file at `figma_url`:

1. `use_figma` to find all TEXT nodes whose `characters` contains `{{`.
2. For each such node, look up the placeholder token in the mapping. If found, set `node.characters = mapped_value`. If not found, leave as-is.
3. Load all needed fonts up front in one `Promise.all` call (six font weights — see `references/rtl-arabic.md`).

Batch by slide. One `use_figma` call per slide keeps payloads under the 50KB limit.

### 5. Swap the logo

`figma.findOne(n => n.name === "logo_container")` returns the cover slide's logo rectangle. Upload the NGO logo via `upload_assets({fileKey, count: 1, nodeId: <logo_container_id>})` — this returns a short-lived URL; POST the logo bytes to it. If the logo is >5MB, downscale to PNG width 1024 first.

### 6. Apply the brand primary color

For each node whose name starts with `brand_primary_` (slide 1 cover bar, TOC badges, section accent backgrounds, strategy frame backgrounds, methodology accents, etc.), set its solid fill to the NGO's primary hex. Convert hex → 0-1 RGB:

```javascript
const hex2rgb = h => ({
  r: parseInt(h.slice(1, 3), 16) / 255,
  g: parseInt(h.slice(3, 5), 16) / 255,
  b: parseInt(h.slice(5, 7), 16) / 255,
});
```

### 7. Verify and report

`get_screenshot` of slide 1 (cover) and one mid-deck slide (e.g. slide 7 methodology_intro). Confirm the logo placed, the brand color applied, Arabic shaped correctly. Reply with `figma_url` and a list of any placeholders that remained unfilled (for the designer to address by hand).

## Hard rules

- **Don't hallucinate scope, deliverables, KPIs, pricing, or timeline.** Missing brief content stays as visible `{{placeholder}}`.
- **Don't write to the master template** (`JtzNUXrAHFupkajwfPz952`). Always write to the duplicated file. If `figma_url` points to the master, stop and ask the designer to duplicate first.
- **Don't generate the deck in English** unless the user explicitly overrides. Default is Arabic RTL.
- **Don't use Figma's REST API.** It doesn't support Slides files. Use only MCP tools (`use_figma`, `get_screenshot`, `upload_assets`, `whoami`).

## What to read when

- Lay out Arabic correctly → `references/rtl-arabic.md`
- See the full placeholder schema for every slide → `references/content-sections.md`
- Extract a logo or color from a stubborn website → `references/brand-extraction.md`
- See the Mord template's known quirks → `references/content-sections.md` ("Known quirks" section)
