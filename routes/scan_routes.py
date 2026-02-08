
# scan_routes.py: Routes for CT and MRI scan uploads and history

from flask import request, redirect, url_for, flash, session, render_template, current_app as app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from database import get_db
from utils.helpers import allowed_file, get_user_storage_usage, update_user_storage, cleanup_old_files, process_generic_scan
from utils.constants import MODEL_METRICS

# Constants
BASE_REPORT_FOLDER = os.path.join(os.getcwd(), "reports")
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_USER_STORAGE = 200 * 1024 * 1024

def ctscan_upload():
    """Handle CT scan upload and AI analysis"""
    if request.method == "POST":
        if "email" not in session:
            flash("Please login first!", "error")
            return redirect(url_for("login"))

        file = request.files.get("ctscan_image")
        if not file or not file.filename:
            flash("No CT scan image selected!", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        if not filename:
            flash("Invalid filename!", "error")
            return redirect(request.url)

        if not allowed_file(filename):
            flash("Only PNG, JPG, JPEG, DCM, or PDF files are supported!", "error")
            return redirect(request.url)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            flash(f"File too large! Maximum size is {app.jinja_env.filters['filesizeformat'](MAX_FILE_SIZE)}.", "error")
            return redirect(request.url)

        user_email = session["email"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM users WHERE email = ?", (user_email,))
        user = cursor.fetchone()

        if not user:
            flash("User not found in database!", "error")
            return redirect(url_for("login"))

        user_id = user[0]
        username = user[1] if user[1] else user_email.split("@")[0]

        user_folder = os.path.join(BASE_REPORT_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)

        current_storage = get_user_storage_usage(user_email)
        if current_storage + file_size > MAX_USER_STORAGE:
            cleanup_size = cleanup_old_files(user_folder)
            if current_storage + file_size - cleanup_size > MAX_USER_STORAGE:
                flash(f"Storage limit ({app.jinja_env.filters['filesizeformat'](MAX_USER_STORAGE)} reached! Please delete old files.", "error")
                return redirect(url_for("history"))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        name, ext = os.path.splitext(filename)
        unique_filename = f"ctscan_{timestamp}{ext}"
        save_path = os.path.join(user_folder, unique_filename)

        file.save(save_path)
        update_user_storage(user_email, file_size)

        flash("🔬 Analyzing CT Scan...", "info")
        analysis_result = process_generic_scan(save_path, "ct")

        report_id = f"CT_{timestamp}"
        report_data = {
            "report_id": report_id,
            "filename": unique_filename,
            "scan_type": "ct",
            "ai_result": analysis_result["diagnosis"],
            "confidence": analysis_result["confidence"],
            "recommendation": analysis_result["recommendation"],
            "risk_category": analysis_result["risk_category"],
            "generated_at": analysis_result["generated_at"]
        }

        try:
            report_json = json.dumps(report_data, indent=2)
            cursor.execute("""
                INSERT INTO scan_reports 
                (user_id, user_email, report_id, filename, scan_type, ai_result, report_data, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_email, report_id, unique_filename, "ct",
                report_data["ai_result"], report_json, save_path
            ))

            cursor.execute("""
                INSERT INTO history (user_email, filename, upload_date, ai_result, scan_type)
                VALUES (?, ?, datetime('now'), ?, 'ct')
            """, (user_email, unique_filename, 
                  f"{report_data['ai_result']} ({report_data['confidence']*100:.1f}% confidence)"))
            
            db.commit()
            
            session["current_scan_report"] = report_data
            session["current_username"] = username
            session.modified = True
            
            flash(f"✅ CT Scan analysis completed: {report_data['ai_result']}", "success")
            return redirect(url_for("scan_history_detail", report_id=report_id, scan_type="ct"))

        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            flash("Analysis completed but database save failed. Report still available!", "warning")
            return redirect(url_for("ctscan_upload"))

    return render_template("ctscan_upload.html")

def mri_upload():
    """Handle MRI scan upload and AI analysis"""
    if request.method == "POST":
        if "email" not in session:
            flash("Please login first!", "error")
            return redirect(url_for("login"))

        file = request.files.get("mri_image")
        if not file or not file.filename:
            flash("No MRI image selected!", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        if not filename:
            flash("Invalid filename!", "error")
            return redirect(request.url)

        if not allowed_file(filename):
            flash("Only PNG, JPG, JPEG, DCM, or PDF files are supported!", "error")
            return redirect(request.url)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            flash(f"File too large! Maximum size is {app.jinja_env.filters['filesizeformat'](MAX_FILE_SIZE)}.", "error")
            return redirect(request.url)

        user_email = session["email"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM users WHERE email = ?", (user_email,))
        user = cursor.fetchone()

        if not user:
            flash("User not found in database!", "error")
            return redirect(url_for("login"))

        user_id = user[0]
        username = user[1] if user[1] else user_email.split("@")[0]

        user_folder = os.path.join(BASE_REPORT_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)

        current_storage = get_user_storage_usage(user_email)
        if current_storage + file_size > MAX_USER_STORAGE:
            cleanup_size = cleanup_old_files(user_folder)
            if current_storage + file_size - cleanup_size > MAX_USER_STORAGE:
                flash(f"Storage limit ({app.jinja_env.filters['filesizeformat'](MAX_USER_STORAGE)} reached! Please delete old files.", "error")
                return redirect(url_for("history"))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        name, ext = os.path.splitext(filename)
        unique_filename = f"mri_{timestamp}{ext}"
        save_path = os.path.join(user_folder, unique_filename)

        file.save(save_path)
        update_user_storage(user_email, file_size)

        flash("🔬 Analyzing MRI...", "info")
        analysis_result = process_generic_scan(save_path, "mri")

        report_id = f"MRI_{timestamp}"
        report_data = {
            "report_id": report_id,
            "filename": unique_filename,
            "scan_type": "mri",
            "ai_result": analysis_result["diagnosis"],
            "confidence": analysis_result["confidence"],
            "recommendation": analysis_result["recommendation"],
            "risk_category": analysis_result["risk_category"],
            "generated_at": analysis_result["generated_at"]
        }

        try:
            report_json = json.dumps(report_data, indent=2)
            cursor.execute("""
                INSERT INTO scan_reports 
                (user_id, user_email, report_id, filename, scan_type, ai_result, report_data, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_email, report_id, unique_filename, "mri",
                report_data["ai_result"], report_json, save_path
            ))

            cursor.execute("""
                INSERT INTO history (user_email, filename, upload_date, ai_result, scan_type)
                VALUES (?, ?, datetime('now'), ?, 'mri')
            """, (user_email, unique_filename, 
                  f"{report_data['ai_result']} ({report_data['confidence']*100:.1f}% confidence)"))
            
            db.commit()
            
            session["current_scan_report"] = report_data
            session["current_username"] = username
            session.modified = True
            
            flash(f"✅ MRI analysis completed: {report_data['ai_result']}", "success")
            return redirect(url_for("scan_history_detail", report_id=report_id, scan_type="mri"))

        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            flash("Analysis completed but database save failed. Report still available!", "warning")
            return redirect(url_for("mri_upload"))

    return render_template("mri_upload.html")

def scan_history_detail(report_id, scan_type):
    """Display detailed CT/MRI scan report"""
    if "email" not in session:
        flash("Please login to view reports!", "error")
        return redirect(url_for("login"))

    try:
        user_email = session["email"]
        username = session.get("current_username", user_email.split("@")[0])
        report_data = session.get("current_scan_report", None)

        if not report_data or report_data.get("report_id") != report_id:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT report_data, filename, upload_date, ai_result
                FROM scan_reports
                WHERE report_id = ? AND user_email = ? AND scan_type = ?
            """, (report_id, user_email, scan_type))
            
            db_result = cursor.fetchone()
            
            if not db_result:
                flash("Report not found or access denied!", "error")
                return redirect(url_for("history"))

            report_json = json.loads(db_result[0]) if db_result[0] else {}
            report_data = {
                "report_id": report_id,
                "filename": db_result[1],
                "upload_date": db_result[2],
                "ai_result": db_result[3],
                "scan_type": scan_type,
                "confidence": report_json.get("confidence", 0.0),
                "recommendation": report_json.get("recommendation", "Consult a radiologist"),
                "risk_category": report_json.get("risk_category", "UNKNOWN"),
                "generated_at": report_json.get("generated_at", datetime.now().isoformat())
            }

        flash(f"📋 Viewing {scan_type.upper()} Report: {report_data['filename']}", "info")
        return render_template("scan_report.html", report=report_data, username=username)

    except Exception as e:
        print(f"❌ Report display error: {str(e)}")
        flash(f"Error loading report: {str(e)}", "error")
        return redirect(url_for("history"))

def history():
    """Display user scan history"""
    if "email" not in session:
        flash("Please login to view history!", "error")
        return redirect(url_for("login"))

    try:
        user_email = session["email"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, filename, upload_date, ai_result, scan_type
            FROM history
            WHERE user_email = ?
            ORDER BY upload_date DESC
        """, (user_email,))
        
        history_records = cursor.fetchall()
        return render_template("history.html", history=history_records)

    except Exception as e:
        print(f"❌ History fetch error: {str(e)}")
        flash(f"Error loading history: {str(e)}", "error")
        return redirect(url_for("home"))

def delete_history(record_id):
    """Delete a single history record and associated file"""
    if "email" not in session:
        flash("Please login to delete records!", "error")
        return redirect(url_for("login"))

    try:
        user_email = session["email"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT filename, scan_type
            FROM history
            WHERE id = ? AND user_email = ?
        """, (record_id, user_email))
        
        record = cursor.fetchone()
        
        if not record:
            flash("Record not found or access denied!", "error")
            return redirect(url_for("history"))

        filename = record[0]
        scan_type = record[1]
        username = user_email.split("@")[0]
        file_path = os.path.join(BASE_REPORT_FOLDER, username, filename)

        file_size = 0
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            os.remove(file_path)

        if scan_type == "xray":
            cursor.execute("DELETE FROM xray_reports WHERE filename = ? AND user_email = ?", 
                          (filename, user_email))
        else:
            cursor.execute("DELETE FROM scan_reports WHERE filename = ? AND user_email = ?", 
                          (filename, user_email))

        cursor.execute("DELETE FROM history WHERE id = ? AND user_email = ?", 
                      (record_id, user_email))
        
        update_user_storage(user_email, -file_size)
        db.commit()
        
        flash(f"Record {filename} deleted successfully!", "success")
        return redirect(url_for("history"))

    except Exception as e:
        print(f"❌ Delete error: {str(e)}")
        flash(f"Error deleting record: {str(e)}", "error")
        return redirect(url_for("history"))

def delete_history_bulk():
    """Delete multiple history records"""
    if "email" not in session:
        flash("Please login to delete records!", "error")
        return redirect(url_for("login"))

    try:
        record_ids = request.form.getlist("record_ids")
        if not record_ids:
            flash("No records selected for deletion!", "error")
            return redirect(url_for("history"))

        user_email = session["email"]
        db = get_db()
        cursor = db.cursor()
        username = user_email.split("@")[0]

        total_size = 0
        for record_id in record_ids:
            cursor.execute("""
                SELECT filename, scan_type
                FROM history
                WHERE id = ? AND user_email = ?
            """, (record_id, user_email))
            
            record = cursor.fetchone()
            
            if record:
                filename = record[0]
                scan_type = record[1]
                file_path = os.path.join(BASE_REPORT_FOLDER, username, filename)

                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    os.remove(file_path)

                if scan_type == "xray":
                    cursor.execute("DELETE FROM xray_reports WHERE filename = ? AND user_email = ?", 
                                 (filename, user_email))
                else:
                    cursor.execute("DELETE FROM scan_reports WHERE filename = ? AND user_email = ?", 
                                 (filename, user_email))

                cursor.execute("DELETE FROM history WHERE id = ? AND user_email = ?", 
                             (record_id, user_email))

        update_user_storage(user_email, -total_size)
        db.commit()
        
        flash(f"Successfully deleted {len(record_ids)} records!", "success")
        return redirect(url_for("history"))

    except Exception as e:
        print(f"❌ Bulk delete error: {str(e)}")
        flash(f"Error deleting records: {str(e)}", "error")
        return redirect(url_for("history"))