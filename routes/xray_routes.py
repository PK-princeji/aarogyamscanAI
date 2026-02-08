import os, time
from datetime import datetime
from flask import request, redirect, url_for, flash, session, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from utils.predict_xray import predict_xray

# Constants
BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------- X-Ray Upload -----------------
def xray_upload_route():
    if request.method == "POST":
        # Patient Info
        patient_name = request.form.get("name")
        patient_age = request.form.get("age")
        patient_gender = request.form.get("gender")
        patient_address = request.form.get("address")

        # X-Ray File
        xray_file = request.files.get("xray_image")
        if not xray_file:
            flash("Please upload an X-Ray image!", "error")
            return redirect(request.url)

        filename = secure_filename(xray_file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        xray_file.save(save_path)

        # AI Prediction
        prob = predict_xray(save_path)

        # Determine label
        if prob < 0.25:
            label = "Normal"
        elif prob < 0.5:
            label = "Low"
        elif prob < 0.75:
            label = "Medium"
        else:
            label = "High"

        # Report
        report = {
            "report_id": "XR_" + str(int(time.time() * 1000)),
            "generated_at": str(datetime.now().strftime("%d-%b-%Y %I:%M %p")),
            "ai_version": "AarogyamScanAI v1.0 (92.5% Accuracy)",
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
                "input": save_path
            }
        }

        session["current_report"] = report
        return redirect(url_for("xray_report_view", report_id=report["report_id"]))

    return render_template("xray_upload.html")

# ----------------- X-Ray Report -----------------
def xray_report_view(report_id):
    report_data = session.get("current_report")
    if not report_data or report_data.get("report_id") != report_id:
        flash("Report not found!", "error")
        return redirect(url_for("xray_upload_route"))
    return render_template("xray_report.html", report=report_data)

# ----------------- Download X-Ray -----------------
def download_report(report_id):
    report_data = session.get("current_report")
    if not report_data or report_data.get("report_id") != report_id:
        flash("Report not found!", "error")
        return redirect(url_for("xray_upload_route"))
    return send_file(report_data["images"]["input"], as_attachment=True)

# ----------------- Download JSON -----------------
def download_json(report_id):
    report_data = session.get("current_report")
    if not report_data or report_data.get("report_id") != report_id:
        flash("Report not found!", "error")
        return redirect(url_for("xray_upload_route"))
    return jsonify(report_data)