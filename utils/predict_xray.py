import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.keras.preprocessing import image
import tensorflow.keras.backend as K

def weighted_bce(y_true, y_pred):
    return K.mean(y_pred)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models", "xray")
CONFIG_PATH = os.path.join(MODEL_DIR, "config.json")
WEIGHTS_PATH = os.path.join(MODEL_DIR, "model.weights.h5")
METADATA_PATH = os.path.join(MODEL_DIR, "metadata.json")

model = None
class_labels = ['Normal', 'Pneumonia', 'Tuberculosis']

def load_model_init():
    global model, class_labels
    try:
        if os.path.exists(CONFIG_PATH) and os.path.exists(WEIGHTS_PATH):
            with open(CONFIG_PATH, 'r') as f:
                model = model_from_json(f.read(), custom_objects={'weighted_bce': weighted_bce})
            model.load_weights(WEIGHTS_PATH)
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, 'r') as f:
                    meta = json.load(f)
                    class_labels = meta.get('labels', class_labels)
            return True
    except Exception as e:
        print(f"Error loading model: {e}")
    return False

load_model_init()

def predict_xray(img_path):
    if model is None: return None
    
    try:
        input_shape = model.input_shape[1:3]
        if input_shape == (None, None): input_shape = (224, 224)
        
        img = image.load_img(img_path, target_size=input_shape)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        preds = model.predict(img_array)[0]
        
        # पूरी रिपोर्ट का डेटा तैयार करना
        report_details = []
        for i, label in enumerate(class_labels):
            report_details.append({
                'disease': label,
                'probability': float(preds[i]),
                'confidence': f"{preds[i]*100:.2f}%"
            })
            
        idx = np.argmax(preds)
        final_diagnosis = class_labels[idx]
        final_confidence = f"{preds[idx]*100:.2f}%"
        
        return {
            'diagnosis': final_diagnosis,
            'confidence': final_confidence,
            'all_predictions': report_details
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return None
