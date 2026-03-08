import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load global model
model_path = r"D:/final_year_project/code_X_Elite/aarogyamScanAi/models/AarogyamScanAI_xray_final.h5"
# model_path = r"D:/final_year_project/code_X_Elite/aarogyamScanAi/models/xray/AarogyamScanAI_xray_1.1.h5"
model = load_model(model_path)

def predict_xray(img_path):
    """
    Takes image path, preprocesses, and returns prediction probability (float).
    """
    img = image.load_img(img_path, target_size=(224, 224), color_mode="rgb")  # RGB for model
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    preds = model.predict(img_array) # binary classification probability
    return float(preds)  # only probability
