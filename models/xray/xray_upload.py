import os
from datetime import datetime
from werkzeug.utils import secure_filename

# Example: Dummy prediction & metrics (replace with your ML model code)
def predict_xray(image_path):
    """
    Dummy X-Ray prediction function
    Returns prediction label and metrics
    """
    pred_label = 1  # 1 = Pneumonia, 0 = Normal
    metrics = {"accuracy": 0.95}
    return pred_label, metrics

def generate_comprehensive_report(predictions, metrics, patient_id=None, image_path=None, patient_info=None):
    """
    Generate a comprehensive analysis report for Pneumonia detection.
    """
    report_id = f"XR_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
    report = {
        "report_id": report_id,
        "patient_id": patient_id if patient_id else "Unknown",
        "diagnosis": "Normal" if predictions == 0 else "Pneumonia",
        "probability": float(predictions),
        "confidence": metrics.get("accuracy", 0.0),
        "risk_category": "HIGH" if predictions == 1 else "LOW",
        "recommendation": "Immediate medical attention required" if predictions == 1 else "Routine follow-up",
        "generated_at": datetime.now().isoformat(),
        "images": {"input": image_path},
        "patient_info": patient_info if patient_info else {}
    }
    return report

def save_uploaded_file(file, upload_folder="uploads"):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    filename = secure_filename(file.filename)
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)
    return save_path
