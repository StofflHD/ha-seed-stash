"""Websocket-API für das Seitenleisten-Panel."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from .const import (
    DATA_HUB,
    LOG_KINDS,
    MAX_LOG,
    SIGNAL_UPDATE,
    WS_CHANGE_QUANTITY,
    WS_DELETE_SEED,
    WS_EXPORT,
    WS_IMPORT,
    WS_IMPORT_PREVIEW,
    WS_SAVE_SEED,
    WS_SET_LOG,
    WS_SUBSCRIBE,
)
from .csv_io import export_csv, parse_csv
from .hub import SeedStash

# Obergrenze für hochgeladene CSV-Dateien
MAX_CSV = 2_000_000


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_subscribe)
    websocket_api.async_register_command(hass, ws_save_seed)
    websocket_api.async_register_command(hass, ws_delete_seed)
    websocket_api.async_register_command(hass, ws_change_quantity)
    websocket_api.async_register_command(hass, ws_set_log)
    websocket_api.async_register_command(hass, ws_import_preview)
    websocket_api.async_register_command(hass, ws_import)
    websocket_api.async_register_command(hass, ws_export)


async def _async_run(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
    action: Callable[[SeedStash], Awaitable[Any]],
) -> None:
    """Aktion auf der Samenkiste ausführen und Ergebnis/Fehler an das Panel senden."""
    stash: SeedStash | None = hass.data.get(DATA_HUB)
    if stash is None:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Seed Stash is not loaded")
        return
    try:
        result = await action(stash)
    except ServiceValidationError as err:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SAVE_SEED,
        vol.Optional("seed_id"): str,
        vol.Required("seed"): dict,
    }
)
@websocket_api.async_response
async def ws_save_seed(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Eintrag anlegen (ohne seed_id) oder ändern."""

    async def action(stash: SeedStash) -> dict[str, Any]:
        if "seed_id" in msg:
            seed = await stash.async_update_seed(msg["seed_id"], msg["seed"])
        else:
            seed = await stash.async_add_seed(msg["seed"])
        return {"seed_id": seed["id"]}

    await _async_run(hass, connection, msg, action)


@websocket_api.websocket_command(
    {vol.Required("type"): WS_DELETE_SEED, vol.Required("seed_id"): str}
)
@websocket_api.async_response
async def ws_delete_seed(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    await _async_run(hass, connection, msg, lambda s: s.async_delete_seed(msg["seed_id"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_CHANGE_QUANTITY,
        vol.Required("seed_id"): str,
        vol.Required("kind"): vol.In(LOG_KINDS),
        vol.Required("count"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100000)),
        vol.Optional("date"): cv.date,
        vol.Optional("note"): vol.Any(None, str),
    }
)
@websocket_api.async_response
async def ws_change_quantity(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    async def action(stash: SeedStash) -> None:
        await stash.async_change_quantity(
            msg["seed_id"], msg["kind"], msg["count"], msg.get("date"), msg.get("note")
        )

    await _async_run(hass, connection, msg, action)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SET_LOG,
        vol.Required("seed_id"): str,
        vol.Required("log"): vol.All(
            [
                {
                    vol.Optional("id"): vol.Any(None, str),
                    vol.Required("date"): cv.date,
                    vol.Required("kind"): vol.In(LOG_KINDS),
                    vol.Required("delta"): vol.All(
                        vol.Coerce(int), vol.Range(min=-100000, max=100000)
                    ),
                    vol.Optional("note"): vol.Any(None, str),
                }
            ],
            vol.Length(max=MAX_LOG),
        ),
    }
)
@websocket_api.async_response
async def ws_set_log(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Bestandsprotokoll eines Eintrags ersetzen (Bestand wird neu berechnet)."""

    async def action(stash: SeedStash) -> None:
        await stash.async_set_log(msg["seed_id"], msg["log"])

    await _async_run(hass, connection, msg, action)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_IMPORT_PREVIEW,
        vol.Required("csv"): vol.All(str, vol.Length(max=MAX_CSV)),
    }
)
@websocket_api.async_response
async def ws_import_preview(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """CSV prüfen, ohne etwas zu speichern."""

    async def action(stash: SeedStash) -> dict[str, Any]:
        return parse_csv(msg["csv"])

    await _async_run(hass, connection, msg, action)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_IMPORT,
        vol.Required("csv"): vol.All(str, vol.Length(max=MAX_CSV)),
        vol.Required("replace"): bool,
    }
)
@websocket_api.async_response
async def ws_import(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Gültige Zeilen der CSV übernehmen (fehlerhafte Zeilen werden ausgelassen)."""

    async def action(stash: SeedStash) -> dict[str, Any]:
        parsed = parse_csv(msg["csv"])
        count = await stash.async_import([row["seed"] for row in parsed["rows"]], msg["replace"])
        return {"imported": count, "skipped": len(parsed["errors"])}

    await _async_run(hass, connection, msg, action)


@websocket_api.websocket_command({vol.Required("type"): WS_EXPORT})
@websocket_api.async_response
async def ws_export(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    async def action(stash: SeedStash) -> dict[str, Any]:
        today = dt_util.now().date().isoformat()
        return {"csv": export_csv(stash.sorted_seeds()), "filename": f"samenkiste-{today}.csv"}

    await _async_run(hass, connection, msg, action)


@websocket_api.websocket_command({vol.Required("type"): WS_SUBSCRIBE})
@callback
def ws_subscribe(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Übersicht senden und bei jeder Änderung erneut senden."""

    @callback
    def send_overview() -> None:
        connection.send_message(websocket_api.event_message(msg["id"], async_overview(hass)))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, SIGNAL_UPDATE, send_overview
    )
    connection.send_result(msg["id"])
    send_overview()


@callback
def async_overview(hass: HomeAssistant) -> dict[str, Any]:
    stash: SeedStash | None = hass.data.get(DATA_HUB)
    if stash is None:
        return {"loaded": False, "seeds": []}

    return {
        "loaded": True,
        "entry_id": stash.entry.entry_id,
        "today": dt_util.now().date().isoformat(),
        "low_stock": stash.low_stock,
        "max_age": stash.max_age,
        "total": stash.total,
        "in_stock": len(stash.in_stock()),
        "low_ids": [seed["id"] for seed in stash.low_stock_seeds()],
        "old_ids": [seed["id"] for seed in stash.old_seeds()],
        "seeds": stash.sorted_seeds(),
    }
