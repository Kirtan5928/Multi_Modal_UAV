from pathlib import Path

from scripts.prepare_yolo_dataset import validate_split


def test_validate_split_missing_root(tmp_path: Path):
    images, labelled, errors = validate_split(tmp_path, "train")
    assert images == 0
    assert labelled == 0
    assert errors


def test_validate_split_accepts_normalized_box(tmp_path: Path):
    images = tmp_path / "images" / "train"
    labels = tmp_path / "labels" / "train"
    images.mkdir(parents=True)
    labels.mkdir(parents=True)
    (images / "frame.jpg").write_bytes(b"not-an-image")
    (labels / "frame.txt").write_text("0 0.5 0.5 0.2 0.1\n", encoding="utf-8")
    count, labelled, errors = validate_split(tmp_path, "train")
    assert count == 1
    assert labelled == 1
    assert errors == []
