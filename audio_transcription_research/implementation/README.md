# Reference Implementation: SOTA Audio Transcription & Diarization (CPU)

This directory contains a sample implementation of a state-of-the-art transcription and diarization pipeline optimized for CPU-only environments.

## Stack
- **Engine**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (via [WhisperX](https://github.com/m-bain/whisperX))
- **Model**: `large-v3-turbo` (OpenAI)
- **Diarization**: `pyannote/speaker-diarization-3.1`
- **Runtime**: Python 3.12+ / `uv`

## Setup

1. **Prerequisites**:
   - Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Obtain a Hugging Face token: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Accept terms for the following models on Hugging Face:
     - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
     - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

2. **Installation**:
   ```bash
   uv sync
   ```

3. **Running**:
   Place an audio file (e.g., `sample.wav`) in this directory and run:
   ```bash
   export HF_TOKEN="your_token_here"
   uv run python transcribe.py
   ```

## Optimizations Used
- **int8 Quantization**: Reduces memory usage and increases CPU throughput.
- **Large-v3-Turbo**: Uses a pruned Whisper model (4 decoder layers) for ~5x speedup over standard Large-v3.
- **WhisperX Alignment**: Ensures word-level precision for speaker assignment.
