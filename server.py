from flask import Flask, request, Response, jsonify
from piper import PiperVoice
from pydub import AudioSegment
import wave
import io
import json
import os
import subprocess
import re
import threading

app = Flask(__name__)

VOICES_DIR = "/voices"
ALIASES_FILE = os.path.join(VOICES_DIR, "aliases.json")

# Built-in voice aliases
BUILTIN_ALIASES = {
    "emma": "en_US-lessac-high",
    "james": "en_US-ryan-high",
    "sophia": "en_GB-cori-high",
    "george": "en_GB-alan-medium",
    "hans": "de_DE-thorsten-high",
    "anna": "de_DE-ramona-low",
    "irina": "ru_RU-irina-medium",
    "dmitri": "ru_RU-dmitri-medium",
}

DEFAULT_VOICE = "emma"

# Custom aliases loaded from file
custom_aliases = {}

# Loaded voices cache
voices = {}
voices_lock = threading.Lock()

def load_custom_aliases():
    """Load custom aliases from file."""
    global custom_aliases
    if os.path.exists(ALIASES_FILE):
        try:
            with open(ALIASES_FILE) as f:
                custom_aliases = json.load(f)
            print(f"Loaded {len(custom_aliases)} custom aliases")
        except Exception as e:
            print(f"Failed to load aliases: {e}")
            custom_aliases = {}
    else:
        custom_aliases = {}

