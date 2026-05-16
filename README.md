🚀 ResumeIQ

AI-powered resume screening that actually explains itself.

ResumeIQ helps you understand how well a resume matches a job description using NLP and semantic AI.
It doesn’t just give a score. It tells you why.

Built for learners, recruiters, and anyone curious about how ATS systems think.

✨ What it does

Drop in a resume and a job description.

ResumeIQ will:

⚡ Analyze semantic similarity between both
🧠 Extract key skills automatically
📊 Generate a match score (0–100%)
🔍 Highlight missing skills
💡 Suggest how to improve the resume

Think of it as a transparent ATS simulator.

🧠 How it works (simple view)

ResumeIQ follows a clean NLP pipeline:

Resume + Job Description → Text Cleaning → Skill Extraction → Embeddings → Similarity Score → Insights

Under the hood:

🧹 Text is cleaned and normalized
🧩 Skills are extracted using NLP patterns
🤖 Sentence-BERT converts text into embeddings
📐 Cosine similarity calculates match strength
🧾 Rules generate feedback and missing skill analysis
🧰 Tech Stack

Built entirely with open-source tools:

Python – Core language
Streamlit – UI layer
spaCy – NLP processing
NLTK – Text preprocessing
sentence-transformers – Semantic embeddings
scikit-learn – Similarity + ML utilities
PyPDF2 / pdfminer.six – Resume parsing
📁 Architecture
ResumeIQ
│
├── app.py                  → Streamlit interface
├── nlp/
│   ├── preprocess.py       → text cleaning pipeline
│   ├── skills.py          → skill extraction logic
│
├── ml/
│   ├── similarity.py       → embedding + cosine score
│   ├── classifier.py       → optional ML layer
│
├── utils/
│   ├── parser.py           → resume extraction
│   ├── helpers.py          → utilities
│
└── assets/
⚙️ Getting Started
1. Clone the project
git clone https://github.com/your-username/ResumeIQ.git
cd ResumeIQ
2. Create environment
python -m venv venv

Activate it:

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Install NLP model
python -m spacy download en_core_web_sm
▶️ Run it
streamlit run app.py

Then open the local link in your browser.

📊 Sample Output
Match Score: 82%
Missing Skills: Docker, AWS, FastAPI
Insights:
Add more backend-related keywords
Improve project descriptions with impact metrics
Align skills with job requirements more closely
🎯 Why this exists

Most ATS tools feel like black boxes.

ResumeIQ tries to fix that by:

Making scoring explainable
Showing why you match or don’t
Helping users actually improve their resumes
🚀 Roadmap
Drag & drop multiple resumes
Recruiter dashboard
Export PDF reports
Job-wise ranking system
Cloud deployment (Streamlit / HF Spaces)
⚠️ Disclaimer

This project is for learning and demonstration purposes. It does not replicate enterprise ATS systems fully.

👩‍💻 Built by

Laiba Amjad
