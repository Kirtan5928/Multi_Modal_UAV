# Technical Design Review — Multi-Modal UAV Intelligence Engine

## Scope

This repository implements an **offline, multi-modal UAV mission analysis
pipeline**. It is not a DRDO project and must not be represented as one.

The target workflow is:

```
mission video/audio
    -> media inspection
    -> sampled visual analysis + tracking
    -> temporal events
    -> adaptive highlight
    -> audio transcription when present
    -> timestamp-aligned Mission Evidence Package
    -> grounded local Qwen reasoning
    -> TTS + PDF + Streamlit
```

The design prioritizes traceability: important generated claims should be
traceable to a timestamp, detection/track, keyframe, transcript segment, or
other explicit evidence.

## 1. Detection is not an event

YOLO provides frame-level observations:

- class
- confidence
- bounding box
- frame
- timestamp

Tracking adds temporal identity:

- first/last observation
- duration
- trajectory
- confidence statistics

The event layer then decides whether a temporally coherent pattern is
significant. A single high-confidence detection is not automatically a
mission event.

## 2. Video processing

The source video remains the quality source of truth. Inference can use sampled
frames and a lower inference resolution.

Initial target:

- source: typically 1920x1080, subject to media inspection
- sampling: configurable, currently 3 FPS
- YOLO input: currently 640 px
- tracking: ByteTrack baseline
- output clips: extracted from the original media

The sampling rate must be benchmarked on the actual target workstation rather
than assumed from specifications.

## 3. Temporal representation

Every visual observation needs a timestamp. Tracks must report temporal
duration from timestamps rather than treating detection count as duration.

The shared models in `src/core/models.py` provide:

- `Detection`
- `Track`
- `Event`

This creates a common contract for later event scoring, highlight extraction,
audio alignment and evidence construction.

## 4. UAV camera motion

Naive frame differencing is unreliable when the camera pans, rotates,
vibrates or changes altitude.

The planned visual-change path is:

```
sampled frames
    -> feature/global-motion estimation
    -> quality gate
    -> motion-compensated comparison
    -> temporal smoothing
    -> visual-change signal
```

This signal is complementary to YOLO/tracking rather than a replacement for
semantic detection.

## 5. Event ontology

The event ontology remains configuration-driven. Candidate categories include:

- object appearance
- object persistence
- object disappearance
- count change
- scene transition
- speech event
- mission phase change
- takeoff / mission start
- landing / mission end

The final domain classes must be selected only after representative frames are
inspected. Provisional classes must not be treated as final requirements.

## 6. Adaptive highlight

The highlight should be generated from scored events:

1. sort events chronologically;
2. add configurable pre/post context;
3. merge overlapping or nearby windows;
4. suppress redundant coverage;
5. preserve chronology;
6. force takeoff/mission-start coverage when present;
7. force landing/mission-end coverage when present;
8. extract clips from the original media;
9. concatenate them into the adaptive highlight.

The highlight is a human-facing output; it is not the same thing as the
Mission Evidence Package.

## 7. Audio

When audio is present:

```
audio extraction
    -> Faster-Whisper
    -> language identification
    -> timestamped transcript
    -> confidence-aware evidence
```

The original-language transcript should be preserved. The final summary/TTS
language remains configurable, with English and Hindi as initial targets.

## 8. Mission Evidence Package

The text-only reasoning model should receive structured evidence rather than a
raw MP4.

A mission package is expected to contain, as applicable:

```
input/mission.mp4
video/sampled_frames/
video/keyframes/
video/detections.json
video/tracks.json
video/events.json
video/highlight.mp4
audio/audio.wav
audio/transcript.json
intelligence/evidence.json
intelligence/summary.json
intelligence/summary.txt
report/report.pdf
report/briefing.wav
metadata.json
```

Evidence should retain provenance references so a reviewer can trace claims
back to source observations.

## 9. Qwen

The local text model is an evidence-grounded reasoning layer. It must:

- use only supplied evidence;
- preserve chronology;
- distinguish detections from confirmed events;
- retain timestamps;
- report uncertainty;
- avoid unsupported conclusions;
- produce structured output before report generation.

A small VLM may be used only for sparse keyframe interpretation if hardware
benchmarking shows it is practical. It is not a replacement for the detector
or tracker.

## 10. Offline deployment

The deployment target is an offline Windows workstation. Final provisioning
must include:

- exact Python/runtime version;
- compatible wheels;
- model files;
- FFmpeg/FFprobe;
- configuration;
- checksums;
- installation scripts;
- runtime verification.

The current project snapshot targets Python 3.14.x, but the final PyTorch/CUDA
combination must be selected only after auditing the facility GPU driver and
runtime.

## 11. Evaluation

The implementation should eventually measure:

- detection/tracking quality;
- event precision, recall and F1;
- highlight event coverage and compression;
- ASR WER/CER where ground truth exists;
- language identification accuracy;
- LLM grounding/factuality/chronology;
- wall-clock processing time;
- CPU/RAM/GPU/VRAM use;
- failure handling.

Train/validation/test data should be split by video or time block rather than
randomly splitting adjacent frames from one continuous recording.

## 12. Development rule

Do not add components merely because they are available. Each component must
produce evidence consumed by the next stage.

The intended chain is:

```
raw media
  -> specialized analysis
  -> structured evidence
  -> temporal events
  -> multimodal evidence
  -> grounded reasoning
  -> operational outputs
```

This keeps the system auditable, offline-capable and defensible.
