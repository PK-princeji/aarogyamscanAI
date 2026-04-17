from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_from_directory, jsonify
import os
import datetime
import random
from werkzeug.utils import secure_filename
from utils.predict_xray import predict_xray

xray_bp = Blueprint('xray', __name__)

# Upload and Predict Route
@xray_bp.route('/xray_upload', methods=['GET', 'POST'])
def xray_upload_route():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file uploaded", "error")
            return redirect(request.url)
            
        p_name = request.form.get('name', 'N/A')
        p_age = request.form.get('age', 'N/A')
        p_gender = request.form.get('gender', 'N/A')
        p_address = request.form.get('address', 'N/A')
        
        filename = secure_filename(file.filename)
        upload_path = os.path.join('static/uploads/xray', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        
        result = predict_xray(upload_path)
        
        if result:
            report_id = f"XR_{random.randint(100000, 999999)}"
            generated_at = datetime.datetime.now().strftime("%d-%b-%Y %I:%M %p")
            
            # डमी डेटा रिपोर्ट ऑब्जेक्ट (HTML के लिए)
            report_data = {
                'report_id': report_id,
                'generated_at': generated_at,
                'ai_version': 'AarogyamScanAI v2.0',
                'patient_info': {'name': p_name, 'age': p_age, 'gender': p_gender, 'address': p_address},
                'analysis': {'label': result['diagnosis'], 'probability': result['confidence'], 'confidence': result['confidence']},
                'images': {'input': upload_path}
            }
            
            # नोट: session में डेटा सेव कर रहे हैं ताकि रिपोर्ट पेज देख सके
            session['last_report'] = report_data
            session['last_result'] = result
            
            return render_template('xray_report.html', 
                                 report=report_data, 
                                 result=result,
                                 p_name=p_name, p_age=p_age, 
                                 p_gender=p_gender, p_address=p_address,
                                 report_id=report_id,
                                 generated_at=generated_at,
                                 img_path=upload_path)
        else:
            flash("AI analysis failed", "error")
            
    return render_template('xray_upload.html')

# app.py की डिमांड के हिसाब से missing functions:
@xray_bp.route('/xray_report/<report_id>')
def xray_report_view(report_id):
    report = session.get('last_report')
    result = session.get('last_result')
    if report:
        return render_template('xray_report.html', report=report, result=result)
    flash("Report not found", "error")
    return redirect(url_for('xray.xray_upload_route'))

@xray_bp.route('/download_report/<report_id>')
def download_report(report_id):
    # यह सिर्फ इमेज सर्व करने के लिए है
    report = session.get('last_report')
    if report and report['images']['input']:
        return send_from_directory(os.path.dirname(report['images']['input']), 
                                 os.path.basename(report['images']['input']))
    return "File not found", 404

@xray_bp.route('/download_json/<report_id>')
def download_json(report_id):
    report = session.get('last_report')
    if report:
        return jsonify(report)
    return jsonify({"error": "Report not found"}), 404
