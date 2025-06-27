from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import sqlite3
import bcrypt
from flask_cors import CORS
import os
from functools import wraps

app = Flask(__name__)
CORS(app)
app.secret_key = 'some_secret_key'

# === Path ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'peo_users.db')

STATEMENTS_FOLDER = os.path.join(BASE_DIR, 'static', 'statements')
NRE_FOLDER = os.path.join(BASE_DIR, 'static', 'nre')
REPORTS_FOLDER = os.path.join(BASE_DIR, 'static', 'reports')
MINUTES_FOLDER = os.path.join(BASE_DIR, 'static', 'minutes')

# === Mail Config ===
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pmleeuw@gmail.com'
app.config['MAIL_PASSWORD'] = 'nhvc dqnz bqvm buvn'
mail = Mail(app)

scheduler = BackgroundScheduler()
scheduler.start()

# === Login Required Decorator ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('serve_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return "Peo Holdings Login API is running."

@app.route('/login-page')
def serve_login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('serve_login'))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password, password_changed FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_hashed = row[0]
        if isinstance(stored_hashed, str):
            stored_hashed = stored_hashed.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed):
            session['logged_in'] = True
            session['username'] = username
            return jsonify({"success": True, "message": "Login successful.", "password_changed": bool(row[1])})

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# === Serve Change Password Page ===
@app.route('/change-password-page')
def serve_change_password_page():
    return render_template('change_password.html')

# === Handle Change Password (POST) ===
@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')

    if not username or not new_password:
        return jsonify({"success": False, "message": "Username and new password required."}), 400

    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ?, password_changed = 1 WHERE username = ?", (hashed_pw, username))
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        return jsonify({"success": True, "message": "Password changed successfully."})
    return jsonify({"success": False, "message": "User not found."}), 404


# === Serve Forgot Password Page ===
@app.route('/forgot-password-page')
def serve_forgot_password_page():
    return render_template('forgot_password.html')

# === Handle Forgot Password (POST) ===
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"success": False, "message": "Username is required."}), 400

    temp_password = "Temp@123"
    hashed_pw = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ?, password_changed = 0 WHERE username = ?", (hashed_pw, username))
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        return jsonify({"success": True, "message": f"Password reset successfully. Your temporary password is: {temp_password}"})
    return jsonify({"success": False, "message": "User not found."}), 404

# === STATEMENTS ===
@app.route('/statements', methods=['GET'])
def list_statements():
    try:
        print("📄 Looking for statements in:", STATEMENTS_FOLDER)
        files = [f for f in os.listdir(STATEMENTS_FOLDER) if f.endswith('.pdf')]
        return jsonify({"success": True, "files": files})
    except Exception as e:
        print("❌ Error in /statements:", e)
        return jsonify({"success": False, "message": str(e)})

