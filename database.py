# database.py : AarogyamScanAI Database Manager 
import os
import sqlite3
from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "aarogyam_scan_ai.db")

def get_db():
    """Get database connection (per request)"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        print("✅ Database connection opened")
    return db

def close_connection(exception=None):
    """Close database connection at app context teardown"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        print("✅ Database connection closed")

def init_db():
    """Initialize all tables for AarogyamScanAI"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # --------- USERS TABLE ---------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT,
            pass_hash TEXT,
            phone TEXT,
            otp_code TEXT,
            otp_expires DATETIME,
            is_verified TINYINT DEFAULT 0,
            location TEXT,
            source_website TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            storage_used INTEGER DEFAULT 0
        )
    """)

    # --------- HISTORY TABLE ---------
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
    if cursor.fetchone():
        # Table exists: ensure user_email and user_name columns exist
        cursor.execute("PRAGMA table_info(history)")
        columns = [col[1] for col in cursor.fetchall()]
        if "user_email" not in columns:
            cursor.execute("ALTER TABLE history ADD COLUMN user_email TEXT")
            print("✅ Added user_email column to existing history table")
        if "user_name" not in columns:
            cursor.execute("ALTER TABLE history ADD COLUMN user_name TEXT")
            print("✅ Added user_name column to existing history table")
    else:
        cursor.execute("""
            CREATE TABLE history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                user_name TEXT,
                filename TEXT NOT NULL,
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                ai_result TEXT,
                scan_type TEXT DEFAULT 'unknown',
                FOREIGN KEY(user_email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

    # --------- X-RAY REPORTS TABLE ---------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS xray_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            diagnosis TEXT,
            probability REAL,
            confidence REAL,
            risk_category TEXT,
            report_data TEXT,
            image_path TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # --------- SCAN REPORTS TABLE ---------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            ai_result TEXT,
            report_data TEXT,
            image_path TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()
    print("✅ Database tables updated successfully in aarogyam_scan_ai.db")

if __name__ == "__main__":
    print(f"🔄 Initializing/updating database: {DATABASE}")
    init_db()
    print("🎉 Done")
