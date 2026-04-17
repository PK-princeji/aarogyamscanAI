import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# --- 📁 MODEL LOADING ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'mri', 'Aarogyam_ScanAI_Finalmri_SCAN.keras')

model = None
if os.path.exists(MODEL_PATH):
    try:
        # compile=False ताकि optimizer का लफड़ा न हो
        model = load_model(MODEL_PATH, compile=False)
        print("✅ MRI MODEL LOADED SUCCESSFULLY (Shape Fixed Mode)")
    except Exception as e:
        print(f"❌ ERROR LOADING MRI MODEL: {e}")
else:
    print(f"❌ FATAL ERROR: MRI Model not found at {MODEL_PATH}")

def predict_mri(img_path):
    global model
    if model is None:
        print("❌ PREDICTION ABORTED: Model not loaded.")
        return None
        
    try:
        # 🚨 FIX 1: color_mode='rgb' ताकि 1 के बजाय 3 चैनल मिलें
        # 🚨 FIX 2: target_size=(224, 224) ताकि मॉडल को वही मिले जो उसे चाहिए
        img = image.load_img(img_path, target_size=(224, 224), color_mode='rgb') 
        
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Normalization (0-1 के बीच लाना)
        img_array = img_array / 255.0
        
        predictions = model.predict(img_array)[0]
        categories = ['Glioma', 'Meningioma', 'No_Tumor', 'Pituitary']
        
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