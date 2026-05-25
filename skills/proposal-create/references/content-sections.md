# Mord deck schema (18 slides)

Every Suhail proposal follows the Mord layout — 18 slides, in fixed order. The runtime walks the deck, replaces `{{placeholders}}` with content from the brief, and swaps the logo + brand primary color.

Sections marked **client-content** have `{{placeholders}}`. Sections marked **boilerplate** stay identical across proposals (TOC labels, closing slide, page footers).

## Slide-by-slide map

| # | Slide | Section ID | Type | Placeholders |
|---|---|---|---|---|
| 1 | Cover | `cover` | client-content | `{{project_title}}`, `{{project_subtitle}}` |
| 2 | الفهرس (TOC) | `toc` | boilerplate | — |
| 3 | الملخص التنفيذي (Executive Summary) | `exec_summary` | client-content | `{{exec_intro}}` (top paragraph, no number) + `{{exec_point_1}}` `{{exec_point_2}}` `{{exec_point_3}}` (3 numbered points) |
| 4 | ارتباط المشروع باستراتيجية الجمعية (Strategic Alignment) | `strategy` | client-content | 6 body slots paired with fixed Arabic labels: `{{strategy_vision}}` (الرؤية الاستراتيجية), `{{strategy_solution}}` (الحل المقترح), `{{strategy_challenge}}` (التحدي المركزي), `{{strategy_value}}` (القيمة الملموسة), `{{strategy_sustainability}}` (قابلية الاستدامة), `{{strategy_feasibility}}` (الجدوى العملية) |
| 5 | السياق العام للمشروع (General Context) | `context` | client-content | `{{context_para_1}}` `{{context_para_2}}` `{{context_para_3}}` `{{context_para_4}}` (4 paragraphs; Mord has a duplicate text node for para 3 that takes the same value — see "Known quirks" below) |
| 6 | فهمنا للمشروع (Project Understanding) | `understanding` | client-content | `{{understanding_intro}}` (top paragraph, ~280 chars), `{{understanding_subtitle}}` (small table sub-header), and 8 challenge cards with **3 fields each**: `{{challenge_N_title}}`, `{{challenge_N_body}}`, `{{challenge_N_priority}}` for N=1..8. Slide 6 hits a Figma MCP timeout on deep tree walks — use direct `slide.children` traversal, not `findAll`. |
| 7 | المنهجية المقترحة (Proposed Methodology) | `methodology_intro` | client-content | `{{methodology_overview}}`, `{{methodology_expected_outcome}}`, `{{methodology_principle}}` (the "لا نبدأ بالحل..." guiding statement) |
| 8 | مراحل المنهجية التنفيذية (Phases Overview) | `methodology_phases` | client-content | 9 phase cards: `{{phase_N_title}}` and `{{phase_N_brief}}` for N=1..9 |
| 9 | المرحلتان 1–2 (Setup + Training detail) | `methodology_detail_a` | client-content | per-phase fields for phases 1, 2 — see "Phase detail fields" below |
| 10 | المرحلتان 3–4 (Challenge + Opportunity detail) | `methodology_detail_b` | client-content | phases 3, 4 |
| 11 | المرحلتان 5–6 (Design + Testing detail) | `methodology_detail_c` | client-content | phases 5, 6 |
| 12 | المرحلتان 7–8 (Improvement + Scaling detail) | `methodology_detail_d` | client-content | phases 7, 8 |
| 13 | المرحلة 9 (Knowledge Transfer detail) | `methodology_detail_e` | client-content | phase 9 |
| 14 | محاور التشخيص الابتكاري والمنتجي (Diagnosis Axes) | `diagnosis` | client-content | `{{diagnosis_axis_N}}` for N=1..22 (Mord lays out 22 axis positions across 2 columns × 11 rows; reading order = right column then left column per row) |
| 15 | المخرجات النهائية للمشروع (Final Deliverables) | `deliverables` | client-content | `{{deliverable_N}}` (typically 6–10 items) — plus one boilerplate intro line on slide (`1:1318`, "المخرجات النهائية التالية منسجمة مع مراحل المنهجية...") that stays fixed across proposals |
| 16 | قياس الأداء (KPIs) | `kpis` | client-content | 12 KPI rows × 3 fields: `{{kpi_N_metric}}`, `{{kpi_N_description}}`, `{{kpi_N_target}}` for N=1..12. Mord's table has a column-header row at the top (`المؤشر` / `الوصف / طريقة القياس` / `المستهدف`) that stays as boilerplate |
| 17 | الجدول الزمني التفصيلي (Detailed Timeline) | `timeline` | client-content | 12-month gantt with 10 phase rows + 12 month headers: `{{timeline_element_N}}` for N=1..10 (phase rows, one per phase), `{{timeline_month_N}}` for N=1..12 (month column headers Jan–Dec). Total 22 placeholders. |
| 18 | شكراً (Thank You) | `closing` | boilerplate | — |

