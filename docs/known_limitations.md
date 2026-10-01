# Known Limitations & Mitigations

This document records limitations that affect implementation or evaluation.

| # | Limitation | Mitigation | Status |
|---|---|---|---|
| 1 | No representative sensitive facility footage can be moved to development | Use public/non-sensitive footage for pipeline development; perform facility-specific training and validation inside the approved environment | Active |
| 2 | Generic pretrained YOLO may miss domain-specific objects or small distant targets | Start with a small pretrained model, inspect representative frames, then fine-tune on approved facility annotations | Planned |
| 3 | UAV camera motion can create false visual-change signals | Use camera-motion compensation/global-motion estimation and quality gates before treating pixel change as evidence | Planned |
| 4 | Tracker ID switches can create false appearance/disappearance events | Track persistence plus logical-track reconciliation/ghost windows | Planned |
| 5 | Detection count is not the same as temporal duration | Shared temporal models store first/last timestamps and compute duration explicitly | Implemented in foundation |
| 6 | Text-only Qwen cannot directly reason over raw MP4 content | Feed structured mission evidence plus selected keyframes where a VLM is used | Architectural decision |
| 7 | LLM summaries can hallucinate unsupported events | Strict evidence-grounded prompt, structured JSON, event/evidence references, uncertainty fields, validation before reporting | Planned |
| 8 | Whisper may produce plausible text from background noise | Preserve timestamps/confidence and separate low-confidence transcript evidence from confirmed evidence | Planned |
| 9 | P2000 4 GB limits concurrent model workloads | Benchmark models sequentially; prefer small/quantized models; keep VLM optional and sparse | Active |
| 10 | Final PyTorch/CUDA choice is not yet locked | Audit facility driver/runtime first; then build the final Python 3.14 wheelhouse | Active |
| 11 | Sensitive mission outputs must not enter Git | Keep data/input, data/output, model files and runtime artifacts gitignored | Implemented |
| 12 | Random frame-level train/validation splitting can leak near-identical frames | Split by video or time block, not adjacent frames | Planned |
| 13 | Stream-copy highlight cuts can land on keyframes rather than exact timestamps | Use stream copy for the robust MVP; optionally re-encode for frame-accurate cuts later | Planned |
| 14 | Model/code/config provenance must be retained for reproducibility | Stamp run metadata, configuration hashes, model versions and code revision into mission outputs | Planned |

Sensitive footage, mission outputs, credentials and large model binaries should
never be committed to the public repository.
