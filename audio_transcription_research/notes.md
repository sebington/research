# Research Notes - Audio Transcription with Speaker Diarization on CPU

## Goal
Find the best SOTA audio transcription + speaker diarization pipeline for:
- Ubuntu Linux
- CPU-only
- 32GB RAM
- Python / uv

## Potential Candidates
1. **WhisperX**: Transcription, alignment, and diarization. Known for high accuracy and good timestamps.
2. **faster-whisper + pyannote-audio**: Use faster-whisper (CTranslate2) for speed on CPU and pyannote for diarization.
3. **insanely-fast-whisper**: Uses Transformers library, optimized for speed.
4. **Stable-ts**: Focuses on reliable timestamps, can be combined with diarization.

## Findings
### WhisperX
- Features: Diarization (pyannote), Word-level timestamps, Voice Activity Detection (VAD).
- Pros: Excellent alignment.
- Cons: Dependencies can be heavy. Might be slow on CPU if not optimized.

### faster-whisper
- Pros: Up to 4x faster than vanilla Whisper on CPU. Uses less memory.
- Cons: Requires manual integration with a diarization model like pyannote.

### pyannote.audio
- SOTA for diarization.
- Version 3.1 is latest.
- Requires Hugging Face token and accepting user terms for certain models (segmentation and speaker-diarization).

## Infrastructure
- Using `uv` for dependency management is highly recommended for speed and reproducibility.

### Whisper Large-v3-Turbo
- Released by OpenAI in late 2024.
- 4 decoder layers instead of 32.
- 5x-8x faster than large-v3 with minimal accuracy loss.
- Ideal for CPU-only environments.
- Supported by `faster-whisper` and consequently can be used in `WhisperX`.

## SOTA Components Detailed Dive
### Transcription (ASR)
- **Model**: `openai/whisper-large-v3-turbo`
- **Why**: Best balance of speed and accuracy in 2025. Pruned version of large-v3 (4 layers vs 32).
- **CPU Optimization**: Use `faster-whisper` implementation with `int8` quantization.

### Diarization
- **Model**: `pyannote/speaker-diarization-3.1`
- **Why**: Industry standard for open-source diarization. Significant improvements in 3.x over 2.x.
- **Requirements**: Needs Hugging Face token and user agreement for `pyannote/segmentation-3.0` and `pyannote/speaker-diarization-3.1`.

### Pipeline & Alignment
- **Tool**: `WhisperX`
- **Why**: Handles the complex task of aligning Whisper transcripts with Pyannote diarization segments using word-level timestamps (via phoneme alignment).
- **Recent Status**: Active (last commit 2 weeks ago), widely used in the community.

### Performance on CPU (32GB RAM)
- **RAM**: Entire pipeline fits comfortably in ~5-6GB RAM. 32GB allows for multi-processing if needed.
- **Speed**: Large-v3-turbo on CPU is typically 5x-10x faster than real-time (depending on CPU core count).

## CPU Optimizations
- **Quantization**: `int8` is the gold standard for CPU. It reduces model size and memory bandwidth requirements while maintaining most of the accuracy.
- **Threading**:
  - `faster-whisper` allows setting `cpu_threads`. Optimal value is usually around the number of physical cores.
  - `OMP_NUM_THREADS` and `MKL_NUM_THREADS` can be tuned for `torch` and `numpy` performance.
- **Model Choice**: `large-v3-turbo` is a "structural" optimization (pruning) that yields more speedup than quantization alone on CPU.
- **Batching**: While batching is huge on GPU, on CPU it can sometimes help but might also increase latency. `WhisperX` supports batched inference.