@app.route('/download/<filename>', methods=['GET'])
def download_statement_file(filename):
    try:
        print(f"⬇️ Serving statement: {filename}")
        return send_from_directory(STATEMENTS_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print("❌ Error in /download:", e)
        return jsonify({"success": False, "message": str(e)}), 500

# === NRE ===
@app.route('/nre/files', methods=['GET'])
def list_nre_files():
    try:
        print("📄 Looking for NRE files in:", NRE_FOLDER)
        files = [f for f in os.listdir(NRE_FOLDER) if f.endswith('.pdf')]
        return jsonify({"success": True, "files": files})
    except Exception as e:
        print("❌ Error in /nre/files:", e)
        return jsonify({"success": False, "message": str(e)})

@app.route('/nre/download/<filename>', methods=['GET'])
def download_nre_file(filename):
    try:
        print(f"⬇️ Serving NRE file: {filename}")
        return send_from_directory(NRE_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print("❌ Error in /nre/download:", e)
        return jsonify({"success": False, "message": str(e)}), 500

# === REPORTS ===
@app.route('/reports/files', methods=['GET'])
def list_report_files():
    try:
        print("📄 Looking for reports in:", REPORTS_FOLDER)
        files = [f for f in os.listdir(REPORTS_FOLDER) if f.endswith('.pdf')]
        return jsonify({"success": True, "files": files})
    except Exception as e:
        print("❌ Error in /reports/files:", e)
        return jsonify({"success": False, "message": str(e)})

@app.route('/reports/download/<filename>', methods=['GET'])
def download_report_file(filename):
    try:
        print(f"⬇️ Serving report: {filename}")
        return send_from_directory(REPORTS_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print("❌ Error in /reports/download:", e)
        return jsonify({"success": False, "message": str(e)}), 500

# === MINUTES ===
@app.route('/minutes/files', methods=['GET'])
def list_minutes_files():
    try:
        print("📄 Looking for minutes in:", MINUTES_FOLDER)
        files = [f for f in os.listdir(MINUTES_FOLDER) if f.endswith('.pdf')]
        return jsonify({"success": True, "files": files})
    except Exception as e:
        print("❌ Error in /minutes/files:", e)
        return jsonify({"success": False, "message": str(e)})

@app.route('/minutes/download/<filename>', methods=['GET'])
def download_minutes_file(filename):
    try:
        print(f"⬇️ Serving minutes file: {filename}")
        return send_from_directory(MINUTES_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print("❌ Error in /minutes/download:", e)
        return jsonify({"success": False, "message": str(e)}), 500

# === Page Routes ===
@app.route('/dashboard')
@login_required
def serve_dashboard():
    return render_template('peo_holdings_dashboard.html')

@app.route('/documents-page')
@login_required
def serve_documents_page():
    return render_template('documents.html')

@app.route('/statements-page')
@login_required
def serve_statements_page():
    return render_template('statements.html')

@app.route('/reports-page')
@login_required
def serve_reports_page():
    return render_template('reports.html')

@app.route('/minutes-page')
@login_required
def serve_minutes_page():
    return render_template('minutes.html')

@app.route('/nre-page')
@login_required
def serve_nre_page():
    return render_template('nre.html')

@app.route('/contributions')
@login_required
def serve_contributions():
    return render_template('contributions.html')

@app.route('/notice-board')
@login_required
def serve_notice_board():
    return render_template('notice_board.html')

@app.route('/financial-overview')
@login_required
def serve_financial_overview():
    return render_template('financial_overview.html')

@app.route('/shares-register')
@login_required
def serve_shares_register():
    return render_template('share_regis.html')

@app.route('/ownership-graph')
@login_required
def serve_ownership_graph():
    return render_template('ownership_graph.html')

@app.route('/ownership-table')
@login_required
def serve_ownership_table():
    return render_template('ownership_table.html')

@app.route('/setup-meeting')
@login_required
def serve_setup_meeting():
    return render_template('setup_meeting.html')

@app.route('/meeting-log')
@login_required
def serve_meeting_log():
    return render_template('meeting_log.html')

@app.route('/schedule-meeting', methods=['POST'])
def schedule_meeting():
    data = request.get_json()
    title = data.get('title', '').strip()
    date = data.get('date', '').strip()
    time = data.get('time', '').strip()
    description = data.get('details', '').strip()

    if not title or not date or not time:
        return jsonify({"success": False, "message": "Title and Date/Time are required."}), 400

    datetime_str = f"{date}T{time}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO meetings (title, datetime, description) VALUES (?, ?, ?)", (title, datetime_str, description))
    conn.commit()

    cursor.execute("SELECT email FROM users")
    users = cursor.fetchall()
    conn.close()

    for (email,) in users:
        msg = Message(
            subject=f"[Meeting Invite] {title}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"You're invited to a meeting:\n\nTitle: {title}\nWhen: {date} at {time}\nDetails: {description}\n\nPeo Holdings"
        )
        mail.send(msg)

    meeting_time = datetime.fromisoformat(datetime_str)
    reminder_time = meeting_time - timedelta(hours=12)

    def send_reminder():
        for (email,) in users:
            reminder = Message(
                subject=f"[Reminder] {title} in 12 hours",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"Reminder: Your meeting '{title}' is happening in 12 hours.\n\nPeo Holdings"
            )
            mail.send(reminder)

    scheduler.add_job(send_reminder, trigger='date', run_date=reminder_time)

    return jsonify({"success": True, "message": "Meeting scheduled and invitations sent!"})

@app.route('/meetings', methods=['GET'])
def get_meetings():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, datetime, description FROM meetings ORDER BY datetime DESC")
        rows = cursor.fetchall()
        conn.close()

        meetings = [{"title": row[0], "datetime": row[1], "description": row[2]} for row in rows]
        return jsonify({"success": True, "meetings": meetings})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
