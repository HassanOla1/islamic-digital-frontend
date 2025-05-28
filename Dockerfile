# Dockerfile
FROM python:3.10

WORKDIR /app

# Install system dependencies required by Pillow and Streamlit
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Run Streamlit with correct command
CMD ["streamlit", "run", "app.py", "--server.port", "80"]