"""Einrichtung und Optionen."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import CONF_LOW_STOCK, CONF_MAX_AGE, DEFAULT_LOW_STOCK, DEFAULT_MAX_AGE, DOMAIN


def _options_schema(options: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_LOW_STOCK, default=options.get(CONF_LOW_STOCK, DEFAULT_LOW_STOCK)
            ): NumberSelector(
                NumberSelectorConfig(min=1, max=50, step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_MAX_AGE, default=options.get(CONF_MAX_AGE, DEFAULT_MAX_AGE)
            ): NumberSelector(
                NumberSelectorConfig(min=1, max=30, step=1, mode=NumberSelectorMode.BOX)
            ),
        }
    )


def _clean(user_input: dict[str, Any]) -> dict[str, Any]:
    return {key: int(value) for key, value in user_input.items()}


class SeedStashConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Samenkiste", data={}, options=_clean(user_input))
        return self.async_show_form(step_id="user", data_schema=_options_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SeedStashOptionsFlow()


class SeedStashOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=_clean(user_input))
        return self.async_show_form(
            step_id="init", data_schema=_options_schema(dict(self.config_entry.options))
        )
