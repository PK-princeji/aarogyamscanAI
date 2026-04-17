from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import os, datetime, random
from werkzeug.utils import secure_filename
from utils.predict_mri import predict_mri

mri_bp = Blueprint('mri', __name__)

@mri_bp.route('/mri_upload', methods=['GET', 'POST'])
def mri_upload_route():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file: return redirect(request.url)
        
        p_name = request.form.get('name', 'Unknown')
        p_age = request.form.get('age', 'N/A')
        p_gender = request.form.get('gender', 'N/A')
        p_address = request.form.get('address', 'N/A')
        
        filename = secure_filename(file.filename)
        path = os.path.join('static/uploads/mri', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file.save(path)
        
        result = predict_mri(path)
        if result:
            report_id = f"MRI_{random.randint(1000, 9999)}"
            gen_at = datetime.datetime.now().strftime("%d-%b-%Y %I:%M %p")
            
            report_data = {
                'report_id': report_id, 'generated_at': gen_at,
                'ai_version': 'NeuroEngine v4.0',
                'patient_info': {'name': p_name, 'age': p_age, 'gender': p_gender, 'address': p_address},
                'analysis': {'label': result['diagnosis'], 'probability': result['confidence']},
                'images': {'input': path}
            }
            session['last_report'] = report_data
            session['last_result'] = result
            return render_template('xray_report.html', report=report_data, result=result, **report_data['patient_info'], report_id=report_id, generated_at=gen_at, img_path=path)
            
    return render_template('mri_upload.html')
