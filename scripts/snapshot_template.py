#!/usr/bin/env python3
"""
Snapshot extractor for Mord master template.

Reads the Figma master template, captures a deterministic JSON representation
of all slides and their node structure, downloads image assets, and commits
to templates/mord.snapshot.json + templates/assets/*.png.

Usage:
  FIGMA_TOKEN=<token> python scripts/snapshot_template.py --file-key <MASTER_TEMPLATE_KEY>

Environment:
  FIGMA_TOKEN: Figma API token (required)

Output:
  templates/mord.snapshot.json: Canonical snapshot document
  templates/assets/*.png: Downloaded images
"""

import json
import os
import re
import sys
import time
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from PIL import Image
from io import BytesIO


# Position-based section identification (slide index → section_id).
# This is the canonical mapping documented in references/content-sections.md.
# Used because Mord's slide names are currently just "1"..."18" (not section-encoded).
SECTION_BY_SLIDE_INDEX = [
    "cover",                 # slide 1
    "toc",                   # slide 2
    "exec_summary",          # slide 3
    "strategy",              # slide 4
    "context",               # slide 5
    "understanding",         # slide 6
    "methodology_intro",     # slide 7
    "methodology_phases",    # slide 8
    "methodology_detail_a",  # slide 9
    "methodology_detail_b",  # slide 10
    "methodology_detail_c",  # slide 11
    "methodology_detail_d",  # slide 12
    "methodology_detail_e",  # slide 13
    "diagnosis",             # slide 14
    "deliverables",          # slide 15
    "kpis",                  # slide 16
    "timeline",              # slide 17
    "closing",               # slide 18
]


def safe_filename(s: str) -> str:
    """Make a string safe for use as a filename on Windows + Unix."""
    return re.sub(r"[<>:\"/\\|?*]", "_", s)


