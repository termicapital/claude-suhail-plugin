# Phase 1 fix-map — restore Mord template after Haiku's mis-placeholdering

**Status:** Mord template (`JtzNUXrAHFupkajwfPz952`) needs surgical repair on slides 6, 7, 9–14, 16, 17. Slides 1–5, 8, 18 are correct. Slide 15 has a small gap.

**Root cause:** Haiku's Phase 1 pass had the placeholder schema but not the per-slide node-ID mapping. It guessed which nodes to placeholderize and guessed wrong — typically replacing the slide title, the Headline footer, and a Subheader label with placeholders, while leaving the actual body paragraphs as original Mord text.

**Approach for the fixer (Haiku):** apply each table below mechanically. For each row: load fonts as needed, then either set `node.characters = <value>` and `node.name = <layer_name>`, or just rename. Use `figma.getNodeByIdAsync(id)`.

**Required font loads (do once at start of the fix run):**

```js
await Promise.all([
  figma.loadFontAsync({family: "Droid Arabic Kufi", style: "Bold"}),
  figma.loadFontAsync({family: "Droid Arabic Kufi", style: "Regular"}),
  figma.loadFontAsync({family: "IBM Plex Sans Arabic", style: "Regular"}),
  figma.loadFontAsync({family: "IBM Plex Sans Arabic", style: "Medium"}),
  figma.loadFontAsync({family: "IBM Plex Sans Arabic", style: "SemiBold"}),
  figma.loadFontAsync({family: "IBM Plex Sans Arabic", style: "Bold"}),
]);
```

**Action vocabulary:**

- `restore` — set `characters` to the original Mord text (boilerplate that was overwritten). Layer name should also be restored to its semantic name (`Page Number`, `Headline`, `Subheader`, or `Title`).
- `set_placeholder` — set `characters` to the `{{placeholder}}` value. Layer name becomes the placeholder slug (without braces).
- `rename` — only change `name`, leave `characters` alone (used for brand-color elements).
- `leave` — do nothing; node is already correct.

**Schema correction (apply this update to `content-sections.md` before/after the fix):**

The methodology detail slides (9–13) actually have **4 fields per phase**, not 3. Mord's columns are: الهدف (objective), الأنشطة الرئيسية (activities), المخرجات (deliverables), **المتطلبات (requirements)** — the schema was missing `requirements`. Slide 16 (KPIs) also needs a third field per KPI: `description` (Mord's middle column "الوصف / طريقة القياس").

Updated phase-detail placeholders per slide:

- Slide 9: phases 1, 2 → `phase_N_objective`, `phase_N_activities`, `phase_N_deliverables`, `phase_N_requirements` for N ∈ {1, 2}
- Slide 10: same shape for N ∈ {3, 4}
- Slide 11: N ∈ {5, 6}
- Slide 12: N ∈ {7, 8}
- Slide 13: N = 9

Updated KPI placeholders (slide 16): `kpi_N_metric`, `kpi_N_description`, `kpi_N_target` for N = 1..12 (Mord row 1 is the column-header row, not a real KPI — see slide 16 table below).

---

## Slide 7 — methodology_intro (3 misplaced placeholders, 3 unreplaced body paragraphs)

| id | action | new characters | new layer name | notes |
|---|---|---|---|---|
| `1:552` | restore | `06` | `Page Number` | was original page footer |
| `1:554` | restore | `المنهجية المقترحة` | `Headline` | was original section headline |
| `1:564` | restore | `الرؤية العامة للمنهجية` | `Subheader` | was original subheader |
| `1:567` | set_placeholder | `{{methodology_overview}}` | `methodology_overview` | body para about methodology overview |
| `1:575` | set_placeholder | `{{methodology_expected_outcome}}` | `methodology_expected_outcome` | body para about expected outcome |
| `1:583` | set_placeholder | `{{methodology_principle}}` | `methodology_principle` | the "لا نبدأ بالحل..." principle line |

---

## Slide 9 — methodology_detail_a (phases 1+2)

