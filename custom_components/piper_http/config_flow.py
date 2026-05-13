"""Config flow for Piper HTTP TTS integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
    LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
    }
)


async def fetch_models(hass, host: str, port: int) -> list[dict]:
    """Fetch available models from the piper-http server.

    Returns a list of model dicts with at least a 'file' key.
    Falls back to well_known voices when on_disk is empty.
    """
    url = f"http://{host}:{port}{ENDPOINT_MODELS}"
    session = async_get_clientsession(hass)
    models: list[dict] = []
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status != 200:
                LOGGER.warning("fetch_models returned HTTP %s from %s", resp.status, url)
                return []
            data = await resp.json()
            # Prefer on-disk models (already downloaded)
            on_disk = data.get("on_disk", [])
            if on_disk:
                models = on_disk
            else:
                # Fall back to well-known Piper voices with .onnx suffix
                well_known = data.get("well_known", [])
                models = [
                    {"file": f"{m['name']}.onnx", "name": m["name"], "label": m["label"]}
                    for m in well_known
                ]
            LOGGER.debug(
                "Fetched %d models from %s (on_disk=%d, well_known=%d)",
                len(models), url, len(on_disk), len(data.get("well_known", [])),
            )
            return models
    except Exception as err:
        LOGGER.warning("Could not fetch models from %s: %s", url, err)
        return []


class PiperHTTPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Piper HTTP TTS."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            models = await fetch_models(self.hass, host, port)
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
        return PiperHTTPOptionsFlow(config_entry)


class PiperHTTPOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Piper HTTP TTS."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        host = self._config_entry.data[CONF_HOST]
        port = self._config_entry.data[CONF_PORT]
        models = await fetch_models(self.hass, host, port)

        if not models:
            LOGGER.warning(
                "No models found on piper-http at %s:%s – abort options",
                host, port,
            )
            return self.async_abort(reason="cannot_connect")

        model_choices = {m["file"]: m["file"] for m in models}
        default_model = self._config_entry.options.get(CONF_MODEL, models[0]["file"])

        schema = vol.Schema(
            {
                vol.Required(CONF_MODEL, default=default_model): vol.In(model_choices),
                vol.Optional(
                    CONF_SPEAKER_ID,
                    default=self._config_entry.options.get(CONF_SPEAKER_ID, DEFAULT_SPEAKER_ID),
                ): vol.All(int, vol.Range(min=0, max=10)),
                vol.Optional(
                    CONF_LENGTH_SCALE,
                    default=self._config_entry.options.get(CONF_LENGTH_SCALE, DEFAULT_LENGTH_SCALE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.3, max=3.0)),
                vol.Optional(
                    CONF_NOISE_SCALE,
                    default=self._config_entry.options.get(CONF_NOISE_SCALE, DEFAULT_NOISE_SCALE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
                vol.Optional(
                    CONF_NOISE_W,
                    default=self._config_entry.options.get(CONF_NOISE_W, DEFAULT_NOISE_W),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
                vol.Optional(
                    CONF_SENTENCE_SILENCE,
                    default=self._config_entry.options.get(CONF_SENTENCE_SILENCE, DEFAULT_SENTENCE_SILENCE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=10.0)),
            }
        )

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