## Phase detail fields (slides 9–13)

Each phase (1..9) has **4** placeholder slots (Mord's table has 4 columns per phase, not 3 — the 4th was missed in v0):

- `{{phase_N_objective}}` — what this phase aims to achieve (Arabic Subheader: الهدف)
- `{{phase_N_activities}}` — what is done during the phase (Arabic Subheader: الأنشطة الرئيسية)
- `{{phase_N_deliverables}}` — what the phase produces (Arabic Subheader: المخرجات)
- `{{phase_N_requirements}}` — what the phase needs to start (Arabic Subheader: المتطلبات)

The 9 phases (Suhail's standard methodology stages):

1. التهيئة وبناء إطار المشروع (Setup & Framing)
2. التدريب التأسيسي (Foundational Training)
3. فهم التحدي (Challenge Understanding)
4. صياغة الفرصة (Opportunity Framing)
5. تصميم القيمة (Value Design)
6. اختبار الفرضيات (Hypothesis Testing)
7. التعديل والتحسين (Refinement)
8. التقدم والتوسع (Progress & Scaling)
9. الإغلاق ونقل المعرفة (Closure & Knowledge Transfer)

## Brand and asset placeholders

- **Logo:** the layer named `logo_container` on slide 1. Runtime replaces its image fill with the NGO logo. (Other slides do not show a logo — Mord puts a small Suhail mark in the footer area, which stays as-is.)
- **Brand primary color:** layers whose name starts with `brand_primary_` (e.g. `brand_primary_accent_bar`, `brand_primary_toc_badge_1`, `brand_primary_strategy_bg`). Runtime sets their solid fill to the NGO's primary hex.
- **Mord's brand primary color (the value the runtime replaces):** teal RGB `(0.027, 0.608, 0.753)` ≈ `#079BC0`. This is the only color Mord uses for client-brandable accents; the dark navy `(0.19, 0.27, 0.41)` ≈ `#304468` is Suhail's neutral and stays fixed across proposals.

## Known quirks in Mord

- **Slide 5 has a duplicated text node** for paragraph 3 (Figma artifact from the original design). Both nodes (`context_para_3` and `context_para_3_dup`) take the same `{{context_para_3}}` value at runtime. Don't dedupe by removing — keep both, the layout depends on the duplicate's invisible/overlapping presence.
- **Slide 6 (Project Understanding) currently hits a Figma MCP `use_figma` timeout** during deep tree walks. Haiku should try smaller-scope queries (e.g. inspect direct children only) or wait and retry; the slide is fine in Figma's own UI.

## Optionality

All 18 slides are mandatory in v1.0. Missing brief content stays as a visible `{{placeholder}}` so the designer sees the gap. **Never** hallucinate scope, deliverables, KPIs, pricing, or timeline.

## Naming conventions (already applied to the Mord master)

- Brand-color elements: layer name starts with `brand_primary_` (e.g. `brand_primary_accent_bar`, `brand_primary_strategy_bg`, `brand_primary_toc_badge_1`)
- Logo: layer named `logo_container` (slide 1 only)
- Client-content text nodes: layer renamed to the placeholder slug without braces (e.g. `exec_intro`, `strategy_vision`, `phase_3_objective`)

Fonts (`Droid Arabic Kufi` Bold/Regular, `IBM Plex Sans Arabic` Regular/Medium/SemiBold/Bold) are uploaded to Guillermo's Figma team. Load via `figma.loadFontAsync` before any text edit.

## Headline strings (slide footers)

The bottom-left of each slide contains a `Page Number` + `Headline`. These are Suhail boilerplate and stay fixed:

- 01 / الفهرس
- 02 / الملخص التنفيذي
- 03 / المشروع واستراتيجية الجمعية
- 04 / السياق العام
- 05 / فهمنا للمشروع
- 06 / المنهجية المقترحة
- 07 / مراحل المنهجية المقترحة
- 08 / التهيئة والتدريب
- 09 / التحدي والفرص
- 10 / التصميم والاختبار
- 11 / التحسين والتوسع
- 12 / نقل المعرفة
- 13 / مراحل التشخيص
- 14 / المخرجات النهائية
- 15 / قياس الأداء
- 16 / الجدول الزمني
