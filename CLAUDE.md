# Claude Instructions

Guidelines for working on this deployment repository.

## Workflow

1. After each modification, commit and push changes
2. User will redeploy via Coolify to test

## Documentation

All documentation belongs in `README.md`:
- Features and capabilities
- API endpoints with examples
- Environment variables
- Configuration parameters
- External resources and URLs
- Deployment instructions

## Repository Structure

```
├── Dockerfile      # Container build definition
├── server.py       # Main application code
├── README.md       # User-facing documentation
└── CLAUDE.md       # AI assistant instructions
```

## Key Files

- `Dockerfile` - Defines the container, installs dependencies, downloads pre-configured voices
- `server.py` - Flask server with TTS synthesis and voice management endpoints
- `/voices/` - Runtime directory for voice models and aliases.json (mounted as volume)

## External Resources

- Piper TTS: https://github.com/rhasspy/piper
- Voice models: https://huggingface.co/rhasspy/piper-voices
- Voice samples: https://rhasspy.github.io/piper-samples/

## Coolify Deployment

- Platform: Coolify (self-hosted PaaS)
- Port: 5000
- Volume: `/voices` for persistence of downloaded voices and custom aliases
