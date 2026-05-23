# Implementation Plan — `proposal-create` v1.0 (team edition)

**Authored by:** Opus 4.7, 2026-05-23
**To be executed by:** Haiku 4.5 (in a separate session)
**Target skill path:** `C:\Users\gjira\.claude\plugins\suhail\skills\proposal-create\`
**Target distribution repo:** GitHub private personal repo under Guillermo's account (e.g. `gjira/suhail-claude-plugin`)

---

## 1. Context Haiku needs before starting

Read these first, in this order:

1. `C:\Users\gjira\.claude\plugins\suhail\skills\proposal-create\SKILL.md` — current v0.3.0. Most logic is preserved; only the slide-building step is replaced.
2. `references/content-sections.md`, `references/rtl-arabic.md`, `references/brand-extraction.md`, `references/slide-templates.md` — keep these; only `slide-templates.md` will be trimmed.
3. `C:\Users\gjira\.claude\projects\C--Users-gjira-OneDrive---Suhail\memory\MEMORY.md` and the linked memory files — context on the user, the Figma MCP account, and the OneDrive reference folder.
4. The Mord template at Figma fileKey `JtzNUXrAHFupkajwfPz952` — this is the single canonical template now. The other two (`s1ZJkZ6vGxhnR5D5zF9bdc` AlUla, `PNVPb5cMrL0xoP9ZAWpbPh` Ofuq) are being removed from scope.

**Figma MCP prefix:** server prefix is environment-specific (UUID). Locate at runtime via ToolSearch (`query="figma whoami"`) — every Figma tool reference in this plan should be mentally prepended with `mcp__<prefix>__`.

---

## 2. The big architectural change vs. v0.3.0

v0.3.0 builds slides procedurally with `figma.createSlide()` + positioning code. Result: visual layout drifts from the Mord design (compare [Kyan generated deck](https://www.figma.com/slides/ewm77Vl7rVuuTgXRuzay2t/) vs Mord template — typography, spacing, illustrations diverge).

v1.0 flips this: **the deck is a structural replay of the Mord template** with text/brand-asset substitution. No more "build from scratch."

**Pipeline:**

```
[one-time, in repo build]                       [per-run, in skill]
Mord (JtzNUXrAHFupkajwfPz952)                    NGO URL + brief
        |                                                |
        v                                                v
snapshot_template.py                            extract brand + parse brief
        |                                                |
        v                                                v
