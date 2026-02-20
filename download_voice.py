#!/usr/bin/env python3
from piper.download import ensure_voice_exists, get_voices
import os

os.makedirs('/voices', exist_ok=True)
voices = get_voices(None, update_voices=True)
ensure_voice_exists('en_US-lessac-medium', ['/voices'], '/voices', voices)
