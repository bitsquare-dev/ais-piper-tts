from flask import Flask, request, Response, jsonify
from piper import PiperVoice
from pydub import AudioSegment
import wave
import io
import json

app = Flask(__name__)

# Voice configuration: alias -> (model_path, language, gender)
VOICE_CONFIG = {
    # English US
    "emma": {"model": "en_US-lessac-high", "language": "en-US", "gender": "female"},
    "james": {"model": "en_US-ryan-high", "language": "en-US", "gender": "male"},
    # English UK
    "sophia": {"model": "en_GB-cori-high", "language": "en-GB", "gender": "female"},
    "george": {"model": "en_GB-alan-medium", "language": "en-GB", "gender": "male"},
    # German
    "hans": {"model": "de_DE-thorsten-high", "language": "de-DE", "gender": "male"},
    "anna": {"model": "de_DE-ramona-low", "language": "de-DE", "gender": "female"},
    # Russian
    "irina": {"model": "ru_RU-irina-medium", "language": "ru-RU", "gender": "female"},
    "dmitri": {"model": "ru_RU-dmitri-medium", "language": "ru-RU", "gender": "male"},
}

DEFAULT_VOICE = "emma"

# Load all voices at startup
voices = {}
for alias, config in VOICE_CONFIG.items():
    model_path = f"/voices/{config['model']}.onnx"
    try:
        voices[alias] = PiperVoice.load(model_path)
        print(f"Loaded voice: {alias} ({config['model']})")
    except Exception as e:
        print(f"Failed to load voice {alias}: {e}")

@app.route("/", methods=["POST"])
def synthesize():
    data = json.loads(request.data)
    text = data.get("text", "")
    voice_alias = data.get("voice", DEFAULT_VOICE)
    output_format = data.get("format", "wav")

    if voice_alias not in voices:
        return jsonify({"error": f"Unknown voice: {voice_alias}", "available": list(voices.keys())}), 400

    voice = voices[voice_alias]

    # Generate WAV to buffer
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    wav_io.seek(0)

    if output_format == "mp3":
        audio = AudioSegment.from_wav(wav_io)
        mp3_io = io.BytesIO()
        audio.export(mp3_io, format="mp3")
        mp3_io.seek(0)
        return Response(mp3_io.getvalue(), mimetype="audio/mpeg")

    return Response(wav_io.getvalue(), mimetype="audio/wav")

@app.route("/voices", methods=["GET"])
def list_voices():
    available = []
    for alias, config in VOICE_CONFIG.items():
        if alias in voices:
            available.append({
                "alias": alias,
                "model": config["model"],
                "language": config["language"],
                "gender": config["gender"],
            })
    return jsonify({"voices": available, "default": DEFAULT_VOICE})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "voices_loaded": len(voices)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
