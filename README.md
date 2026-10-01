# Multi-Modal UAV Intelligence Engine

Offline, multi-modal UAV mission analysis pipeline.

The system is designed to transform UAV mission media into traceable visual/audio
evidence, temporally grouped events, an adaptive highlight, and—when audio is
present—a timestamped transcript, grounded local-LLM summary, TTS briefing, PDF
report, and Streamlit interface.

**Important:** this project is not a DRDO project and must not be described as
one. Facility footage remains inside the approved environment and is never
committed to Git.

## Current target environment

The latest project environment snapshot targets:

- Windows 10 Pro
- Intel Xeon E-2176M
- 16 GB RAM
- NVIDIA Quadro P2000, 4 GB VRAM
- 1 TB storage
- Python 3.14.x

The GPU/runtime choice is deliberately not considered final until the facility
GPU driver/CUDA stack is audited and benchmarked. Do not rebuild the final
wheelhouse from assumptions.

## Architecture

```
Raw mission media
      |
      +--> FFprobe / FFmpeg --> metadata + sampled frames
      |                              |
      |                              +--> YOLO --> tracking --> visual evidence
      |                                                      |
      |                                                      +--> events
      |
      +--> audio extraction --> Faster-Whisper --> transcript
                                               |
                                               v
                                  timestamp-aligned evidence
                                               |
                                               v
                                  Mission Evidence Package
                                               |
                                               v
                                  local Qwen reasoning
                                               |
                       +-----------------------+-------------------+
                       |                       |                   |
                 highlight.mp4           summary.json/txt      report.pdf
                                               |
                                          TTS briefing
```

A text-only LLM does not receive the raw MP4 as its reasoning input. Visual
analysis produces structured evidence and selected keyframes; audio analysis
produces timestamped transcript evidence.

## Repository layout

```
config/         YAML configuration and event ontology
src/core/       shared temporal/domain data models
src/media/      FFprobe/FFmpeg wrappers and media handling
src/vision/     YOLO, tracking, visual analysis, keyframes
src/fusion/     event scoring and evidence construction
src/audio/      Faster-Whisper pipeline
src/llm/        local Qwen integration and schema validation
src/tts/        offline TTS
src/report/     PDF generation
src/ui/         Streamlit interface
scripts/        offline installation/build utilities
tests/          unit/integration tests
docs/           design and implementation documentation
```

## Temporal data contract

Visual observations must carry a source timestamp. Tracks expose their actual
temporal duration rather than using detection count as a proxy.

The shared models in `src/core/models.py` currently define:

- `Detection`: frame index, timestamp, class, confidence, bounding box, track ID
- `Track`: first/last frame, first/last timestamp, confidence, trajectory,
  computed duration
- `Event`: event ID/type, start/end timestamps, score, confidence, tracks and
  evidence references

This keeps later event detection, highlight extraction, audio alignment, and
LLM evidence grounding on one temporal representation.

## Setup

Development and offline deployment must use the exact Python/runtime versions
selected after the facility hardware audit.

At home (internet available), the project can build a wheelhouse for the exact
target platform. At the facility, installation must use `pip --no-index` and
the transferred wheelhouse/models only.

Do not transfer or commit sensitive mission footage.

## Development phases

1. Environment + media foundation
2. YOLO + tracking baseline
3. Visual event detection + camera-motion-aware change analysis
4. Adaptive highlight generation
5. Faster-Whisper + audio/video alignment
6. Mission Evidence Package
7. Local Qwen reasoning
8. TTS + PDF + Streamlit integration
9. Offline validation + facility testing

The immediate engineering priority is to make the video/evidence foundation
traceable and testable before adding the event/highlight/LLM layers.
