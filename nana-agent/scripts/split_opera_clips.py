"""
Split large MP3 files into short clips from different sections (no ffmpeg needed).
Each clip is capped in size for GitHub / Render.
"""

from __future__ import annotations

from pathlib import Path

BITRATE_TABLE = {
    1: {3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]},
    2: {3: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]},
    0: {3: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]},
}

SAMPLE_RATE_TABLE = {
    3: [44100, 48000, 32000, 0],
    2: [22050, 24000, 16000, 0],
    0: [11025, 12000, 8000, 0],
}


def frame_length(header: bytes) -> int | None:
    if len(header) < 4:
        return None
    if header[0] != 0xFF or (header[1] & 0xE0) != 0xE0:
        return None
    version_id = (header[1] >> 3) & 0x03
    layer = (header[1] >> 1) & 0x03
    layer_map = {1: 3, 2: 2, 3: 1}
    layer_num = layer_map.get(layer)
    if layer_num != 3 or version_id == 1:
        return None
    bitrate_idx = (header[2] >> 4) & 0x0F
    sr_idx = (header[2] >> 2) & 0x03
    padding = (header[2] >> 1) & 0x01
    ver_key = 1 if version_id == 3 else (2 if version_id == 2 else 0)
    br_table = BITRATE_TABLE.get(ver_key, {}).get(3)
    if not br_table or bitrate_idx in (0, 15):
        return None
    bitrate = br_table[bitrate_idx] * 1000
    sr_table = SAMPLE_RATE_TABLE.get(version_id)
    if not sr_table or sr_idx > 2:
        return None
    sample_rate = sr_table[sr_idx]
    if not sample_rate or not bitrate:
        return None
    if version_id == 3:
        length = int(144 * bitrate / sample_rate) + padding
    else:
        length = int(72 * bitrate / sample_rate) + padding
    if length < 24 or length > 4000:
        return None
    return length


def iter_frames(data: bytes):
    i = 0
    n = len(data)
    if data.startswith(b"ID3") and n >= 10:
        size = (
            ((data[6] & 0x7F) << 21)
            | ((data[7] & 0x7F) << 14)
            | ((data[8] & 0x7F) << 7)
            | (data[9] & 0x7F)
        )
        i = 10 + size
    while i + 4 <= n:
        fl = frame_length(data[i : i + 4])
        if fl is None or i + fl > n:
            i += 1
            continue
        yield i, fl
        i += fl


def split_mp3(
    src: Path,
    out_dir: Path,
    prefix: str,
    num_clips: int = 5,
    max_bytes: int = 3 * 1024 * 1024,
) -> list[Path]:
    data = src.read_bytes()
    frames = list(iter_frames(data))
    if len(frames) < num_clips * 20:
        raise RuntimeError(f"Too few frames in {src.name}: {len(frames)}")

    chunk = len(frames) // num_clips
    out_dir.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []

    for c in range(num_clips):
        start_f = c * chunk
        total = 0
        end_f = start_f
        while end_f < len(frames) and total < max_bytes:
            total += frames[end_f][1]
            end_f += 1
        start_off = frames[start_f][0]
        last_off, last_len = frames[end_f - 1]
        end_off = last_off + last_len
        clip = data[start_off:end_off]
        out = out_dir / f"{prefix}_{c + 1:02d}.mp3"
        out.write_bytes(clip)
        out_paths.append(out)
        print(f"  wrote {out.name} ({len(clip) / 1024 / 1024:.2f} MB)")
    return out_paths


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    full_dir = root / "public" / "audio_full_local"
    out_dir = root / "public" / "audio"
    for old in out_dir.glob("su_liu_niang_*.mp3"):
        old.unlink()
    for old in out_dir.glob("gao_qin_fu_*.mp3"):
        old.unlink()
    for old in ("opera_su_liu_niang.mp3", "opera_gao_qin_fu.mp3"):
        p = out_dir / old
        if p.exists():
            p.unlink()

    jobs = [
        ("opera_su_liu_niang.mp3", "su_liu_niang", 5),
        ("opera_gao_qin_fu.mp3", "gao_qin_fu", 5),
    ]
    for src_name, prefix, n in jobs:
        src = full_dir / src_name
        if not src.exists():
            print("missing", src)
            continue
        print("splitting", src.name)
        split_mp3(src, out_dir, prefix, n)


if __name__ == "__main__":
    main()
