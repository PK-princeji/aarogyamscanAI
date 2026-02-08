
# helpers.py: Utility functions for file handling and storage management

import os
import random
from datetime import datetime
import sqlite3

# Constants
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_storage_usage(user_email):
    """Get current storage usage for a user"""
    from database import get_db
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT storage_used FROM users WHERE email = ?", (user_email,))
        result = cursor.fetchone()
        if result is None:
            print(f"❌ No user found with email: {user_email}")
            return 0
        return result['storage_used']
    except sqlite3.Error as e:
        print(f"❌ Database error in get_user_storage_usage: {e}")
        return 0

def update_user_storage(user_email, file_size):
    """Update user's storage usage by adding or subtracting file_size"""
    from database import get_db
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET storage_used = storage_used + ? WHERE email = ?", (file_size, user_email))
        db.commit()
    except sqlite3.Error as e:
        print(f"❌ Database error in update_user_storage: {e}")
        db.rollback()

def process_generic_scan(file_path, scan_type):
    """Placeholder for CT/MRI AI processing"""
    if scan_type == "ct":
        possible_results = [
            "CT Scan: Normal findings",
            "CT Scan: Mild abnormalities detected",
            "CT Scan: Moderate abnormalities - follow up recommended",
            "CT Scan: Significant findings - immediate consultation needed"
        ]
    elif scan_type == "mri":
        possible_results = [
            "MRI: Normal brain/spine structure",
            "MRI: Minor degenerative changes",
            "MRI: Moderate abnormalities detected",
            "MRI: Significant findings requiring attention"
        ]
    else:
        possible_results = ["Scan analysis: Processing completed"]
    
    result = random.choice(possible_results)
    return {
        "diagnosis": result,
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "recommendation": "Consult with radiologist for detailed interpretation",
        "risk_category": random.choice(["LOW", "MEDIUM"]),
        "generated_at": datetime.now().isoformat()
    }

def get_folder_size(folder):
    """Calculate total size of a folder"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
    except Exception as e:
        print(f"❌ Error calculating folder size: {e}")
    return total

def cleanup_old_files(user_folder, max_age_days=30):
    """Remove files older than max_age_days to free up storage"""
    cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
    deleted_size = 0
    
    try:
        for filename in os.listdir(user_folder):
            file_path = os.path.join(user_folder, filename)
            if os.path.isfile(file_path):
                file_age = os.path.getmtime(file_path)
                if file_age < cutoff_time:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_size += file_size
                    print(f"✅ Cleaned up: {filename} ({file_size} bytes)")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    return deleted_size