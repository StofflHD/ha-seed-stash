"""Seed Stash – pflegt die Samenkiste: Sorten, Bestand und Entnahmen."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DATA_HUB, DOMAIN
from .hub import SeedStash
from .panel import async_register_panel, async_register_static_path, async_remove_panel
from .services import async_setup_services
from .websocket import async_setup_websocket

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type SeedStashConfigEntry = ConfigEntry[SeedStash]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Einmalig: Websocket-API, Aktionen und Panel-Dateien bereitstellen."""
    async_setup_websocket(hass)
    async_setup_services(hass)
    await async_register_static_path(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SeedStashConfigEntry) -> bool:
    stash = SeedStash(hass, entry)
    await stash.async_load()
    entry.runtime_data = stash
    hass.data[DATA_HUB] = stash

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await async_register_panel(hass)
    stash.async_notify()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SeedStashConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.pop(DATA_HUB, None)
        # Beim Reload bleibt das Panel bestehen, sonst landet man auf der Startseite
        if entry.disabled_by is not None:
            async_remove_panel(hass)
        entry.runtime_data.async_notify()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: SeedStashConfigEntry) -> None:
    async_remove_panel(hass)
    await SeedStash(hass, entry).async_remove()


async def _async_update_listener(hass: HomeAssistant, entry: SeedStashConfigEntry) -> None:
    """Geänderte Optionen (Schwellen) sofort in Sensoren und Panel übernehmen."""
    entry.runtime_data.async_notify()
