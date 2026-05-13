"""Config flow for Piper HTTP TTS integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HOST,
    CONF_LENGTH_SCALE,
    CONF_MODEL,
    CONF_NOISE_SCALE,
    CONF_NOISE_W,
    CONF_PORT,
    CONF_SENTENCE_SILENCE,
    CONF_SPEAKER_ID,
    DEFAULT_HOST,
    DEFAULT_LENGTH_SCALE,
    DEFAULT_MODEL,
    DEFAULT_NOISE_SCALE,
    DEFAULT_NOISE_W,
    DEFAULT_PORT,
    DEFAULT_SENTENCE_SILENCE,
    DEFAULT_SPEAKER_ID,
    DOMAIN,
    FALLBACK_MODELS,
)

_LOGGER = logging.getLogger(__name__)


class PiperHTTPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Piper HTTP TTS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            _LOGGER.warning("Config flow step_user: host=%s port=%s", user_input.get(CONF_HOST), user_input.get(CONF_PORT))
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(f"{host}_{port}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"{host}:{port}",
                data={CONF_HOST: host, CONF_PORT: port},
                options={
                    CONF_MODEL: DEFAULT_MODEL,
                    CONF_SPEAKER_ID: DEFAULT_SPEAKER_ID,
                    CONF_LENGTH_SCALE: DEFAULT_LENGTH_SCALE,
                    CONF_NOISE_SCALE: DEFAULT_NOISE_SCALE,
                    CONF_NOISE_W: DEFAULT_NOISE_W,
                    CONF_SENTENCE_SILENCE: DEFAULT_SENTENCE_SILENCE,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        _LOGGER.warning("async_get_options_flow called")
        return PiperHTTPOptionsFlow()


class PiperHTTPOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Piper HTTP TTS."""

    async def async_step_init(self, user_input=None):
        """Handle the options step."""
        _LOGGER.warning("async_step_init called")
        _LOGGER.warning("hass=%s config_entry=%s", self.hass is not None, self.config_entry is not None)

        if self.config_entry is not None:
            _LOGGER.warning("data=%s", self.config_entry.data)
            _LOGGER.warning("options=%s", self.config_entry.options)

        host = self.config_entry.data[CONF_HOST]
        port = self.config_entry.data[CONF_PORT]
        _LOGGER.warning("host=%s port=%s", host, port)

        models_dict: dict[str, str] = {}
        _LOGGER.warning("FALLBACK_MODELS has %d entries", len(FALLBACK_MODELS))
        for m in FALLBACK_MODELS:
            label = m.get("label", m["file"])
            _LOGGER.warning("adding model: %s = %s", m["file"], label)
            models_dict[m["file"]] = label

        current_model = self.config_entry.options.get(CONF_MODEL, DEFAULT_MODEL)
        _LOGGER.warning("current_model=%s", current_model)
        _LOGGER.warning("models_dict keys=%s", list(models_dict.keys()))

        schema = vol.Schema(
            {
                vol.Optional(CONF_MODEL, default=current_model): vol.In(models_dict),
                vol.Optional(
                    CONF_SPEAKER_ID,
                    default=self.config_entry.options.get(CONF_SPEAKER_ID, DEFAULT_SPEAKER_ID),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=8)),
                vol.Optional(
                    CONF_LENGTH_SCALE,
                    default=self.config_entry.options.get(CONF_LENGTH_SCALE, DEFAULT_LENGTH_SCALE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=5.0)),
                vol.Optional(
                    CONF_NOISE_SCALE,
                    default=self.config_entry.options.get(CONF_NOISE_SCALE, DEFAULT_NOISE_SCALE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
                vol.Optional(
                    CONF_NOISE_W,
                    default=self.config_entry.options.get(CONF_NOISE_W, DEFAULT_NOISE_W),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
                vol.Optional(
                    CONF_SENTENCE_SILENCE,
                    default=self.config_entry.options.get(CONF_SENTENCE_SILENCE, DEFAULT_SENTENCE_SILENCE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=10.0)),
            }
        )

        _LOGGER.warning("schema built, about to show form")

        if user_input is not None:
            _LOGGER.warning("user_input=%s", user_input)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=schema)
