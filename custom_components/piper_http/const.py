"""Constants for the Piper HTTP TTS integration."""

from __future__ import annotations

import logging

DOMAIN = "piper_http"
LOGGER = logging.getLogger(__package__)

# Config keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_MODEL = "model"
CONF_SPEAKER_ID = "speaker_id"
CONF_LENGTH_SCALE = "length_scale"
CONF_NOISE_SCALE = "noise_scale"
CONF_NOISE_W = "noise_w"
CONF_SENTENCE_SILENCE = "sentence_silence"
CONF_OUTPUT_FORMAT = "output_format"
CONF_DENGLISCH = "denglisch"

# Defaults
DEFAULT_HOST = "192.168.2.7"
DEFAULT_PORT = 5000
DEFAULT_MODEL = "de_DE-thorsten-high.onnx"
DEFAULT_SPEAKER_ID = 1
DEFAULT_LENGTH_SCALE = 1.0
DEFAULT_NOISE_SCALE = 0.667
DEFAULT_NOISE_W = 0.8
DEFAULT_SENTENCE_SILENCE = 0.0
DEFAULT_DENGLISCH = True

# API endpoints
ENDPOINT_TTS = "/"
ENDPOINT_VOICE = "/voice"
ENDPOINT_MODELS = "/models"

# Fallback model list (known Piper voices) used when the server
# cannot be reached during config/options flow.
# Each entry: {"file": "name.onnx", "label": "Display Name"}
FALLBACK_MODELS: list[dict[str, str]] = [
    {"file": "de_DE-thorsten-high.onnx", "label": "Thorsten (High) — Deutsch"},
    {"file": "de_DE-thorsten-medium.onnx", "label": "Thorsten (Medium) — Deutsch"},
    {"file": "de_DE-thorsten-low.onnx", "label": "Thorsten (Low) — Deutsch"},
    {"file": "de_DE-jarvis-high.onnx", "label": "Jarvis (High) — Deutsch"},
    {"file": "de_DE-eva_k-x-low.onnx", "label": "Eva K. (X-Low) — Deutsch"},
    {"file": "de_DE-kerstin-low.onnx", "label": "Kerstin (Low) — Deutsch"},
    {"file": "de_DE-mls-medium.onnx", "label": "MLS (Medium) — Deutsch"},
    {"file": "de_DE-pavoque-low.onnx", "label": "Pavoque (Low) — Deutsch"},
    {"file": "de_DE-ramona-low.onnx", "label": "Ramona (Low) — Deutsch"},
    {"file": "de_DE-glados-high.onnx", "label": "GLaDOS (High) — Deutsch"},
    {"file": "de_DE-glados-turret-high.onnx", "label": "GLaDOS Turret (High) — Deutsch"},
    {"file": "de_DE-thorsten-tesslow.onnx", "label": "Thorsten (Tesseract) — Deutsch"},
    {"file": "en_GB-alan-low.onnx", "label": "Alan (Low) — English GB"},
    {"file": "en_GB-alan-medium.onnx", "label": "Alan (Medium) — English GB"},
    {"file": "en_US-amy-low.onnx", "label": "Amy (Low) — English US"},
    {"file": "en_US-amy-medium.onnx", "label": "Amy (Medium) — English US"},
    {"file": "en_US-lessac-medium.onnx", "label": "Lessac (Medium) — English US"},
    {"file": "en_US-lessac-high.onnx", "label": "Lessac (High) — English US"},
    {"file": "en_US-libritts-high.onnx", "label": "LibriTTS (High) — English US"},
]

# All model names used as selector options
MODEL_OPTIONS: list[str] = [m["file"] for m in FALLBACK_MODELS]
