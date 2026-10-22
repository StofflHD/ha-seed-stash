"""Seitenleisten-Panel registrieren."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import (
    DOMAIN,
    PANEL_COMPONENT,
    PANEL_ICON,
    PANEL_TITLE,
    PANEL_URL_PATH,
    STATIC_URL,
)

FRONTEND_DIR = Path(__file__).parent / "frontend"

# Merkt sich, ob das Panel registriert ist – überlebt Reloads des Config Entries
DATA_PANEL_REGISTERED = f"{DOMAIN}_panel_registered"


async def async_register_static_path(hass: HomeAssistant) -> None:
    """Einmalig beim Start: JS-Dateien des Panels ausliefern."""
    if hass.http is None:
        return
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(FRONTEND_DIR), cache_headers=False)]
    )


async def async_register_panel(hass: HomeAssistant) -> None:
    if "frontend" not in hass.config.components or hass.data.get(DATA_PANEL_REGISTERED):
        return
    version = (await async_get_integration(hass, DOMAIN)).version
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=PANEL_COMPONENT,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        # Versionsparameter, damit Browser nach Updates die neue Datei laden
        module_url=f"{STATIC_URL}/seed-stash-panel.js?v={version}",
        require_admin=False,
    )
    hass.data[DATA_PANEL_REGISTERED] = True


def async_remove_panel(hass: HomeAssistant) -> None:
    """Panel entfernen – nur beim Löschen/Deaktivieren, nicht beim Reload."""
    if not hass.data.pop(DATA_PANEL_REGISTERED, False):
        return
    frontend.async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
