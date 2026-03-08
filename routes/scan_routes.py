import os
import sqlite3
from flask import render_template, request, flash, redirect, url_for, session, current_app as app
from database import get_db  # Using your official database connection

def history():
    if 'email' not in session:
        flash("Authentication required. Please login first.", "error")
        return redirect(url_for('login'))
        
    user_email = session['email']
    user_history = []
    
    # FIXED: Using get_db() to ensure data is read from the master database
    try:
        db = get_db()
        db.row_factory = sqlite3.Row  # This allows HTML to use scan['filename']
        cursor = db.cursor()
        
        query = """
            SELECT id, user_email, user_name, filename, upload_date, ai_result 
            FROM scans 
            WHERE user_email = ? 
            ORDER BY upload_date DESC
        """
        cursor.execute(query, (user_email,))
        user_history = cursor.fetchall()
        
        print(f"📊 Found {len(user_history)} records in DB for {user_email}")
        
    except Exception as e:
        print(f"❌ Database fetch error: {e}")
        flash("An error occurred while fetching your history.", "error")

    return render_template('history.html', history=user_history)

def delete_history(record_id):
    if 'email' not in session:
        flash("Authentication required.", "error")
        return redirect(url_for('login'))
        
    user_email = session['email']
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM scans WHERE id = ? AND user_email = ?", (record_id, user_email))
        db.commit()
        
        if cursor.rowcount > 0:
            flash("Scan record permanently deleted.", "success")
        else:
            flash("Record not found.", "error")
            
    except Exception as e:
        print(f"❌ Database delete error: {e}")
        flash("Failed to delete record.", "error")
            
    return redirect(url_for('history'))

# Placeholders for your other routes
def ctscan_upload():
    return render_template('ctscan.html')

def mri_upload():
    return render_template('mri.html')

def scan_history_detail(report_id, scan_type):
    return "Detail View"

def delete_history_bulk():
    return "Bulk Delete"