**The damage pattern below repeats on slides 9, 10, 11, 12 with different node IDs.**

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:703` | restore | `مراحل المنهجية: التهيئة والتدريب` | `Title` |
| `1:713` | restore | `التهيئة والتدريب` | `Headline` |
| `1:750` | restore | `الأنشطة الرئيسية` | `Subheader` |
| `1:729` | set_placeholder | `{{phase_1_objective}}` | `phase_1_objective` |
| `1:753` | set_placeholder | `{{phase_1_activities}}` | `phase_1_activities` |
| `1:777` | set_placeholder | `{{phase_1_deliverables}}` | `phase_1_deliverables` |
| `1:800` | set_placeholder | `{{phase_1_requirements}}` | `phase_1_requirements` |
| `1:740` | leave | (keep `{{phase_2_objective}}`) | (already named `phase_2_objective`) |
| `1:766` | set_placeholder | `{{phase_2_activities}}` | `phase_2_activities` |
| `1:788` | set_placeholder | `{{phase_2_deliverables}}` | `phase_2_deliverables` |
| `1:812` | set_placeholder | `{{phase_2_requirements}}` | `phase_2_requirements` |

(Note: `1:711` Page Number was correctly preserved as "08" — no action.)

---

## Slide 10 — methodology_detail_b (phases 3+4)

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:820` | restore | `مراحل المنهجية: التحدي والفرص` | `Title` |
| `1:830` | restore | `التحدي والفرص` | `Headline` |
| `1:867` | restore | `الأنشطة الرئيسية` | `Subheader` |
| `1:846` | set_placeholder | `{{phase_3_objective}}` | `phase_3_objective` |
| `1:870` | set_placeholder | `{{phase_3_activities}}` | `phase_3_activities` |
| `1:894` | set_placeholder | `{{phase_3_deliverables}}` | `phase_3_deliverables` |
| `1:917` | set_placeholder | `{{phase_3_requirements}}` | `phase_3_requirements` |
| `1:857` | leave | (keep `{{phase_4_objective}}`) | already correct |
| `1:883` | set_placeholder | `{{phase_4_activities}}` | `phase_4_activities` |
| `1:905` | set_placeholder | `{{phase_4_deliverables}}` | `phase_4_deliverables` |
| `1:929` | set_placeholder | `{{phase_4_requirements}}` | `phase_4_requirements` |

(Page Number `1:828` = "09" already correct.)

---

## Slide 11 — methodology_detail_c (phases 5+6)

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:937` | restore | `مراحل المنهجية: التصميم والاختبار` | `Title` |
| `1:947` | restore | `التصميم والاختبار` | `Headline` |
| `1:984` | restore | `الأنشطة الرئيسية` | `Subheader` |
| `1:963` | set_placeholder | `{{phase_5_objective}}` | `phase_5_objective` |
| `1:987` | set_placeholder | `{{phase_5_activities}}` | `phase_5_activities` |
| `1:1011` | set_placeholder | `{{phase_5_deliverables}}` | `phase_5_deliverables` |
| `1:1034` | set_placeholder | `{{phase_5_requirements}}` | `phase_5_requirements` |
| `1:974` | leave | (keep `{{phase_6_objective}}`) | already correct |
| `1:1000` | set_placeholder | `{{phase_6_activities}}` | `phase_6_activities` |
| `1:1022` | set_placeholder | `{{phase_6_deliverables}}` | `phase_6_deliverables` |
| `1:1046` | set_placeholder | `{{phase_6_requirements}}` | `phase_6_requirements` |

(Page Number `1:945` = "10" already correct.)

---

## Slide 12 — methodology_detail_d (phases 7+8)

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:1054` | restore | `مراحل المنهجية: التحسين والتوسع` | `Title` |
| `1:1064` | restore | `التحسين والتوسع` | `Headline` |
| `1:1101` | restore | `الأنشطة الرئيسية` | `Subheader` |
| `1:1080` | set_placeholder | `{{phase_7_objective}}` | `phase_7_objective` |
| `1:1104` | set_placeholder | `{{phase_7_activities}}` | `phase_7_activities` |
| `1:1128` | set_placeholder | `{{phase_7_deliverables}}` | `phase_7_deliverables` |
| `1:1151` | set_placeholder | `{{phase_7_requirements}}` | `phase_7_requirements` |
| `1:1091` | leave | (keep `{{phase_8_objective}}`) | already correct |
| `1:1117` | set_placeholder | `{{phase_8_activities}}` | `phase_8_activities` |
| `1:1139` | set_placeholder | `{{phase_8_deliverables}}` | `phase_8_deliverables` |
| `1:1163` | set_placeholder | `{{phase_8_requirements}}` | `phase_8_requirements` |

(Page Number `1:1062` = "11" already correct.)

---

## Slide 13 — methodology_detail_e (phase 9 only)

