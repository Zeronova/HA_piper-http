"""TTS platform for Piper HTTP TTS integration."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import aiohttp

from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_HOST,
    CONF_LENGTH_SCALE,
    CONF_MODEL,
    CONF_NOISE_SCALE,
    CONF_NOISE_W,
    CONF_PORT,
    CONF_SENTENCE_SILENCE,
    CONF_SPEAKER_ID,
    DEFAULT_LENGTH_SCALE,
    DEFAULT_NOISE_SCALE,
    DEFAULT_NOISE_W,
    DEFAULT_SENTENCE_SILENCE,
    DEFAULT_SPEAKER_ID,
    DOMAIN,
    ENDPOINT_TTS,
    ENDPOINT_VOICE,
    LOGGER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Piper HTTP TTS entities."""
    async_add_entities([PiperHTTPProvider(config_entry)])


class PiperHTTPProvider(TextToSpeechEntity):
    """Piper HTTP TTS entity."""

    _attr_name = "Piper HTTP TTS"
    _attr_has_entity_name = True

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the Piper HTTP TTS entity."""
        super().__init__()
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

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["de", "en"]

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "de"

    def _build_tts_params(self, message: str) -> dict[str, str]:
        """Build query parameters for the TTS request."""
        options = self._config_entry.options
        params: dict[str, str] = {"text": message}

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

    async def async_get_tts_audio(
        self,
        message: str,
        language: str,
        options: dict[str, Any] | None = None,
    ) -> TextToSpeechEntity.TtsAudio:
        """Load TTS audio from the piper-http server."""
        params = self._build_tts_params(message)
        query = urlencode(params)
        url = f"{self._base_url}{ENDPOINT_TTS}?{query}"
        LOGGER.debug("Fetching TTS audio: %s (text='%s')", url, message[:50])

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        LOGGER.error(
                            "Piper HTTP returned %s: %s", resp.status, error_text
                        )
                        return self.TtsAudio(
                            media_id="", ext="wav", data=b""
                        )
                    audio_data = await resp.read()
                    content_type = resp.headers.get("Content-Type", "audio/wav")

        except (aiohttp.ClientError, TimeoutError) as err:
            LOGGER.error("Error fetching TTS audio from %s: %s", url, err)
            return self.TtsAudio(media_id="", ext="wav", data=b"")

        ext = "ogg" if "ogg" in content_type else "wav"
        return self.TtsAudio(media_id="", ext=ext, data=audio_data)

    async def async_update_options(self, config_entry: ConfigEntry) -> None:
        """Update entity when options change."""
        old_model = self._config_entry.options.get(CONF_MODEL)
        new_model = config_entry.options.get(CONF_MODEL)
        self._config_entry = config_entry
        if old_model != new_model:
            await self._switch_model(new_model)

    async def _switch_model(self, model: str) -> None:
        """Switch the active model on the piper-http server."""
        import json

        url = f"{self._base_url}{ENDPOINT_VOICE}"
        model_name = model.split(".onnx")[0] + ".onnx"
        payload = {"model": model_name}
        LOGGER.info("Switching Piper model to %s", model_name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                ) as resp:
                    if resp.status == 200:
                        LOGGER.info("Switched Piper model to %s", model)
                    else:
                        LOGGER.warning(
                            "Failed to switch model: %s %s",
                            resp.status,
                            await resp.text(),
                        )
        except (aiohttp.ClientError, TimeoutError) as err:
            LOGGER.error("Error switching model: %s", err)
