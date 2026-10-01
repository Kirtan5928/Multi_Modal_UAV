"""Media inspection CLI.

Reads container/stream metadata with FFprobe and emits JSON. No video frames
are loaded, so this is safe as the first step for large mission files.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def find_ffprobe() -> str:
    root = Path(__file__).resolve().parents[2]
    bundled = root / "tools" / "ffmpeg" / "bin" / "ffprobe.exe"
    if bundled.exists():
        return str(bundled)
    found = shutil.which("ffprobe")
    if found:
        return found
    raise FileNotFoundError(
        "ffprobe.exe not found. Put FFmpeg under tools/ffmpeg/bin or add ffprobe to PATH."
    )


def inspect_media(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)

    cmd = [
        find_ffprobe(),
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        str(path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
    raw = json.loads(completed.stdout)

    streams = []
    for stream in raw.get("streams", []):
        streams.append(
            {
                "index": stream.get("index"),
                "codec_type": stream.get("codec_type"),
                "codec_name": stream.get("codec_name"),
                "codec_long_name": stream.get("codec_long_name"),
                "width": stream.get("width"),
                "height": stream.get("height"),
                "fps": stream.get("r_frame_rate"),
                "duration_s": stream.get("duration"),
                "sample_rate": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "channel_layout": stream.get("channel_layout"),
            }
        )

    return {
        "file": str(path.resolve()),
        "format": raw.get("format", {}),
        "streams": streams,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect UAV mission media with FFprobe.")
    parser.add_argument("input", type=Path, help="Input MP4/MOV/AVI/MKV file")
    parser.add_argument("-o", "--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    result = inspect_media(args.input)
    payload = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
