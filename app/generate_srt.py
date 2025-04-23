import whisper
import os
import sys
import torch


def transcribe_to_srt(video_path):
    if not os.path.isfile(video_path):
        print(f"File tidak ditemukan: {video_path}")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔥 Running on: {device.upper()}")

    print("🚀 Memuat model Whisper...")
    model = whisper.load_model(
        "small", device=device
    )  # Bisa ganti "tiny", "base", "medium", "large"

    print(f"🎬 Memproses video: {video_path}")
    result = model.transcribe(video_path, task="transcribe", verbose=False)

    srt_path = os.path.splitext(video_path)[0] + ".srt"
    print(f"📝 Menulis hasil ke: {srt_path}")

    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"], start=1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()

            srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print("✅ Berhasil! Subtitle telah dibuat.")


def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_srt.py <video_file>")
        sys.exit(1)

    video_path = sys.argv[1]
    transcribe_to_srt(video_path)
