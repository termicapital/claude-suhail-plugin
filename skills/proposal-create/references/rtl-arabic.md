# RTL Arabic in Figma Slides

## Key facts

- **Figma Slides has no RTL canvas mode.** Slides themselves stay left-to-right. Only text alignment flips.
- **Bidi is automatic.** When you assign Arabic characters to a text node, Figma's text engine shapes them correctly (joining, ligatures). You just need the right font and alignment.
- **Text alignment is the lever.** Every text node holding Arabic content: `textAlignHorizontal = "RIGHT"`.
- **Layout flips manually.** Place the logo on the right side of the cover, page numbers on the left, body content right-aligned, footers RTL. Suhail's reference templates already follow this; mirror them visually.

## Arabic font candidate chain

Figma's font availability varies per workspace. Loop these via `figma.loadFontAsync({ family, style })` and pick the first that loads successfully:

1. `IBM Plex Sans Arabic` — preferred (modern, professional)
2. `Noto Sans Arabic` — strong fallback, broad workspace coverage
3. `Cairo` — common in Saudi non-profit decks
4. `Tajawal` — common alternative
5. `Inter` — last resort (will not shape Arabic; only use if all above fail, and surface a warning)

```javascript
async function loadArabic(style = "Regular") {
  const candidates = [
    { family: "IBM Plex Sans Arabic", style },
    { family: "Noto Sans Arabic",     style },
    { family: "Cairo",                style },
    { family: "Tajawal",              style },
    { family: "Inter",                style },
  ];
  for (const f of candidates) {
    try {
      await figma.loadFontAsync(f);
      return f;
    } catch (_) { /* try next */ }
  }
  throw new Error("No Arabic-capable font available in this workspace");
}
```

Cache the resolved family per session so subsequent calls don't re-probe.

## Text node setup template

```javascript
const arRegular = await loadArabic("Regular");
const arBold    = await loadArabic("Bold");

function arText({ chars, x, y, w, h, size = 24, weight = "Regular", color = { r: 0.1, g: 0.1, b: 0.1 } }) {
  const t = figma.createText();
  t.fontName = weight === "Bold" ? arBold : arRegular;
  t.fontSize = size;
  t.characters = chars;            // assign AFTER fontName is set
  t.textAlignHorizontal = "RIGHT";
  t.resize(w, h);
  t.x = x;
  t.y = y;
  t.fills = [{ type: "SOLID", color }];
  return t;
}
```

## Pricing tables: mixed numerals

Western digits (`1, 2, 3`) read better in pricing than Arabic-Indic (`١, ٢, ٣`) for most Saudi business contexts. Default to Western digits.

When mixing Latin numerals with Arabic text in a single line (e.g. `الإجمالي: 45,000 ريال`), brackets and signs can flip due to bidi resolution. Wrap pure-digit runs with U+200F (Right-to-Left Mark) on each side to lock them:

```javascript
const RLM = "‏";
const amount = `${RLM}45,000${RLM} ريال`;
```

## Common mistakes

- **Assigning `characters` before `fontName`** — Figma throws "font not loaded". Always set `fontName` first.
- **Forgetting to load `Bold` separately** — even within the same family, each weight needs its own `loadFontAsync`.
- **Setting `textAutoResize` after `characters`** — fine, but `resize(w, h)` after that can override. Pick one: either auto-resize and let it grow, or fix size and let it truncate.
- **Using `Inter` for Arabic** — it'll render as boxes/missing glyphs. The fallback to Inter is only for graceful failure detection, not actual rendering.
- **Right-aligning the whole frame instead of each text node** — frame alignment doesn't propagate; set it per text node.
