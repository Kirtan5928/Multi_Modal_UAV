"""Shared, JSON-serializable domain models for the UAV pipeline.

These models deliberately use only the Python standard library so they do not
add another runtime dependency to the offline deployment.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Detection:
    frame_index: int
    timestamp_s: float
    class_name: str
    confidence: float
    bbox_xyxy: list[float]
    track_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Track:
    track_id: int
    class_name: str
    first_frame: int
    last_frame: int
    first_seen_s: float
    last_seen_s: float
    detections: int = 0
    mean_confidence: float = 0.0
    trajectory: list[list[float]] = field(default_factory=list)

    @property
    def duration_s(self) -> float:
        return max(0.0, self.last_seen_s - self.first_seen_s)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["duration_s"] = self.duration_s
        return payload


@dataclass(slots=True)
class Event:
    event_id: str
    event_type: str
    start_s: float
    end_s: float
    score: float
    confidence: float | None = None
    track_ids: list[int] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    description: str | None = None

    @property
    def duration_s(self) -> float:
        return max(0.0, self.end_s - self.start_s)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["duration_s"] = self.duration_s
        return payload
