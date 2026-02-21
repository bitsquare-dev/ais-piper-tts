# Piper TTS Server

A containerized Text-to-Speech API server using [Piper TTS](https://github.com/rhasspy/piper). Supports multiple voices, MP3/WAV output, and dynamic voice management.

## Features

- Multiple pre-configured voices (English, German, Russian)
- WAV and MP3 output formats
- Dynamic voice downloading at runtime
- Custom voice aliases
- Health check endpoint
- Volume support for voice persistence

## Pre-configured Voices

| Alias | Model | Language | Gender |
|-------|-------|----------|--------|
| `emma` | en_US-lessac-high | English US | Female |
| `james` | en_US-ryan-high | English US | Male |
| `sophia` | en_GB-cori-high | English UK | Female |
| `george` | en_GB-alan-medium | English UK | Male |
| `hans` | de_DE-thorsten-high | German | Male |
| `anna` | de_DE-ramona-low | German | Female |
| `irina` | ru_RU-irina-medium | Russian | Female |
| `dmitri` | ru_RU-dmitri-medium | Russian | Male |

## API Endpoints

### Synthesize Speech

```
POST /
```

**Request Body:**
```json
{
  "text": "Hello world",
  "voice": "emma",
  "format": "wav"
}
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `text` | Yes | - | Text to synthesize |
| `voice` | No | `emma` | Voice alias or model name |
| `format` | No | `wav` | Output format: `wav` or `mp3` |

**Response:** Audio file (audio/wav or audio/mpeg)

**Example:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Hello world", "voice":"james", "format":"mp3"}' \
  http://localhost:5000 --output speech.mp3
```

### List Voices

```
GET /voices
```

Returns all available voices with their aliases and load status.

**Example:**
```bash
curl http://localhost:5000/voices
```

### Download Voice

```
POST /voices/download
```

Download a new voice from Hugging Face.

**Request Body:**
```json
{
  "model": "es_ES-davefx-medium",
  "alias": "carlos"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `model` | Yes | Voice model name |
| `alias` | No | Optional alias to assign |

**Example:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"model":"fr_FR-upmc-medium", "alias":"pierre"}' \
  http://localhost:5000/voices/download
```

### Delete Voice

```
DELETE /voices/<model_name>
```

Delete a dynamically added voice (built-in voices cannot be deleted).

**Example:**
```bash
curl -X DELETE http://localhost:5000/voices/es_ES-davefx-medium
```

### List Aliases

```
GET /aliases
```

Returns built-in and custom aliases.

**Example:**
```bash
curl http://localhost:5000/aliases
```

### Create Alias

```
POST /aliases
```

**Request Body:**
```json
{
  "alias": "maria",
  "model": "es_ES-sharvard-medium"
}
```

**Example:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"alias":"maria", "model":"es_ES-sharvard-medium"}' \
  http://localhost:5000/aliases
```

### Delete Alias

```
DELETE /aliases/<alias>
```

Delete a custom alias (built-in aliases cannot be deleted).

**Example:**
```bash
curl -X DELETE http://localhost:5000/aliases/maria
```

### Reload Aliases

```
POST /aliases/reload
```

Reload aliases from the config file (useful after manual edits).

**Example:**
```bash
curl -X POST http://localhost:5000/aliases/reload
```

### Health Check

```
GET /health
```

**Example:**
```bash
curl http://localhost:5000/health
```

## Deployment

### Docker

```bash
docker build -t piper-tts .
docker run -p 5000:5000 -v piper-voices:/voices piper-tts
```

### Coolify

1. Create a new service from this repository
2. Set the exposed port to `5000`
3. Add a volume mount: `piper-voices:/voices` (for voice persistence)
4. Deploy

## Voice Naming Convention

Piper voices follow this naming format:
```
{lang}_{REGION}-{name}-{quality}
```

Examples:
- `en_US-lessac-high`
- `de_DE-thorsten-medium`
- `fr_FR-upmc-medium`

Quality levels: `x_low`, `low`, `medium`, `high`

Browse all available voices: https://huggingface.co/rhasspy/piper-voices

## Custom Aliases File

Custom aliases are stored in `/voices/aliases.json`:

```json
{
  "maria": "es_ES-sharvard-medium",
  "pierre": "fr_FR-upmc-medium"
}
```

This file is persisted in the `/voices` volume and survives container restarts.

## License

Piper TTS is licensed under MIT. See [rhasspy/piper](https://github.com/rhasspy/piper) for details.
