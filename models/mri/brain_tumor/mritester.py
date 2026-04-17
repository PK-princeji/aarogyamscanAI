import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models

# आपके मॉडल्स के पाथ
MODELS = [
    r"D:\final_year_project\code_X_Elite\aarogyamScanAi\models\mri\brain_tumor\model_path\Aarogyam_ScanAI_Final.keras",
    r"D:\final_year_project\code_X_Elite\aarogyamScanAi\models\mri\brain_tumor\Aarogyam_ScanAI_Final.keras",
    r"D:\final_year_project\code_X_Elite\aarogyamScanAi\models\mri\Aarogyam_ScanAI_FinalCT_SCAN.keras"
]

IMAGE_PATH = r"D:\Window_C\Downloads\rahuylmind.jpeg"
class_names = ['Glioma', 'Meningioma', 'No_Tumor', 'Pituitary']

def build_architecture():
    """वही ढांचा बनाना जो आपके ट्रेनिंग कोड में था"""
    base_model = EfficientNetB0(input_shape=(224, 224, 3), include_top=False, weights=None)
    model = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(4, activation='softmax')
    ])
    return model

def test_model_v3(model_path):
    print(f"\n🔍 Testing Model: {os.path.basename(model_path)}")
    if not os.path.exists(model_path):
        print("❌ File Not Found!")
        return

    try:
        # 1. पहले सिंपल लोड ट्राई करें
        print("⏳ Attempt 1: Standard loading...")
        model = load_model(model_path, compile=False)
    except Exception:
        try:
            # 2. अगर फेल हुआ, तो ढांचा बनाकर सिर्फ़ वेट्स लोड करें
            print("🔄 Attempt 1 failed. Attempt 2: Loading weights into architecture...")
            model = build_architecture()
            model.load_weights(model_path)
        except Exception as e:
            print(f"❌ All attempts failed for this model. Error: {str(e)[:100]}")
            return

    # प्रेडिक्शन पार्ट
    try:
        img = image.load_img(IMAGE_PATH, target_size=(224, 224), color_mode="rgb")
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        preds = model.predict(img_array, verbose=0)[0]
        idx = np.argmax(preds)
        
        print(f"✅ SUCCESS! Result: {class_names[idx]} ({preds[idx]*100:.2f}%)")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")

def run():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    print("\n🚀 AAROGYAM ScanAI: The Final MRI Model Rescue")
    print("-" * 50)
    for path in MODELS:
        test_model_v3(path)

if __name__ == "__main__":
    run()