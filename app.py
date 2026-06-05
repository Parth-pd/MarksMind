from flask import Flask, render_template, redirect, request, session
from werkzeug.security import generate_password_hash, check_password_hash #for password hashing
from flask import redirect, url_for
from datetime import date
import sqlite3
import database #importing database.py file
import ai #importing ai.py file
import json
import statistics #for statistics functions


app = Flask(__name__)

app.secret_key = 'marksmind'

database.init_db()
database.load_csv('data/data.csv')

def get_db():
    conn = sqlite3.connect('marksmind.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    COLUMNS = [description[0] for description in cursor.description]
    DATA = cursor.fetchall()
    COUNT = len(DATA)
    cursor.execute('SELECT DISTINCT batch FROM students')
    BATCHES = [row[0] for row in cursor.fetchall()]

    # for subjects
    cursor.execute('SELECT * FROM students')
    all_columns = [desc[0] for desc in cursor.description]
    non_subjects = ["sr", "roll", "name", "batch", "total", "ranking", "cgpa"]
    SUBJECTS = [col for col in all_columns if col not in non_subjects]

    conn.close()
    return render_template('index.html', data=DATA, columns=COLUMNS, batches=BATCHES, subjects=SUBJECTS, count=COUNT, user=session)

@app.route('/search')
def search():
    conn = get_db()
    cursor = conn.cursor()
    name = request.args.get("search")
    roll = name.zfill(3)
    cursor.execute("SELECT * FROM students WHERE name LIKE ? OR roll LIKE ?", ('%' + name + '%' , '%' + roll + '%'))
    COLUMNS = [description[0] for description in cursor.description]
    DATA = cursor.fetchall()
    COUNT = len(DATA)
    conn.close()
    return render_template('search_results.html', data=DATA, columns=COLUMNS, count=COUNT)


@app.route('/filter')
def filter():
    batch = request.args.get("batch")
    factor = request.args.get("factor")
    subject = request.args.get("subject")
    min = request.args.get("min")
    max = request.args.get("max")
    top = request.args.get("top")

    ALLOWED_COLUMNS = ['DSquiz1', 'PTSPquiz1', 'DMquiz1','DSmid', 'total', 'CGPA', 'ranking']

    conn = get_db()
    cursor = conn.cursor()

    if (top == "all"):
        top_string = ""
    else:
        top_string = f" LIMIT {top}"

    if (factor == "no_filter"):
        if (batch == "all"):
            cursor.execute("SELECT * FROM students")
        else:
            cursor.execute("SELECT * FROM students WHERE batch = ?", (batch,))

    elif (factor == "subjects"):
        if subject not in ALLOWED_COLUMNS: #for making it safe from sql injections
            return "INVALID SUBJECT"

        if (batch == "all"):

            query = f"SELECT * FROM students WHERE {subject} BETWEEN {min} AND {max} ORDER BY {subject} DESC" + top_string
            cursor.execute(query)
        else:
            query = f"SELECT * FROM students WHERE batch = '{batch}' AND {subject} BETWEEN {min} AND {max} ORDER BY {subject} DESC" + top_string
            cursor.execute(query)

    elif (factor == "total"):
        if (batch == "all"):
            query = f"SELECT * FROM students WHERE total BETWEEN {min} AND {max} ORDER BY total DESC" + top_string
            cursor.execute(query)
        else:
            query = f"SELECT * FROM students WHERE batch = '{batch}' AND total BETWEEN {min} AND {max} ORDER BY total DESC" + top_string
            cursor.execute(query)

    elif (factor == "ranking"):
        if (batch == "all"):
            query = f"SELECT * FROM students ORDER BY ranking" + top_string
            cursor.execute(query)
        else:
            query = f"SELECT * FROM students WHERE batch = '{batch}' ORDER BY ranking" + top_string
            cursor.execute(query)

    elif (factor == "cgpa"):
        if (batch == "all"):
            query = f"SELECT * FROM students WHERE cgpa BETWEEN {min} AND {max} ORDER BY cgpa DESC" + top_string
            cursor.execute(query)
        else:
            query = f"SELECT * FROM students WHERE batch = '{batch}' AND cgpa BETWEEN {min} AND {max} ORDER BY cgpa DESC" + top_string
            cursor.execute(query)

    COLUMNS = [description[0] for description in cursor.description]
    DATA = cursor.fetchall()
    COUNT = len(DATA)
    conn.close()
    return render_template("search_results.html", data=DATA, columns=COLUMNS, count=COUNT)


@app.route('/natural_query')
def natural_query():
    user_input = request.args.get('natural_query')
    try:
        query = ai.natural_query(user_input) #to use the natural_query function which is in ai.py
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        COLUMNS = [description[0] for description in cursor.description]
        DATA = cursor.fetchall()
        COUNT = len(DATA)
        conn.close()
        return render_template("search_results.html", data=DATA, columns=COLUMNS, count=COUNT)
    except:
        return "⚠️ Something Went Wrong, Please try manual filtering"


@app.route('/summary')
def summary():

    try:
        roll = request.args.get('roll')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE roll = ?', (roll,))
        ROW = cursor.fetchone()
        conn.close()
        sum = ai.summary(ROW)
        return (sum)
    except:
        return "⚠️ Something Went Wrong, Please try later"


@app.route('/register',  methods=["GET", "POST"])
def register():
    if (request.method=='GET'):
        return render_template("register.html")
    if (request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        password_check = request.form.get('password_check')

        if (not username or not password):
            NOTE = "Username and Password are required"
            return render_template('register.html', error=NOTE)
        if (password != password_check):
            NOTE = "Passwords are not matching"
            return render_template('register.html', error=NOTE)


        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        data = cursor.fetchall()
        entries = len(data)
        if (entries != 0):
            conn.close()
            NOTE = "Sorry, this username already exists"
            return render_template('register.html', error=NOTE)

        hashed = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed,))
        conn.commit()
        conn.close()
        session['username'] = username
        return redirect(url_for('index'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if (request.method=='GET'):
        return render_template("login.html")

    if (request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            NOTE = "Please fill both fields"
            return render_template('login.html', error=NOTE)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        data = cursor.fetchone()
        if not data:
            NOTE = "username does not exists"
            return render_template('login.html', error=NOTE)
        if not check_password_hash(data['password'], password):
            NOTE = "Wrong Password"
            return render_template('login.html', error=NOTE)
        else:
            session['username'] = username
            return redirect(url_for('index'))


@app.route('/tasks', methods=["GET", "POST"])
def tasks():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db()
    cursor = conn.cursor()

    if (request.method=='GET'):
        cursor.execute('SELECT * FROM tasks WHERE username = ? ORDER BY id', (session['username'],))
        DATA = cursor.fetchall()
        conn.close()
        return render_template('tasks.html', data=DATA, user=session, today=date.today().isoformat())
    if (request.method=='POST'):
        username = session['username']
        title = request.form.get('title')
        if not title:
            return redirect('/tasks')
        deadline = request.form.get('deadline')
        cursor.execute('INSERT INTO tasks (username, title, deadline) VALUES (?,?,?)', (username, title, deadline))
        conn.commit()
        conn.close()
        return redirect('/tasks')

@app.route('/tasks/<int:id>', methods=["POST"])
def done(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT done FROM tasks WHERE id = ?', (id,))
    DONE = cursor.fetchone()[0]
    if (DONE == 0):
        cursor.execute('UPDATE tasks SET done = ? WHERE id = ?', (1, id))
    else:
        cursor.execute('UPDATE tasks SET done = ? WHERE id = ?', (0, id))
    conn.commit()
    conn.close()
    return redirect('/tasks')

@app.route('/delete/<int:id>', methods=["POST"])
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/tasks')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/quiz')
def quiz():
    if 'username' not in session:
        return redirect('/login')
    return render_template("quiz.html", user=session)


@app.route('/quiz_generator')
def quiz_generator():
    if 'username' not in session:
        return redirect('/login')
    sub = request.args.get('sub')
    diff = request.args.get('diff')
    number = request.args.get('number')
    type = request.args.get('type')

    query = f"Subject = {sub}, difficulty = {diff}, total questions = {number}, question type = {type}"


    try:
        QUESTIONS = ai.questions(query)
        QUESTIONS = json.loads(QUESTIONS)
    except:
        return {"error": "Invalid JSON"}

    return QUESTIONS


@app.route('/desired_quiz')
def desired_quiz():
    if 'username' not in session:
        return redirect('/login')
    query = request.args.get('query')
    try:
        QUESTIONS = ai.questions(query)
        QUESTIONS = json.loads(QUESTIONS)
    except:
        return {"error": "Invalid JSON"}
    return QUESTIONS

@app.route('/charts')
def charts():
    if 'username' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    # getting all batches dynamically
    cursor.execute('SELECT DISTINCT batch FROM students')
    BATCHES = [row[0] for row in cursor.fetchall()]

    conn.close()
    return render_template('charts.html', batches=BATCHES, user=session)


@app.route('/charts/subjects')
def charts_subjects():
    batch = request.args.get('batch', 'all')

    conn = get_db()
    cursor = conn.cursor()

    # Step 1: Get all column names from the table
    cursor.execute('SELECT * FROM students LIMIT 1')
    all_columns = [desc[0] for desc in cursor.description]

    # Step 2: Filter to only subject/marks columns
    non_subjects = ['roll', 'name', 'batch', 'total', 'ranking', 'cgpa', 'sr']
    subject_cols = [col for col in all_columns if col.lower() not in non_subjects]

    # Step 3: Build AVG(col) query dynamically
    # e.g. "SELECT AVG(DSquiz1), AVG(DMquiz1), AVG(PTSPquiz1) FROM students WHERE batch = 'ece'"
    avg_selects = ', '.join([f'AVG({col})' for col in subject_cols])

    if batch == 'all':
        cursor.execute(f'SELECT {avg_selects} FROM students')
    else:
        cursor.execute(f"SELECT {avg_selects} FROM students WHERE batch = ?", (batch,))

    row = cursor.fetchone()
    conn.close()

    # Step 4: Round averages, replace None with 0
    averages = [round(row[i] or 0, 2) for i in range(len(subject_cols))]

    return {'labels': subject_cols, 'values': averages}


@app.route('/charts/batches')
def charts_batches():

    conn = get_db()
    cursor = conn.cursor()

    # Get subject columns (same logic as above)
    cursor.execute('SELECT * FROM students LIMIT 1')
    all_columns = [desc[0] for desc in cursor.description]
    non_subjects = ['roll', 'name', 'batch', 'total', 'ranking', 'cgpa', 'sr']
    subject_cols = [col for col in all_columns if col.lower() not in non_subjects]

    # Get all batches
    cursor.execute('SELECT DISTINCT batch FROM students')
    batches = [row[0] for row in cursor.fetchall()]

    avg_selects = ', '.join([f'AVG({col})' for col in subject_cols])

    result = {}
    for b in batches:
        cursor.execute(f"SELECT {avg_selects} FROM students WHERE batch = ?", (b,))
        row = cursor.fetchone()
        result[b] = [round(row[i] or 0, 2) for i in range(len(subject_cols))]

    conn.close()
    return {'labels': subject_cols, 'batches': result}


@app.route('/charts/distribution')
def charts_distribution():

    batch = request.args.get('batch', 'all')

    conn = get_db()
    cursor = conn.cursor()

    if batch == 'all':
        cursor.execute('SELECT total FROM students WHERE total IS NOT NULL')
    else:
        cursor.execute('SELECT total FROM students WHERE batch = ? AND total IS NOT NULL', (batch,))

    totals = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not totals:
        return {'labels': [], 'values': []}

    min_val = min(totals)
    max_val = max(totals)
    bucket_count = 6
    bucket_size = (max_val - min_val) / bucket_count

    # Edge case: all students have same total
    if bucket_size == 0:
        return {'labels': [str(int(min_val))], 'values': [len(totals)]}

    labels = []
    values = []

    for i in range(bucket_count):
        low  = min_val + i * bucket_size
        high = min_val + (i + 1) * bucket_size
        labels.append(f"{int(low)}–{int(high)}")
        # Count students in this range
        # Last bucket is inclusive on both ends
        if i == bucket_count - 1:
            count = sum(1 for t in totals if low <= t <= high)
        else:
            count = sum(1 for t in totals if low <= t < high)
        values.append(count)

    return {'labels': labels, 'values': values}
