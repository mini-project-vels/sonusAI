import os
import json
import logging
import soundfile as sf
import librosa
from datasets import load_dataset
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_audio"))
    gen_dir = os.path.join(target_dir, "genuine")
    df_dir = os.path.join(target_dir, "deepfake")
    
    os.makedirs(gen_dir, exist_ok=True)
    os.makedirs(df_dir, exist_ok=True)
    
    meta_path = os.path.join(target_dir, "metadata.json")
    
    logging.info("Streaming ASVspoof2021_DF dataset...")
    
    try:
        ds = load_dataset("SpeechAntiSpoofingBenchmarks/ASVspoof2021_DF", streaming=True)
    except Exception as e:
        logging.error(f"Failed to load dataset: {e}")
        return
        
    splits = list(ds.keys())
    split_name = splits[0] if "eval" not in splits else "eval"
    
    gen_count = 0
    sub_count = 0 
    
    # Load existing metadata to skip downloads if possible
    metadata = {"dataset": "ASVspoof2021_DF", "samples": []}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                metadata = json.load(f)
            for s in metadata.get("samples", []):
                if s.get("ground_truth") == "GENUINE": gen_count += 1
                if s.get("ground_truth") == "DEEPFAKE": sub_count += 1
            logging.info(f"Found existing downloads: Genuine: {gen_count}, Deepfake: {sub_count}")
            # Reset counts because we want strictly 10 and we don't know which are good.
            gen_count = 0
            sub_count = 0
            metadata = {"dataset": "ASVspoof2021_DF", "samples": []}
        except:
            pass
    
    for item in ds[split_name]:
        if gen_count >= 10 and sub_count >= 10:
            break
            
        label = str(item.get("label", "")).lower()
        
        is_genuine = "bonafide" in label or "genuine" in label
        is_spoof = "spoof" in label or "deepfake" in label
        
        if not is_genuine and not is_spoof:
            continue
            
        if is_genuine and gen_count >= 10:
            continue
        if is_spoof and sub_count >= 10:
            continue
            
        category = "genuine" if is_genuine else "deepfake"
        cat_dir = gen_dir if is_genuine else df_dir
        idx = gen_count + 1 if is_genuine else sub_count + 1
        
        filename = f"{category}_{idx:02d}.wav"
        out_path = os.path.join(cat_dir, filename)
        
        audio_data = item.get("audio", {})
        array = audio_data.get("array")
        sr = audio_data.get("sampling_rate", 16000)
        
        if array is None:
            continue
            
        if sr != 16000:
            array = librosa.resample(array, orig_sr=sr, target_sr=16000)
            
        sf.write(out_path, array, 16000, subtype="PCM_16")
        
        metadata["samples"].append({
            "id": f"{category}_{idx:02d}",
            "filename": filename,
            "category": category,
            "ground_truth": "DEEPFAKE" if is_spoof else "GENUINE",
            "source": "ASVspoof2021_DF"
        })
        
        logging.info(f"Saved {filename}")
        
        if is_genuine:
            gen_count += 1
        else:
            sub_count += 1
            
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    logging.info("-" * 40)
    logging.info("Download Complete!")
    logging.info(f"Genuine: {gen_count}")
    logging.info(f"Deepfake: {sub_count}")
    logging.info(f"Metadata saved to: {meta_path}")

if __name__ == "__main__":
    main()

