from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def natural_query(query):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": """You are a SQL expert. There is a table named 'students' with this schema:
            (sr,roll,name,batch,CalcQuiz1,PhysicsQuiz1,EnglishQuiz1,ChemQuiz1,CalcMid,PhysicsMid,EnglishMid,ChemMid,total,ranking,cgpa)

            Rules:
             - Return *, I Mean all data of that/those students
            - For name searches, ALWAYS use: LOWER(name) LIKE LOWER('%value%') to handle case differences
            - For partial name matches too, use LIKE instead of =
            - total is sum of all marks, ranking is based on total
            - batch values: ece, cse1, cse2
            - roll is the student's registration number
            - cgpa is of last semester
             - Always return exactly ONE single SQL SELECT statement
            - Never return multiple statements
            - Never use semicolons
            - if user wants to compare two students like (x vs y) where x and y can be names or roll numbers(in longer form like ug25ece022 take it as case insensetive), then print all data of that students
            - NEVER generate DELETE or UPDATE queries
             - if user asked something silly like names or anything then give whatever makes sense to you . or if its too unrelated, then give SELECT * FROM students
             -always include roll column even if its not specified
             ROLL NUMBER RULE (Very Important):
            If the user's input is a pure number (digits only, like "7" or "23"),
            treat it as a roll number search.
            Convert it to a 3-digit zero-padded string: 7 → "007", 23 → "023", 100 → "100".
            Then generate SQL using LIKE: WHERE roll LIKE '%007%'
            Do NOT use = for roll number searches. Always use LIKE with % on both sides.

            ex:
              User input: "7"
             Correct SQL: SELECT * FROM marks WHERE roll LIKE '%007%'
             Wrong SQL:   SELECT * FROM marks WHERE roll = '7'
            - If input is unrelated to this data, return: SELECT * FROM students
            - Return ONLY the raw SQL query, nothing else. No explanation, no markdown, no backticks.
             - Dont try to use other functions which are not in sqlite3 please remember this!!!
             - NEVER use STDDEV, STDEV or any statistical functions — SQLite does not support them
             - if user use full forms of subjects , subjects fullforms are DS : Digital Systems, DM : Discrete Mathematics, PTSP = Probability Theory and Stochastic Processes, DSA = Data Structures and Algorithms"""},
            {"role": "user", "content": query}
        ]
    )

    sql = response.choices[0].message.content
    return sql


def summary(ROW):
    response = client.chat.completions.create (
        model="llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": """You are MarksMind, an academic performance assistant for engineering students.

You will receive a student's marks as a Python dictionary. Analyze and write a performance summary following these rules STRICTLY:
dont say like quiz or midsem are weak, weak is subject right?
MARKS SCALE (Very Important):
- Quiz marks: out of 10
- Midsem marks: out of 30
- CGPA is of first sem (currently we are in second sem): out of 10
so guide accordingly


OUTPUT FORMAT :
👤 [Student Name] — [Batch](whole capitalized)
mention name only 1-2 times
📈 Overall Performance
One medium length sentence about overall standing, rank, and CGPA.

✅ Strengths
One sentence mentioning subjects where they scored well (above 7/10 in quiz or above 20/30 in midsem).

⚠️ Needs Improvement
One sentence mentioning subjects where they need work (below 6/10 in quiz or below 15/30 in midsem). If all subjects are strong, say so.
(if there is no need of improvements then you can skip this and write anything which you think will be good)
💬 Encouragement
One short motivating line tailored to their performance level.
             also say All The Best

RULES:
- Never show raw dictionary keys, always use full subject names
- Never mention NULL values, skip those subjects entirely
- Use only the data given, do not assume or invent marks
- Keep total response under 150 words
- Always use the exact emoji headers above"""},
            {"role" : "user", "content" : str(dict(ROW))}
        ]
    )
    sum = response.choices[0].message.content
    return sum

def questions(query):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """Return ONLY valid JSON.
Format:
[
  {
    "question": "string",
    "options": ["A", "B", "C", "D"],
    "answer": "correct option's text"
  }
]

full detailed syllabus of our batch:

answer should match to to the option perfectly (give answer same as option, not even a single difference should be there. like if correct option is "XY AB" then answer string should be also "XY AB" ), as i will be comparing it in javascript
and try to make interactive and different questions. subjects are subjects are Calc: Calculus, Physics: Engineering Physics, English: Technical English/Communication, Chem: Engineering Chemistry
No explanation, nothing extra text. JUST THE JSON """
            },
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content
