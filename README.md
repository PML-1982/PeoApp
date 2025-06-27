# 🏢 Peo Holdings Web App (PeoApp)

**PeoApp** is a Flask-based internal dashboard and document access platform for Peo Holdings. It provides users with the ability to:

- Log in securely
- View and download PDF documents (statements, reports, minutes, NRE files)
- Track scheduled meetings
- Navigate a responsive dashboard

---

## 🔧 Technologies Used

- Python (Flask)
- SQLite3
- HTML/CSS/JS (Vanilla)
- Flask-Mail, APScheduler, bcrypt, flask-cors
- Render (for deployment)

---

## 🚀 Running Locally

> Prerequisite: Python 3.x, pip, and `virtualenv` (recommended)

```bash
# Clone the repository
git clone https://github.com/PML-1982/PeoApp.git
cd PeoApp

# Set up a virtual environment
python -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py

App runs locally at: http://127.0.0.1:5000

🌍 Deployment (Render)
Hosted at: https://peoapp.onrender.com

Uses gunicorn as production WSGI server

Environment-agnostic URLs (JS fetch() and a.href) use relative paths (e.g. /login)

⚠️ Notes
SQLite Database: Make sure peo_users.db is accessible and in the correct directory

Sensitive Data: Email credentials are currently hardcoded. Use environment variables for security in production

👤 Author
Pule Motshoane Leeuw
📧 pmleeuw@gmail.com
🌍 South Africa

📂 Folder Structure
PeoApp/
│
├── app.py
├── peo_users.db
├── requirements.txt
├── Procfile
├── templates/
├── static/
│   ├── images/
│   ├── reports/
│   ├── statements/
│   ├── minutes/
│   └── nre/
