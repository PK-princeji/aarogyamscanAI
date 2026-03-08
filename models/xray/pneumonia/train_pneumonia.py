
import sys
import os

# कॉमन कोड इंपोर्ट करने के लिए पाथ सेट करना (Magic Trick) 🪄
sys.path.append(os.path.abspath("../../../")) 

from models.global_utils.trainer import train_engine

# बस पाथ बताओ, बाकी काम कॉमन कोड करेगा
DATASET = r"D:/final_year_project/code_X_Elite/aarogyamScanAi/dataset/xray/pneumonia"
SAVE_PATH = "pneumonia_model.h5"

if __name__ == "__main__":
    print("🚀 Training Pneumonia Model...")
    train_engine(DATASET, SAVE_PATH, epochs=15)
