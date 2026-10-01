from src.core.models import Detection, Event, Track


def test_detection_keeps_timestamp_and_track_id():
    detection = Detection(42, 14.0, "person", 0.8, [1, 2, 30, 40], 7)
    assert detection.to_dict()["timestamp_s"] == 14.0
    assert detection.to_dict()["track_id"] == 7


def test_track_duration_uses_time_not_detection_count():
    track = Track(7, "car", 0, 47, 0.0, 15.666, detections=12)
    assert track.duration_s == 15.666
    assert track.to_dict()["duration_s"] == 15.666


def test_event_duration_is_temporal():
    event = Event("evt-1", "object_persistence", 10.0, 18.5, 0.72)
    assert event.duration_s == 8.5
