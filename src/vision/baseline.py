"""Reproducible YOLO baseline diagnostics for UAV video."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO


def run(video: Path, weights: Path, output: Path, sample_fps: float = 3.0,
        imgsz: int = 640, conf: float = 0.25, iou: float = 0.45,
        tracker: str = "bytetrack.yaml", device: str = "auto",
        save_frames: Path | None = None) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    if save_frames:
        save_frames.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(
            f"OpenCV could not open {video}. Normalize the media with FFmpeg first "
            "if the source container/codec is unsupported."
        )

    source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / source_fps if source_fps > 0 else 0.0
    stride = max(1, round(source_fps / sample_fps)) if source_fps > 0 else 1

    model = YOLO(str(weights))
    class_counts: Counter[str] = Counter()
    confidences: list[float] = []
    detections = 0
    tracks: set[int] = set()
    sampled_frames = 0
    inference_s = 0.0
    rows: list[dict] = []

    frame_index = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_index += 1
        if frame_index % stride:
            continue

        sampled_frames += 1
        start = time.perf_counter()
        result = model.track(
            frame, persist=True, tracker=tracker, imgsz=imgsz,
            conf=conf, iou=iou,
            device=None if device == "auto" else device, verbose=False
        )[0]
        inference_s += time.perf_counter() - start

        boxes = result.boxes
        annotated = frame
        timestamp_s = frame_index / source_fps if source_fps else 0.0

        if boxes is not None and len(boxes):
            xyxy = boxes.xyxy.cpu().tolist()
            cls_ids = boxes.cls.cpu().tolist()
            confs = boxes.conf.cpu().tolist()
            ids = boxes.id.cpu().tolist() if boxes.id is not None else [None] * len(xyxy)

            for bbox, cls_id, score, track_id in zip(xyxy, cls_ids, confs, ids):
                class_name = str(result.names[int(cls_id)])
                class_counts[class_name] += 1
                confidences.append(float(score))
                detections += 1
                if track_id is not None:
                    tracks.add(int(track_id))
                rows.append({
                    "frame_index": frame_index,
                    "timestamp_s": round(timestamp_s, 3),
                    "class_name": class_name,
                    "confidence": round(float(score), 6),
                    "bbox_xyxy": [round(float(v), 2) for v in bbox],
                    "track_id": int(track_id) if track_id is not None else None,
                })
            annotated = result.plot()

        if save_frames:
            cv2.imwrite(str(save_frames / f"frame_{frame_index:06d}.jpg"), annotated)

    cap.release()

    summary = {
        "video": str(video),
        "weights": str(weights),
        "source": {
            "fps": source_fps, "width": width, "height": height,
            "frame_count": frame_count, "duration_s": round(duration, 3),
        },
        "sampling": {
            "requested_fps": sample_fps, "actual_stride": stride,
            "sampled_frames": sampled_frames,
            "effective_fps": round(sampled_frames / duration, 3) if duration else 0.0,
        },
        "inference": {
            "imgsz": imgsz, "conf": conf, "iou": iou, "tracker": tracker,
            "total_inference_s": round(inference_s, 3),
            "mean_inference_ms": round((inference_s / sampled_frames) * 1000, 3)
            if sampled_frames else 0.0,
        },
        "detections": {
            "total": detections, "class_counts": dict(class_counts),
            "unique_track_ids": len(tracks),
            "confidence_min": min(confidences) if confidences else None,
            "confidence_median": statistics.median(confidences) if confidences else None,
            "confidence_max": max(confidences) if confidences else None,
        },
        "rows": rows,
    }
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible UAV YOLO baseline.")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-fps", type=float, default=3.0)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--save-frames", type=Path)
    args = parser.parse_args()
    summary = run(**vars(args))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
