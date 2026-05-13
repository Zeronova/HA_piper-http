"""Constants for the Piper HTTP TTS integration."""

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

# Defaults
DEFAULT_HOST = "192.168.2.7"
DEFAULT_PORT = 5000
DEFAULT_MODEL = ""
DEFAULT_SPEAKER_ID = 1
DEFAULT_LENGTH_SCALE = 1.0
DEFAULT_NOISE_SCALE = 0.667
DEFAULT_NOISE_W = 0.8
DEFAULT_SENTENCE_SILENCE = 0.0

# API endpoints
ENDPOINT_TTS = "/"
ENDPOINT_VOICE = "/voice"
ENDPOINT_MODELS = "/models"
