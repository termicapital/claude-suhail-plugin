"""Fetch a client's logo from their website and quantize dominant brand colors.

Used as the second pass after WebFetch when the model couldn't infer brand color
or logo URL. Prints JSON to stdout.

Usage:
    python fetch_brand.py --url https://kyan.org.sa --out C:\\tmp\\brand
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from collections import Counter
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch_html(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
    r.raise_for_status()
    return r.text


def find_logo_url(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    # High-res icon
    for link in soup.find_all("link", rel=lambda v: v and "icon" in v.lower()):
        sizes = link.get("sizes", "")
        if "192" in sizes or "256" in sizes or "512" in sizes:
            if link.get("href"):
                return urljoin(base_url, link["href"])

    # og:image
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return urljoin(base_url, og["content"])

    # apple-touch-icon
    apple = soup.find("link", rel=lambda v: v and "apple-touch-icon" in v.lower())
    if apple and apple.get("href"):
        return urljoin(base_url, apple["href"])

    # First <img> in <header> or with logo-ish class
    header = soup.find("header")
    if header:
        img = header.find("img")
        if img and img.get("src"):
            return urljoin(base_url, img["src"])

    for img in soup.find_all("img"):
        cls = " ".join(img.get("class") or []).lower()
        ident = (img.get("id") or "").lower()
        alt = (img.get("alt") or "").lower()
        if "logo" in cls or "logo" in ident or "logo" in alt:
            if img.get("src"):
                return urljoin(base_url, img["src"])

    # Plain favicon as last resort
    fav = soup.find("link", rel=lambda v: v and v.lower() == "icon")
    if fav and fav.get("href"):
        return urljoin(base_url, fav["href"])

    return None


def download(url: str, out_dir: str) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        r.raise_for_status()
    except Exception:
        return None

    ext = os.path.splitext(urlparse(url).path)[1].lower() or ".png"
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"}:
        ext = ".png"
    path = os.path.join(out_dir, f"logo{ext}")
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def normalize(path: str) -> str | None:
    """Downscale to PNG, max width 1024."""
    if path.endswith(".svg"):
        return path
    try:
        img = Image.open(path).convert("RGBA")
    except Exception:
        return None

    if img.size[0] > 1024:
        ratio = 1024 / img.size[0]
        img = img.resize((1024, int(img.size[1] * ratio)), Image.LANCZOS)

    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
    norm_path = os.path.splitext(path)[0] + "_norm.png"
    bg.save(norm_path, "PNG")
    return norm_path


def quantize_colors(path: str) -> tuple[str | None, str | None]:
    try:
        img = Image.open(path).convert("RGB").resize((64, 64), Image.LANCZOS)
    except Exception:
        return None, None

    counts: Counter = Counter()
    for px in img.getdata():
        r, g, b = px
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum > 240 or lum < 30:
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        sat = 0 if mx == 0 else (mx - mn) / mx
        if sat < 0.15:
            continue
        quant = (r & 0xF0, g & 0xF0, b & 0xF0)
        counts[quant] += 1

    if not counts:
        return None, None

    ordered = counts.most_common(2)
    primary = "#{:02X}{:02X}{:02X}".format(*ordered[0][0])
    secondary = "#{:02X}{:02X}{:02X}".format(*ordered[1][0]) if len(ordered) > 1 else None
    return primary, secondary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    try:
        html = fetch_html(args.url)
    except Exception as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1

    logo_url = find_logo_url(html, args.url)
    logo_path: str | None = None
    primary = None
    secondary = None

    if logo_url:
        raw = download(logo_url, args.out)
        if raw:
            logo_path = normalize(raw) or raw
            if logo_path and not logo_path.endswith(".svg"):
                primary, secondary = quantize_colors(logo_path)

    print(json.dumps({
        "logo_url": logo_url,
        "logo_path": logo_path,
        "primary_hex": primary,
        "secondary_hex": secondary,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
