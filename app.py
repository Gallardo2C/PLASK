import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ---------------------- LANDING ----------------------
@app.route('/')
def landing():
    data = {
        "name": "Jade D. Gallardo",
        "tagline": "Developer • Designer • Dreamer"
    }
    return render_template('landing.html', **data)


# ---------------------- JOBS ----------------------
@app.route('/jobs')
def jobs():
    # Require login
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, title, company, location, description, posted FROM jobs ORDER BY id DESC')
    jobs_data = [
        {
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "description": row[4],
            "posted": row[5]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return render_template('jobs.html', jobs=jobs_data, username=session['user'])


# ---------------------- ADD JOB ----------------------
@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if 'user' not in session:
        flash('Please log in to post a job.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        location = request.form['location']
        description = request.form['description']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)',
                  (title, company, location, description))
        conn.commit()
        conn.close()

        flash('Job added successfully!', 'success')
        return redirect(url_for('jobs'))

    return render_template('add_job.html')


# ---------------------- REGISTER ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_pw = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_pw, role)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "⚠️ Username already exists!"
        conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')



# ---------------------- LOGIN ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT password, role FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session['user'] = username
            session['role'] = user[1]

            if user[1] == 'employer':
                return redirect(url_for('employer_dashboard'))
            else:
                return redirect(url_for('jobs'))
        else:
            return "Invalid username or password!"

    return render_template('login.html')


# ---------------------- LOGOUT ----------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# ---------------------- RESUME ----------------------
@app.route('/resume')
def resume():
    data = {
        "name": "Jade Deevyd D. Gallardo",
        "title": "Software Developer",
        "email": "jade@gmail.com",
        "phone": "+63 900 123 4567",
        "summary": "not PASSIONATE developer with no EXPERIENCE in Python, Flask, and modern web technologies.",
        "experience": [
            {"role": "Backend Developer", "company": "TechCorp", "years": "2023–2025",
             "description": "Built APIs and managed databases using Flask and PostgreSQL with the Help of Tito."},
            {"role": "Intern", "company": "HardBard", "years": "2022–2022",
             "description": "Assisted in developing internal tools and consultations of Tito Gpt."}
        ],
        "education": [
            {"degree": "BS in Computer Science", "school": "University of the Calajo-an", "years": "2019–2023"}
        ],
        "skills": ["Python", "Flask", "SQL", "HTML", "CSS", "JavaScript"]
    }
    return render_template('resume.html', **data)

@app.route('/employer')
def employer_dashboard():
    if 'user' not in session or session.get('role') != 'employer':
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, title, company, location, description, posted FROM jobs ORDER BY id DESC')
    jobs_data = [
        {
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "description": row[4],
            "posted": row[5]
        }
        for row in c.fetchall()
    ]
    conn.close()

    return render_template('employer.html', jobs=jobs_data, username=session['user'])

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    role = session.get('role')

    # Connect to database and get user info
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users WHERE username = ?', (username,))
    user_data = c.fetchone()
    conn.close()

    if not user_data:
        return "User not found."

    user_info = {
        'id': user_data[0],
        'username': user_data[1],
        'role': user_data[2]
    }

    return render_template('profile.html', user=user_info)

@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Only allow deletion for employers (optional: check user role here)
    c.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('employer_dashboard'))  # redirect back to the dashboard



if __name__ == '__main__':
    app.run(debug=True)
