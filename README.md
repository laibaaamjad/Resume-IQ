# 🚀 ResumeIQ

**AI-powered resume screening that actually explains itself.**

ResumeIQ helps you understand how well a resume matches a job description using NLP and semantic AI.
It doesn’t just give a score. It tells you *why*.

Built for learners, recruiters, and anyone curious about how ATS systems think.

---

## ✨ What it does

Drop in a resume and a job description, and ResumeIQ will:

* ⚡ Analyze semantic similarity between both
* 🧠 Extract key skills automatically
* 📊 Generate a match score (0–100%)
* 🔍 Highlight missing skills
* 💡 Suggest how to improve the resume

Think of it as a transparent ATS simulator.

---

## 🧠 How it works

ResumeIQ follows a clean NLP pipeline:

```
Resume + Job Description
→ Text Cleaning
→ Skill Extraction
→ Embeddings
→ Similarity Score
→ Insights
```

### Under the hood:

* 🧹 Text is cleaned and normalized
* 🧩 Skills are extracted using NLP patterns
* 🤖 Sentence-BERT converts text into embeddings
* 📐 Cosine similarity calculates match strength
* 🧾 Rule-based logic generates feedback and missing skill analysis

---

## 🧰 Tech Stack

Built entirely with open-source tools:

* Python – Core language
* Streamlit – UI layer
* spaCy – NLP processing
* NLTK – Text preprocessing
* sentence-transformers – Semantic embeddings
* scikit-learn – Similarity + ML utilities
* PyPDF2 / pdfminer.six – Resume parsing

---

## 📁 Project Structure

```
ResumeIQ/
│
├── app.py                  # Streamlit interface
│
├── nlp/
│   ├── preprocess.py       # Text cleaning pipeline
│   ├── skills.py           # Skill extraction logic
│
├── ml/
│   ├── similarity.py      # Embedding + cosine score
│   ├── classifier.py      # Optional ML layer
│
├── utils/
│   ├── parser.py          # Resume extraction
│   ├── helpers.py         # Utility functions
│
└── assets/
```

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ResumeIQ.git
cd ResumeIQ
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Download spaCy model

```bash
python -m spacy download en_core_web_sm
```

---

## ▶️ Run the app

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

---

## 📊 Sample Output

* **Match Score:** 82%
* **Missing Skills:** Docker, AWS, FastAPI

### Insights:

* Add more backend-related keywords
* Improve project descriptions with measurable impact
* Align skills more closely with job requirements

---

## 🎯 Why this exists

Most ATS tools feel like black boxes.

ResumeIQ tries to change that by:

* Making scoring explainable
* Showing *why* you match or don’t
* Helping users improve their resumes instead of just rejecting them

---

## 🚀 Roadmap

* Drag & drop multiple resumes
* Recruiter dashboard
* Export PDF reports
* Job-wise ranking system
* Cloud deployment (Streamlit / HuggingFace Spaces)

---

## ⚠️ Disclaimer

This project is for educational and demonstration purposes only.
It does not replicate enterprise ATS systems fully.

---

## 👩‍💻 Built by

**Laiba Amjad**


