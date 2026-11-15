"""Turns the raw Playwright recording into the README media: a silent MP4 (full demo) and a short GIF (highlights).

    python tools/demo/make_media.py --raw build/demo --mp4 build/astroatlas-demo.mp4 --gif docs/media/demo.gif

Needs `ffmpeg` on the PATH. The GIF covers the featured case, the map and the place profile (the first ~30 seconds of the tour).
"""
import argparse
import json
import pathlib
import subprocess


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="build/demo")
    ap.add_argument("--mp4", default="build/astroatlas-demo.mp4")
    ap.add_argument("--gif", default="docs/media/demo.gif")
    ap.add_argument("--gif-seconds", type=float, default=30.0)
    ap.add_argument("--gif-width", type=int, default=800)
    ap.add_argument("--gif-fps", type=int, default=10)
    a = ap.parse_args()
    raw = pathlib.Path(a.raw)
    meta = json.loads((raw / "scenes.json").read_text(encoding="utf-8"))
    start = meta["trim_start"]
    scenes = {s["name"]: s["t"] for s in meta["scenes"]}
    end = start + meta["duration"]
    mp4, gif = pathlib.Path(a.mp4), pathlib.Path(a.gif)
    mp4.parent.mkdir(parents=True, exist_ok=True)
    gif.parent.mkdir(parents=True, exist_ok=True)

    run("ffmpeg", "-y", "-loglevel", "error", "-ss", start, "-t", end - start, "-i", raw / "demo.webm", "-an",
        "-vf", "fps=24,scale=1280:720:flags=lanczos", "-c:v", "libx264", "-crf", 26, "-preset", "slow", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", mp4)

    g0 = scenes["featured"]
    palette = raw / "palette.png"
    vf = f"fps={a.gif_fps},scale={a.gif_width}:-1:flags=lanczos"
    run("ffmpeg", "-y", "-loglevel", "error", "-ss", g0, "-t", a.gif_seconds, "-i", raw / "demo.webm", "-vf", vf + ",palettegen=max_colors=96", palette)
    run("ffmpeg", "-y", "-loglevel", "error", "-ss", g0, "-t", a.gif_seconds, "-i", raw / "demo.webm", "-i", palette,
        "-lavfi", vf + "[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4", "-loop", 0, gif)
    print(f"mp4: {mp4} ({mp4.stat().st_size / 1e6:.1f} MB) | gif: {gif} ({gif.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
