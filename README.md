# 🚀 ResumeIQ

**AI-powered resume screening that actually explains itself.**

ResumeIQ helps you understand how well a resume matches a job description using NLP and semantic AI. It doesn't just give a score. It tells you *why*, and it remembers every analysis you run.

Built for learners, recruiters, and anyone curious about how ATS systems think.

---

## ✨ What it does

Drop in a resume and a job description, and ResumeIQ will:

- ⚡ Analyze semantic similarity between both
- 🧠 Extract key skills automatically
- 📊 Generate a match score (0–100%)
- 🔍 Highlight missing skills
- 🏷️ Classify the job category of the resume and the JD
- 💡 Suggest how to improve the resume
- 📥 Export a text or JSON report

### 🆕 Accounts and history

- 🔐 **Login / sign up** with bcrypt-hashed passwords
- 📜 **Persistent history**: every job description and resume you analyze is saved, together with the score, matched/missing skills and insights
- 📂 **Load into Analyze**: reopen an old job description and CV with one click instead of pasting or uploading them again
- 🗑 **Delete** any saved analysis
- 👤 Each user only sees their own history
- ♻️ The same JD + CV pair is stored only once (deduplicated by content hash)

---

## 🧠 How it works

```
Resume + Job Description
  → Text Cleaning
  → Skill Extraction
  → Embeddings
  → Similarity Score
  → Insights
  → Saved to database (history)
```

- 🧹 Text is cleaned and normalized
- 🧩 Skills are extracted using NLP patterns and a skills database
- 🤖 Sentence-BERT converts text into embeddings
- 📐 Cosine similarity calculates semantic match strength
- ⚖️ A composite score blends semantic similarity and skill overlap (weights adjustable in the sidebar)
- 🧾 Rule-based logic generates feedback and missing-skill analysis

---

## 🧰 Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| UI | Streamlit, Plotly, pandas |
| NLP | spaCy, NLTK |
| Embeddings | sentence-transformers (Sentence-BERT) |
| ML utilities | scikit-learn |
| Backend / DB | SQLAlchemy, PyMySQL, MySQL (RDS / local), SQLite for local dev |
| Auth | bcrypt |
| Cloud | AWS EC2, S3, Elastic Beanstalk, RDS |

---

## 📁 Project Structure

```
ResumeIQ/
│
├── app.py                  # Streamlit UI: login, analysis, history
├── db.py                   # Database models + user/history functions
├── requirements.txt
│
├── core/
│   ├── extractor.py        # PDF / TXT text extraction
│   ├── preprocessor.py     # Text cleaning pipeline
│   ├── skill_extractor.py  # Skill extraction + comparison
│   ├── matcher.py          # Embeddings + cosine + composite score
│   ├── classifier.py       # Job category classifier
│   └── feedback.py         # Suggestions and quick wins
│
├── utils/
│   ├── text_cleaner.py     # Contact info, name heuristics, text stats
│   └── report_generator.py # Text report export
│
├── data/
│   ├── skills_db.py        # Skills vocabulary
│   └── sample_resume.txt
│
├── database/
│   └── setup_mysql.sql     # Creates DB, app user and read-only user
│
├── tests/                  # Unit tests
├── assets/style.css
└── .streamlit/config.toml
```

---

## 🗄️ Database Schema

| Table | Purpose |
|---|---|
| `users` | username, bcrypt password hash, created_at |
| `job_descriptions` | title, full text, content hash, owner |
| `resumes` | filename, extracted text, content hash, optional S3 key, owner |
| `comparisons` | links a JD and a resume; score, matched skills, missing skills, insights |

Tables are created automatically on first start (`db.init_db()`).

---

## ⚙️ Getting Started (local)

> **Python 3.11 or 3.12 is required.** Newer versions (3.13+) have no prebuilt wheels for spaCy/thinc and the install will fail.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ResumeIQ.git
cd ResumeIQ
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows (PowerShell)
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

