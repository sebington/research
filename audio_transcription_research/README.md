# State-of-the-Art Audio Transcription & Diarization on CPU

This report outlines the "Best Way" to achieve state-of-the-art (SOTA) audio transcription with speaker diarization on a CPU-only Ubuntu Linux system with 32GB RAM.

## Executive Summary

For a CPU-only environment, the optimal SOTA pipeline in 2025 is:
- **ASR Model**: `openai/whisper-large-v3-turbo`
- **Diarization Model**: `pyannote/speaker-diarization-3.1`
- **Engine**: `faster-whisper` (CTranslate2) with `int8` quantization.
- **Pipeline Orchestrator**: `WhisperX` (for word-level alignment and diarization merging).

This stack provides high accuracy, handles multiple speakers effectively, and is optimized for CPU throughput and memory efficiency.

---

## 1. Components & Rationales

### A. Transcription: OpenAI Whisper Large-v3-Turbo
While `large-v3` is the most accurate, `large-v3-turbo` (released late 2024) offers a significant performance boost on CPU.
- **Structure**: 4 decoder layers vs. 32 in the full model.
- **Speed**: ~5x-8x faster than `large-v3` on CPU.
- **Accuracy**: Minimal degradation compared to the full model, still far superior to `medium` or `small`.

### B. Diarization: Pyannote.audio 3.1
Pyannote remains the open-source leader in speaker diarization.
- **Improvements**: Version 3.1 introduced better segmentation and speaker embeddings, significantly reducing Diarization Error Rate (DER) compared to 2.x versions.
- **CPU Performance**: Efficient enough to run in real-time or faster on modern CPUs.

### C. Backend: Faster-Whisper (CTranslate2)
Running the original OpenAI Whisper code on CPU is inefficient.
- **Optimization**: Uses CTranslate2, a fast inference engine for Transformer models.
- **Quantization**: `int8` quantization is recommended. it reduces the model size from ~3GB to ~1.5GB and significantly increases throughput on CPU by using integer arithmetic.

### D. Pipeline: WhisperX
Transcription and Diarization are two separate tasks. The "magic" is in how they are merged.
- **Alignment**: Whisper's native timestamps are coarse (1s). WhisperX uses phoneme-level alignment (via wav2vec2) to get precise word-level timestamps.
- **Merging**: Precise timestamps allow for highly accurate assignment of speaker labels to specific words/segments.

---

## 2. Infrastructure Requirements (32GB RAM)

- **RAM Usage**:
  - Whisper (int8): ~1.5GB
  - Alignment Model: ~300MB
  - Diarization Model: ~500MB
  - **Total**: ~2.5GB - 3GB active RAM.
- **Feasibility**: With 32GB RAM, you have ample headroom. You can even run 4-8 parallel transcription jobs if you have enough CPU cores.

---

## 3. Implementation Guide

A reference implementation is provided in the `implementation/` directory.

### Prerequisites
1. **System**: Ubuntu Linux with `ffmpeg` installed (`sudo apt install ffmpeg`).
2. **Tools**: `uv` for Python package management.
3. **Hugging Face**:
   - Create an account and get a token.
   - Accept the user agreement for [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) and [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1).

### Setup & Run
```bash
cd implementation
uv sync
export HF_TOKEN="your_huggingface_token"
uv run python transcribe.py
```

---

## 4. Troubleshooting & Tips

- **Dependency Versions**: The ecosystem is currently sensitive to `torch` and `torchaudio` versions (specifically 2.6+ changes). The provided `pyproject.toml` pins working versions (`torch==2.5.1`, `whisperx==3.3.1`).
- **Language Detection**: For faster processing, specify the language explicitly if known (`language="en"`).
- **Thread Tuning**: Experiment with `OMP_NUM_THREADS` or the `cpu_threads` parameter in `faster-whisper` to find the sweet spot for your specific CPU.