templates/mord.snapshot.json                    apply substitutions
templates/assets/*.png         ----merged----> recreate nodes in new Figma file
        |                                                |
        v                                                v
committed to git                                return Figma URL
```

**Key principle:** the snapshot is the source of truth, not the live Mord file. Teammates don't need access to the Mord template at runtime — only at snapshot-refresh time (rare; done by you).

---

## 3. Phases

Each phase below has a clear deliverable, exit criteria, and pitfalls.

### Phase 0 — Strip v0.3.0 down (≈30 min)

**Goal:** remove dead code paths from the procedural slide-builder.

**Steps:**

1. Edit `references/slide-templates.md`:
   - Drop AlUla and Ofuq references.
   - Keep Mord (`JtzNUXrAHFupkajwfPz952`) as the only template, with a note: "Used at snapshot time only; runtime uses the cached snapshot."
2. Edit `SKILL.md`:
   - Remove sections "Workflow steps 6 (Build the slides...)" and "Slides API gotchas" (most still apply but will be re-stated in the snapshot-replay code, not in SKILL.md).
   - Replace with placeholder text: "See `WORKFLOW.md` — to be written in Phase 3."
3. Don't delete `scripts/fetch_brand.py` or `scripts/parse_brief.py` — those are reused.
4. Don't delete `assets/suhail-default-palette.json`.

**Exit criteria:** `SKILL.md` no longer references procedural slide building. Skill still loads without errors when invoked (Haiku can run `/proposal-create` and confirm it prints the new "WIP" message rather than crashing).

---

### Phase 1 — Add `{{placeholders}}` to Mord itself (Opus partially completed 2026-05-23; Haiku to finish slides 6–18)

**Approach change from original plan:** Guillermo doesn't read Arabic, so manual edits in Figma UI weren't feasible. Instead, **Mord (`JtzNUXrAHFupkajwfPz952`) itself is the master template** — no separate copy. Opus 4.7 hand-edited slides 1–5 via the Figma MCP during a planning session, establishing the naming conventions documented in `references/content-sections.md`. Haiku must finish slides 6–18 using the same conventions.

**Setup complete (do not redo):**

- Custom fonts uploaded to the Figma team (Droid Arabic Kufi + IBM Plex Sans Arabic, all weights Mord uses). `figma.loadFontAsync` works for both families.
- Brand primary color identified: teal RGB `(0.027, 0.608, 0.753)` ≈ `#079BC0`. The dark navy `(0.19, 0.27, 0.41)` ≈ `#304468` is Suhail's neutral, stays fixed.
- Slides 1–5 fully done: cover, TOC, exec_summary, strategy, context. See `references/content-sections.md` for the placeholder list per slide and the naming conventions.

**What Haiku must do for slides 6–18:**

For each slide:
1. Inspect text nodes (use `slide.findAll(n => n.type === "TEXT")` — but **be careful with slide 6**, which timed out under deep walks in Opus's session; try direct-children-only queries first, or smaller scoped walks).
2. Classify each text node:
   - Boilerplate (slide title, "نقاط يغطيها العرض" sublabels, Page Number, Headline, subheader labels like "الرؤية الاستراتيجية") → leave untouched.
   - Client content (long Arabic body paragraphs, named card titles + bodies) → replace with `{{semantic_placeholder}}`.
3. Identify brand-color elements: any non-text node whose first fill is solid teal `(0.027, 0.608, 0.753)`. Rename to `brand_primary_<section>_<role>`.
4. Rename the slide itself: `NN — <slug> | section=<section_id>` (per the section_id column in `references/content-sections.md`).
5. **Always load all needed font weights before any `setRangeFontName` or `node.characters = ...`** — text nodes can have mixed font runs (Opus hit this on slide 5 where one paragraph had a Medium run inside what looked like a Regular paragraph). Load IBM Plex Sans Arabic Regular/Medium/SemiBold/Bold + Droid Arabic Kufi Regular/Bold up front.

**Per-slide placeholder targets (Haiku, follow the schema in `content-sections.md`):**

- Slide 6 (`understanding`): intro paragraph + 8 challenge cards (title + body each)
- Slide 7 (`methodology_intro`): `{{methodology_overview}}`, `{{methodology_expected_outcome}}`, `{{methodology_principle}}` — done text node IDs in the inspection that succeeded: 1:567, 1:575, 1:583
- Slide 8 (`methodology_phases`): 9 phase cards (title + brief each)
- Slides 9–13 (`methodology_detail_a..e`): per-phase objective/activities/deliverables
- Slide 14 (`diagnosis`): N diagnosis axes
- Slide 15 (`deliverables`): N final deliverables
- Slide 16 (`kpis`): N KPI rows (metric + target)
- Slide 17 (`timeline`): 12-month gantt — 114 text nodes; expect this to need 3–4 separate `use_figma` calls
- Slide 18 (`closing`): only rename the slide to `18 — closing | section=closing`; "شكراً" stays.

**Steps (for Guillermo, before invoking Haiku):**

1. In Figma UI: open Mord (`JtzNUXrAHFupkajwfPz952`), select "Duplicate" → move the copy into the **shared Suhail team space** (not personal drafts), rename to **"Suhail — Master Proposal Template"**. Note the new fileKey and the Suhail team's `planKey` (visible via `whoami` once the team is connected — every teammate's Figma account must be a member of this team so `create_new_file` can target it). Note the new fileKey from the URL.
2. Walk each slide. Replace Mord-specific text with placeholders from the canonical schema in `references/content-sections.md`. Suggested placeholder tokens (one per section):
   - `{{client_name_ar}}` — Arabic NGO name (e.g. "جمعية مرود")
   - `{{client_name_en}}` — Latin transliteration if used anywhere
   - `{{section_about}}` — about-client paragraph
   - `{{section_problem}}` — opportunity/problem paragraph
   - `{{section_solution}}` — proposed solution
   - `{{section_scope}}` — scope/deliverables (bullet list — see "list placeholders" below)
   - `{{section_methodology}}` — methodology
   - `{{section_timeline}}` — timeline (table/bullet)
   - `{{section_team}}` — team
   - `{{section_investment}}` — pricing (table)
   - `{{section_next_steps}}` — next steps
   - `{{section_contact}}` — contact info
3. **Logo:** rename the Mord logo layer (or its container frame) to exactly `logo_container`. Leave the existing logo image in place — runtime will swap it out.
4. **Brand color:** identify Mord's primary accent color usages (likely 3–6 elements: cover gradient/bar, section heading underlines, callout boxes). Rename each of those nodes' parent layer to `brand_primary` (the runtime will recolor any node named `brand_primary` or with `brand_primary` as a prefix, e.g. `brand_primary_cover`). Tip: in Figma, select the elements and rename in bulk.
5. **List placeholders:** for slides that contain bullet lists (scope, timeline, team), use one placeholder per bullet slot (e.g. `{{section_scope_1}}` … `{{section_scope_5}}`). The runtime will fill what it has and remove unused bullet slots.
6. **Section tag for optional-section removal:** at the slide level, rename the slide to start with its section id (e.g. `"02 — about | section=about"`). The runtime parses `section=<id>` from the slide name to decide whether to keep or drop it.
7. Save. Send Haiku the new fileKey (call it `MASTER_TEMPLATE_KEY`).

**Exit criteria:** the master template file exists, has placeholders in every client-variable spot, has `logo_container` and `brand_primary` named layers, and each slide name encodes its section id.

**Pitfall:** Figma text nodes can have mixed runs (different fonts/sizes within one node). When you replace text with a placeholder like `{{section_about}}`, make sure the entire run is the same style — otherwise the runtime substitution loses styling. Workaround: select the text node, "Reset all styles" (option-shift-K), then retype the placeholder.

---

### Phase 2 — Build the snapshot extractor (≈3–4 hours, **Haiku**)

**Goal:** a script that reads `MASTER_TEMPLATE_KEY` once and emits a deterministic JSON file + image assets, both committed to the repo.

**Deliverables:**

- `scripts/snapshot_template.py` — Python script using Figma REST API (requires `FIGMA_TOKEN` env var; Guillermo creates this at https://www.figma.com/developers/api#access-tokens, stored in `.env` which is `.gitignore`d).
- `templates/mord.snapshot.json` — committed to repo.
- `templates/assets/*.png` (and `*.svg` for vectors that can be serialized that way) — committed to repo.

**What the snapshot JSON contains, per slide:**

```json
{
  "version": 1,
  "source_file_key": "<MASTER_TEMPLATE_KEY>",
  "captured_at": "2026-05-23T...",
  "slides": [
    {
      "name": "01 — cover | section=cover",
      "section_id": "cover",
      "background": { "type": "SOLID", "color": [1, 1, 1] },
      "children": [ <node tree> ]
    }
  ]
}
```

**Per node, capture:**

- `type` (TEXT, RECTANGLE, FRAME, VECTOR, ELLIPSE, IMAGE_FILL_RECT, GROUP, INSTANCE)
- `name` (preserves `logo_container`, `brand_primary*` markers)
- `x`, `y`, `width`, `height`, `rotation`
- `fills` — solid colors stay as `{type, color}`; image fills become `{type: "IMAGE", asset_ref: "logo_container_0.png"}` and the image bytes are downloaded into `templates/assets/`
- `strokes`, `strokeWeight`, `strokeAlign`
- `effects` (drop shadows, blurs)
- `cornerRadius`
- `opacity`, `visible`, `blendMode`
- For TEXT: `characters`, `fontName` (family + style), `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `textAlignHorizontal` (MUST preserve "RIGHT" for Arabic), `textAlignVertical`, `fills` (per-character runs if mixed — see Pitfall in Phase 1)
- For VECTOR: `vectorPaths` (winding + path commands), `fills`
- For GROUP/FRAME: recurse into `children`; preserve `clipsContent`, `layoutMode`, `itemSpacing`, `padding*`
- For INSTANCE: a component instance — for v1.0, **detach instances** during snapshot (treat them as their flattened children); we don't want to set up Figma libraries across teammate accounts.

**Implementation notes:**

- Use `requests` + the endpoint `GET https://api.figma.com/v1/files/{file_key}` — returns the full document tree.
- For each `IMAGE` fill, the API returns an `imageRef` (hash). Call `GET https://api.figma.com/v1/files/{file_key}/images?ids=<comma-separated-node-ids>` to get a temporary download URL. Download the bytes, save to `templates/assets/<slide>_<nodeid>.png`.
- For vectors that aren't easily reconstructable from `vectorPaths`, use `GET .../images?ids=<id>&format=svg` and store the SVG. Runtime will use `figma.createNodeFromSvg(svg)`.
- Make the script idempotent: running twice produces identical output (sort children, hash images, etc.). Otherwise repo diffs become noisy.
- Run it once during Phase 2 to populate the repo, then again whenever the master template changes.

**Exit criteria:**

- `python scripts/snapshot_template.py --file-key $MASTER_TEMPLATE_KEY` produces `templates/mord.snapshot.json` and `templates/assets/*.png` without error.
- JSON validates against a simple schema (Haiku writes the schema as `templates/snapshot.schema.json`).
- Re-running the script produces no `git diff`.

**Pitfall:** Figma's REST API rate limits (~50 requests / minute for free, higher for paid). The snapshot script may need ~30+ image requests. Add a 1.5s sleep between calls or batch IDs.

---

### Phase 3 — Build the snapshot-replay workflow (≈4–6 hours, **Haiku**)

**Goal:** given the snapshot + brief + brand, create a new Figma Slides file that visually matches Mord, populated with the NGO's content.

**Deliverables:**

- `WORKFLOW.md` — replaces the deleted slide-building section of SKILL.md.
- `scripts/build_deck.py` (orchestrator) — reads the snapshot, applies substitutions, prepares a single JSON payload, hands off to `use_figma` calls.
- New SKILL.md workflow section pointing to the above.

**Steps in the runtime workflow:**

1. **Locate Figma MCP tools** (same as v0.3.0 Step 0).
2. **Brand extraction** (unchanged from v0.3.0 — `WebFetch` → `fetch_brand.py` fallback → default palette).
3. **Brief parsing** (unchanged — `parse_brief.py` → 11-section JSON; missing sections produce `null`, not placeholders).
4. **Load snapshot** — read `templates/mord.snapshot.json`.
5. **Substitute placeholders** — walk every TEXT node in the snapshot:
   - Replace `{{client_name_ar}}` etc. with brief content
   - If a placeholder maps to a section with `null` brief content AND the slide's `section_id` is in an "optional" list (Phase 4), mark the entire slide for removal
   - If a placeholder remains unsubstituted on a non-optional slide, leave the literal `{{token}}` text (visible to user, like v0.3.0 `[ـ ـ ـ]`) — **never hallucinate scope/pricing/timeline**.
6. **Substitute brand assets:**
   - Find nodes named `logo_container` → upload NGO logo via `upload_assets`, replace fill `asset_ref` with the new image hash
   - Find nodes named `brand_primary*` → replace solid fill color with NGO primary hex (use hex→0-1 RGB snippet from v0.3.0 SKILL.md)
7. **Filter optional slides** — drop any slide whose all-placeholder text was null and whose section is in the optional list.
8. **Create new Figma file:**
   - `whoami` → grab `planKey`
   - `create_new_file({ name: "<client> — عرض فني", editorType: "slides", planKey })`
9. **Replay nodes via `use_figma`** — one call per slide to limit payload size:
   - For each slide: `figma.createSlide()`, set name, create a content `FRAME` (per v0.3.0 gotcha #4 — slides need a content frame to behave predictably), then recursively create children from the snapshot.
   - Apply v0.3.0 gotchas: `fixOffsets` for indices ≥ 4, SLIDE_GRID guards, font loading via `figma.loadFontAsync()` for every unique font in the slide before placing text.
10. **Upload logo asset(s)** — via `upload_assets` (per v0.3.0 step 5; downscale to 1024px PNG if > 5 MB).
11. **Verify** — `get_screenshot` of slide 1 (cover) and one mid-deck slide. Confirm logo placed and Arabic shaped correctly. Reply with the Figma Slides URL.

**Crucial details to preserve from v0.3.0** (these still bite in v1.0):

- `PYTHONIOENCODING=utf-8` for any Python script call (Windows console + Arabic).
- `slide.height` is unreliable after appending children — use `W=1920, H=1080` constants.
- SLIDE_GRID nodes throw on `.fills` access — guard with `if (node.type === "SLIDE_GRID") continue`.
- `get_metadata` does **not** work on Slides files — use `get_screenshot` for verification.
- All TEXT nodes need `textAlignHorizontal = "RIGHT"` for Arabic.

**Image asset upload at replay time:**

Each cached asset in `templates/assets/` needs to be re-uploaded into the new Figma file (image hashes don't transfer across files). Pattern:
- For each unique asset_ref: `upload_assets({ fileKey: newFileKey, count: 1 })` → POST bytes → capture new hash.
- In the node tree, substitute `asset_ref: "logo_container_0.png"` with `imageHash: "<new hash>"` before passing the tree to `use_figma`.

**Exit criteria:**

- Running `/proposal-create` with the existing Kyan brief produces a Figma Slides file that, when screenshotted, is visually indistinguishable from a hand-copied Mord deck (apart from logo + accent color).
- Optional sections (sections with `null` brief content) are absent from the deck (slide count < 11 when brief is partial).
- Skill respects the "no hallucination" rule.

---

### Phase 4 — Optional-section catalog (small, ≈30 min, **Haiku**)

**Goal:** decide which sections are mandatory vs. optional, so the skill knows what to skip.

**Deliverable:** a list at the top of `references/content-sections.md`:

```markdown
## Section optionality

Mandatory (always present, leave `{{placeholder}}` if missing in brief):
- cover
- about
- problem
- solution
- scope
- investment
- contact
- next_steps

Optional (slide is removed if brief lacks content):
- methodology
- timeline
- team
```

Confirmed by Guillermo 2026-05-23: `next_steps` is mandatory, `team` is optional.

---

### Phase 5 — Repo, distribution, and per-teammate setup (≈1–2 hours, **Haiku + Guillermo**)

**Goal:** a teammate can install the skill in one command.

**Deliverables:**

1. `git init` in `C:\Users\gjira\.claude\plugins\suhail\`. Commit everything except `.env`, `__pycache__`, and `.git`. Add a `.gitignore`.
2. Create GitHub private repo (Guillermo creates it — Haiku writes the README and instructs).
3. Remote already exists: `https://github.com/termicapital/claude-suhail-plugin.git`. Target repo name is `proposal-skill` — Haiku should first ask Guillermo to confirm the rename (`gh repo rename proposal-skill --repo termicapital/claude-suhail-plugin`). GitHub creates redirects from the old URL, but the repo URL change affects any teammate who already cloned. If renamed, update the remote: `git remote set-url origin https://github.com/termicapital/proposal-skill.git`.
4. **`README.md` at repo root** (concise, teammate-focused):
   - One-paragraph "what is this".
   - Install steps (assumes repo renamed to `proposal-skill`):
     ```sh
     git clone https://github.com/termicapital/proposal-skill.git ~/.claude/plugins/suhail
     cd ~/.claude/plugins/suhail
     pip install -r requirements.txt
     ```
     (Windows path: `%USERPROFILE%\.claude\plugins\suhail`.) Note the clone target directory is still `suhail` — that's the plugin name in `plugin.json`; the repo name and the plugin name don't have to match.
   - Per-teammate Figma setup:
     - Add the Figma MCP connector to their Claude Code.
     - Ensure their Figma account is Pro tier (required for `create_new_file`).
     - **No Figma Personal Access Token needed at runtime** — the token is only used by `snapshot_template.py`, which only Guillermo runs.
   - Usage: `/proposal-create client_url=https://kyan.org.sa brief=path/to/brief.docx`.
   - "When the template changes" subsection — instructions for re-running the snapshot script.
5. **`requirements.txt`:** `requests`, `beautifulsoup4`, `Pillow`, `python-docx`.
6. **`.env.example`:** `FIGMA_TOKEN=your_token_here`.
7. **`SETUP.md`:** longer-form per-teammate setup, with screenshots-as-text-walkthroughs for the Figma MCP connector flow.
8. **`TEMPLATE_EDITING.md`:** how Guillermo (or a future admin) edits the master template and re-runs `snapshot_template.py`.

**Exit criteria:** a teammate on a fresh machine can follow `README.md` and successfully run `/proposal-create` against the Kyan example brief, producing a deck that matches the Mord style.

---

## 4. Out of scope for v1.0 (so Haiku doesn't gold-plate)

- Multiple template variants (short vs full, strategy vs implementation). Single template only.
- Pricing table auto-format. Pricing slide takes whatever's in the brief; if you want richer formatting later, that's v2.0.
- Bilingual versions. Arabic only.
- Hosted snapshot refresh (CI). Manual refresh only.
- Figma component libraries. Instances are detached during snapshot.
- Auto-publishing to Anthropic marketplace.

---

## 5. Risks and how to mitigate them

| Risk | Likelihood | Mitigation |
|---|---|---|
| Snapshot misses a node property → visual regression | Medium | Phase 3 includes a screenshot-diff smoke test: generate from snapshot, compare cover to Mord cover by eye before declaring done |
| `use_figma` payload exceeds size limit for big snapshots | Medium | Replay one slide per `use_figma` call. If a single slide is still too large, split by section within the slide |
| Arabic fonts not loaded in the new file → broken shaping | High | `figma.loadFontAsync()` for every (family, style) tuple in the snapshot's TEXT nodes, before any `setRangeFontName`. Fail loud if a font is unavailable |
| Image rehosting fails (>10 MB cap, transient network) | Low | Pre-downscale all `templates/assets/*.png` to ≤1024px wide at snapshot time. Retry once on 5xx |
| Teammate's Figma plan blocks `create_new_file` | Medium | `whoami` early; if `tier` isn't `pro`+, halt with a clear message linking to upgrade |
| Master template drifts and snapshot becomes stale | Medium | Snapshot script prints the master's `lastModified` timestamp; runtime warns if snapshot > 90 days old |
| Optional-section removal accidentally drops the wrong slide | Low | `section=<id>` is encoded in slide name; runtime double-checks against the catalog in Phase 4 |

---

## 6. Suggested execution order for Haiku

1. **Phase 0** first (fast cleanup, low risk).
2. **Phase 4** next (no code; just confirms the optional-section catalog with Guillermo).
3. **Pause and wait for Guillermo to deliver `MASTER_TEMPLATE_KEY`** (Phase 1 is manual).
4. **Phase 2** (snapshot extractor) — Haiku writes `snapshot_template.py`, Guillermo runs it once with the new key, snapshot committed.
5. **Phase 3** (replay workflow) — biggest piece; do it in three sub-commits:
   - 3a: load snapshot + apply substitutions + build payload (no Figma calls yet) — testable in isolation
   - 3b: `create_new_file` + node replay for one slide (cover) — visual sanity check
   - 3c: full deck replay + brand swap + optional slide filtering — end-to-end
6. **Phase 5** last (repo + docs only after everything works locally).

---

## 7. Acceptance checklist

Before declaring v1.0 done:

- [ ] `/proposal-create client_url=https://kyan.org.sa brief=<kyan_brief.docx>` produces a Slides file that:
  - [ ] Looks visually identical to Mord layout (compare screenshots side-by-side)
  - [ ] Has Kyan's logo on the cover
  - [ ] Uses Kyan's primary brand color for accent elements
  - [ ] Contains the Kyan content in the right sections
  - [ ] Arabic is right-aligned and shaped correctly
- [ ] Same command with a brief missing the "timeline" section produces a deck **without** the timeline slide.
- [ ] Same command with a brief missing "pricing" leaves `{{section_investment}}` as a visible placeholder (because pricing is mandatory).
- [ ] A teammate following `README.md` from scratch can run the skill successfully.
- [ ] `snapshot_template.py` is idempotent (re-running produces no `git diff`).
- [ ] Repo is pushed to GitHub and Guillermo confirms collaborator access works.

---

## 8. Resolved decisions (Guillermo, 2026-05-23)

1. **Master template:** Mord itself (`JtzNUXrAHFupkajwfPz952`) — no separate copy. Opus partially placeholdered it during the planning session.
2. **Figma team:** `team::1638593656956740161` ("El equipo de g.irarrazaval"). This is the only team `whoami` reports; no separate Suhail team exists yet. The master template plus the uploaded custom fonts live in this team.
3. **Optionality:** all 18 slides are mandatory for v1.0. The optional-section mechanism described in Phase 4 stays in code as a no-op for v1.0; revisit in v2.0 if proposal variants emerge.
4. **Repo name:** Guillermo decided NOT to rename; keep `termicapital/claude-suhail-plugin` as-is.
5. **Custom fonts:** uploaded to the Figma team and verified loadable. `Droid Arabic Kufi` (Bold, Regular) + `IBM Plex Sans Arabic` (Regular, Medium, SemiBold, Bold). Sources cached at `C:\Users\gjira\Downloads\suhail-fonts\for-figma-upload\` in case re-upload is ever needed.

## 9. Phase 1 completion notes for Haiku

Slides done by Opus (do NOT re-edit unless verifying):
- Slide 1 (cover): `{{project_title}}`, `{{project_subtitle}}`; `logo_container`, `brand_primary_accent_bar`
- Slide 2 (toc): boilerplate; 10 `brand_primary_toc_badge_N` + `brand_primary_toc_accent`
- Slide 3 (exec_summary): `{{exec_intro}}` + `{{exec_point_1..3}}`; `brand_primary_exec_bg`/`_accent`
- Slide 4 (strategy): 6 strategy placeholders; `brand_primary_strategy_bg`/`_accent`
- Slide 5 (context): `{{context_para_1..4}}` (para 3 has a duplicate text node — keep both with same placeholder); `brand_primary_context_*` (bg, accent, 14 decorative vectors)

Remaining slides for Haiku: 6 through 18. See `references/content-sections.md` for the per-slide schema and the "Known quirks" section for the slide 6 timeout workaround.
