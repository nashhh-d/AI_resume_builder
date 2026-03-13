from flask import Flask, request, jsonify
from flask_cors import CORS

from skill_matcher import suggest_skills
from summary_generator import generate_summary
from resume_generator import build_docx, build_pdf

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return {"message": "AI Resume Builder Backend Running"}


@app.route("/generate", methods=["POST"])
def generate_resume():
    try:
        data = request.get_json()

        # ----- Personal -----
        personal = data.get("personal", {})
        name = personal.get("full_name", "")
        email = personal.get("email", "")
        phone = personal.get("phone", "")
        linkedin = personal.get("linkedin", "")
        job_title = personal.get("target_role", "")

        # ----- Other Sections -----
        education = data.get("education", {})
        experience = data.get("experience", [])
        skills = data.get("skills", [])
        projects = data.get("projects", [])
        certifications = data.get("certifications", [])

        # ----- Skill Suggestions -----
        suggested_skills = suggest_skills(job_title, skills)

        # ----- Summary -----
        summary = generate_summary(job_title, experience, skills + suggested_skills)

        resume_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "education": [education],
            "experience": experience,
            "skills": skills,
            "projects": projects,
            "certifications": certifications
        }

        docx_file = build_docx(resume_data, summary, suggested_skills)
        pdf_file = build_pdf(resume_data, summary, suggested_skills)

        return jsonify({
            "suggested_skills": suggested_skills,
            "resume_summary": summary,
            "download_docx": docx_file,
            "download_pdf": pdf_file
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
