
import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.densenet import preprocess_input

class HealthMaster:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(__file__)) # Project Root
        self.models = {}

    def _get_path(self, modality, disease):
        # Path logic: models/xray/pneumonia/pneumonia_model.h5
        return os.path.join(self.base_path, 'models', modality, disease, f'{disease}_model.h5')

    def predict(self, img_path, modality, disease):
        # 1. मॉडल लोड करें (Lazy Loading)
        model_key = f"{modality}_{disease}"
        
        if model_key not in self.models:
            model_path = self._get_path(modality, disease)
            if os.path.exists(model_path):
                print(f"⏳ Loading Model: {model_key}...")
                self.models[model_key] = tf.keras.models.load_model(model_path)
            else:
                return {"error": f"Model file not found for {disease} at {model_path}"}

        # 2. इमेज प्रोसेस करें
        try:
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array) # DenseNet Logic
        except:
            return {"error": "Image processing failed"}

        # 3. रिजल्ट
        model = self.models[model_key]
        preds = model.predict(img_array)
        score = np.max(preds)
        class_idx = np.argmax(preds)
        
        # रिजल्ट वापस करें
        return {
            "disease": disease,
            "class_index": int(class_idx),
            "confidence": float(round(score * 100, 2)),
            "raw_output": preds.tolist()
        }
