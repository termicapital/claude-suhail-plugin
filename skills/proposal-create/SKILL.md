---
name: proposal-create
description: Generate a Suhail-branded Arabic (RTL) proposal as a Figma Slides deck for a non-profit client. Use when the user says "create a proposal", "make a proposal", "proposal for <client>", "Suhail proposal", "propuesta", or uses Arabic "عرض", "عرض فني", "مقترح", especially when paired with a client website URL or content brief. Triggers on client names like Kyan, Ofuq, MORD, AlUla volunteers.
version: 0.1.0
---

# proposal-create

Generates an Arabic-language Figma Slides proposal for a Suhail non-profit client. The skill fetches the client's brand identity from their website, parses a project brief, and builds the deck via the Figma MCP — logo on cover, brand color as accent, content laid out RTL, with 11 canonical sections.

## Required inputs

- `client_url` — the client's website (e.g. `https://kyan.org.sa`). Source of logo, brand color, official Arabic name, mission.
- `brief` — the project brief. Either a file path (`.docx` / `.md` / `.txt`) or inline text. Source of scope, deliverables, methodology, timeline, pricing, team.

## Optional inputs

- `client_name` — display name override (defaults to the org name extracted from the website).
- `output_name` — Figma file name (defaults to `<client> — عرض فني`).
- `template_key` — Figma fileKey of a reference Slides template to screenshot for visual cues. Defaults to `s1ZJkZ6vGxhnR5D5zF9bdc` (Association of Volunteers in AlUla). Alternates: `JtzNUXrAHFupkajwfPz952` (Mord), `PNVPb5cMrL0xoP9ZAWpbPh` (Ofuq).
- `primary_hex`, `secondary_hex`, `logo_path` — manual overrides if the website scrape is wrong.

If either required input is missing, ask the user **once** with a single combined question. Do not loop.

## Workflow

1. **Brand extraction.** WebFetch `client_url` asking for JSON `{logo_url, primary_hex, secondary_hex, org_name_ar, mission_ar}`. If `logo_url` or `primary_hex` is null, run `scripts/fetch_brand.py --url <client_url> --out <tempdir>` for a Pillow-based fallback. If still null, use `assets/suhail-default-palette.json` and tell the user the logo wasn't found so they can replace it manually. See `references/brand-extraction.md`.

2. **Brief parsing.** If `brief` is a file path, call `scripts/parse_brief.py <path>` → returns JSON keyed by the 11 canonical sections. If inline, do the same section assignment in-context. Missing sections become explicit `"[ـ ـ ـ]"` placeholders in the deck — **never** hallucinate scope, deliverables, pricing, or timeline. See `references/content-sections.md` for the canonical schema.

3. **Reference visual style.** Call `get_screenshot(template_key, nodeId="0:1")` for an all-slides overview of one template, then a handful of individual slide nodes if needed. The proposal is built around the **client's** brand — the template is purely a layout/typography/density reference. Don't propagate any of the template's own client logos or organization names into the new file.

4. **Create the file.** Call `mcp__44c58728-7ce5-4a19-8f50-be1fe9a16701__whoami` → take the first `plans[].key` as `planKey`. Then `create_new_file({ name: "<client> — عرض فني", editorType: "slides", planKey })`. If `planKey` is missing or `tier` is not paid/team, stop and tell the user the Figma plan must be upgraded.

5. **Upload the logo.** `upload_assets({ fileKey, count: 1 })` → returns a short-lived URL. POST the logo bytes to that URL. If the logo file is >5 MB, downscale to PNG width 1024 first (10 MB MCP cap). Capture the returned image hash / URL.

6. **Build the slides** with a sequence of `use_figma` calls grouped by logical section so one failure doesn't redo everything:
   - **Call 1** — probe the Slides API surface, build the cover (logo right, Arabic title, accent bar).
   - **Call 2** — about-client + opportunity/problem.
   - **Call 3** — solution + scope/deliverables.
   - **Call 4** — methodology + timeline.
   - **Call 5** — investment + next steps + contact.
   Every text node: `textAlignHorizontal = "RIGHT"`. Arabic font fallback chain (see `references/rtl-arabic.md`). Brand color as accent bar, headings, and dividers (converted to 0-1 floats — see snippet below).

7. **Verify & return.** `get_screenshot` of the cover. Confirm the logo is placed and Arabic is shaped correctly. Reply with `https://www.figma.com/slides/<fileKey>/<name>`.

## Hex → Figma RGB snippet

Inside any `use_figma` `code`:

```javascript
const hex2rgb = h => ({
  r: parseInt(h.slice(1, 3), 16) / 255,
  g: parseInt(h.slice(3, 5), 16) / 255,
  b: parseInt(h.slice(5, 7), 16) / 255,
});
```

## Slides API probe (run once on the first `use_figma` call)

```javascript
return {
  slideKeys: Object.keys(figma).filter(k => /slide/i.test(k)),
  firstChildType: figma.currentPage.children[0]?.type,
  canCreateSlide: typeof figma.createSlide === "function",
};
```

Use the result to pick between `figma.createSlide()` and `figma.currentPage.appendChild(figma.createSlide())` patterns. Persist the answer in the conversation so later calls don't re-probe.

## What to read when

- Lay out Arabic correctly → `references/rtl-arabic.md`
- Map a brief section to the right slide → `references/slide-templates.md` + `references/content-sections.md`
- Extract a logo or color from a stubborn website → `references/brand-extraction.md`
- Figma plan / planKey edge cases → check `whoami` output structure

## Hard rules

- **Don't hallucinate commercial commitments.** If the brief omits scope, deliverables, pricing, or timeline, leave a visible placeholder. These are contracts.
- **Don't call `get_metadata` on the new file.** It's a Slides file; the tool only works on Design files. Use `get_screenshot` for verification.
- **Don't skip the API probe.** Slides API surface changes; probe once per session before assuming method names.
- **Don't generate the deck in English unless the user explicitly overrides.** Default is Arabic RTL.