Pattern differs slightly — only one phase. Phase 9's body cells got `phase_9_objective`/`phase_9_deliverables` placeholders, others still have Mord text.

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:1170` | restore | `مراحل المنهجية: نقل المعرفة` | `Title` |
| `1:1180` | restore | `نقل المعرفة` | `Headline` |
| `1:1196` | leave | (keep `{{phase_9_deliverables}}` — but reassign as objective below; see notes) | reassign |
| `1:1209` | set_placeholder | `{{phase_9_activities}}` | `phase_9_activities` |
| `1:1220` | set_placeholder | `{{phase_9_deliverables}}` | `phase_9_deliverables` |
| `1:1232` | set_placeholder | `{{phase_9_requirements}}` | `phase_9_requirements` |

**Slide 13 nuance:** node `1:1196` is at column 1 (x=1503, the Objective column position) but Haiku named it `phase_9_deliverables`. Re-set: `characters = "{{phase_9_objective}}"`, `name = "phase_9_objective"`.

(Page Number `1:1178` = "12" already correct.)

---

## Slide 14 — diagnosis (off-by-one numbering + 1 unreplaced node + headline destroyed)

The slide has 22 axis-label positions across two columns × 11 rows. Haiku skipped `1:1275` (still has Mord text "قابلية القياس") and overshot the count by putting `{{diagnosis_axis_22}}` on the Headline footer (`1:1304`). The fix is to renumber axes 15–22 to match reading order and restore the Headline.

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:1275` | set_placeholder | `{{diagnosis_axis_15}}` | `diagnosis_axis_15` |
| `1:1277` | set_placeholder | `{{diagnosis_axis_16}}` | `diagnosis_axis_16` |
| `1:1280` | set_placeholder | `{{diagnosis_axis_17}}` | `diagnosis_axis_17` |
| `1:1282` | set_placeholder | `{{diagnosis_axis_18}}` | `diagnosis_axis_18` |
| `1:1285` | set_placeholder | `{{diagnosis_axis_19}}` | `diagnosis_axis_19` |
| `1:1287` | set_placeholder | `{{diagnosis_axis_20}}` | `diagnosis_axis_20` |
| `1:1290` | set_placeholder | `{{diagnosis_axis_21}}` | `diagnosis_axis_21` |
| `1:1292` | set_placeholder | `{{diagnosis_axis_22}}` | `diagnosis_axis_22` |
| `1:1304` | restore | `مراحل التشخيص` | `Headline` |

(Slide title `1:1294` and Page Number `1:1302` already correct.)

Schema correction for slide 14 in `content-sections.md`: `diagnosis_axis_N` for N=1..22 (not "4–6 axes" — Mord actually shows 22).

---

## Slide 15 — deliverables (near complete, 1 long text needs check)

Audit found 20 placeholders correct + 1 long unreplaced text at `1:1318` with chars `"المخرجات النهائية التالية منسجمة مع مراحل الم..."`. This is the slide's intro line. Decision needed: is this a `{{deliverables_intro}}` placeholder, or Suhail boilerplate?

**Recommendation:** treat as boilerplate — it's a generic "the following deliverables align with methodology phases" statement that wouldn't change per proposal. **No action** on `1:1318`; mark in schema as fixed intro text.

