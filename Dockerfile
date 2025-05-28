# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .  # ✅ Assumes requirements.txt is in frontend/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Run frontend
CMD ["streamlit", "run", "app.py", "--server.port", "80"]