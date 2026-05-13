"""Config flow for Piper HTTP TTS integration."""

from __future__ import annotations

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
    LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
    }
)


class PiperHTTPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Piper HTTP TTS."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            LOGGER.info("Config flow: host=%s port=%s", host, port)
            await self.async_set_unique_id(f"{host}_{port}")
            self._abort_if_unique_id_configured()
            options = {
                CONF_MODEL: DEFAULT_MODEL,
                CONF_SPEAKER_ID: DEFAULT_SPEAKER_ID,
                CONF_LENGTH_SCALE: DEFAULT_LENGTH_SCALE,
                CONF_NOISE_SCALE: DEFAULT_NOISE_SCALE,
                CONF_NOISE_W: DEFAULT_NOISE_W,
                CONF_SENTENCE_SILENCE: DEFAULT_SENTENCE_SILENCE,
            }
            LOGGER.info("Config flow: creating entry with options=%s", options)
            return self.async_create_entry(
                title=f"Piper HTTP ({host}:{port})",
                data=user_input,
                options=options,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        LOGGER.info("Options flow: created")
        return PiperHTTPOptionsFlow()


class PiperHTTPOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Piper HTTP TTS."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""

        LOGGER.info("Options flow: async_step_init called")
        LOGGER.info("Options flow: hass=%s", self.hass is not None)
        LOGGER.info("Options flow: config_entry=%s", self.config_entry is not None)

        if self.config_entry is not None:
            LOGGER.info("Options flow: data=%s", self.config_entry.data)
            LOGGER.info("Options flow: options=%s", self.config_entry.options)

        host = self.config_entry.data[CONF_HOST]
        port = self.config_entry.data[CONF_PORT]
        LOGGER.info("Options flow: host=%s port=%s", host, port)

        # Build model options from FALLBACK_MODELS (static, no HTTP)
        models_dict: dict[str, str] = {}
        LOGGER.info("Options flow: FALLBACK_MODELS has %d entries", len(FALLBACK_MODELS))
        for m in FALLBACK_MODELS:
            label = m.get("label", m["file"])
            LOGGER.info("Options flow: adding model %s = %s", m["file"], label)
            models_dict[m["file"]] = label

        current_model = self.config_entry.options.get(CONF_MODEL, DEFAULT_MODEL)
        LOGGER.info("Options flow: current_model=%s", current_model)
        LOGGER.info("Options flow: models_dict keys=%s", list(models_dict.keys()))

        schema = vol.Schema(
            {
                vol.Optional(CONF_MODEL, default=current_model): vol.In(models_dict),
                vol.Optional(
                    CONF_SPEAKER_ID,
                    default=self.config_entry.options.get(CONF_SPEAKER_ID, DEFAULT_SPEAKER_ID),
                ): vol.All(int, vol.Range(min=0, max=10)),
                vol.Optional(
                    CONF_LENGTH_SCALE,
                    default=self.config_entry.options.get(CONF_LENGTH_SCALE, DEFAULT_LENGTH_SCALE),
                ): vol.All(float, vol.Range(min=0.3, max=3.0)),
                vol.Optional(
                    CONF_NOISE_SCALE,
                    default=self.config_entry.options.get(CONF_NOISE_SCALE, DEFAULT_NOISE_SCALE),
                ): vol.All(float, vol.Range(min=0.0, max=2.0)),
                vol.Optional(
                    CONF_NOISE_W,
                    default=self.config_entry.options.get(CONF_NOISE_W, DEFAULT_NOISE_W),
                ): vol.All(float, vol.Range(min=0.0, max=2.0)),
                vol.Optional(
                    CONF_SENTENCE_SILENCE,
                    default=self.config_entry.options.get(CONF_SENTENCE_SILENCE, DEFAULT_SENTENCE_SILENCE),
                ): vol.All(float, vol.Range(min=0.0, max=10.0)),
            }
        )

        LOGGER.info("Options flow: schema built, about to show form")

        if user_input is not None:
            LOGGER.info("Options flow: user_input=%s", user_input)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
