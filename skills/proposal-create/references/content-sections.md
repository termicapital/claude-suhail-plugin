# Canonical proposal sections

Every Suhail proposal has the same 11 sections. The brief is parsed into this schema; each section maps to one slide in the deck. Missing sections become visible placeholders, never hallucinated content.

| # | Slide name (EN) | عنوان الشريحة | What goes here |
|---|---|---|---|
| 1 | Cover | الغلاف | Client logo prominent, project title, date. No agency logo required — the client is the visual subject. |
| 2 | About the client | نبذة عن العميل | 2–3 sentences on the client's mission, sector, scale (pull from website) |
| 3 | Opportunity / Problem | الفرصة | The need the client has, stated as an opportunity. From brief. |
| 4 | Proposed solution | الحل المقترح | What Suhail will deliver, at a 1-paragraph level. From brief. |
| 5 | Scope & deliverables | النطاق والمخرجات | Bulleted list of concrete deliverables. From brief. |
| 6 | Methodology / Phases | المنهجية والمراحل | Suhail's approach broken into 3–5 phases. From brief. |
| 7 | Timeline | الجدول الزمني | Phase-by-phase weeks/months, or Gantt-style bars. From brief. |
| 8 | Team | الفريق | Roles assigned (PM, tech lead, designers, etc.). From brief. |
| 9 | Investment / Pricing | الاستثمار | Pricing table. **Never invent numbers.** From brief only. |
| 10 | Next steps | الخطوات التالية | Sign-off, kickoff date, prerequisites. From brief. |
| 11 | Contact | التواصل | Agency point of contact (name, email, phone) — taken from the brief or from `whoami` if available. Brand visuals not required. |

## Section schema (JSON)

`scripts/parse_brief.py` and the in-context parser both emit:

```json
{
  "cover":        { "title_ar": "...", "subtitle_ar": "...", "date": "..." },
  "about_client": { "text_ar": "...", "tags_ar": ["..."] },
  "opportunity":  { "text_ar": "..." },
  "solution":     { "text_ar": "..." },
  "scope":        { "items_ar": ["...", "..."] },
  "methodology":  { "phases": [{ "name_ar": "...", "text_ar": "..." }] },
  "timeline":     { "phases": [{ "name_ar": "...", "duration_ar": "..." }] },
  "team":         { "roles": [{ "title_ar": "...", "name_ar": "..." }] },
  "investment":   { "rows": [{ "item_ar": "...", "amount_ar": "..." }], "total_ar": "..." },
  "next_steps":   { "items_ar": ["...", "..."] },
  "contact":      { "name_ar": "...", "email": "...", "phone": "..." }
}
```

## Placeholder convention

When a section has no source content in the brief, write `"[ـ ـ ـ]"` (Arabic tatweel dashes) as the text value. The skill renders that exactly on the slide so the user immediately sees what to fill in. **Do not** write a "lorem ipsum" — empty placeholders are safer than plausible-looking fake content.

## Headline strings

Use these exact Arabic headings on each slide (copy-paste, don't translate fresh):

- `الغلاف` — cover
- `نبذة عن العميل` — about
- `الفرصة` — opportunity
- `الحل المقترح` — solution
- `النطاق والمخرجات` — scope
- `المنهجية والمراحل` — methodology
- `الجدول الزمني` — timeline
- `الفريق` — team
- `الاستثمار` — investment
- `الخطوات التالية` — next steps
- `التواصل` — contact
