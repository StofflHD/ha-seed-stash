"""Aktionen für Automationen und Sprachassistenten."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_COUNT,
    ATTR_DATE,
    ATTR_KIND,
    ATTR_NOTE,
    ATTR_SEED,
    DATA_HUB,
    DOMAIN,
    FIELD_NAME,
    FIELD_NR,
    FIELD_QUANTITY,
    LOG_ADDED,
    LOG_GERMINATED,
    LOG_REMOVED,
    SERVICE_ADD_SEEDS,
    SERVICE_TAKE_SEEDS,
)
from .hub import SeedStash

_BASE = {
    vol.Required(ATTR_SEED): vol.All(vol.Any(str, int), vol.Coerce(str)),
    vol.Required(ATTR_COUNT): vol.All(vol.Coerce(int), vol.Range(min=1, max=100000)),
    vol.Optional(ATTR_DATE): cv.date,
    vol.Optional(ATTR_NOTE): str,
}

TAKE_SCHEMA = vol.Schema(
    {
        **_BASE,
        vol.Optional(ATTR_KIND, default=LOG_GERMINATED): vol.In([LOG_GERMINATED, LOG_REMOVED]),
    }
)
ADD_SCHEMA = vol.Schema(_BASE)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    async def change(call: ServiceCall, kind: str) -> ServiceResponse:
        stash: SeedStash | None = hass.data.get(DATA_HUB)
        if stash is None:
            raise ServiceValidationError("Seed Stash ist nicht geladen")
        seed = stash.resolve(call.data[ATTR_SEED])
        seed = await stash.async_change_quantity(
            seed["id"],
            kind,
            call.data[ATTR_COUNT],
            call.data.get(ATTR_DATE),
            call.data.get(ATTR_NOTE),
        )
        result: dict[str, Any] = {
            "nr": seed[FIELD_NR],
            "name": seed[FIELD_NAME],
            "quantity": seed[FIELD_QUANTITY],
        }
        return result

    async def take_seeds(call: ServiceCall) -> ServiceResponse:
        return await change(call, call.data[ATTR_KIND])

    async def add_seeds(call: ServiceCall) -> ServiceResponse:
        return await change(call, LOG_ADDED)

    hass.services.async_register(
        DOMAIN, SERVICE_TAKE_SEEDS, take_seeds, TAKE_SCHEMA, SupportsResponse.OPTIONAL
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_SEEDS, add_seeds, ADD_SCHEMA, SupportsResponse.OPTIONAL
    )
