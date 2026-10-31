# ResumeIQ - Streamlit web server + application code
# Image: laibaaamjad/resumeiq:v1  (pushed to Docker Hub)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf \
    NLTK_DATA=/usr/local/share/nltk_data

WORKDIR /app

# curl is used by the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# CPU-only PyTorch keeps the image ~1.5 GB instead of ~5 GB (no CUDA on EC2 anyway)
RUN pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# Python dependencies (layer cached unless requirements change)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Bake the NLP models into the image so containers start fast and offline
RUN python -m nltk.downloader -d $NLTK_DATA punkt punkt_tab stopwords wordnet omw-1.4 \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Application code
COPY . .

EXPOSE 8501

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -fs http://localhost:8501/_stcore/health || exit 1

# Create tables + seed demo user (idempotent), then start the web server
CMD ["sh", "-c", "python db.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true"]
