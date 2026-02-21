from flask import Flask, request, Response
from piper import PiperVoice
from pydub import AudioSegment
import wave
import io
import json
import struct

app = Flask(__name__)
voice = PiperVoice.load("/voices/en_US-lessac-medium.onnx")

@app.route("/", methods=["POST"])
def synthesize():
    data = json.loads(request.data)
    text = data.get("text", "")
    output_format = data.get("format", "wav")

    # Collect audio from synthesize_stream_raw
    audio_bytes = b""
    for chunk in voice.synthesize_stream_raw(text):
        audio_bytes += chunk

    # Create WAV in memory
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(voice.config.sample_rate)
        wav_file.writeframes(audio_bytes)
    wav_io.seek(0)

    if output_format == "mp3":
        audio = AudioSegment.from_wav(wav_io)
        mp3_io = io.BytesIO()
        audio.export(mp3_io, format="mp3")
        mp3_io.seek(0)
        return Response(mp3_io.getvalue(), mimetype="audio/mpeg")

    return Response(wav_io.getvalue(), mimetype="audio/wav")

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
