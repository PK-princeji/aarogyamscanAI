
import sys
import os
# Global Utils को इंपोर्ट करने का जादुई कोड
sys.path.append(os.path.abspath("../../../")) 

from global_utils.universal_trainer import train_engine

# --- SETTINGS ---
# ऑटोमैटिक फोल्डर नाम डिटेक्ट करना
DISEASE_NAME = os.path.basename(os.path.dirname(__file__)) 
MODALITY = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

# डेटासेट पाथ सेट करना
DATA_DIR = f"../../../../dataset/{MODALITY}/{DISEASE_NAME}"
SAVE_PATH = f"{DISEASE_NAME}_model.h5"

if __name__ == "__main__":
    print(f"🏥 Training {MODALITY.upper()} - {DISEASE_NAME.upper()}")
    train_engine(DATA_DIR, SAVE_PATH)
