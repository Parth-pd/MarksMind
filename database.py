import csv
import sqlite3

def init_db():
    conn = sqlite3.connect('marksmind.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS students (
                       roll TEXT,
                       name TEXT,
                       batch TEXT,
                       CalcQuiz1 REAL,
                       PhysicsQuiz1 REAL,
                       EnglishQuiz1 REAL,
                       ChemQuiz1 REAL,
                       CalcMid REAL,
                       PhysicsMid REAL,
                       EnglishMid REAL,
                       ChemMid REAL,
                       total REAL,
                       ranking INTEGER,
                       cgpa REAL
                   )''')
    conn.commit()
    cursor.execute('''

                  CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL,
                      created_at TEXT NOT NULL DEFAULT (datetime('now'))
                  )''')
    conn.commit()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    title TEXT NOT NULL,
    deadline DATE,
    done INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def load_csv(filepath):
    conn = sqlite3.connect('marksmind.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0:
        with open(filepath) as f:
            reader = csv.DictReader(f)

            for row in reader:
                cursor.execute('''
                INSERT INTO students
                (roll, name, batch, CalcQuiz1, PhysicsQuiz1, EnglishQuiz1, ChemQuiz1,
                 CalcMid, PhysicsMid, EnglishMid, ChemMid, total, ranking, cgpa)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''',(
                    row['roll'], row['name'], row['batch'],
                    row['CalcQuiz1'], row['PhysicsQuiz1'], row['EnglishQuiz1'], row['ChemQuiz1'],
                    row['CalcMid'], row['PhysicsMid'], row['EnglishMid'], row['ChemMid'],
                    row['total'], row['ranking'], row['cgpa']
                ))

            conn.commit()
    conn.close()
