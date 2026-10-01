"""Validate a YOLO-format dataset before training."""

from __future__ import annotations

import argparse
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def validate_split(root: Path, split: str) -> tuple[int, int, list[str]]:
    images_dir = root / "images" / split
    labels_dir = root / "labels" / split
    if not images_dir.exists():
        return 0, 0, [f"missing {images_dir}"]

    errors: list[str] = []
    image_files = [p for p in images_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS]
    labelled = 0

    for image in image_files:
        label = labels_dir / f"{image.stem}.txt"
        if not label.exists():
            errors.append(f"missing label: {label}")
            continue
        labelled += 1
        for line_no, line in enumerate(label.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 5:
                errors.append(f"{label}:{line_no}: expected 5 fields")
                continue
            try:
                cls = int(parts[0])
                values = [float(x) for x in parts[1:]]
            except ValueError:
                errors.append(f"{label}:{line_no}: non-numeric annotation")
                continue
            if cls < 0:
                errors.append(f"{label}:{line_no}: negative class id")
            if any(v < 0.0 or v > 1.0 for v in values):
                errors.append(f"{label}:{line_no}: coordinates must be normalized to [0,1]")

    return len(image_files), labelled, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()

    total_images = 0
    total_labelled = 0
    all_errors: list[str] = []
    for split in ("train", "val", "test"):
        images, labelled, errors = validate_split(args.dataset, split)
        if images:
            print(f"{split}: {images} images, {labelled} labelled")
        total_images += images
        total_labelled += labelled
        all_errors.extend(errors)

    if not (args.dataset / "data.yaml").exists():
        all_errors.append("missing data.yaml")

    print(f"total images: {total_images}")
    print(f"labelled images: {total_labelled}")
    if all_errors:
        print(f"errors: {len(all_errors)}")
        for error in all_errors[:50]:
            print(f"  - {error}")
        raise SystemExit(1)
    print("dataset validation: OK")


if __name__ == "__main__":
    main()
