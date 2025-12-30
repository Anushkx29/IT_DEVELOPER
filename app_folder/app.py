from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)

app.secret_key = "secret_key_123"

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Anushkx_29",
    database="portfolio_builder"
)
cursor = db.cursor(dictionary=True)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid email or password"

    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (
                request.form["name"],
                request.form["email"],
                request.form["password"]
            )
        )
        db.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- DASHBOARD (GET + POST) ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # ✅ FETCH PROFILE FIRST
    cursor.execute(
        "SELECT * FROM profiles WHERE user_id = %s",
        (user_id,)
    )
    profile = cursor.fetchone()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        location = request.form.get("location")
        bio = request.form.get("bio")
        github = request.form.get("github")
        linkedin = request.form.get("linkedin")

        if profile:
            cursor.execute("""
                UPDATE profiles SET
                name=%s, email=%s, phone=%s,
                location=%s, bio=%s,
                github=%s, linkedin=%s
                WHERE user_id=%s
            """, (name, email, phone, location, bio, github, linkedin, user_id))
        else:
            cursor.execute("""
                INSERT INTO profiles
                (user_id, name, email, phone, location, bio, github, linkedin)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, name, email, phone, location, bio, github, linkedin))

        db.commit()
        return redirect(url_for("dashboard"))

    return render_template("dashboard.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#---------------SKILLS-------------------------
 
from flask import flash

@app.route("/skills", methods=["GET", "POST"])
def skills():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        skill = request.form["skill"]
        description = request.form["description"]
        level = request.form["level"]

        cursor.execute("""
            INSERT INTO skills (user_id, skill_name, description, level)
            VALUES (%s, %s, %s, %s)
        """, (user_id, skill, description, level))
        db.commit()

        return redirect(url_for("skills"))

    return render_template("skills.html")




# ---------------- PROJECTS ----------------
@app.route("/projects", methods=["GET", "POST"])
def projects():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # ---------- SAVE PROJECT ----------
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        tech_stack = request.form["tech_stack"]
        project_link = request.form["project_link"]

        cursor.execute("""
            INSERT INTO projects (user_id, title, description, tech_stack, project_link)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, title, description, tech_stack, project_link))

        db.commit()
        return redirect(url_for("projects"))

    return render_template("projects.html")



@app.route("/certificates", methods=["GET","POST"])
def certificates():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        issued_by = request.form["issued_by"]
        cert_link = request.form["cert_link"]
        info = request.form["info"]

        cursor.execute("""
            INSERT INTO certificates
            (user_id, certificate_title, issued_by, certificate_link, additional_info)
            VALUES (%s,%s,%s,%s,%s)
        """, (user_id, title, issued_by, cert_link, info))
        db.commit()

    return render_template("certificates.html")



# =========================
# UPLOAD RESUME (PDF ONLY)
# =========================

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload-resume", methods=["GET", "POST"])
def upload_resume():

    if request.method == "POST":

        print("📥 POST REQUEST RECEIVED")

        if "resume" not in request.files:
            print("❌ resume not in request.files")
            return "No file part"

        file = request.files["resume"]

        print("📄 File object:", file)

        if file.filename == "":
            print("❌ Empty filename")
            return "No selected file"

        if not allowed_file(file.filename):
            print("❌ Invalid file type")
            return "Invalid file type"

        filename = secure_filename(file.filename)

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        print("✅ File saved at:", save_path)

        # SAVE TO DATABASE
        cursor.execute(
            "INSERT INTO resumes (filename) VALUES (%s)",
            (filename,)
        )
        db.commit()

        print("✅ Saved to database")

        return "Resume uploaded successfully ✅"

    return render_template("upload_resume.html")


# =========================
# HOME / DASHBOARD
# =========================
@app.route("/")
def index():
    return redirect(url_for("education"))


# =========================
# EDUCATION PAGE
# =========================
@app.route("/education", methods=["GET", "POST"])
def education():

    if request.method == "POST":
        # -------- FORM DATA --------
        school = request.form.get("school")
        degree = request.form.get("degree")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        location = request.form.get("location")
        description = request.form.get("description")

        # -------- BASIC VALIDATION --------
        if not school:
            flash("School name is required", "error")
            return redirect(url_for("education"))

        # -------- DEBUG --------
        print("===== EDUCATION DATA =====")
        print(request.form)
        print("==========================")

        # -------- INSERT INTO DATABASE --------
        cursor.execute("""
            INSERT INTO education
            (school, degree, start_date, end_date, location, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (school, degree, start_date, end_date, location, description))

        db.commit()   # 🔴 THIS WAS MISSING

        # -------- SUCCESS --------
        flash("Education details saved successfully!", "success")
        return redirect(url_for("education"))

    return render_template("education.html")



@app.route("/experience", methods=["GET", "POST"])
def experience():

    if request.method == "POST":
        job_title = request.form.get("job_title")
        employer = request.form.get("employer")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        location = request.form.get("location")
        description = request.form.get("description")

        if not job_title:
            flash("Job title is required", "error")
            return redirect(url_for("experience"))

        cursor = db.cursor()

        query = """
            INSERT INTO experience
            (job_title, employer, start_date, end_date, location, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            job_title,
            employer,
            start_date,
            end_date,
            location,
            description
        ))

        db.commit()
        cursor.close()

        flash("Experience saved successfully!", "success")
        return redirect(url_for("experience"))

    return render_template("experience.html")

 


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)