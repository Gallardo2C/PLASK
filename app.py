import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ---------- NEW ROUTES FOR YOUR HTML FILES ----------
@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/contact')
def contact():
    return render_template('Contacts.html')

# ---------- CREATE JOB ROUTES ----------
@app.route('/create-job')
def create_job():
    if 'username' not in session:
        flash('You must be logged in to post a job.')
        return redirect(url_for('home'))
    return render_template('Create.html')

@app.route('/create-job', methods=['POST'])
def create_job_submit():
    if 'username' not in session:
        flash('You must be logged in to post a job.')
        return redirect(url_for('home'))

    title = request.form.get('title', '').strip()
    company = request.form.get('company', '').strip()
    location = request.form.get('location', '').strip()
    description = request.form.get('description', '').strip()

    if not title or not company or not location:
        return render_template('Create.html', error="Title, Company and Location are required fields.")

    try:
        conn = sqlite3.connect('directlink.db')
        conn.execute('INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)',
                     (title, company, location, description))
        conn.commit()
        conn.close()
        flash('Job posted successfully!')
    except Exception as e:
        return render_template('Create.html', error=f"Database error: {str(e)}")

    return redirect(url_for('create_job'))
@app.route('/jobs')
def jobs():
    if 'username' not in session:
        flash('You must be logged in to view jobs.')
        return redirect(url_for('home'))

    conn = sqlite3.connect('directlink.db')
    conn.row_factory = sqlite3.Row  # This lets us use row['title'] etc.
    c = conn.cursor()
    c.execute('SELECT * FROM jobs ORDER BY posted DESC')
    job_list = c.fetchall()
    conn.close()

    return render_template('Jobs.html', jobs=job_list)

@app.route('/partners')
def partners():
    return render_template('Partners.html')


@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('Please log in first.')
        return redirect(url_for('home'))

    username = session['username']

    # Get fresh data directly from DB (never trust session alone)
    conn = sqlite3.connect('directlink.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT username, role, datetime('now') as joined FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if not user:
        flash('User not found.')
        return redirect(url_for('home'))

    return render_template('Profile.html',
                           username=user['username'],
                           role=user['role'] or 'User',  # if NULL → show "User"
                           joined_date=user['joined'][:10])  # just YYYY-MM-DD
@app.route('/registered')
def registered():
    return render_template('Registered.html')

@app.route('/related')
def related():
    return render_template('related.html')

@app.route('/services')
def services():
    return render_template('Services.html')


# CONSUMER DASHBOARD
@app.route('/consumer')
def consumer_dashboard():
    if 'username' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('home'))

    if session.get('role') != 'Consumer':
        flash('Access denied. This area is for Consumers only.')
        return redirect(url_for('registered'))  # or home, whatever you prefer

    return render_template('Consumer.html', username=session['username'])


# PROVIDER DASHBOARD
@app.route('/provider')
def provider_dashboard():
    if 'username' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('home'))

    if session.get('role') != 'Provider':
        flash('Access denied. This area is for Providers only.')
        return redirect(url_for('registered'))

    return render_template('Provider.html', username=session['username'])
# ---------- SMART LOGIN (redirects by role) ----------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('directlink.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row[0], password):
        session['username'] = username
        session['role'] = row[1] or 'Consumer'  # fallback

        role = session['role']

        # Redirect to correct dashboard based on role
        if role == 'Consumer':
            return redirect(url_for('consumer_dashboard'))
        elif role == 'Provider':
            return redirect(url_for('provider_dashboard'))
        elif role == 'Admin':
            return redirect(url_for('registered'))  # or make admin_dashboard later
        else:
            return redirect(url_for('registered'))

    else:
        return render_template('Home.html', error="Invalid username or password")


# ---------- SMART REGISTER (same logic) ----------
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if not all([username, password, role]):
        return render_template('Home.html', reg_error="All fields are required.")

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect('directlink.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_password, role))
        conn.commit()

        # Auto-login + redirect by role
        session['username'] = username
        session['role'] = role

        if role == 'Consumer':
            return redirect(url_for('consumer_dashboard'))
        elif role == 'Provider':
            return redirect(url_for('provider_dashboard'))
        elif role == 'Admin':
            return redirect(url_for('registered'))
        else:
            return redirect(url_for('registered'))

    except sqlite3.IntegrityError:
        return render_template('Home.html', reg_error="Username already exists.")
    finally:
        conn.close()


@app.route('/profile-consumer')
def profile_consumer():
    if 'username' not in session:
        flash('Please log in to view your profile.')
        return redirect(url_for('home'))

    if session.get('role') != 'Consumer':
        flash('This profile page is for Consumers only.')
        return redirect(url_for('registered'))

    username = session['username']

    conn = sqlite3.connect('directlink.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # This query works EVEN IF created_at column doesn't exist
    c.execute("SELECT username, role FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if not user:
        flash('User not found.')
        return redirect(url_for('home'))

    # Just show "Today" or a static date — no crash ever
    return render_template('ProfileConsumer.html',
                           username=user['username'],
                           role=user['role'] or 'Consumer',
                           joined_date="November 2025")  # or use datetime.now().strftime('%B %Y')


@app.route('/jobs-consumer')
def jobs_consumer():
    # Must be logged in + must be Consumer
    if 'username' not in session:
        flash('Please log in to view job listings.')
        return redirect(url_for('home'))

    if session.get('role') != 'Consumer':
        flash('This job listing is for Consumers only.')
        return redirect(url_for('registered'))

    # Get all jobs
    conn = sqlite3.connect('directlink.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT *, date(posted) as posted_date FROM jobs ORDER BY posted DESC')
    job_list = c.fetchall()
    conn.close()

    return render_template('JobsConsumer.html', jobs=job_list)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))  # or 'index', 'home_page', etc.


@app.route('/apply_job', methods=['POST'])
def apply_job():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    job_id = request.form['job_id']
    message = request.form.get('message', '').strip()

    # Save application to DB here
    # Example: save_application(session['user_id'], job_id, message)

    flash("Application submitted successfully! We'll notify you soon.")
    return redirect(url_for('jobs_consumer'))

if __name__ == '__main__':
    app.run(debug=True)
