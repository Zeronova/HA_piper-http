"""Config flow for Piper HTTP TTS integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector

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
    ENDPOINT_MODELS,
    FALLBACK_MODELS,
    LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
    }
)


async def _fetch_models(hass, host: str, port: int) -> list[dict]:
    """Fetch available models from the piper-http server.

    Returns a list of model dicts with at least 'file' and 'label' keys.
    Falls back to FALLBACK_MODELS if the server is unreachable.
    """
    url = f"http://{host}:{port}{ENDPOINT_MODELS}"
    session = async_get_clientsession(hass)
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                LOGGER.warning("fetch_models returned HTTP %s – using fallback", resp.status)
                return list(FALLBACK_MODELS)
            data = await resp.json()

            on_disk = data.get("on_disk", [])
            if on_disk:
                return [
                    {"file": m["file"], "label": m["file"].replace(".onnx", "")}
                    for m in on_disk
                ]

            well_known = data.get("well_known", [])
            if well_known:
                return [
                    {"file": f"{m['name']}.onnx", "label": f"{m['label']}"}
                    for m in well_known
                ]

            return list(FALLBACK_MODELS)
    except Exception as err:
        LOGGER.warning("Could not fetch models: %s – using fallback", err)
        return list(FALLBACK_MODELS)


def _model_options(models: list[dict]) -> dict[str, str]:
    """Return a {file: label} dict for vol.In."""
    return {m["file"]: m.get("label", m["file"]) for m in models}


class PiperHTTPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Piper HTTP TTS."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            models = await _fetch_models(self.hass, host, port)
            if not models:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}_{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Piper HTTP ({host}:{port})",
                    data=user_input,
                    options={
                        CONF_MODEL: models[0]["file"],
                        CONF_SPEAKER_ID: DEFAULT_SPEAKER_ID,
                        CONF_LENGTH_SCALE: DEFAULT_LENGTH_SCALE,
                        CONF_NOISE_SCALE: DEFAULT_NOISE_SCALE,
                        CONF_NOISE_W: DEFAULT_NOISE_W,
                        CONF_SENTENCE_SILENCE: DEFAULT_SENTENCE_SILENCE,
                    },
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
        return PiperHTTPOptionsFlow()


class PiperHTTPOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Piper HTTP TTS."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        host = self.config_entry.data[CONF_HOST]
        port = self.config_entry.data[CONF_PORT]

        LOGGER.debug("Piper HTTP options: host=%s port=%s", host, port)

        models = await _fetch_models(self.hass, host, port)
        models_dict = _model_options(models)

        current_model = self.config_entry.options.get(
            CONF_MODEL,
            list(models_dict.keys())[0],
        )

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

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
