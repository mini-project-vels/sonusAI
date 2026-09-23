import os
import sys
import logging
import torch
import numpy as np
import json
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class DeepfakeDetector:
    def __init__(self, model_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path or settings.DEEPFAKE_MODEL_PATH
        self.model = None
        self.is_loaded = False
        self.expected_length = 64600  # AASIST expects exactly ~4 seconds of 16kHz audio
        self.sample_rate = 16000

    def load_model(self):
        """Loads the AASIST model architecture and weights."""
        if self.is_loaded:
            return

        logger.info("Loading deepfake detection model...")
        logger.info(f"Target Device: {self.device.type.upper()}")

        if not os.path.exists(self.model_path):
            error_msg = (
                f"AASIST model checkpoint not found at: {self.model_path}. "
                "Please download the official pretrained AASIST.pth (from clovaai/aasist) "
                "along with the 'models' architecture python files into the target directory."
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            sys.path.append(os.path.dirname(self.model_path))
            
            try:
                from AASIST import Model # type: ignore
            except ImportError:
                error_msg = (
                    "AASIST architecture files not found. You must place AASIST.py "
                    "(and related files) in the same directory as the checkpoint."
                )
                logger.error(error_msg)
                raise ImportError(error_msg)
                
            config_path = os.path.join(os.path.dirname(self.model_path), "AASIST.conf")
            if not os.path.exists(config_path):
                 # Fallback to known default config if conf wasn't specifically provided
                 config = {
                    "nb_samp": 64600,
                    "first_conv": 128,
                    "filts": [70, [1,32], [32,32], [32,64], [64,64]],
                    "gat_dims": [64,32],
                    "pool_ratios": [0.5,0.7,0.5,0.5],
                    "temperatures": [2.0,2.0,100.0,100.0]
                 }
            else:
                 with open(config_path, "r") as f:
                     config = json.load(f)
                 
            self.model = Model(config)
            checkpoint = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint)
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            
            logger.info("Deepfake detection model loaded successfully.")
            logger.info(f"AASIST model path: {self.model_path}")
            logger.info(f"Checkpoint exists: True")
            logger.info(f"Device: {self.device.type.upper()}")
            logger.info(f"Model loaded: {self.is_loaded}")
            logger.info(f"Expected sample rate: {self.sample_rate}")
            logger.info(f"Expected samples per window: {self.expected_length}")
            
        except Exception as e:
            logger.error(f"Failed to load the deepfake model: {str(e)}")
            raise RuntimeError(f"Deepfake model initialization failed: {str(e)}")

    def extract_features(self, waveform: np.ndarray, sample_rate: int) -> torch.Tensor:
        if sample_rate != self.sample_rate:
            raise ValueError(f"AASIST requires 16kHz audio, got {sample_rate}Hz")
            
        tensor = torch.from_numpy(waveform).float()
        return tensor

    def predict(self, waveform: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """Runs inference with windowed chunking for waveforms longer than expected length."""
        if not self.is_loaded:
            self.load_model()

        tensor_audio = self.extract_features(waveform, sample_rate)
        
        total_samples = tensor_audio.shape[0]
        windows = []
        
        # Follow official truncation / padding behavior:
        # If longer, split into sequential windows to evaluate the whole file
        if total_samples <= self.expected_length:
            pad_len = self.expected_length - total_samples
            # Pad with repeating signal or zeros depending on convention. We'll use zeros.
            padded = torch.nn.functional.pad(tensor_audio, (0, pad_len), mode="constant", value=0)
            windows.append(padded)
        else:
            for start in range(0, total_samples, self.expected_length):
                end = start + self.expected_length
                chunk = tensor_audio[start:end]
                
                if chunk.shape[0] < self.expected_length:
                    pad_len = self.expected_length - chunk.shape[0]
                    chunk = torch.nn.functional.pad(chunk, (0, pad_len), mode="constant", value=0)
                    
                windows.append(chunk)

        batch_tensor = torch.stack(windows).to(self.device)
        
        with torch.no_grad():
            try:
                _, outputs = self.model(batch_tensor)
            except Exception as e:
                logger.error(f"Inference failed: {str(e)}")
                raise RuntimeError(f"Inference run failed: {str(e)}")
                
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            mean_probs = probabilities.mean(dim=0).cpu().numpy()
            
            # Official AASIST Data Utils maps bonafide = 1, spoof = 0.
            # outputs: [spoof, bonafide]
            # Mapping documentation:
            # 0 -> SPOOF/FAKE
            # 1 -> REAL/BONA_FIDE
            fake_prob = float(mean_probs[0])
            real_prob = float(mean_probs[1])
            
        prediction = "REAL" if real_prob > fake_prob else "FAKE"
        
        logger.info(f"Model Inference Complete. Windows={len(windows)}, Real={real_prob:.4f}, Fake={fake_prob:.4f}")

        return {
            "fake_probability": fake_prob,
            "real_probability": real_prob,
            "prediction": prediction,
            "model": "AASIST",
            "metadata": {
                "windows_analyzed": len(windows),
                "inference_device": self.device.type
            }
        }

# Singleton instance to be used by the API
detector = DeepfakeDetector()
