FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    TTS==0.22.0 \
    flask \
    torch --index-url https://download.pytorch.org/whl/cpu

# Copy app
COPY handler.py .

# Run
CMD ["python", "handler.py"]
