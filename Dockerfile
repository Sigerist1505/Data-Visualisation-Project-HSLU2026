FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (full stack: Streamlit + Jupyter)
COPY requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

# Copy project files (.dockerignore excludes venv, video, temp files)
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Streamlit (8501) + Jupyter (8888)
EXPOSE 8501 8888

CMD ["./start.sh"]