class FigmaSnapshotExtractor:
    """Extracts a deterministic snapshot from a Figma file."""

    API_BASE = "https://api.figma.com/v1"
    RATE_LIMIT_DELAY = 1.5  # seconds between requests

    def __init__(self, file_key: str, token: str):
        self.file_key = file_key
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"X-Figma-Token": token})
        self.assets_dir = Path("templates/assets")
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.downloaded_images = {}  # maps imageRef -> filename
        self.last_request_time = 0

    def _throttle(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request with rate limiting."""
        self._throttle()
        url = f"{self.API_BASE}{path}"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def fetch_file(self) -> Dict:
        """Fetch the full document tree from Figma."""
        print(f"Fetching file {self.file_key}...")
        return self._get(f"/files/{self.file_key}")

    def get_image_url(self, node_ids: List[str], format: str = "png") -> Dict[str, str]:
        """Get download URLs for images."""
        if not node_ids:
            return {}
        ids_str = ",".join(node_ids)
        print(f"Fetching image URLs for {len(node_ids)} nodes...")
        data = self._get(
            f"/files/{self.file_key}/images",
            params={"ids": ids_str, "format": format}
        )
        return data.get("images", {})

    def download_image(self, node_id: str, url: str, slide_name: str) -> str:
        """Download an image and save to assets folder. Returns filename."""
        self._throttle()
        filename = safe_filename(f"{slide_name}_{node_id}.png")
        filepath = self.assets_dir / filename

        # Skip if already downloaded
        if filepath.exists():
            return filename

        print(f"  Downloading {filename}...")
        resp = requests.get(url)
        resp.raise_for_status()

        # Downscale if > 1024px wide
        img = Image.open(BytesIO(resp.content))
        if img.width > 1024:
            ratio = 1024 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1024, new_height), Image.Resampling.LANCZOS)

        img.save(filepath, "PNG", optimize=True)
        return filename

    def extract_node(self, node: Dict, slide_name: str = "") -> Dict:
        """Extract a node's properties into a snapshot-safe format."""
        result = {
            "id": node.get("id"),
            "type": node.get("type"),
            "name": node.get("name", ""),
            "x": node.get("x", 0),
            "y": node.get("y", 0),
            "width": node.get("width", 0),
            "height": node.get("height", 0),
        }

        # Rotation
        if "rotation" in node and node["rotation"] != 0:
            result["rotation"] = node["rotation"]

        # Opacity and visibility
        if "opacity" in node and node["opacity"] != 1:
            result["opacity"] = node["opacity"]
        if not node.get("visible", True):
            result["visible"] = False

        # Blend mode
        if node.get("blendMode") and node["blendMode"] != "PASS_THROUGH":
            result["blendMode"] = node["blendMode"]

        # Fills
        if "fills" in node and node["fills"]:
            result["fills"] = self._extract_fills(node["fills"], node.get("id", ""), slide_name)

        # Strokes
        if "strokes" in node and node["strokes"]:
            result["strokes"] = self._extract_strokes(node["strokes"])
            if "strokeWeight" in node:
                result["strokeWeight"] = node["strokeWeight"]
            if "strokeAlign" in node:
                result["strokeAlign"] = node["strokeAlign"]

        # Effects (shadows, blurs)
        if "effects" in node and node["effects"]:
            result["effects"] = node["effects"]

        # Corner radius
        if "cornerRadius" in node and node["cornerRadius"] != 0:
            result["cornerRadius"] = node["cornerRadius"]
        if "cornerRadii" in node:
            result["cornerRadii"] = node["cornerRadii"]

        # Text-specific properties
        if node["type"] == "TEXT":
            result["characters"] = node.get("characters", "")
            if "fontSize" in node:
                result["fontSize"] = node["fontSize"]
            if "fontName" in node:
                result["fontName"] = node["fontName"]
            if "fontWeight" in node:
                result["fontWeight"] = node["fontWeight"]
            if "lineHeight" in node:
                result["lineHeight"] = node["lineHeight"]
            if "letterSpacing" in node:
                result["letterSpacing"] = node["letterSpacing"]
            if "textAlignHorizontal" in node:
                result["textAlignHorizontal"] = node["textAlignHorizontal"]
            if "textAlignVertical" in node:
                result["textAlignVertical"] = node["textAlignVertical"]
            # Text decoration
            if "textDecoration" in node:
                result["textDecoration"] = node["textDecoration"]

        # Vector paths
        if node["type"] == "VECTOR" and "vectorPaths" in node:
            result["vectorPaths"] = node["vectorPaths"]

        # Frame/Group layout properties
        if node["type"] in ("FRAME", "GROUP"):
            if "layoutMode" in node and node["layoutMode"] != "NONE":
                result["layoutMode"] = node["layoutMode"]
            if "itemSpacing" in node:
                result["itemSpacing"] = node["itemSpacing"]
            if "paddingLeft" in node:
                result["paddingLeft"] = node["paddingLeft"]
            if "paddingRight" in node:
                result["paddingRight"] = node["paddingRight"]
            if "paddingTop" in node:
                result["paddingTop"] = node["paddingTop"]
            if "paddingBottom" in node:
                result["paddingBottom"] = node["paddingBottom"]
            if "clipsContent" in node and node["clipsContent"]:
                result["clipsContent"] = True

        # Children (recursive — preserve Figma's source order; do NOT sort, since
        # node IDs like "1:104" / "1:1310" don't sort to layer order, and Figma's
        # order is the actual stacking/layout order)
        if "children" in node:
            result["children"] = [
                self.extract_node(child, slide_name)
                for child in node["children"]
            ]

        return result

    def _extract_fills(self, fills: List[Dict], node_id: str, slide_name: str) -> List[Dict]:
        """Extract fill properties, downloading images if needed."""
        result = []
        for fill in fills:
            if not fill.get("visible", True):
                continue

            fill_copy = {"type": fill.get("type")}

            if fill["type"] == "SOLID":
                fill_copy["color"] = fill.get("color", {})
                if "opacity" in fill:
                    fill_copy["opacity"] = fill["opacity"]
            elif fill["type"] == "IMAGE":
                # Download the image
                img_ref = fill.get("imageRef")
                if img_ref:
                    if img_ref not in self.downloaded_images:
                        urls = self.get_image_url([node_id], format="png")
                        if node_id in urls:
                            filename = self.download_image(node_id, urls[node_id], slide_name)
                            self.downloaded_images[img_ref] = filename
                    if img_ref in self.downloaded_images:
                        fill_copy["asset_ref"] = self.downloaded_images[img_ref]
            elif fill["type"] in ("GRADIENT_LINEAR", "GRADIENT_RADIAL"):
                # Simplified gradient capture
                fill_copy["gradientStops"] = fill.get("gradientStops", [])
                fill_copy["rotation"] = fill.get("rotation", 0)

            result.append(fill_copy)

        return result

    def _extract_strokes(self, strokes: List[Dict]) -> List[Dict]:
        """Extract stroke properties."""
        result = []
        for stroke in strokes:
            if not stroke.get("visible", True):
                continue
            stroke_copy = {"type": stroke.get("type")}
            if stroke["type"] == "SOLID":
                stroke_copy["color"] = stroke.get("color", {})
            result.append(stroke_copy)
        return result

    def extract_slide(self, slide: Dict, slide_index: int) -> Dict:
        """Extract a slide's snapshot. slide_index is 1-based."""
        raw_name = slide.get("name", "unknown")
        slide_name_safe = safe_filename(raw_name.split(" | ")[0].strip()) or f"slide_{slide_index}"

        # Determine section_id. Prefer parsing from slide name if encoded
        # ("01 — cover | section=cover"); otherwise fall back to position.
        section_id = None
        if "section=" in raw_name:
            section_id = raw_name.split("section=")[1].split("|")[0].strip()
        if not section_id:
            idx = slide_index - 1
            section_id = SECTION_BY_SLIDE_INDEX[idx] if 0 <= idx < len(SECTION_BY_SLIDE_INDEX) else "unknown"

        snapshot = {
            "slide_index": slide_index,
            "name": raw_name,
            "section_id": section_id,
            "id": slide.get("id"),
        }

        # Capture background
        if "background" in slide:
            bg = slide["background"]
            if bg and "color" in bg:
                snapshot["background"] = {"type": "SOLID", "color": bg["color"]}

        # Capture children (preserve source order)
        if "children" in slide:
            snapshot["children"] = [
                self.extract_node(child, slide_name_safe)
                for child in slide["children"]
            ]

        return snapshot

    def _collect_slides(self, doc: Dict) -> List[Dict]:
        """Walk Page → SLIDE_GRID → SLIDE_ROW → SLIDE to collect every SLIDE node.

        Mord's structure differs from a flat page-children layout — Figma Slides
        files nest SLIDEs inside SLIDE_GRID and SLIDE_ROW containers. Preserve
        the document's natural order (don't sort)."""
        slides: List[Dict] = []

        def walk(node: Dict) -> None:
            ntype = node.get("type")
            if ntype == "SLIDE":
                slides.append(node)
                return
            # Recurse through pages, slide grids, and slide rows
            for child in node.get("children", []) or []:
                walk(child)

        for page in doc.get("document", {}).get("children", []) or []:
            walk(page)

        return slides

    def run(self) -> Dict:
        """Main extraction logic."""
        doc = self.fetch_file()

        snapshot = {
            "version": 1,
            "source_file_key": self.file_key,
            "lastModified": doc.get("lastModified"),
            "slides": [],
        }

        slides = self._collect_slides(doc)
        print(f"Found {len(slides)} slides")

        for i, slide in enumerate(slides, start=1):
            print(f"Processing slide {i}/{len(slides)}: {slide.get('name', 'unknown')}")
            snapshot["slides"].append(self.extract_slide(slide, i))

        # Do NOT sort slides — order matches Figma's source order, which matches
        # the canonical proposal flow (cover → TOC → exec_summary → ... → closing).
        return snapshot

    def save_snapshot(self, snapshot: Dict) -> None:
        """Save snapshot JSON to templates/mord.snapshot.json."""
        output_path = Path("templates/mord.snapshot.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write with sorted keys for determinism
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False, sort_keys=True)

        print(f"\nSnapshot saved to {output_path}")
        print(f"Assets saved to {self.assets_dir}")
        print(f"Total images downloaded: {len(self.downloaded_images)}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract Mord master template to JSON snapshot + assets"
    )
    parser.add_argument(
        "--file-key",
        required=True,
        help="Figma file key (e.g., JtzNUXrAHFupkajwfPz952)"
    )
    args = parser.parse_args()

    token = os.getenv("FIGMA_TOKEN")
    if not token:
        print("Error: FIGMA_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        extractor = FigmaSnapshotExtractor(args.file_key, token)
        snapshot = extractor.run()
        extractor.save_snapshot(snapshot)
        print("\n✓ Snapshot extraction complete")
    except requests.exceptions.HTTPError as e:
        print(f"Error: Figma API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
