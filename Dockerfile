FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install torch from PyTorch CPU index
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install other packages from regular PyPI
RUN pip install --no-cache-dir TTS==0.22.0 flask

# Copy app
COPY handler.py .

# Run
CMD ["python", "handler.py"]
