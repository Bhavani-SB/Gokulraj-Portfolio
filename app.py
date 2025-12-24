from flask import Flask, render_template, request, redirect, session
import json
import os
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")

# ✅ Correct data file path
DATA_FILE = os.path.join("static", "cms_data.json")

# -------------------- Load / Save CMS Data --------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "name": "",
            "title": "",
            "subtitle": "",
            "hero_text": "",
            "hero_media": "",
            "about_text": "",
            "skills": [],
            "achievements": [],
            "experience": [],
            "projects": [],
            "blogs": [],
            "contact_email": "",
            "social_links": {"linkedin": "", "github": ""}
        }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# -------------------- Frontend --------------------
@app.route("/")
def home():
    data = load_data()   # ✅ FIXED
    return render_template("home.html", data=data)

# -------------------- Admin Login --------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("login.html")

# -------------------- Dashboard --------------------
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    data = load_data()

    if request.method == "POST":
        # Hero text content
        data["name"] = request.form.get("name","").strip()
        data["title"] = request.form.get("title","").strip()
        data["subtitle"] = request.form.get("subtitle","").strip()
        data["hero_text"] = request.form.get("hero_text","").strip()
        data["about_text"] = request.form.get("about_text","").strip()

        # ✅ HERO MEDIA upload (image / video)
        if "hero_media" in request.files:
            file = request.files["hero_media"]
            if file and file.filename:
                upload_folder = os.path.join("static", "uploads")
                os.makedirs(upload_folder, exist_ok=True)

                filename = file.filename.replace(" ", "_")
                file.save(os.path.join(upload_folder, filename))

                # store ONLY filename
                data["hero_media"] = filename

        # Contact & social
        data["contact_email"] = request.form.get("contact_email","").strip()
        data["social_links"]["linkedin"] = request.form.get("linkedin","").strip()
        data["social_links"]["github"] = request.form.get("github","").strip()

        save_data(data)
        return redirect("/dashboard")

    return render_template("dashboard.html", data=data)

# -------------------- Logout --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
