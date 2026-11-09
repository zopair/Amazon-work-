"""Validate rasterized cover dimensions using ImageMagick identify."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .cover import calculate_cover_geometry

ROOT = Path(__file__).resolve().parents[1]


def validate(image: Path, manifest_path: Path, profiles_path: Path, tolerance_px: int = 1) -> dict:
    if tolerance_px < 0:
        raise ValueError("tolerance_px must be non-negative")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    profile = profiles["profiles"][manifest["kdp_profile"]]
    geometry = calculate_cover_geometry(profile, int(manifest["page_count"]))
    command = ["identify", "-format", "%w %h", str(image)]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    values = result.stdout.strip().split()
    if len(values) != 2:
        raise RuntimeError(f"ImageMagick returned unexpected dimensions: {result.stdout!r}")
    actual = {"width_px": int(values[0]), "height_px": int(values[1])}
    expected = {
        "width_px": int(geometry["cover_width_px_at_dpi"]),
        "height_px": int(geometry["cover_height_px_at_dpi"]),
    }
    deltas = {key: abs(actual[key] - expected[key]) for key in expected}
    passed = all(delta <= tolerance_px for delta in deltas.values())
    report = {
        "status": "PASS" if passed else "FAIL",
        "image": str(image),
        "dpi": geometry["dpi"],
        "expected": expected,
        "actual": actual,
        "absolute_pixel_delta": deltas,
        "tolerance_px": tolerance_px,
        "geometry_in": {
            "width": geometry["cover_width_in"],
            "height": geometry["cover_height_in"],
        },
        "validator": "ImageMagick identify",
    }
    if not passed:
        raise ValueError(json.dumps(report, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--manifest", default="config/books/happy-little-train.json")
    parser.add_argument("--profiles", default="config/kdp_profiles.json")
    parser.add_argument("--tolerance-px", type=int, default=1)
    parser.add_argument("--report", default="dist/cover-image-geometry.json")
    args = parser.parse_args()
    try:
        report = validate(args.image, ROOT / args.manifest, ROOT / args.profiles, args.tolerance_px)
        report_path = ROOT / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"COVER GEOMETRY VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