Note also: `1:1318` has the wrong layer name (it's a long Arabic phrase). Rename to `deliverables_intro_fixed` so anyone reading the file knows it's intentional boilerplate.

---

## Slide 16 — KPIs (off-by-one + missing description placeholders)

Mord has 12 real KPI rows + 1 column-header row at the top. Haiku numbered the header row as `kpi_1`, shifting everything by +1. Also, the **middle column** ("الوصف / طريقة القياس" — description / measurement method) was missed entirely.

Fix in three parts:

### 16a — Restore the column header row

| id | action | new characters | new layer name |
|---|---|---|---|
| `1:1444` | restore | `المؤشر` | `KPI Header — metric` |
| `1:1448` | restore | `المستهدف` | `KPI Header — target` |

(`1:1446` is the middle-column header "الوصف / طريقة القياس" — leave it; already correct as boilerplate.)

### 16b — Shift kpi placeholders down by one

The placeholder `kpi_N_*` on Haiku's existing nodes should become `kpi_(N-1)_*`. After shift, kpi_2 → kpi_1, kpi_3 → kpi_2, …, kpi_13 → kpi_12.

| id | current chars | new characters | new layer name |
|---|---|---|---|
| `1:1451` | `{{kpi_2_metric}}` | `{{kpi_1_metric}}` | `kpi_1_metric` |
| `1:1455` | `{{kpi_2_target}}` | `{{kpi_1_target}}` | `kpi_1_target` |
| `1:1458` | `{{kpi_3_metric}}` | `{{kpi_2_metric}}` | `kpi_2_metric` |
| `1:1460` | `{{kpi_3_target}}` | `{{kpi_2_target}}` | `kpi_2_target` |
| `1:1465` | `{{kpi_4_metric}}` | `{{kpi_3_metric}}` | `kpi_3_metric` |
| `1:1469` | `{{kpi_4_target}}` | `{{kpi_3_target}}` | `kpi_3_target` |
| `1:1472` | `{{kpi_5_metric}}` | `{{kpi_4_metric}}` | `kpi_4_metric` |
| `1:1476` | `{{kpi_5_target}}` | `{{kpi_4_target}}` | `kpi_4_target` |
| `1:1479` | `{{kpi_6_metric}}` | `{{kpi_5_metric}}` | `kpi_5_metric` |
| `1:1483` | `{{kpi_6_target}}` | `{{kpi_5_target}}` | `kpi_5_target` |
| `1:1486` | `{{kpi_7_metric}}` | `{{kpi_6_metric}}` | `kpi_6_metric` |
| `1:1490` | `{{kpi_7_target}}` | `{{kpi_6_target}}` | `kpi_6_target` |
| `1:1493` | `{{kpi_8_metric}}` | `{{kpi_7_metric}}` | `kpi_7_metric` |
| `1:1497` | `{{kpi_8_target}}` | `{{kpi_7_target}}` | `kpi_7_target` |
| `1:1500` | `{{kpi_9_metric}}` | `{{kpi_8_metric}}` | `kpi_8_metric` |
| `1:1504` | `{{kpi_9_target}}` | `{{kpi_8_target}}` | `kpi_8_target` |
| `1:1507` | `{{kpi_10_metric}}` | `{{kpi_9_metric}}` | `kpi_9_metric` |
| `1:1509` | `{{kpi_10_target}}` | `{{kpi_9_target}}` | `kpi_9_target` |
| `1:1514` | `{{kpi_11_metric}}` | `{{kpi_10_metric}}` | `kpi_10_metric` |
| `1:1521` | `{{kpi_11_target}}` | `{{kpi_10_target}}` | `kpi_10_target` |
| `1:1525` | `{{kpi_12_metric}}` | `{{kpi_11_metric}}` | `kpi_11_metric` |
| `1:1528` | `{{kpi_12_target}}` | `{{kpi_11_target}}` | `kpi_11_target` |
| `1:1532` | `{{kpi_13_metric}}` | `{{kpi_12_metric}}` | `kpi_12_metric` |

(Note: there's no `kpi_12_target` in Haiku's existing placeholders — possibly the last row only has 13 metric + 12 target, or Haiku missed one. Confirm by inspecting positions ≥ y=26283.)

### 16c — Add description placeholders for the middle column

The middle column on each KPI row currently has real Mord text. Replace with `{{kpi_N_description}}` matching the corresponding row.

| id | new characters | new layer name |
|---|---|---|
| `1:1453` | `{{kpi_1_description}}` | `kpi_1_description` |
| `1:1462` | `{{kpi_2_description}}` | `kpi_2_description` |
| `1:1467` | `{{kpi_3_description}}` | `kpi_3_description` |
| `1:1474` | `{{kpi_4_description}}` | `kpi_4_description` |
| `1:1481` | `{{kpi_5_description}}` | `kpi_5_description` |
| `1:1488` | `{{kpi_6_description}}` | `kpi_6_description` |
| `1:1495` | `{{kpi_7_description}}` | `kpi_7_description` |
| `1:1502` | `{{kpi_8_description}}` | `kpi_8_description` |
| `1:1511` | `{{kpi_9_description}}` | `kpi_9_description` |
| `1:1516` | `{{kpi_10_description}}` | `kpi_10_description` |
| `1:1518` | `{{kpi_10_target}}` | `kpi_10_target` (already a target slot, was Mord text — verify) |
| `1:1523` | `{{kpi_11_description}}` | `kpi_11_description` |
| `1:1530` | `{{kpi_12_description}}` | `kpi_12_description` |

(`1:1435` Headline "قياس الأداء" and `1:1433` Page Number "15" already correct.)

**Verify slide 16 visually** after applying — the off-by-one + description columns are intricate. If anything's misaligned, re-inspect with `slide.findAll(n => n.type === "TEXT")` and adjust.

---

## Slide 17 — timeline (NEEDS FRESH INSPECTION PASS)

Audit found only **10 placeholders** for a 114-text-node slide. Page Number ("16") and Headline ("الجدول الزمني") were preserved, but the bulk of the timeline grid (months, phase rows, milestones) is still Mord-specific text.

**Action for Haiku:** do a fresh inspection of slide `1:1864` first — get all 114 text nodes' positions, sizes, and contents — then design placeholders based on the actual grid structure. Likely shape:

- `{{timeline_month_N}}` for each month header (N=1..12)
- `{{timeline_phase_N_label}}` for each row label
- `{{timeline_phase_N_start_month}}` and `{{timeline_phase_N_end_month}}` for each phase's start/end (if Mord encodes these as text)
- Or, if Mord uses positioned rectangles for the gantt bars, those would be renamed `brand_primary_timeline_phase_N` instead

Don't guess — inspect first.

---

## Slide 6 — understanding (Figma MCP timeout — NEEDS RETRY WITH SMALLER QUERIES)

Slide `1:541` consistently times out on `findAll` and deep tree walks via `use_figma`. The slide is fine in Figma's UI. Workarounds Haiku should try:

1. Access children directly without recursion: `const children = slide.children; for (const c of children) { ... }`
2. Iterate slide.children at depth 1, then for each child do `child.children` separately in a follow-up call
3. Use `figma.getNodeByIdAsync` for known child IDs (need to enumerate via Figma REST API offline if MCP won't cooperate)

From the screenshot I captured earlier, slide 6 is partially placeholdered:
- Right column (التحدي / challenge title) has `{{challenge_1_title}}` through `{{challenge_8_title}}` ✓
- Middle column (أثر التحدي / challenge body) has `{{challenge_1_body}}` through `{{challenge_8_body}}` ✓
- **Left column (توصيف الأولوية / priority description) still has 8 rows of Mord text** — needs placeholders `{{challenge_N_priority}}` (new field)
- **Top-of-slide intro paragraph** is unclear from the screenshot — may need `{{understanding_intro}}` applied if not already

Schema correction for slide 6: each challenge card has **3 fields** (title, body, priority), not 2. Update `content-sections.md` accordingly.

---

## Final pass — slide name encoding

After all per-slide fixes above, set the slide-level `name` property to encode section IDs (this previously didn't persist when I attempted, but the test in this session confirmed `slide.name` IS writable; just apply in the same `use_figma` call as the other fixes for that slide so the change isn't reset by an intervening operation).

| Slide id | Set `slide.name` to |
|---|---|
| `1:109` | `01 — cover \| section=cover` |
| `1:191` | `02 — toc \| section=toc` |
| `1:318` | `03 — exec_summary \| section=exec_summary` |
| `1:385` | `04 — strategy \| section=strategy` |
| `1:455` | `05 — context \| section=context` |
| `1:541` | `06 — understanding \| section=understanding` |
| `1:588` | `07 — methodology_intro \| section=methodology_intro` |
| `1:698` | `08 — methodology_phases \| section=methodology_phases` |
| `1:815` | `09 — methodology_detail_a \| section=methodology_detail_a` |
| `1:932` | `10 — methodology_detail_b \| section=methodology_detail_b` |
| `1:1049` | `11 — methodology_detail_c \| section=methodology_detail_c` |
| `1:1166` | `12 — methodology_detail_d \| section=methodology_detail_d` |
| `1:1234` | `13 — methodology_detail_e \| section=methodology_detail_e` |
| `1:1310` | `14 — diagnosis \| section=diagnosis` |
| `1:1421` | `15 — deliverables \| section=deliverables` |
| `1:1533` | `16 — kpis \| section=kpis` |
| `1:1864` | `17 — timeline \| section=timeline` |
| `1:1868` | `18 — closing \| section=closing` |

If `slide.name` reverts again after Haiku's pass, the runtime should fall back to **position-based section identification** (slide index → section_id via the table in `content-sections.md`). All 18 slides always present in fixed order.

---

## Verification after fixes

For each fixed slide, run a quick audit:

```js
const audit = async (id) => {
  const s = await figma.getNodeByIdAsync(id);
  const t = s.findAll(n => n.type === "TEXT");
  return {
    pageNum: t.find(n => n.name === "Page Number")?.characters,
    headline: t.find(n => n.name === "Headline")?.characters,
    placeholders: t.filter(n => /\{\{/.test(n.characters||"")).length,
    longUnreplaced: t.filter(n => !/\{\{/.test(n.characters||"") && (n.characters||"").length > 50).length,
  };
};
```

Acceptance per slide:
- `pageNum` matches `0N` pattern (no `{{`)
- `headline` is plain Arabic (no `{{`)
- `placeholders` matches expected count from schema
- `longUnreplaced` = 0 (or only known boilerplate intros like slide 15's `1:1318`)
