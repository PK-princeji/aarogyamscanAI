# auth_routes.py: User authentication with OTP verification (SQLite)

from flask import request, redirect, url_for, flash, session, render_template
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText

# -----------------------
# COMMON EMAIL FUNCTION
# -----------------------
def send_email(to_email, subject, body):
    """Send email using Gmail SMTP"""
    sender_email = "princeji3242@gmail.com"
    sender_password = "dszpycyj eubz xypr"  # Gmail App Password

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()


# -----------------------
# Login Route
# -----------------------
def login():
    """Handle user login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required!", "error")
            return redirect(url_for("login"))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            if user["is_verified"] == 0:
                flash("Please verify your account via OTP before login.", "error")
                session["pending_email"] = email
                return redirect(url_for("verify_otp"))

            # Set session
            session["email"] = user["email"]
            session["name"] = user["name"]
            session["logged_in"] = True
            session.modified = True

            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password!", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# -----------------------
# Registration Route
# -----------------------
def register():
    """Handle user registration with OTP and debug logging"""
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        phone = request.form.get("phone")

        print(f"[DEBUG] Received form data: email={email}, name={name}, password={'***' if password else None}, phone={phone}")

        if not all([email, name, password, confirm_password, phone]):
            flash("All fields are required!", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash("Email already registered!", "error")
            return redirect(url_for("register"))

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        otp_expires = datetime.now() + timedelta(minutes=10)

        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, phone, otp_code, otp_expires)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, email, generate_password_hash(password), phone, otp, otp_expires))
            db.commit()
            print(f"[DEBUG] User {email} inserted into DB with OTP {otp}")
        except Exception as e:
            flash(f"Database error: {e}", "error")
            return redirect(url_for("register"))

        # Send OTP Email
        subject = "OTP Verification – AarogyamScanAI"
        body = f"""
Hello {name},

we receved your request for a email verification codeuse with your AarogyamScanAI account.

Your OTP for registration is: {otp}
This OTP is valid for 10 minutes.

Only enter this OTP on an official website. Don't share it with anyone .

Regards,
CodeXElite Team
"""
        try:
            send_email(email, subject, body)
            flash(f"OTP sent successfully to {email}", "success")
            print(f"[DEBUG] OTP sent successfully to {email}")
        except Exception as e:
            flash(f"Failed to send OTP email: {e}", "error")
            print(f"[DEBUG] Email sending error: {e}")

        session["pending_email"] = email
        return redirect(url_for("verify_otp"))

    return render_template("register.html")


# -----------------------
# OTP Verification Route
# -----------------------
def verify_otp():
    """Verify user account using OTP and send Thank You email"""
    if request.method == "POST":
        email = session.get("pending_email")
        input_otp = request.form.get("otp")

        if not email or not input_otp:
            flash("Email or OTP missing!", "error")
            return redirect(url_for("verify_otp"))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT otp_code, otp_expires, name FROM users WHERE email=?", (email,))
        row = cursor.fetchone()

        if row:
            otp_expires = datetime.fromisoformat(row["otp_expires"])
            if row["otp_code"] == input_otp and datetime.now() < otp_expires:
                cursor.execute("""
                    UPDATE users
                    SET is_verified=1, otp_code=NULL, otp_expires=NULL
                    WHERE email=?
                """, (email,))
                db.commit()

                # Send Thank You Email
                subject = "Registration Successful – AarogyamScanAI"
                body = f"""
Hello {row['name']},

Thank you for registering on AarogyamScanAI.

Your account has been successfully verified.
You can now log in using your registered email address and the password you created during registration to access our AI services.

Regards,
CodeXElite Team
Founder of AarogyamScanAI
"""
                try:
                    send_email(email, subject, body)
                    print(f"[DEBUG] Thank You email sent to {email}")
                except Exception as e:
                    print(f"[DEBUG] Thank You email failed: {e}")

                flash("Account verified successfully! You can now login.", "success")
                session.pop("pending_email", None)
                db.close()
                return redirect(url_for("login"))

        flash("Invalid or expired OTP. Try again.", "error")
        db.close()
        return redirect(url_for("verify_otp"))

    return render_template("verify_otp.html")


# -----------------------
# History Route
# -----------------------
def history():
    if 'name' not in session or 'email' not in session:
        return redirect(url_for('login'))

    username = session['name']
    user_email = session['email']

    db = get_db()
    history = db.execute("""
        SELECT id, filename, upload_date, ai_result, scan_type
        FROM history
        WHERE user_name = ? AND user_email = ?
        ORDER BY upload_date DESC
    """, (username, user_email)).fetchall()
    db.close()

    print(f"[DEBUG] Username: {username}, History records: {len(history)}")
    return render_template('history.html', history=history, username=username)


# -----------------------
# Logout Route
# -----------------------
def logout():
    """Handle user logout"""
    session.clear()
    flash("You have been logged out!", "success")
    return redirect(url_for("login"))
