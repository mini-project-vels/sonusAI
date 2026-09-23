import os
import sys
import argparse

# Add app to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.audio.preprocessing import process_audio
from app.models.deepfake_detector import detector

def main():
    parser = argparse.ArgumentParser(description="Test AASIST Model")
    parser.add_argument("audio_path", type=str, help="Path to audio file (.wav)")
    args = parser.parse_args()

    if not os.path.exists(args.audio_path):
        print(f"Error: audio file not found at {args.audio_path}")
        sys.exit(1)

    print("================================")
    print("VocaShield AASIST Test")
    print("======================")

    # Load audio bytes
    with open(args.audio_path, 'rb') as f:
        file_bytes = f.read()

    # Preprocessing
    audio_info = process_audio(file_bytes)
    waveform = audio_info["waveform"]
    sample_rate = audio_info["processed_sample_rate"]
    duration = audio_info["duration_seconds"]

    print("\nAudio:")
    print(f"Duration: {duration}s")
    print(f"Sample rate: {sample_rate}Hz")

    # Load model if not loaded
    detector.load_model()

    print("\nModel:")
    print(f"AASIST")
    print(f"Device: {detector.device.type.upper()}")

    # Inference
    result = detector.predict(waveform, sample_rate)

    print("\nRaw model output:")
    print(f"Windows analyzed: {result['metadata']['windows_analyzed']}")
    
    # In DeepfakeDetector we converted to float, so it's clean
    print(f"\nPrediction:\n{result['prediction']}")
    
    print(f"\nReal probability:\n{result['real_probability']:.4f}")
    print(f"Fake probability:\n{result['fake_probability']:.4f}")
    print("================================")

if __name__ == "__main__":
    main()
