# Use stable Python
FROM python:3.11-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create required directories
RUN mkdir -p web_uploads generated_videos audio_files

# This tells Google SDK where credentials will be
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json

# (Optional but recommended fallback)
ENV GOOGLE_CLOUD_PROJECT=your-project-id

# Expose port
EXPOSE 10000

# Start app
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 2 --threads 2