NLTK data (punkt, stopwords, wordnet) is downloaded automatically on first run.

### 4. Initialize the database and demo account

```bash
python db.py
```

With no configuration this uses a local SQLite file (`resumeiq.db`) and creates:

| | |
|---|---|
| Demo user | `demo` |
| Demo password | `Demo@12345` |

plus one sample analysis so the History page is not empty. Override with the `DEMO_USER` and `DEMO_PASS` environment variables.

### 5. Run the app

```bash
streamlit run app.py
```

Open the local URL shown in the terminal and log in.

---

## 🔧 Configuration

All configuration is done through environment variables, so the same code runs locally, on EC2 and on Elastic Beanstalk.

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///resumeiq.db` |
| `DEMO_USER` | Demo account username | `demo` |
| `DEMO_PASS` | Demo account password | `Demo@12345` |

MySQL example:

```
DATABASE_URL=mysql+pymysql://resumeiq_app:<password>@<host>:3306/resumeiq
```

Never commit real credentials. `.env` and `*.db` are git-ignored.

---

## ☁️ AWS Deployment

ResumeIQ is deployed twice, once per service model.

| | Part I: IaaS | Part II: PaaS |
|---|---|---|
| Compute | EC2 (Ubuntu) | Elastic Beanstalk (Python 3.11) |
| Database | MySQL installed on the EC2 instance | Amazon RDS (MySQL) |
| Code storage | Cloned / copied onto the instance | Application bundle stored in S3 |
| Web server | nginx reverse proxy + systemd | Beanstalk-managed nginx + `Procfile` |
| Live URL | `http://<EC2-PUBLIC-IP>` | `http://<ENV-NAME>.<region>.elasticbeanstalk.com` |

### Deployment notes

- Use an instance with at least **2 GB RAM** (for example `t3.medium`). PyTorch and sentence-transformers will run out of memory on a micro instance.
- Streamlit needs **websockets**. The nginx configuration must forward the `Upgrade` and `Connection` headers, otherwise the page stays on "Please wait...".
- Elastic Beanstalk `Procfile`:
  ```
  web: streamlit run app.py --server.port=8000 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
  ```
- Set `DATABASE_URL` in the Beanstalk **Environment properties** (or the systemd unit on EC2).
- A single-instance Beanstalk environment (no load balancer) avoids websocket stickiness problems.
- Run `database/setup_mysql.sql` once on each database server.

### Database accounts

`database/setup_mysql.sql` creates two MySQL accounts:

| Account | Privileges | Used by |
|---|---|---|
| `resumeiq_app` | SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX | The application |
| `evaluator` | `SELECT` only | Read-only access for course evaluation |

### Live deployments

| Part | URL | Database host |
|---|---|---|
| EC2 | _add URL_ | _add host_ |
| Elastic Beanstalk | _add URL_ | _add RDS endpoint_ |

---

## 🧪 Tests

```bash
python -m pytest tests/
```

---

## 📊 Sample Output

- Match Score: 82%
- Missing Skills: Docker, AWS, FastAPI

Insights:

- Add more backend-related keywords
- Improve project descriptions with measurable impact
- Align skills more closely with job requirements

---

## 🎯 Why this exists

Most ATS tools feel like black boxes. ResumeIQ tries to change that by:

- Making scoring explainable
- Showing why you match or don't
- Helping users improve their resumes instead of just rejecting them
- Keeping a history so you never have to re-upload and re-compare

---

## 🚀 Roadmap

- [x] User accounts and login
- [x] Persistent analysis history
- [x] Cloud deployment (AWS EC2 + Elastic Beanstalk + RDS)
- [ ] Original resume PDF storage in S3
- [ ] Drag and drop multiple resumes
- [ ] Recruiter dashboard
- [ ] Export PDF reports
- [ ] Job-wise candidate ranking

---

## ⚠️ Disclaimer

This project is for educational and demonstration purposes only. It does not replicate enterprise ATS systems fully. Do not upload real personal resumes to a public deployment.
