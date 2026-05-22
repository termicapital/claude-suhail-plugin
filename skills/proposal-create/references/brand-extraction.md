# Brand extraction

Two-pass strategy: model-driven WebFetch first, Pillow script fallback, then default palette.

## Pass 1 — WebFetch

Call `WebFetch` on `client_url` with this prompt:

```
Return ONLY a JSON object (no prose, no markdown fences) with these keys:
{
  "logo_url": "absolute URL to the org's logo image, preferring SVG/PNG. null if none found.",
  "primary_hex": "#RRGGBB of the main brand color. Look for CSS variables like --primary, --brand, the dominant logo color, or button/header colors. null if uncertain.",
  "secondary_hex": "#RRGGBB of a clear secondary brand color, or null.",
  "org_name_ar": "the org's official Arabic name as it appears on the site. null if not present.",
  "mission_ar": "1-2 sentence Arabic mission statement copied verbatim from the about/home page. null if none."
}
```

If WebFetch refuses or returns wrapped output, parse defensively (regex out the JSON block) before falling through.

## Pass 2 — Pillow script

`scripts/fetch_brand.py --url <client_url> --out <tempdir>`. It:

1. Fetches the homepage with `requests` (Mozilla UA).
2. Parses with BeautifulSoup.
3. Hunts for the logo in this priority:
   - `<link rel="icon" sizes="192x192" href="...">` or any high-res icon
   - `<meta property="og:image" content="...">`
   - `<link rel="apple-touch-icon" href="...">`
   - First `<img>` inside `<header>` or with class containing `logo`
   - `<link rel="icon" href="...">` (favicon, last resort)
4. Downloads to `<tempdir>/logo.<ext>`. If the file is >5 MB or wider than 1024 px, opens with Pillow, resizes to 1024 px width, saves as PNG.
5. Color quantization on the logo:
   - Open, convert to RGB, resize to 64×64
   - Build a histogram of quantized colors (8-bit per channel → top-10 bins)
   - Discard near-white (`luminance > 240`), near-black (`luminance < 30`), and near-grey (saturation < 0.15)
   - Pick the highest-count remaining cluster as `primary_hex`, second-highest as `secondary_hex`
6. Prints JSON: `{"logo_path": "...", "primary_hex": "#xxxxxx", "secondary_hex": "#xxxxxx"}`.

If the website blocks the scrape (403/captcha), the script exits 1 with a clear stderr message. Catch that and proceed to pass 3.

## Pass 3 — Default palette

Load `assets/suhail-default-palette.json`. Use Suhail-house colors. Tell the user explicitly: *"I couldn't extract brand colors from the website — using Suhail defaults. You can pass `primary_hex` and `secondary_hex` to override."*

## Logo edge cases

- **Logo is SVG.** Pillow can't quantize SVG. Use `cairosvg` or `wand` if installed; otherwise render to PNG via headless conversion. Script falls back to "logo found but couldn't sample colors" and only returns `logo_path`.
- **Logo has transparent background.** Convert to RGB with a white background before quantization, otherwise transparent pixels skew the histogram.
- **No logo at all.** Skip image upload. Generate a text-only cover with the org's Arabic name in large type. Tell the user.
- **Logo is huge (>10 MB after download).** Downscale aggressively. The MCP `upload_assets` cap is 10 MB; aim for <2 MB to be safe.

## User overrides

The skill accepts manual overrides at any time:
- `primary_hex="#0a4d8c"`
- `logo_path="C:\path\to\logo.png"`

If provided, skip the corresponding pass entirely.
