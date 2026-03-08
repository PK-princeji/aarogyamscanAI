
import cv2
import numpy as np

def preprocess_xray(image_path, size=224):
    # X-ray के लिए स्पेशल कंट्रास्ट (CLAHE)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img = clahe.apply(img)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = cv2.resize(img, (size, size))
    return img / 255.0
