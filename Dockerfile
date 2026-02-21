FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir piper-tts flask pydub

# Pre-download voice at build time so container starts instantly
RUN mkdir -p /voices && \
    curl -L -o /voices/en_US-lessac-medium.onnx \
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx" && \
    curl -L -o /voices/en_US-lessac-medium.onnx.json \
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

COPY server.py /app/server.py
WORKDIR /app

EXPOSE 5000

CMD ["python3", "server.py"]
