# MarksMind — Your Smart Grade Companion

A web app for tracking and analyzing academic marks of the batch, with AI-powered search, quizzes, and performance summaries.
Built with Flask, SQLite, and Groq API.


#### Video Demo: https://youtu.be/Lxt1vOSQKLs

---

#### Description

MarksMind is a full-stack web application that lets students and teachers view, search, filter, and analyze marks data — using both manual filters and plain English AI queries.

I built this as my CS50x Final Project. The idea came from the frustration of managing marks in messy spreadsheets and trying to see at which rank I stand, so I initially tried to convert the marks data into sqlite3 database and doing manual quries, then I thought to make a web app that do this easily for me.So, MarksMind stores everything in a SQLite database and gives you a clean interface to explore it — plus some AI features on top.

Currently the data which I'm using is dummy (made with the help of Claude.ai), but the structure can work for any institution with some minor changes in the codes.

---

## Features

- **Marks Dashboard** — view all students across batches in a clean card layout
- **Live Search** — search by name or roll number without any page reload (AJAX)
- **Manual Filter Panel** — filter by batch, subject, score range, sort order, and top-N
- **Natural Language Querying** — type plain English like *" Top 7 students from MECH "* and get results via Text-to-SQL (AI converts your words to SQL query)
- **AI Performance Summary** — click any student's summary button to get an AI-generated summary of their marks and performance
- **AI Quiz Generator** — generate MCQ or True/False quizzes on any subject with difficulty control, or just type what you want like *"5 hard questions on binary trees"*
- **Study Tasks** — a simple task manager to store and track pending study tasks or assignments with deadlines
- **Charts & Analytics** — visual charts showing subject-wise averages, batch comparisons, and score distributions
- **User Authentication** — register, login, logout with secure password hashing. I have used sessions also, for better user experiences

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite3 |
| Frontend | HTML, CSS, JavaScript (Fetch API), Jinja2 |
| Charts | Chart.js |
| AI (api for queries & quiz) | Groq API — `llama-3.3-70b-versatile` |
| AI (frontend and debugging help) | Claude by Anthropic |
| Auth | Flask sessions + Werkzeug password hashing |

---

## Project Structure

```
project/
├── app.py                   ← All Flask routes
├── ai.py                    ← All Groq API functions
├── database.py              ← DB setup and CSV loading
├── marksmind.db             ← SQLite database
├── data/
│   └── data.csv             ← Student marks data
├── templates/
│   ├── index.html           ← Dashboard (search, filter, cards, modal)
│   ├── charts.html          ← Charts page
│   ├── tasks.html           ← Study tasks page
│   ├── quiz.html            ← Quiz generator page
│   ├── login.html           ← Login page
│   ├── register.html        ← Register page
│   └── search_results.html  ← Partial template for AJAX results
└── static/
    └── style.css            ← Shared styles for all pages
```

The Python side is split into three files on purpose:
- `app.py` — handles routes and requests
- `ai.py` — handles all Groq API calls and prompts
- `database.py` — handles DB creation and data loading

This way if something breaks or needs updating, I get to know exactly which file to go to.

---

## How to Run

### Prerequisites

- Python 3.x
- A [Groq API key](https://console.groq.com) (free tier works fine)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/parth-pd/project.git
cd project

# 2. Install dependencies
pip install flask groq werkzeug

# 3. Add your Groq API key inside ai.py
# Find the line: client = Groq(api_key="")
# And paste your key there

# 4. Run the app
flask run
```

Then open `http://127.0.0.1:5000` in your browser.

> The database comes with sample dummy students data so you can try all features right away.

---

## How the Quiz Feature Works

The quiz page has two ways to generate questions:

**Structured mode** — you pick a subject (DS, DM, PTSP, DSA, etc.), difficulty (easy / moderate / hard), number of questions, and question type (MCQ or True/False). The app sends these settings to Groq, which returns questions in JSON format.

**Free-form mode** — you just type what you want, like *"give me 5 moderate questions on graphs"* or *"quiz me on probability distributions"*. Same API call, just your text as the query.

Once questions load, you pick answers and hit "See Results". It highlights correct answers in green and wrong ones in red, and gives you a score with a message depending on how you did.

The tricky part was making sure the `answer` field in the AI response exactly matches one of the `options` — even one character difference breaks the comparison in JavaScript. The system prompt specifically instructs the model to make the answer string identical to the correct option. Took a few tries to get right.

---

## Design Decisions

### 1. Why AJAX for search instead of full page reloads?

The first version reloaded the whole page on every keystroke. It felt slow and the filter panel kept resetting. AJAX using `fetch()` only updates the results section, leaving the rest of the page untouched. `search_results.html` is a partial template — just the cards, no full HTML structure — so Flask can return it and JavaScript can inject it directly into the page.

### 2. Why a separate `search_results.html` partial?

Both `/search` and `/filter` routes return the same table/card layout. Instead of writing the same HTML twice, both routes render the same partial template. The modal lives in `index.html` (not the partial) so it doesn't get wiped on every AJAX refresh.

### 3. Why f-strings for dynamic SQL column names?

SQLite's `?` placeholder only works for values, not column names. So `ORDER BY ?` doesn't work. f-strings let you put column names directly in the query — but to avoid SQL injection, every column name is checked against a hardcoded whitelist before being used. If it's not on the list, the query is rejected.

### 4. Why return `"ERROR:"` strings instead of JSON for errors?

Every other route returns HTML, so adding JSON just for error handling would mean checking `Content-Type` headers or wrapping things in `try/catch`. A plain string with a prefix — `if (data.startsWith("ERROR:"))` — is one clean check with no extra overhead. Simple is better at this scale.

### 5. Why `str(dict(row))` when passing DB rows to Groq?

`sqlite3.Row` objects look like dicts but aren't. Passing one directly to Groq either fails or gives garbage output. `dict(row)` converts it to a real dictionary, and `str()` turns that into a readable string the model can process in its prompt.

### 6. Why Werkzeug for password hashing?

Storing passwords as plain text is a bad idea — if the database ever leaks, every account is compromised. Werkzeug's `generate_password_hash()` adds a random salt and hashes the password. You can't reverse it to get the original. `check_password_hash()` handles the comparison safely.

### 7. Why SQLite and not PostgreSQL?

MarksMind is for one college, one batch, a known number of users. SQLite is a single file, zero setup, works perfectly at this scale. PostgreSQL makes sense when you need concurrent writes under heavy load or multiple institutions — neither applies here.

### 8. Why Groq?

Free tier gives 100,000 tokens/day which is more than enough for a student project. The `llama-3.3-70b-versatile` model handles both SQL generation and natural language summaries well. The API is also OpenAI-compatible so switching providers later would be easy.

---

## Limitations

- **Roll number format is institution-specific** — the zero-padding rule in the AI prompt is built for the UG25YYYXXX format used at my college. Different institutions would need to update this.
- **Groq rate limit** — 100k tokens/day on the free tier. Heavy quiz generation or summary use can hit this.
- **Single institution data** — the schema and batch names match my college's data. Adapting it for another institution means updating the CSV and possibly the schema.

---

## Acknowledgements

- [CS50x](https://cs50.harvard.edu/x) — for teaching me how to actually think about programming
- [Groq](https://groq.com) — free API access made the AI features possible
- [Flask Docs](https://flask.palletsprojects.com) — used this constantly throughout the project
- [Chart.js](https://www.chartjs.org) — for the charts page
- [Claude by Anthropic](https://claude.ai) — helped me understand concepts, debug, and design the frontend
