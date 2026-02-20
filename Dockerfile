FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir piper-tts

# Pre-download voice at build time so container starts instantly
COPY download_voice.py /tmp/download_voice.py
RUN python3 /tmp/download_voice.py && rm /tmp/download_voice.py

EXPOSE 5000

CMD ["python3", "-m", "piper.http_server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--model", "/voices/en_US-lessac-medium.onnx"]
