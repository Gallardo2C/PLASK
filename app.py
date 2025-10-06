from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def landing():
    data = {
        "name": "Jade D. Gallardo",
        "tagline": "Developer • Designer • Dreamer"
    }
    return render_template('landing.html', **data)

@app.route('/resume')
def resume():
    data = {
        "name": "Jade Deevyd D. Gallardo",
        "title": "Software Developer",
        "email": "jade@gmail.com",
        "phone": "+63 900 123 4567",
        "summary": "not PASSIONATE developer with no EXPERIENCE in Python, Flask, and modern web technologies.",
        "experience": [
            {"role": "Backend Developer", "company": "TechCorp", "years": "2023–2025", "description": "Built APIs and managed databases using Flask and PostgreSQL with the Help of Tito."},
            {"role": "Intern", "company": "HardBard", "years": "2022–2022", "description": "Assisted in developing internal tools and consultations of Tito Gpt."}
        ],
        "education": [
            {"degree": "BS in Computer Science", "school": "University of the Calajo-an", "years": "2019–2023"}
        ],
        "skills": ["Python", "Flask", "SQL", "HTML", "CSS", "JavaScript"]
    }
    return render_template('resume.html', **data)

if __name__ == '__main__':
    app.run(debug=True)
