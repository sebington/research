import whisperx
import gc
import os
import torch

def transcribe_with_diarization(audio_file, hf_token, device="cpu", compute_type="int8"):
    """
    Transcribes audio and performs speaker diarization using WhisperX.

    Optimized for CPU usage with int8 quantization and Large-v3-Turbo model.
    """
    print(f"Loading model: large-v3-turbo on {device} with {compute_type}...")
    # 1. Transcribe with WhisperX
    model = whisperx.load_model("large-v3-turbo", device, compute_type=compute_type)

    print(f"Loading audio: {audio_file}")
    audio = whisperx.load_audio(audio_file)

    print("Step 1: Transcribing...")
    # Batch size can be adjusted; on CPU 1-4 is usually sufficient,
    # but WhisperX handles batching internally.
    result = model.transcribe(audio, batch_size=4)

    # Delete model to free memory for alignment if needed (32GB is plenty though)
    # gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    print(f"Step 2: Aligning for language: {result['language']}")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    # 3. Diarize
    print("Step 3: Diarizing...")
    # Note: Requires HF_TOKEN with access to pyannote/speaker-diarization-3.1
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
    diarize_segments = diarize_model(audio)

    # 4. Assign speaker labels to transcription segments
    print("Step 4: Assigning speakers...")
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return result

if __name__ == "__main__":
    # Example usage
    AUDIO_PATH = "sample.wav"
    # Get HF Token from environment variable for security
    HF_TOKEN = os.getenv("HF_TOKEN")

    if not HF_TOKEN:
        print("Warning: HF_TOKEN environment variable not set. Diarization will fail if using restricted models.")

    if not os.path.exists(AUDIO_PATH):
        print(f"Note: Audio file not found at {AUDIO_PATH}. Please provide a valid wav/mp3 file.")
    else:
        try:
            output = transcribe_with_diarization(AUDIO_PATH, HF_TOKEN)
            print("\n--- Final Transcript ---\n")
            for segment in output["segments"]:
                speaker = segment.get('speaker', 'Unknown')
                print(f"[{segment['start']:05.2f} - {segment['end']:05.2f}] {speaker}: {segment['text'].strip()}")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            if "401" in str(e):
                print("Hint: Check your Hugging Face token and ensure you have accepted the terms for Pyannote models.")
