from routes.mri_routes import mri_upload_route
# app.py: Main Flask application with route imports and configuration
from flask import Flask, g
import os
import sqlite3
from database import get_db, close_connection, init_db
from routes.xray_routes import xray_upload_route, xray_report_view, download_report
from routes.scan_routes import ctscan_upload, mri_upload, history, delete_history, mri_report_view
from routes.auth_routes import login, register, logout
from routes.misc_routes import home, about_project, about_team, plan, xray_solution, ctscan_solution, mri_solution, download_file
from routes.misc_routes import not_found_error, internal_error, request_entity_too_large
from routes.auth_routes import login, register, verify_otp, logout
from routes.xray_routes import download_json

# ===== CONSTANTS =====
# Directory for storing uploaded files
UPLOAD_FOLDER = 'static/uploads'
# SQLite database file (NEW one)
DATABASE = 'aarogyam_scan_ai.db'
# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024
# Maximum storage per user (200MB)
MAX_USER_STORAGE = 200 * 1024 * 1024
# Base folder for reports
BASE_REPORT_FOLDER = os.path.join(os.getcwd(), "reports")

# Create directories if they don't exist
os.makedirs(BASE_REPORT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== FLASK APP CONFIG =====
# Initialize Flask application
app = Flask(__name__)
app.secret_key = "aarogyam_scanai_secret_2025_v1.0"  # Secret key for session management
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['BASE_REPORT_FOLDER'] = BASE_REPORT_FOLDER
app.config['DATABASE'] = DATABASE   # set database file in config

# ===== TEMPLATE FILTERS =====
@app.template_filter('basename')
def basename_filter(path):
    """Extract basename from file path for display"""
    return os.path.basename(path)

@app.template_filter('filesizeformat')
def filesizeformat(value):
    """Convert file size to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"

# ===== DATABASE INITIALIZATION =====
def initialize_database():
    """Initialize and update database schema with error handling"""
    try:
        with app.app_context():
            print("Initializing database...")
            init_db()  # only our schema creation
            print("✅ Database initialization completed")
    except sqlite3.Error as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# Register database connection cleanup
app.teardown_appcontext(close_connection)

# Run database initialization
initialize_database()

# ===== ROUTE REGISTRATION =====
# Register routes from separate modules
app.route('/')(home)
app.route('/about_project')(about_project)
app.route('/about_team')(about_team)
app.route('/plan')(plan)
app.route('/xray_solution')(xray_solution)
app.route('/ctscan_solution')(ctscan_solution)
app.route('/mri_solution')(mri_solution)
app.route('/xray_upload', methods=['GET', 'POST'])(xray_upload_route)
app.route('/xray_report/<report_id>', methods=['GET'])(xray_report_view)
app.route('/download_report/<report_id>', methods=['GET'])(download_report)
app.route('/reports/<username>/<filename>')(download_file)
app.route('/ctscan_upload', methods=['GET', 'POST'])(ctscan_upload)
app.route('/mri_upload', methods=['GET', 'POST'])(mri_upload)
app.route('/history')(history)
app.route('/delete_history/<int:record_id>')(delete_history)
app.route('/download_json/<report_id>', methods=['GET'])(download_json)
app.add_url_rule("/login", "login", login, methods=["GET", "POST"])
app.add_url_rule("/register", "register", register, methods=["GET", "POST"])
app.add_url_rule("/verify-otp", "verify_otp", verify_otp, methods=["GET", "POST"])
app.add_url_rule("/logout", "logout", logout)

# ===== ERROR HANDLERS =====
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)
app.register_error_handler(413, request_entity_too_large)
app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    return response

# ===== RUN SERVER =====

# =============== NEW MRI AI ROUTES (Bypass) ===============
from flask import request, redirect, render_template, session, flash
from werkzeug.utils import secure_filename
import os, random, datetime
from utils.predict_mri import predict_mri

@app.route('/mri_scan_ai', methods=['GET', 'POST'])
def mri_scan_ai():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file uploaded", "error")
            return redirect(request.url)
        
        p_name = request.form.get('name', 'Unknown')
        p_age = request.form.get('age', 'N/A')
        p_gender = request.form.get('gender', 'N/A')
        p_address = request.form.get('address', 'N/A')
        
        filename = secure_filename(file.filename)
        path = os.path.join('static', 'uploads', 'mri', filename)
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

@app.route('/mri_theory')
def mri_theory():
    return render_template('mri.html')
# ==========================================================


from routes.scan_routes import ctscan_upload, mri_upload, history, delete_history, mri_report_view

app.route('/mri_report_view', methods=['GET'])(mri_report_view)
if __name__ == '__main__':
    print("🚀 Starting AarogyamScanAI Server...")
    print(f"📁 Reports Directory: {BASE_REPORT_FOLDER}")
    print(f"💾 Database: {DATABASE}")
    print(f"🔒 Max Storage: {app.jinja_env.filters['filesizeformat'](MAX_USER_STORAGE)} per user")
    print(f"📤 Max File Size: {app.jinja_env.filters['filesizeformat'](MAX_FILE_SIZE)} per upload")
    print("-" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
