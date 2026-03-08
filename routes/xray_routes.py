import os
import time
import sqlite3
from datetime import datetime
from flask import request, redirect, url_for, flash, session, render_template, send_file, jsonify, current_app as app
from werkzeug.utils import secure_filename
from utils.predict_xray import predict_xray
from database import get_db  # Using your official database connection

def xray_upload_route():
    if 'email' not in session:
        flash("Authentication required. Please login to upload and analyze scans.", "error")
        return redirect(url_for('login'))
        
    if request.method == "POST":
        patient_name = request.form.get("name")
        patient_age = request.form.get("age")
        patient_gender = request.form.get("gender")
        patient_address = request.form.get("address")
        
        xray_file = request.files.get("xray_image")
        
        if not xray_file or xray_file.filename == '':
            flash("No file detected. Please upload a valid X-Ray image.", "error")
            return redirect(request.url)

        user_email = session['email']
        
        base_upload_dir = os.path.join(app.root_path, "static", "reports", user_email)
        os.makedirs(base_upload_dir, exist_ok=True)
        
        original_filename = secure_filename(xray_file.filename)
        unique_filename = f"XR_{int(time.time())}_{original_filename}"
        
        save_path = os.path.join(base_upload_dir, unique_filename)
        xray_file.save(save_path)

        try:
            prob = predict_xray(save_path)
        except Exception as e:
            print(f"AI Prediction Engine Error: {e}")
            flash("AI Processing failed. Please ensure the image is a valid medical scan.", "error")
            return redirect(request.url)

        if prob < 0.25:
            label = "Normal"
        elif prob < 0.5:
            label = "Low Risk"
        elif prob < 0.75:
            label = "Medium Risk"
        else:
            label = "High Risk (Pneumonia Detected)"

        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # FIXED: Using get_db() to ensure data goes to the master database
        try:
            db = get_db()
            cursor = db.cursor()
            query = """
                INSERT INTO scans (user_email, user_name, filename, upload_date, ai_result) 
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (user_email, patient_name, unique_filename, upload_date, label))
            db.commit()
            print(f"✅ Record saved securely for {user_email}")
        except Exception as e:
            print(f"❌ Database Insertion Error: {e}")
            flash("Warning: Report generated but failed to save in history.", "error")

        report = {
            "report_id": f"XR_{int(time.time() * 1000)}",
            "generated_at": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
            "ai_version": "AarogyamScanAI v1.0 (92.83% Accuracy)",
            "patient_info": {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "address": patient_address
            },
            "analysis": {
                "label": label,
                "probability": round(prob, 4),
                "confidence": f"{round(prob*100, 2)}%"
            },
            "images": {
                "input": save_path,
                "relative_path": f"reports/{user_email}/{unique_filename}"
            }
        }

        session["current_report"] = report
        flash("AI Analysis executed successfully.", "success")
        return redirect(url_for("xray_report_view", report_id=report["report_id"]))

    return render_template("xray_upload.html")

def xray_report_view(report_id):
    report_data = session.get("current_report")
    if not report_data or report_data.get("report_id") != report_id:
        flash("Session expired or report not found.", "error")
        return redirect(url_for("xray_upload_route"))
    return render_template("xray_report.html", report=report_data)

def download_report(report_id):
    report_data = session.get("current_report")
    if not report_data or report_data.get("report_id") != report_id:
        flash("Unauthorized access.", "error")
        return redirect(url_for("xray_upload_route"))
    return send_file(report_data["images"]["input"], as_attachment=True)

def download_json(report_id):
    report_data = session.get("current_report")
    if not report_data or report_data.get("report_id") != report_id:
        flash("Unauthorized access.", "error")
        return redirect(url_for("xray_upload_route"))
    return jsonify(report_data)
