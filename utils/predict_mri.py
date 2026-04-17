import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models

# --- 📁 MODEL PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# आपकी मेन फाइल का पाथ (अगर नाम अलग हो तो यहाँ बदल लेना)
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'mri', 'Aarogyam_ScanAI_Finalmri_SCAN.keras')

model = None

# --- 🏗️ ARCHITECTURE BUILDER ---
def build_architecture():
    """वही ढांचा बनाना जो आपके ट्रेनिंग कोड में था"""
    base_model = EfficientNetB0(input_shape=(224, 224, 3), include_top=False, weights=None)
    m = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(4, activation='softmax')
    ])
    return m

# --- 🚀 ROBUST MODEL LOADING (Your Logic) ---
if os.path.exists(MODEL_PATH):
    try:
        # Attempt 1: Standard Load
        print("⏳ Attempt 1: Standard loading MRI model...")
        model = load_model(MODEL_PATH, compile=False)
        print("✅ MRI MODEL LOADED SUCCESSFULLY (Standard Mode)")
    except Exception as e1:
        print(f"🔄 Attempt 1 failed. Trying Architecture Method...")
        try:
            # Attempt 2: Build Architecture & Load Weights
            model = build_architecture()
            model.load_weights(MODEL_PATH)
            print("✅ MRI MODEL LOADED SUCCESSFULLY (Architecture + Weights Mode)")
        except Exception as e2:
            print(f"❌ ALL LOADING ATTEMPTS FAILED. Error: {e2}")
else:
    print(f"❌ FATAL ERROR: MRI Model not found at -> {MODEL_PATH}")


# --- 🧠 PREDICTION FUNCTION ---
def predict_mri(img_path):
    global model
    if model is None:
        print("❌ PREDICTION ABORTED: The MRI model is not loaded in memory.")
        return None
        
    try:
        # 🚨 Image Processing (Exactly as per your working test script)
        img = image.load_img(img_path, target_size=(224, 224), color_mode="rgb")
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        # Note: EfficientNetB0 natively expects 0-255 inputs, so no need for / 255.0
        
        predictions = model.predict(img_array, verbose=0)[0]
        categories = ['Glioma', 'Meningioma', 'No_Tumor', 'Pituitary']
        
        # Mapping results
        all_preds = []
        for i, prob in enumerate(predictions):
            all_preds.append({
                'disease': categories[i],
                'probability': float(prob),
                'confidence': f"{round(float(prob) * 100, 2)}%"
            })
            
        max_idx = np.argmax(predictions)
        return {
            'diagnosis': categories[max_idx],
            'confidence': f"{round(float(predictions[max_idx]) * 100, 2)}%",
            'all_predictions': all_preds
        }
    except Exception as e:
        print(f"❌ PREDICTION ERROR: {e}")
        return None