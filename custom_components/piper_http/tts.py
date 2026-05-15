"""TTS platform for Piper HTTP TTS integration."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlencode

from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DENGLISCH,
    CONF_HOST,
    CONF_LENGTH_SCALE,
    CONF_MODEL,
    CONF_NOISE_SCALE,
    CONF_NOISE_W,
    CONF_PORT,
    CONF_SENTENCE_SILENCE,
    CONF_SPEAKER_ID,
    DEFAULT_DENGLISCH,
    DEFAULT_LENGTH_SCALE,
    DEFAULT_MODEL,
    DEFAULT_NOISE_SCALE,
    DEFAULT_NOISE_W,
    DEFAULT_SENTENCE_SILENCE,
    DEFAULT_SPEAKER_ID,
    DOMAIN,
    ENDPOINT_TTS,
    ENDPOINT_VOICE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Piper HTTP TTS entities."""
    _LOGGER.warning("TTS async_setup_entry called")
    async_add_entities([PiperHTTPProvider(config_entry)])


class PiperHTTPProvider(TextToSpeechEntity):
    """Piper HTTP TTS entity."""

    _attr_name = "Piper HTTP TTS"
    _attr_has_entity_name = True
    _attr_supported_languages = ["de", "en"]
    _attr_default_language = "de"

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the Piper HTTP TTS entity."""
        super().__init__()
        _LOGGER.warning("PiperHTTPProvider.__init__")
        self._config_entry = config_entry
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data[CONF_PORT]
        self._base_url = f"http://{self._host}:{self._port}"
        self._attr_unique_id = f"{self._host}_{self._port}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": f"Piper HTTP TTS ({self._host}:{self._port})",
            "manufacturer": "Piper",
            "model": "Piper TTS Server",
            "sw_version": "0.1.0",
        }
        self._current_model: str | None = None

    def _build_tts_params(self, message: str) -> dict[str, str]:
        """Build query parameters for the TTS request."""
        options = self._config_entry.options
        params: dict[str, str] = {"text": message}

        # Denglisch-Wortersetzungen (optional)
        if self._config_entry.options.get(CONF_DENGLISCH, DEFAULT_DENGLISCH):
            params["denglisch"] = "true"

        # Send model — server now switches per request
        model = options.get(CONF_MODEL, DEFAULT_MODEL)
        if model:
            model_name = model.split(".onnx")[0] + ".onnx"
            params["model"] = model_name

        speaker_id = options.get(CONF_SPEAKER_ID, DEFAULT_SPEAKER_ID)
        if speaker_id != DEFAULT_SPEAKER_ID:
            params["speaker_id"] = str(speaker_id)

        length_scale = options.get(CONF_LENGTH_SCALE, DEFAULT_LENGTH_SCALE)
        if length_scale != DEFAULT_LENGTH_SCALE:
            params["length_scale"] = f"{length_scale:.3f}"

        noise_scale = options.get(CONF_NOISE_SCALE, DEFAULT_NOISE_SCALE)
        if noise_scale != DEFAULT_NOISE_SCALE:
            params["noise_scale"] = f"{noise_scale:.3f}"

        noise_w = options.get(CONF_NOISE_W, DEFAULT_NOISE_W)
        if noise_w != DEFAULT_NOISE_W:
            params["noise_w"] = f"{noise_w:.3f}"

        sentence_silence = options.get(CONF_SENTENCE_SILENCE, DEFAULT_SENTENCE_SILENCE)
        if sentence_silence != DEFAULT_SENTENCE_SILENCE:
            params["sentence_silence"] = f"{sentence_silence:.2f}"

        return params

    async def async_added_to_hass(self) -> None:
        """Load the configured model on the server when HA starts."""
        await super().async_added_to_hass()
        desired_model = self._config_entry.options.get(CONF_MODEL, DEFAULT_MODEL)
        if desired_model:
            await self._switch_model(desired_model)

    async def async_get_tts_audio(
        self,
        message: str,
        language: str,
        options: dict[str, Any] | None = None,
    ) -> tuple[str | None, bytes | None]:
        """Load TTS audio from the piper-http server.

        The configured model is sent as a query parameter so the
        server switches automatically on each request.
        Returns a tuple of (extension, audio_data) or (None, None) on error.
        """
        params = self._build_tts_params(message)
        query = urlencode(params)
        url = f"{self._base_url}{ENDPOINT_TTS}?{query}"
        _LOGGER.debug("Fetching TTS audio: %s (text='%s')", url, message[:50])

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, timeout=30) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    _LOGGER.error(
                        "Piper HTTP returned %s: %s", resp.status, error_text
                    )
                    return (None, None)

                audio_data = await resp.read()
                content_type = resp.headers.get("Content-Type", "audio/wav")

        except Exception as err:
            _LOGGER.error("Error fetching TTS audio from %s: %s", url, err)
            return (None, None)

        ext = "ogg" if "ogg" in content_type else "wav"
        return (ext, audio_data)

    async def async_update_options(self, config_entry: ConfigEntry) -> None:
        """Update entity when options change."""
        old_model = self._config_entry.options.get(CONF_MODEL)
        new_model = config_entry.options.get(CONF_MODEL)
        self._config_entry = config_entry
        if old_model != new_model:
            await self._switch_model(new_model)

    async def _switch_model(self, model: str) -> None:
        """Switch the active model (and synthesis params) on the piper-http server."""
        import json

        url = f"{self._base_url}{ENDPOINT_VOICE}"
        model_name = model.split(".onnx")[0] + ".onnx"

        # Send all configured synthesis params so the server matches
        options = self._config_entry.options
        payload: dict[str, Any] = {"model": model_name}
        if CONF_SPEAKER_ID in options:
            payload["speaker_id"] = options[CONF_SPEAKER_ID]
        if CONF_LENGTH_SCALE in options:
            payload["length_scale"] = options[CONF_LENGTH_SCALE]
        if CONF_NOISE_SCALE in options:
            payload["noise_scale"] = options[CONF_NOISE_SCALE]
        if CONF_NOISE_W in options:
            payload["noise_w"] = options[CONF_NOISE_W]
        if CONF_SENTENCE_SILENCE in options:
            payload["sentence_silence"] = options[CONF_SENTENCE_SILENCE]

        _LOGGER.info("Switching Piper model to %s (params=%s)", model_name, payload)

        session = async_get_clientsession(self.hass)

        try:
            async with session.post(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            ) as resp:
                if resp.status == 200:
                    _LOGGER.info("Switched Piper model to %s", model)
                    self._current_model = model
                else:
                    _LOGGER.warning(
                        "Failed to switch model: %s %s",
                        resp.status,
                        await resp.text(),
                    )
        except Exception as err:
            _LOGGER.error("Error switching model: %s", err)
