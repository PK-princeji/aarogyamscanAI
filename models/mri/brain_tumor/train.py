import io
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# ==========================================
# 1. Server Initialization & Configuration
# ==========================================
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows your JavaScript frontend (React/Next.js) to communicate with this Python API securely.
CORS(app)

# ==========================================
# 2. AI Model Loading & Constants
# ==========================================
print("[INFO] Booting up Aarogyam ScanAI Engine...")
try:
    # Load the pre-trained EfficientNet model into memory.
    # Doing this globally ensures it only loads once when the server starts, not on every request.
    MODEL_PATH = 'Aarogyam_ScanAI_Final.keras'
    model = load_model(MODEL_PATH)
    
    # Define the exact class labels in the alphabetical order used during training.
    CLASS_NAMES = ['Glioma', 'Meningioma', 'No_Tumor', 'Pituitary']
    print("[INFO] Model loaded successfully and is ready for inference.")
except Exception as e:
    print(f"[ERROR] Failed to load the AI model. Ensure the .keras file is in the root directory. Error: {e}")

# Knowledge Base: Medical definitions mapping for rich frontend display
MEDICAL_KNOWLEDGE_BASE = {
    'Glioma': "A glioma is a type of tumor that occurs in the brain and spinal cord, originating from the gluey supportive cells (glial cells).",
    'Meningioma': "A meningioma is a tumor that arises from the meninges — the membranes that surround the brain and spinal cord. They are usually slow-growing.",
    'Pituitary': "Pituitary tumors are abnormal growths that develop in your pituitary gland, a small but vital gland located at the base of the brain.",
    'No_Tumor': "The MRI scan appears clear. No abnormal tumor growths or lesions were detected in this analysis."
}

# ==========================================
# 3. The API Endpoint (The "Bridge")
# ==========================================
@app.route('/api/v1/predict', methods=['POST'])
def predict_tumor():
    """
    Handles POST requests containing an MRI image.
    Validates the image, preprocesses it, runs it through the AI model, 
    and returns a rich JSON response with the diagnosis and an encoded thumbnail.
    """
    try:
        # --- Stage 1: Request Validation ---
        # Ensure the user actually attached a file with the key 'file'
        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({
                'success': False, 
                'error': 'Bad Request: No file attached. Please upload a valid MRI image.'
            }), 400
        
        uploaded_file = request.files['file']
        file_bytes = uploaded_file.read()
        
        # --- Stage 2: Image Preprocessing ---
        # The AI model strictly requires images to be exactly 224x224 pixels.
        # We load the image from memory (io.BytesIO) to avoid saving it to the hard drive.
        img = image.load_img(io.BytesIO(file_bytes), target_size=(224, 224))
        
        # Convert the visual image into a mathematical matrix (3D Array)
        img_array = image.img_to_array(img)
        
        # Add a batch dimension -> changes shape from (224, 224, 3) to (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # --- Stage 3: AI Inference (Prediction) ---
        predictions = model.predict(img_array)
        
        # Extract the highest probability score and its corresponding index
        max_confidence = float(np.max(predictions) * 100)
        predicted_index = np.argmax(predictions)
        
        # --- Stage 4: The "Bouncer" Threshold (Data Integrity Check) ---
        # If the model is less than 60% confident, the user likely uploaded a selfie, 
        # a landscape, or a completely unrelated image.
        if max_confidence < 60.0:
            return jsonify({
                'success': False, 
                'error': f'Image Recognition Failure (Confidence: {max_confidence:.2f}%). The uploaded image does not appear to be a valid Brain MRI scan.'
            }), 400
            
        # --- Stage 5: Response Formatting ---
        predicted_class = CLASS_NAMES[predicted_index]
        tumor_description = MEDICAL_KNOWLEDGE_BASE.get(predicted_class, "Medical details currently unavailable.")
        
        # Encode the original image to Base64 so it can be transmitted via JSON
        # This allows the frontend to immediately render the exact image that was analyzed.
        encoded_image_string = base64.b64encode(file_bytes).decode('utf-8')
        base64_image_url = f"data:image/jpeg;base64,{encoded_image_string}"
        
        # Send the successful payload back to the JavaScript client
        return jsonify({
            'success': True,
            'data': {
                'diagnosis': predicted_class,
                'confidence_percentage': round(max_confidence, 2),
                'medical_description': tumor_description,
                'thumbnail_base64': base64_image_url
            }
        }), 200

    except Exception as e:
        # Catch any unexpected server errors (e.g., corrupted image file)
        print(f"[ERROR] Exception during prediction: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Internal Server Error: Something went wrong while processing the image.'
        }), 500

# ==========================================
# 4. Server Execution
# ==========================================
if __name__ == '__main__':
    # Run the Flask development server on port 5000
    print("[INFO] Starting server on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)