def save_custom_aliases():
    """Save custom aliases to file."""
    try:
        with open(ALIASES_FILE, "w") as f:
            json.dump(custom_aliases, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save aliases: {e}")
        return False

def get_all_aliases():
    """Get merged aliases (custom overrides builtin)."""
    merged = dict(BUILTIN_ALIASES)
    merged.update(custom_aliases)
    return merged

def get_reverse_aliases():
    """Get reverse mapping (model -> alias)."""
    aliases = get_all_aliases()
    return {v: k for k, v in aliases.items()}

def get_voice_metadata(model_name):
    """Extract language and gender from model name or config."""
    json_path = os.path.join(VOICES_DIR, f"{model_name}.onnx.json")
    language = "unknown"
    gender = "unknown"

    # Parse from model name (e.g., en_US-lessac-high)
    match = re.match(r"([a-z]{2})_([A-Z]{2})-", model_name)
    if match:
        language = f"{match.group(1)}-{match.group(2)}"

    # Try to get more info from config
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                config = json.load(f)
                if "language" in config:
                    lang = config["language"]
                    language = f"{lang.get('code', language)}"
        except:
            pass

    return {"language": language, "gender": gender}

def discover_voices():
    """Discover all available voice models in VOICES_DIR."""
    discovered = {}
    if not os.path.exists(VOICES_DIR):
        return discovered

    for filename in os.listdir(VOICES_DIR):
        if filename.endswith(".onnx") and not filename.endswith(".onnx.json"):
            model_name = filename[:-5]  # Remove .onnx
            discovered[model_name] = get_voice_metadata(model_name)

    return discovered

def load_voice(model_name):
    """Load a voice model, return PiperVoice or None."""
    model_path = os.path.join(VOICES_DIR, f"{model_name}.onnx")
    if not os.path.exists(model_path):
        return None

    with voices_lock:
        if model_name not in voices:
            try:
                voices[model_name] = PiperVoice.load(model_path)
                print(f"Loaded voice: {model_name}")
            except Exception as e:
                print(f"Failed to load voice {model_name}: {e}")
                return None
        return voices[model_name]

def resolve_voice(voice_param):
    """Resolve voice alias or model name to model name."""
    aliases = get_all_aliases()
    if voice_param in aliases:
        return aliases[voice_param]
    return voice_param

def download_voice(model_name):
    """Download a voice model from Hugging Face."""
    # Parse model name (e.g., en_US-lessac-high)
    match = re.match(r"([a-z]{2})_([A-Z]{2})-([a-z0-9_]+)-([a-z_]+)", model_name)
    if not match:
        return False, "Invalid model name format. Expected: lang_REGION-name-quality"

    lang_code = match.group(1)
    region = match.group(2)
    name = match.group(3)
    quality = match.group(4)

    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
    url_path = f"{lang_code}/{lang_code}_{region}/{name}/{quality}/{model_name}"

    onnx_url = f"{base_url}/{url_path}.onnx"
    json_url = f"{base_url}/{url_path}.onnx.json"

    onnx_path = os.path.join(VOICES_DIR, f"{model_name}.onnx")
    json_path = os.path.join(VOICES_DIR, f"{model_name}.onnx.json")

    try:
        # Download ONNX model
        result = subprocess.run(
            ["curl", "-L", "-f", "-o", onnx_path, onnx_url],
            capture_output=True, timeout=300
        )
        if result.returncode != 0:
            return False, f"Failed to download model: {result.stderr.decode()}"

        # Download JSON config
        result = subprocess.run(
            ["curl", "-L", "-f", "-o", json_path, json_url],
            capture_output=True, timeout=60
        )
        if result.returncode != 0:
            os.remove(onnx_path)  # Clean up
            return False, f"Failed to download config: {result.stderr.decode()}"

        return True, "Voice downloaded successfully"
    except Exception as e:
        return False, str(e)

# Initialize
def init():
    print("Initializing Piper TTS server...")
    load_custom_aliases()
    print("Pre-loading configured voices...")
    for alias, model_name in get_all_aliases().items():
        voice = load_voice(model_name)
        if voice:
            print(f"  {alias} -> {model_name}: OK")
        else:
            print(f"  {alias} -> {model_name}: NOT FOUND")

init()

@app.route("/", methods=["POST"])
def synthesize():
    data = json.loads(request.data)
    text = data.get("text", "")
    voice_param = data.get("voice", DEFAULT_VOICE)
    output_format = data.get("format", "wav")

    model_name = resolve_voice(voice_param)
    voice = load_voice(model_name)

    if voice is None:
        return jsonify({
            "error": f"Voice not found: {voice_param}",
            "hint": "Use GET /voices to list available voices, or POST /voices/download to add new ones"
        }), 400

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
    discovered = discover_voices()
    reverse_aliases = get_reverse_aliases()

    voice_list = []
    for model_name, meta in discovered.items():
        alias = reverse_aliases.get(model_name)
        is_builtin = model_name in BUILTIN_ALIASES.values()
        voice_list.append({
            "model": model_name,
            "alias": alias,
            "language": meta["language"],
            "loaded": model_name in voices,
            "builtin": is_builtin,
        })

    # Sort by alias (aliased first), then model name
    voice_list.sort(key=lambda v: (v["alias"] is None, v["alias"] or v["model"]))

    return jsonify({
        "voices": voice_list,
        "default": DEFAULT_VOICE,
        "total": len(voice_list),
        "loaded": len(voices),
    })

@app.route("/voices/download", methods=["POST"])
def download_voice_endpoint():
    data = json.loads(request.data)
    model_name = data.get("model")
    alias = data.get("alias")  # Optional alias to set

    if not model_name:
        return jsonify({"error": "Missing 'model' parameter"}), 400

    # Check if already exists
    model_path = os.path.join(VOICES_DIR, f"{model_name}.onnx")
    already_exists = os.path.exists(model_path)

    if not already_exists:
        success, message = download_voice(model_name)
        if not success:
            return jsonify({"error": message}), 400

    # Set alias if provided
    if alias:
        custom_aliases[alias] = model_name
        save_custom_aliases()

    return jsonify({
        "status": "exists" if already_exists else "downloaded",
        "model": model_name,
        "alias": alias,
    })

@app.route("/aliases", methods=["GET"])
def list_aliases():
    return jsonify({
        "builtin": BUILTIN_ALIASES,
        "custom": custom_aliases,
        "merged": get_all_aliases(),
    })

@app.route("/aliases", methods=["POST"])
def set_alias():
    data = json.loads(request.data)
    alias = data.get("alias")
    model = data.get("model")

    if not alias or not model:
        return jsonify({"error": "Missing 'alias' or 'model' parameter"}), 400

    # Validate model exists
    model_path = os.path.join(VOICES_DIR, f"{model}.onnx")
    if not os.path.exists(model_path):
        return jsonify({"error": f"Model not found: {model}"}), 400

    custom_aliases[alias] = model
    if save_custom_aliases():
        return jsonify({"status": "created", "alias": alias, "model": model})
    else:
        return jsonify({"error": "Failed to save alias"}), 500

@app.route("/aliases/<alias>", methods=["DELETE"])
def delete_alias(alias):
    if alias in BUILTIN_ALIASES:
        return jsonify({"error": "Cannot delete built-in alias"}), 400

    if alias not in custom_aliases:
        return jsonify({"error": "Alias not found"}), 404

    del custom_aliases[alias]
    if save_custom_aliases():
        return jsonify({"status": "deleted", "alias": alias})
    else:
        return jsonify({"error": "Failed to save"}), 500

@app.route("/aliases/reload", methods=["POST"])
def reload_aliases():
    load_custom_aliases()
    return jsonify({"status": "reloaded", "custom_aliases": len(custom_aliases)})

@app.route("/voices/<model_name>", methods=["DELETE"])
def delete_voice(model_name):
    # Don't allow deleting pre-configured voices
    if model_name in BUILTIN_ALIASES.values():
        return jsonify({"error": "Cannot delete built-in voice"}), 400

    onnx_path = os.path.join(VOICES_DIR, f"{model_name}.onnx")
    json_path = os.path.join(VOICES_DIR, f"{model_name}.onnx.json")

    if not os.path.exists(onnx_path):
        return jsonify({"error": "Voice not found"}), 404

    # Unload from memory
    with voices_lock:
        if model_name in voices:
            del voices[model_name]

    # Remove any custom aliases pointing to this model
    aliases_to_remove = [k for k, v in custom_aliases.items() if v == model_name]
    for alias in aliases_to_remove:
        del custom_aliases[alias]
    if aliases_to_remove:
        save_custom_aliases()

    # Delete files
    os.remove(onnx_path)
    if os.path.exists(json_path):
        os.remove(json_path)

    return jsonify({"status": "deleted", "model": model_name, "aliases_removed": aliases_to_remove})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "voices_loaded": len(voices)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
