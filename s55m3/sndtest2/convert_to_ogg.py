"""
WAV to OGG Batch Converter
Place this script in the root folder containing your subfolders with WAV files.
Requires ffmpeg installed and in PATH.

Converts all .wav files to .ogg (Vorbis) with quality optimization.
Removes original .wav files after successful conversion.
"""

import os
import subprocess
import sys

# OGG quality: -1 to 10 (0 = ~64kbps, 3 = ~112kbps, 5 = ~160kbps, 6 = ~192kbps)
# For game audio samples, quality 4-5 is usually good enough
OGG_QUALITY = 5

# Sample rate: None = keep original, or set e.g. 44100, 22050
# Lower sample rate = smaller files. 44100 is CD quality, 22050 is fine for engine sounds
SAMPLE_RATE = 44100

# Mono conversion: True = force mono (halves file size), False = keep channels
FORCE_MONO = True

# Delete original WAV after successful conversion
DELETE_ORIGINAL = True


def find_wavs(root):
    """Find all .wav files recursively"""
    wavs = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.lower().endswith('.wav'):
                wavs.append(os.path.join(dirpath, f))
    wavs.sort()
    return wavs


def get_file_size(path):
    try:
        return os.path.getsize(path)
    except:
        return 0


def human_size(nbytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def convert_wav_to_ogg(wav_path, ogg_path):
    """Convert a single WAV to OGG using ffmpeg"""
    cmd = ['ffmpeg', '-y', '-i', wav_path]

    # audio codec
    cmd += ['-c:a', 'libvorbis']

    # quality
    cmd += ['-q:a', str(OGG_QUALITY)]

    # sample rate
    if SAMPLE_RATE:
        cmd += ['-ar', str(SAMPLE_RATE)]

    # mono
    if FORCE_MONO:
        cmd += ['-ac', '1']

    # no video
    cmd += ['-vn']

    cmd.append(ogg_path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("  WAV -> OGG Batch Converter")
    print("=" * 60)
    print()

    if not check_ffmpeg():
        print("ERROR: ffmpeg not found in PATH!")
        print("Install ffmpeg: https://ffmpeg.org/download.html")
        print("  Windows: winget install ffmpeg")
        print("  Or download and add to PATH")
        sys.exit(1)

    print(f"Scanning: {script_dir}")
    print(f"Settings:")
    print(f"  Quality:    {OGG_QUALITY} (vorbis -1 to 10)")
    print(f"  SampleRate: {SAMPLE_RATE or 'keep original'}")
    print(f"  Mono:       {FORCE_MONO}")
    print(f"  Delete WAV: {DELETE_ORIGINAL}")
    print()

    wavs = find_wavs(script_dir)

    if not wavs:
        print("No .wav files found!")
        sys.exit(0)

    total_size = 0
    print(f"Found {len(wavs)} WAV files:")
    print("-" * 60)
    for w in wavs:
        rel = os.path.relpath(w, script_dir)
        sz = get_file_size(w)
        total_size += sz
        print(f"  {rel:50s} {human_size(sz):>10s}")

    print("-" * 60)
    print(f"  Total: {len(wavs)} files, {human_size(total_size)}")
    print()

    input("Press ENTER to begin conversion (Ctrl+C to cancel)...")
    print()

    converted = 0
    failed = 0
    total_before = 0
    total_after = 0

    for i, wav_path in enumerate(wavs):
        rel = os.path.relpath(wav_path, script_dir)
        ogg_path = os.path.splitext(wav_path)[0] + '.ogg'

        sz_before = get_file_size(wav_path)
        total_before += sz_before

        print(f"[{i+1}/{len(wavs)}] {rel}...", end=" ", flush=True)

        ok = convert_wav_to_ogg(wav_path, ogg_path)

        if ok and os.path.exists(ogg_path):
            sz_after = get_file_size(ogg_path)
            total_after += sz_after
            ratio = (1 - sz_after / sz_before) * 100 if sz_before > 0 else 0
            print(f"OK ({human_size(sz_before)} -> {human_size(sz_after)}, -{ratio:.0f}%)")
            converted += 1

            if DELETE_ORIGINAL:
                os.remove(wav_path)
        else:
            print("FAILED")
            failed += 1

    print()
    print("=" * 60)
    print(f"  Converted: {converted}/{len(wavs)}")
    if failed > 0:
        print(f"  Failed:    {failed}")
    print(f"  Size:      {human_size(total_before)} -> {human_size(total_after)} (-{(1 - total_after/total_before)*100:.0f}%)")
    if DELETE_ORIGINAL:
        print(f"  Original WAVs deleted")
    print("=" * 60)


if __name__ == '__main__':
    main()
