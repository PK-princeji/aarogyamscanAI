
import tensorflow as tf
import numpy as np
import os

class XrayMaster:
    def __init__(self):
        # यहाँ हम अलग-अलग मॉडल्स लोड करेंगे
        self.models = {}
        base_path = os.path.dirname(__file__)
        
        # Pneumonia Model Load
        p_path = os.path.join(base_path, "pneumonia", "pneumonia_model.h5")
        if os.path.exists(p_path):
            self.models['pneumonia'] = tf.keras.models.load_model(p_path)
            
        # TB Model Load
        t_path = os.path.join(base_path, "tuberculosis", "tb_model.h5")
        if os.path.exists(t_path):
            self.models['tuberculosis'] = tf.keras.models.load_model(t_path)

    def predict(self, img_array):
        results = {}
        # हर मॉडल से पूछो कि उसे क्या लगता है
        for disease, model in self.models.items():
            pred = model.predict(img_array)[0][0] # Binary output assumed
            results[disease] = float(pred)
            
        return results # Output: {'pneumonia': 0.98, 'tb': 0.02}
