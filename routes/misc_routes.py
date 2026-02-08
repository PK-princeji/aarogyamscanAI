
# misc_routes.py: Miscellaneous routes and error handlers

import os
from flask import render_template, send_from_directory, session, flash, redirect, url_for, current_app as app
from datetime import datetime
from database import get_db
from utils.helpers import get_user_storage_usage, get_folder_size
from utils.constants import MODEL_METRICS

# Constants
BASE_REPORT_FOLDER = os.path.join(os.getcwd(), "reports")
MAX_USER_STORAGE = 200 * 1024 * 1024

def home():
    """Render home page with user storage information"""
    user_storage = 0
    if 'email' in session:
        user_storage = get_user_storage_usage(session['email'])
    return render_template('index.html', 
                         user_storage=user_storage,
                         max_storage=MAX_USER_STORAGE)

def about_project():
    """Render about project page"""
    return render_template('about_project.html')

def about_team():
    """Render about team page"""
    return render_template('about_team.html')

def plan():
    """Render pricing/plan page"""
    return render_template('plan.html')

def xray_solution():
    """Render X-Ray solution information page"""
    return render_template('xray_solution.html',  model_metrics=MODEL_METRICS)

def ctscan_solution():
    """Render CT Scan solution information page"""
    return render_template('ctscan.html')

def mri_solution():
    """Render MRI solution information page"""
    return render_template('mri.html')

def download_file(username, filename):
    """Legacy route for downloading files"""
    user_folder = os.path.join(BASE_REPORT_FOLDER, username)
    file_path = os.path.join(user_folder, filename)
    
    if not os.path.exists(file_path):
        flash("File not found!", "error")
        return redirect(url_for("history"))
    
    return send_from_directory(user_folder, filename, as_attachment=True)

def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

def request_entity_too_large(error):
    """Handle 413 errors (file too large)"""
    return render_template('413.html'), 413
