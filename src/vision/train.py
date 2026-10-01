"""Ultralytics training entry point with reproducible experiment settings."""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def train(data: Path, model_path: Path, output_dir: Path, imgsz: int,
          epochs: int, batch: int, seed: int, workers: int, device: str,
          lr0: float, optimizer: str, freeze: int | None,
          patience: int, amp: bool) -> None:
    model = YOLO(str(model_path))
    kwargs = {
        "data": str(data), "imgsz": imgsz, "epochs": epochs, "batch": batch,
        "seed": seed, "workers": workers,
        "device": None if device == "auto" else device,
        "lr0": lr0, "optimizer": optimizer, "patience": patience,
        "amp": amp, "project": str(output_dir), "exist_ok": True,
    }
    if freeze is not None:
        kwargs["freeze"] = freeze
    model.train(**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the UAV detector from a YOLO dataset.")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("runs/aerial"))
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--lr0", type=float, default=0.001)
    parser.add_argument("--optimizer", default="AdamW")
    parser.add_argument("--freeze", type=int)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--no-amp", action="store_true")
    args = parser.parse_args()
    train(args.data, args.model, args.output_dir, args.imgsz, args.epochs,
          args.batch, args.seed, args.workers, args.device, args.lr0,
          args.optimizer, args.freeze, args.patience, not args.no_amp)


if __name__ == "__main__":
    main()
