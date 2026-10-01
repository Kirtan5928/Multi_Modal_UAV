# Facility Video Annotation Guide

## What annotation means

For object-detection transfer learning, an annotation is a label attached to an
object in a video frame. The basic annotation is a **bounding box**:

- draw a rectangle tightly around the object;
- assign the object class;
- save the label in the detector's dataset format.

Example:

`[box around aircraft] -> aircraft`

The model learns from many such labeled examples.

## Do we annotate every frame?

No. For video, we normally sample representative frames. Adjacent frames are
highly redundant. Sampling must preserve difficult conditions such as:

- near/far objects;
- different sizes;
- different viewpoints;
- partial occlusion;
- motion blur;
- lighting changes;
- background clutter;
- different camera positions.

## Why facility annotation matters

Public aerial datasets can provide a useful starting point, but facility footage
has its own camera characteristics and object appearance. Facility-specific
fine-tuning is therefore a planned stage.

Sensitive facility footage must remain inside the approved facility environment.
Only non-sensitive/public material should be moved to the development machine.

## Initial workflow

1. Inspect the two available videos.
2. Extract representative frames.
3. Identify the actual object categories present.
4. Build a final class ontology from observed requirements.
5. Annotate a small pilot set.
6. Train a baseline transfer-learning model.
7. Evaluate on held-out frames/videos.
8. Inspect false positives and false negatives.
9. Expand annotations specifically around failure cases.
10. Repeat training and evaluation.

## Important split rule

Do not randomly mix adjacent frames from one continuous video between training
and validation. That can make metrics look artificially strong because nearly
identical frames appear in both sets.

Prefer a video-level or time-block-level split, for example:

- earlier time blocks -> training;
- later independent blocks -> validation/test.

The exact split will be decided after inspecting the available footage.

## Current class status

The previously proposed classes are only a starting hypothesis:

- person
- car
- truck
- motorcycle
- aircraft
- building
- tank
- other_vehicle

Do not finalize this list until representative facility/public frames are reviewed.
Additional classes may be required, and unused classes should not be forced into
the dataset.

## Annotation tool

The first requirement is a local/offline annotation workflow. The project should
not depend on a cloud annotation service for sensitive footage.

The chosen tool must be tested on the actual facility machine before sensitive
data is loaded.
