FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir piper-tts flask pydub

# Pre-download voices at build time
RUN mkdir -p /voices

# English US - Female (emma)
RUN curl -L -o /voices/en_US-lessac-high.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx" && \
    curl -L -o /voices/en_US-lessac-high.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx.json"

# English US - Male (james)
RUN curl -L -o /voices/en_US-ryan-high.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx" && \
    curl -L -o /voices/en_US-ryan-high.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json"

# English UK - Female (sophia)
RUN curl -L -o /voices/en_GB-cori-high.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx" && \
    curl -L -o /voices/en_GB-cori-high.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx.json"

# English UK - Male (george)
RUN curl -L -o /voices/en_GB-alan-medium.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx" && \
    curl -L -o /voices/en_GB-alan-medium.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"

# German - Male (hans)
RUN curl -L -o /voices/de_DE-thorsten-high.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx" && \
    curl -L -o /voices/de_DE-thorsten-high.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"

# German - Female (anna)
RUN curl -L -o /voices/de_DE-ramona-low.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/ramona/low/de_DE-ramona-low.onnx" && \
    curl -L -o /voices/de_DE-ramona-low.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/ramona/low/de_DE-ramona-low.onnx.json"

# Russian - Female (irina)
RUN curl -L -o /voices/ru_RU-irina-medium.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx" && \
    curl -L -o /voices/ru_RU-irina-medium.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json"

# Russian - Male (dmitri)
RUN curl -L -o /voices/ru_RU-dmitri-medium.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx" && \
    curl -L -o /voices/ru_RU-dmitri-medium.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx.json"

# Mark /voices as a volume for persistence of dynamically downloaded voices
VOLUME /voices

COPY server.py /app/server.py
WORKDIR /app

EXPOSE 5000

CMD ["python3", "server.py"]
