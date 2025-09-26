FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch and torchaudio FIRST
RUN pip install --no-cache-dir \
    torch==2.0.1+cpu \
    torchaudio==2.0.2+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Then install TTS and flask
RUN pip install --no-cache-dir TTS flask

# Copy app
COPY handler.py .

# Set environment variable to force CPU
ENV CUDA_VISIBLE_DEVICES=""

# Run
CMD ["python", "handler.py"]
