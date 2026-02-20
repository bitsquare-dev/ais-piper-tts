FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir piper-tts

# Pre-download voice at build time so container starts instantly
RUN python3 -c "
from piper.download import ensure_voice_exists, get_voices
import os
os.makedirs('/voices', exist_ok=True)
voices = get_voices(None, update_voices=True)
ensure_voice_exists('en_US-lessac-medium', ['/voices'], '/voices', voices)
"

EXPOSE 5000

CMD ["python3", "-m", "piper.http_server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--model", "/voices/en_US-lessac-medium.onnx"]
