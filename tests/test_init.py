"""Tests für Einrichtung, Sensoren, Aktionen und Websocket-API."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.seed_stash.const import DOMAIN
from custom_components.seed_stash.hub import SeedStash
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from .test_csv import EXCEL_CSV


def _entity_id(hass: HomeAssistant, entry: MockConfigEntry, key: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
    assert entity_id
    return entity_id


async def _call(client, msg: dict) -> tuple[dict, dict]:
    """Befehl senden; Antwort und das dabei ausgelöste Abo-Update zurückgeben.

    Das Update kann vor der Antwort eintreffen, weil die Änderung schon während
    des Befehls gemeldet wird.
    """
    await client.send_json_auto_id(msg)
    first = await client.receive_json()
    second = await client.receive_json()
    result, event = (first, second) if first["type"] == "result" else (second, first)
    return result, event["event"]


async def test_config_flow_and_options(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"low_stock": 4.0, "max_age_years": 6.0}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    entry = result["result"]
    assert entry.options == {"low_stock": 4, "max_age_years": 6}
    await hass.async_block_till_done()

    # Nur eine Samenkiste
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"low_stock": 2, "max_age_years": 3}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.runtime_data.low_stock == 2


async def test_sensors(hass: HomeAssistant, stash: SeedStash, setup_entry: MockConfigEntry) -> None:
    total = hass.states.get(_entity_id(hass, setup_entry, "total_seeds"))
    assert total.state == "22"
    assert hass.states.get(_entity_id(hass, setup_entry, "strains")).state == "3"

    low = hass.states.get(_entity_id(hass, setup_entry, "low_stock"))
    assert low.state == "1"
    assert low.attributes["threshold"] == 3
    assert low.attributes["seeds"][0]["code"] == "LA"

    old = hass.states.get(_entity_id(hass, setup_entry, "old_seeds"))
    assert old.state == "1"
    assert old.attributes["seeds"][0]["received"] == "2018-2019"

    # Optionen wirken ohne Reload
    hass.config_entries.async_update_entry(
        setup_entry, options={"low_stock": 5, "max_age_years": 1}
    )
    await hass.async_block_till_done()
    assert hass.states.get(_entity_id(hass, setup_entry, "low_stock")).state == "2"
    assert hass.states.get(_entity_id(hass, setup_entry, "old_seeds")).state == "3"


async def test_services(
    hass: HomeAssistant, stash: SeedStash, setup_entry: MockConfigEntry
) -> None:
    response = await hass.services.async_call(
        DOMAIN,
        "take_seeds",
        {"seed": "bc", "count": 3, "note": "Keimtest"},
        blocking=True,
        return_response=True,
    )
    assert response == {"nr": 1, "name": "Bubble Cross F2", "quantity": 12}
    log = stash.resolve("BC")["log"][-1]
    assert (log["kind"], log["delta"], log["note"]) == ("germinated", -3, "Keimtest")

    await hass.services.async_call(
        DOMAIN, "add_seeds", {"seed": 7, "count": 2, "date": "2026-09-01"}, blocking=True
    )
    assert stash.resolve("HK")["quantity"] == 7
    await hass.async_block_till_done()
    assert hass.states.get(_entity_id(hass, setup_entry, "total_seeds")).state == "21"

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "take_seeds", {"seed": "LA", "count": 5, "kind": "removed"}, blocking=True
        )
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "take_seeds", {"seed": "XX", "count": 1}, blocking=True
        )


async def test_ws_subscribe_and_edit(
    hass: HomeAssistant, stash: SeedStash, hass_ws_client: WebSocketGenerator
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "seed_stash/subscribe"})
    assert (await client.receive_json())["success"]
    event = (await client.receive_json())["event"]
    assert event["loaded"] is True
    assert event["today"] == "2026-09-15"
    assert event["total"] == 22
    assert [s["nr"] for s in event["seeds"]] == [1, 2, 7]
    la = stash.resolve("LA")["id"]
    assert event["low_ids"] == [la]

    result, event = await _call(
        client,
        {"type": "seed_stash/save_seed", "seed": {"name": "Neu", "quantity": 3, "code": "NE"}},
    )
    assert result["success"]
    new_id = result["result"]["seed_id"]
    assert event["total"] == 25

    result, event = await _call(
        client,
        {
            "type": "seed_stash/change_quantity",
            "seed_id": new_id,
            "kind": "germinated",
            "count": 2,
            "date": "2026-09-14",
        },
    )
    assert result["success"]
    assert next(s for s in event["seeds"] if s["id"] == new_id)["quantity"] == 1

    await client.send_json_auto_id(
        {"type": "seed_stash/save_seed", "seed_id": new_id, "seed": {"name": "Neu", "code": "LA"}}
    )
    result = await client.receive_json()
    assert not result["success"]
    assert "Kürzel" in result["error"]["message"]

    result, event = await _call(client, {"type": "seed_stash/delete_seed", "seed_id": new_id})
    assert result["success"]
    assert len(event["seeds"]) == 3


async def test_ws_set_log(
    hass: HomeAssistant, stash: SeedStash, hass_ws_client: WebSocketGenerator
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)
    seed = stash.resolve("LA")

    await client.send_json_auto_id(
        {
            "type": "seed_stash/set_log",
            "seed_id": seed["id"],
            "log": [
                {"id": seed["log"][0]["id"], "date": "2026-09-01", "kind": "added", "delta": 6},
                {"date": "2026-09-10", "kind": "germinated", "delta": -2, "note": "Keimtest"},
            ],
        }
    )
    assert (await client.receive_json())["success"]
    assert seed["quantity"] == 4

    await client.send_json_auto_id(
        {
            "type": "seed_stash/set_log",
            "seed_id": seed["id"],
            "log": [{"date": "2026-09-01", "kind": "germinated", "delta": -1}],
        }
    )
    result = await client.receive_json()
    assert not result["success"]
    assert "negativ" in result["error"]["message"]
    assert seed["quantity"] == 4


async def test_ws_import_and_export(
    hass: HomeAssistant, stash: SeedStash, hass_ws_client: WebSocketGenerator
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "seed_stash/import_preview", "csv": EXCEL_CSV})
    result = await client.receive_json()
    assert result["success"]
    assert len(result["result"]["rows"]) == 7
    assert len(stash.seeds) == 3

    await client.send_json_auto_id({"type": "seed_stash/import_preview", "csv": "x;y\n1;2"})
    result = await client.receive_json()
    assert not result["success"]

    await client.send_json_auto_id({"type": "seed_stash/import", "csv": EXCEL_CSV, "replace": True})
    result = await client.receive_json()
    assert result["result"] == {"imported": 7, "skipped": 0}
    assert stash.total == 46
    assert stash.resolve("Doppelt")["code"] is None

    await client.send_json_auto_id({"type": "seed_stash/export"})
    result = (await client.receive_json())["result"]
    assert result["filename"] == "samenkiste-2026-09-15.csv"
    assert result["csv"].count("\r\n") == 8


async def test_ws_not_loaded(hass: HomeAssistant, hass_ws_client: WebSocketGenerator) -> None:
    assert await async_setup_component(hass, DOMAIN, {})
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "seed_stash/subscribe"})
    assert (await client.receive_json())["success"]
    assert (await client.receive_json())["event"] == {"loaded": False, "seeds": []}

    await client.send_json_auto_id({"type": "seed_stash/export"})
    result = await client.receive_json()
    assert result["error"]["code"] == "not_found"


async def test_unload_and_remove(
    hass: HomeAssistant, stash: SeedStash, setup_entry: MockConfigEntry
) -> None:
    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    await hass.async_block_till_done()
    assert "seed_stash_hub" not in hass.data
    assert await hass.config_entries.async_remove(setup_entry.entry_id)
