# Phase 3 — Aerial-Domain Detection Adaptation

## Objective

The facility-day baseline showed that the generic detector is not sufficient for distant UAV/aircraft imagery. Phase 3 therefore focuses on making detection and tracking measurable and adaptable before any event, highlight, or LLM layer is built.

The sensitive facility footage remains at the facility. Public aerial datasets are used at home to build and validate the adaptation pipeline.

## Evidence-driven experiment

We will compare:

1. Generic baseline — existing YOLO11n checkpoint, 640px, 3 FPS, confidence 0.25, ByteTrack.
2. Aerial-domain adaptation — pretrained checkpoint fine-tuned on selected public aerial data.
3. Facility adaptation — the aerial-adapted checkpoint fine-tuned on manually annotated facility frames, if guide approval permits.
4. Inference strategy variants — full-frame resolution versus higher resolution and tiled inference, measured rather than assumed to help.

Ultralytics documents pretrained-weight fine-tuning and supports custom YOLO datasets; the project keeps the exact checkpoint and settings under version control while model binaries remain outside Git.

## Public data strategy

### VisDrone

VisDrone is the first public dataset because it is specifically collected from drone-mounted cameras and includes detection and multi-object tracking benchmarks. Its published dataset contains 288 video clips, 261,908 frames, and 10,209 static images, with annotations for pedestrians and multiple vehicle categories. It is useful for the vehicle/person side of our domain adaptation.

### UAVDT

UAVDT is a second candidate focused on aerial vehicle detection/tracking. We will use it only for classes that map cleanly to the final ontology and will preserve its sequence boundaries when constructing validation data.

### xView

xView is an overhead satellite-imagery dataset with many small/fine-grained objects, including aircraft and buildings. It is not treated as a drop-in substitute for UAV video because the viewpoint differs. It is an optional later experiment for small-object/aircraft representation, subject to its download and usage terms.

## What we will not do

- We will not mix incompatible label taxonomies blindly.
- We will not train on sensitive facility footage at home.
- We will not call a detector improvement successful based only on visual inspection.
- We will not split adjacent frames from one video randomly across train and test.
- We will not lock the final facility class list until representative facility frames are reviewed.
- We will not assume tiled inference is better; it will be benchmarked.

## Annotation plan

If the guide approves annotation at the facility, annotate selected frames locally using bounding boxes and export in YOLO format. Each annotation records: class_id center_x center_y width height, with normalized coordinates. The selected frames should cover distance, scale, motion blur, lighting, background, and representative object types.

The facility test split must remain held out from training and should be separated by video or time block to avoid near-duplicate leakage.

## First experiment matrix

| Experiment | Dataset | imgsz | Purpose |
|---|---|---:|---|
| B0 | existing baseline | 640 | reproduce failure |
| A1 | aerial public data | 640 | domain adaptation |
| A2 | aerial public data | 960 | small-object test |
| A3 | aerial public data | 1280 if hardware allows | small-object test |
| F1 | facility annotations | 960 | facility adaptation |
| F2 | facility annotations | 1280 if hardware allows | facility small-object test |

Every run records checkpoint path, dataset manifest, class mapping, seed, training settings, hardware, runtime, and validation metrics.

## Definition of done

Phase 3 is complete when:

- the baseline can be reproduced;
- a public aerial adaptation model trains end-to-end;
- evaluation produces per-class precision/recall/mAP;
- small-object behavior is measured at multiple input sizes;
- the facility annotation format is ready;
- the facility-specific training path can run offline once approved;
- tracking can consume the adapted detector without changing the downstream evidence schema.

## Sources

- VisDrone dataset repository: https://github.com/VisDrone/VisDrone-Dataset
- UAVDT benchmark: https://sites.google.com/view/grli-uavdt
- xView dataset: https://xviewdataset.org/
- Ultralytics training documentation: https://docs.ultralytics.com/modes/train
