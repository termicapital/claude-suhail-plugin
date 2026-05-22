# Slide templates

The client's brand is what appears on the proposal — logo, colors, name, mission all sourced from the client's website. The agency (Suhail, Toroon, etc.) does not need to brand the deck. These three Figma Slides files are purely visual references for layout/typography/density.

They live in the MCP-connected user's drafts (Pro plan), so MCP read calls go against the Pro quota — no rate-limit budgeting needed.

| # | fileKey | URL | Use case |
|---|---|---|---|
| 1 | `s1ZJkZ6vGxhnR5D5zF9bdc` | https://www.figma.com/slides/s1ZJkZ6vGxhnR5D5zF9bdc/Assocation-of-volunteer-in-AlUla--No.1---Copy- | **Default.** Main proposal template (Association of Volunteers in AlUla, ~26 slides). |
| 2 | `JtzNUXrAHFupkajwfPz952` | https://www.figma.com/slides/JtzNUXrAHFupkajwfPz952/Mord----No.2---Copy- | Variant — alternate cover style (Mord, ~22 slides). |
| 3 | `PNVPb5cMrL0xoP9ZAWpbPh` | https://www.figma.com/slides/PNVPb5cMrL0xoP9ZAWpbPh/Ofuq--no.4---Copy- | Variant — denser content layout (Ofuq, ~17 slides). |

## Recommended screenshot calls before generating

```
get_screenshot(fileKey=<template_key>, nodeId="0:1", maxDimension=2048)
```

`nodeId="0:1"` on a Slides file returns a tiled view of all slides in one PNG (vertically stacked or horizontally laid out depending on the file). Useful for an overview; for detail call `get_screenshot` on individual slide node IDs.

Then individual cover and content slides as needed. Used purely to inform the model's choices about layout density, type scale, and color use — not consumed by the generated file.

## Slide-by-slide layout (default template)

Approximate positions on a 1920×1080 slide canvas. Treat as a starting point; tune against the screenshot.

### 1. Cover (`الغلاف`)
- Background: white
- Accent bar: 24 px wide, full height, right edge, brand `primary_hex`
- Client logo: 180×180, top-right (x ≈ 1700, y ≈ 60)
- Title (Arabic): 64 pt Bold, right-aligned, center vertical
- Subtitle (Arabic): 28 pt Regular, right-aligned, below title
- Date (footer left): 14 pt Regular
- No agency mark required — the cover belongs to the client.

### 2. About the client (`نبذة عن العميل`)
- Heading: 40 pt Bold, top-right (y ≈ 80)
- Body: 22 pt Regular, right-aligned, max width ~1100 px, right side
- Client logo: top-left, ~120×120
- Tags: pill chips along the bottom

### 3. Opportunity (`الفرصة`)
- Heading top-right
- Single large quote-style paragraph, 26 pt
- Background accent shape (soft tint of `primary_hex`) behind the paragraph

### 4. Proposed solution (`الحل المقترح`)
- Heading top-right
- One illustrative icon or stylized shape on left
- Solution paragraph right-aligned, right column

### 5. Scope & deliverables (`النطاق والمخرجات`)
- Heading top-right
- 2-column grid of deliverable cards (4–8 cards), each: title (Bold) + 1-line description (Regular)
- Brand color used as card top-border

### 6. Methodology / Phases (`المنهجية والمراحل`)
- Heading top-right
- Horizontal phase sequence (3–5 boxes), RTL flow (first phase on the right)
- Each box: phase number, name, 1-line description

### 7. Timeline (`الجدول الزمني`)
- Heading top-right
- Horizontal Gantt-style bars, weeks/months on a baseline, phase names right-aligned
- RTL flow: month 1 on the right

### 8. Team (`الفريق`)
- Heading top-right
- Grid of role cards: role title (Bold), name (Regular)
- Optional avatar circles (use initials if no photo)

### 9. Investment / Pricing (`الاستثمار`)
- Heading top-right
- Table: item (right column), amount (left column)
- Total row at bottom, brand color background
- Amounts: Western digits, wrap with RLM (see `rtl-arabic.md`)

### 10. Next steps (`الخطوات التالية`)
- Heading top-right
- Numbered list (Arabic numerals: 1، 2، 3)
- Each step: 1–2 lines right-aligned

### 11. Contact (`التواصل`)
- Heading top-right
- Contact card: name, email, phone — pulled from brief or `whoami`
- Closing thank-you line: `شكراً لكم` (Bold, large, centered)
