# Responsibility: Extract audio from video files and analyze audio quality

import logging
import math
import shutil
import struct
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_audio(video_path: str, audio_path: str) -> None:
    """
    Extract mono 16 kHz WAV audio from a video file.
    Raises RuntimeError if ffmpeg is missing or extraction fails.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed or not on PATH")

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path,
        "-y",
    ]
    logger.info("Extracting audio: video=%s", video_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg failed: %s", result.stderr[-500:])
        raise RuntimeError("Failed to extract audio from video")

    if not Path(audio_path).exists() or Path(audio_path).stat().st_size == 0:
        raise RuntimeError("Extracted audio file is empty")

    logger.info("Audio extracted: path=%s", audio_path)


def analyze_audio_quality(audio_path: str) -> dict:
    """
    Analyze audio quality from a WAV file: volume, silence ratio, dynamic range.
    Returns metrics useful for coaching feedback.
    """
    try:
        with open(audio_path, "rb") as f:
            header = f.read(44)
            if len(header) < 44:
                return _default_audio_quality("Audio file too small to analyze")

            num_channels = struct.unpack_from("<H", header, 22)[0]
            sample_rate = struct.unpack_from("<I", header, 24)[0]
            bits_per_sample = struct.unpack_from("<H", header, 34)[0]
            data_size = struct.unpack_from("<I", header, 40)[0]

            bytes_per_sample = bits_per_sample // 8
            total_samples = data_size // (bytes_per_sample * max(num_channels, 1))
            duration_s = total_samples / sample_rate if sample_rate > 0 else 0

            raw = f.read()
            if bits_per_sample == 16:
                fmt = f"<{len(raw) // 2}h"
                samples = struct.unpack(fmt, raw[:len(raw) - (len(raw) % 2)])
            else:
                return _default_audio_quality("Unsupported bit depth")

        if not samples:
            return _default_audio_quality("No audio samples found")

        rms_sum = sum(s * s for s in samples)
        rms = math.sqrt(rms_sum / len(samples))
        max_val = 32768.0
        avg_volume_db = 20 * math.log10(max(rms / max_val, 1e-10))

        threshold = int(rms * 0.15)
        silent_samples = sum(1 for s in samples if abs(s) < threshold)
        silence_ratio = round(silent_samples / len(samples) * 100, 1)

        chunk_size = sample_rate
        chunks = [samples[i:i+chunk_size] for i in range(0, len(samples), chunk_size)]
        chunk_rms = []
        for chunk in chunks:
            if chunk:
                cr = math.sqrt(sum(s * s for s in chunk) / len(chunk))
                chunk_rms.append(cr)

        dynamic_range = 0
        if chunk_rms:
            max_rms = max(chunk_rms)
            min_rms = min(c for c in chunk_rms if c > 0) if any(c > 0 for c in chunk_rms) else 1
            dynamic_range = round(20 * math.log10(max_rms / max(min_rms, 1e-10)), 1)

        speaking_segments = 0
        in_speech = False
        for chunk_r in chunk_rms:
            if chunk_r > threshold and not in_speech:
                speaking_segments += 1
                in_speech = True
            elif chunk_r <= threshold:
                in_speech = False

        pace_assessment = "optimal"
        if duration_s > 0:
            words_per_minute = 0
            pace_assessment = "optimal"

        volume_assessment = "good"
        if avg_volume_db < -35:
            volume_assessment = "too quiet"
        elif avg_volume_db > -10:
            volume_assessment = "too loud"
        elif avg_volume_db < -25:
            volume_assessment = "slightly quiet"
        elif avg_volume_db > -15:
            volume_assessment = "slightly loud"

        silence_assessment = "good"
        if silence_ratio > 60:
            silence_assessment = "excessive silence"
        elif silence_ratio > 40:
            silence_assessment = "noticeable pauses"
        elif silence_ratio < 10:
            silence_assessment = "very few pauses — consider adding breathing moments"

        notes_parts = [f"Volume: {volume_assessment} ({avg_volume_db:.1f} dB)"]
        notes_parts.append(f"Silence ratio: {silence_ratio}% — {silence_assessment}")
        if dynamic_range > 20:
            notes_parts.append("good vocal variety")
        elif dynamic_range > 10:
            notes_parts.append("moderate vocal range")
        else:
            notes_parts.append("limited vocal variety — try varying your tone more")

        logger.info(
            "Audio quality: volume=%.1f dB silence=%.1f%% dynamic=%.1f dB duration=%.1fs",
            avg_volume_db, silence_ratio, dynamic_range, duration_s,
        )
        return {
            "duration_s": round(duration_s, 1),
            "avg_volume_db": round(avg_volume_db, 1),
            "silence_ratio": silence_ratio,
            "dynamic_range_db": dynamic_range,
            "volume_assessment": volume_assessment,
            "silence_assessment": silence_assessment,
            "sample_rate": sample_rate,
            "notes": ". ".join(notes_parts) + ".",
        }

    except Exception as e:
        logger.error("Audio quality analysis failed: %s", str(e))
        return _default_audio_quality("Audio quality analysis could not be completed")


def _default_audio_quality(notes: str) -> dict:
    return {
        "duration_s": 0,
        "avg_volume_db": -25,
        "silence_ratio": 30,
        "dynamic_range_db": 15,
        "volume_assessment": "unknown",
        "silence_assessment": "unknown",
        "sample_rate": 16000,
        "notes": notes,
    }
