from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import requests
import json

from parser import extract_text
from predictor import resume_similarity, final_prediction
from skills import skills

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ⚠️ REPLACE WITH YOUR GOOGLE APPS SCRIPT WEB APP URL
GOOGLE_SHEETS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzy_SVNkj3Ae5a5cdhuH-0SA61IRUrBGbOoiRiqHy7pMsK_zI54AvZTIB1IJvCJMZY/exec"


def send_to_google_sheets(data):
    """Send candidate data to Google Sheets via Apps Script Web App"""
    try:
        payload = {
            "timestamp": data.get("timestamp"),
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "qualification": data.get("qualification"),
            "passedout": data.get("passedout"),
            "percentage": data.get("percentage"),
            "skills": data.get("skills"),
            "experience": data.get("experience"),
            "resume_filename": data.get("resume_filename"),
            "jd": data.get("jd"),
            "similarity": data.get("similarity"),
            "overall_score": data.get("overall_score"),
            "prediction": data.get("prediction"),
            "detected_skills": data.get("detected_skills"),
            "missing_skills": data.get("missing_skills"),
            "strengths": data.get("strengths"),
            "weaknesses": data.get("weaknesses"),
            "recommendations": data.get("recommendations"),
        }
        response = requests.post(
            GOOGLE_SHEETS_WEBAPP_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Google Sheets error: {e}")
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    # Candidate Details
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    qualification = request.form["qualification"]
    passedout = int(request.form["passedout"])
    percentage = float(request.form["percentage"])
    user_skills = request.form["skills"].lower()
    experience = request.form["experience"]
    job_description = request.form["jd"].lower()

    # Upload Resume
    resume = request.files["resume"]
    filename = secure_filename(resume.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(filepath)

    # Extract Text
    resume_text = extract_text(filepath)

    # Similarity Score
    similarity = resume_similarity(resume_text, job_description)

    # Skill Detection
    detected_skills = []
    missing_skills = []
    for skill in skills:
        if skill in resume_text or skill in user_skills:
            detected_skills.append(skill)
        if skill in job_description:
            if skill not in detected_skills:
                missing_skills.append(skill)

    # Prediction
    overall_score, prediction = final_prediction(
        similarity,
        percentage,
        qualification,
        passedout,
        detected_skills
    )

    # Strengths
    strengths = []
    if percentage >= 80:
        strengths.append("Excellent Academic Performance")
    if similarity >= 70:
        strengths.append("Resume matches Job Description")
    if len(detected_skills) >= 6:
        strengths.append("Strong Technical Skill Set")
    if experience != "Fresher":
        strengths.append("Industry Experience")

    # Weaknesses
    weaknesses = []
    if percentage < 65:
        weaknesses.append("Academic percentage is comparatively low")
    if similarity < 50:
        weaknesses.append("Resume needs better alignment with Job Description")
    if len(missing_skills) > 0:
        weaknesses.append("Missing important technical skills")

    # Recommendations
    recommendations = []
    if len(missing_skills) > 0:
        recommendations.append("Learn: " + ", ".join(missing_skills))
    if similarity < 70:
        recommendations.append("Customize your resume for each job role.")
    if percentage < 75:
        recommendations.append("Highlight projects and certifications.")

    # Prepare data for Google Sheets
    sheet_data = {
        "timestamp": request.form.get("timestamp") or "",
        "name": name,
        "email": email,
        "phone": phone,
        "qualification": qualification,
        "passedout": passedout,
        "percentage": percentage,
        "skills": user_skills,
        "experience": experience,
        "resume_filename": filename,
        "jd": job_description,
        "similarity": similarity,
        "overall_score": overall_score,
        "prediction": prediction,
        "detected_skills": ", ".join(detected_skills),
        "missing_skills": ", ".join(missing_skills),
        "strengths": "; ".join(strengths),
        "weaknesses": "; ".join(weaknesses),
        "recommendations": "; ".join(recommendations),
    }

    # Send to Google Sheets (async, don't block)
    try:
        send_to_google_sheets(sheet_data)
    except Exception as e:
        print(f"Failed to send to Google Sheets: {e}")

    # Render Result
    return render_template(
        "results.html",
        name=name,
        email=email,
        phone=phone,
        qualification=qualification,
        passedout=passedout,
        percentage=percentage,
        experience=experience,
        similarity=similarity,
        detected_skills=detected_skills,
        missing_skills=missing_skills,
        overall_score=overall_score,
        prediction=prediction,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations
    )


if __name__ == "__main__":
    app.run(debug=True)