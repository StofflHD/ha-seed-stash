"""Tests für Datenmodell und Bestandsführung."""

from __future__ import annotations

from datetime import date

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.seed_stash.hub import SeedStash, validate_seed
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError


def test_validate_defaults_and_empty_strings() -> None:
    seed = validate_seed({"name": "  Test  ", "code": "", "type": "", "flower_min": 56})
    assert seed["name"] == "Test"
    assert seed["code"] is None
    assert seed["type"] is None
    assert seed["quantity"] == 0
    assert seed["total_runtime"] is False
    # Ein einzelner Wert gilt für beide Grenzen
    assert (seed["flower_min"], seed["flower_max"]) == (56, 56)


@pytest.mark.parametrize("received", ["2024-11", "2024", "2018-2019"])
def test_validate_received_ok(received: str) -> None:
    assert validate_seed({"name": "X", "received": received})["received"] == received


@pytest.mark.parametrize(
    ("received", "expected"),
    [("11.2024", "2024-11"), ("03-2025", "2025-03"), ("Mrz-25", "2025-03"), ("", None)],
)
def test_validate_received_free_input(received: str, expected: str | None) -> None:
    """Im Panel gelten dieselben Formate wie beim Import."""
    assert validate_seed({"name": "X", "received": received})["received"] == expected


@pytest.mark.parametrize("received", ["2024-13", "24", "2018-19", "irgendwann"])
def test_validate_received_invalid(received: str) -> None:
    with pytest.raises(ServiceValidationError, match="„Eingang“: nicht erkannt"):
        validate_seed({"name": "X", "received": received})


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"name": " "}, "Bitte eine Sorte angeben"),
        ({"name": "X", "flower_min": 0}, "Ungültige Angabe bei „Blütetage von“"),
        ({"name": "X", "code": "X" * 21}, "„Kürzel“: Höchstens 20 Zeichen"),
        ({"name": "X", "type": "bogus"}, "Ungültige Angabe bei „Art“"),
    ],
)
def test_validate_messages(data: dict, message: str) -> None:
    with pytest.raises(ServiceValidationError, match=message):
        validate_seed(data)


@pytest.mark.parametrize(
    "data",
    [
        {"name": ""},
        {"name": "X", "type": "bogus"},
        {"name": "X", "flower_min": 60, "flower_max": 50},
        {"name": "X", "quantity": -1},
    ],
)
def test_validate_rejects(data: dict) -> None:
    with pytest.raises(ServiceValidationError):
        validate_seed(data)


async def test_add_assigns_next_nr_and_logs(stash: SeedStash) -> None:
    seed = await stash.async_add_seed({"name": "Neu", "quantity": 4})
    assert seed["nr"] == 8
    assert seed["created"] == "2026-09-15"
    assert seed["log"] == [
        {
            "id": seed["log"][0]["id"],
            "date": "2026-09-15",
            "kind": "added",
            "delta": 4,
            "quantity": 4,
            "note": None,
        }
    ]
    # Ohne Menge kein Protokolleintrag
    assert (await stash.async_add_seed({"name": "Leer"}))["log"] == []


async def test_unique_nr_and_code(stash: SeedStash) -> None:
    with pytest.raises(ServiceValidationError, match="Nr. 1"):
        await stash.async_add_seed({"name": "X", "nr": 1})
    with pytest.raises(ServiceValidationError, match="Kürzel"):
        await stash.async_add_seed({"name": "X", "code": "bc"})
    assert len(stash.seeds) == 3


async def test_update_keeps_quantity_without_value(stash: SeedStash) -> None:
    seed = stash.resolve("BC")
    await stash.async_update_seed(seed["id"], {"name": "Bubble Cross F3", "code": "BC"})
    assert seed["name"] == "Bubble Cross F3"
    assert seed["quantity"] == 15
    assert seed["nr"] == 1
    # Felder, die fehlen, werden geleert
    assert seed["lineage"] is None
    assert len(seed["log"]) == 1

    await stash.async_update_seed(seed["id"], {"name": "Bubble Cross F3", "quantity": 12})
    assert seed["quantity"] == 12
    assert seed["log"][-1]["kind"] == "correction"
    assert seed["log"][-1]["delta"] == -3


async def test_update_own_nr_and_code_allowed(stash: SeedStash) -> None:
    seed = stash.resolve(1)
    await stash.async_update_seed(seed["id"], {"name": "X", "nr": 1, "code": "BC"})
    with pytest.raises(ServiceValidationError):
        await stash.async_update_seed(seed["id"], {"name": "X", "nr": 2})


async def test_change_quantity(hass: HomeAssistant, stash: SeedStash) -> None:
    events = async_capture_events(hass, "seed_stash_quantity_changed")
    seed = stash.resolve("LA")

    await stash.async_change_quantity(seed["id"], "germinated", 1, date(2026, 9, 10), " Test ")
    assert seed["quantity"] == 1
    # Älteres Datum wird chronologisch vor dem Anlegen einsortiert
    assert [item["date"] for item in seed["log"]] == ["2026-09-10", "2026-09-15"]
    assert seed["log"][0]["note"] == "Test"

    await stash.async_change_quantity(seed["id"], "added", 10)
    await stash.async_change_quantity(seed["id"], "correction", 3)
    assert seed["quantity"] == 3
    await hass.async_block_till_done()
    assert [e.data["delta"] for e in events] == [-1, 10, -8]
    assert events[0].data["code"] == "LA"

    with pytest.raises(ServiceValidationError, match="nur noch 3"):
        await stash.async_change_quantity(seed["id"], "removed", 4)
    with pytest.raises(ServiceValidationError, match="Zukunft"):
        await stash.async_change_quantity(seed["id"], "added", 1, date(2026, 9, 16))
    with pytest.raises(ServiceValidationError):
        await stash.async_change_quantity(seed["id"], "added", 0)
    assert seed["quantity"] == 3


async def test_resolve(stash: SeedStash) -> None:
    assert stash.resolve("7")["code"] == "HK"
    assert stash.resolve("hk")["nr"] == 7
    assert stash.resolve("lemon auto")["nr"] == 2
    with pytest.raises(ServiceValidationError):
        stash.resolve("99")


async def test_low_and_old(stash: SeedStash) -> None:
    assert stash.total == 22
    assert [s["code"] for s in stash.low_stock_seeds()] == ["LA"]
    # 2018-2019 zählt mit dem älteren Jahr; Grenze bei 5 Jahren ist 2021
    assert [s["code"] for s in stash.old_seeds()] == ["HK"]

    seed = stash.resolve("HK")
    await stash.async_change_quantity(seed["id"], "germinated", 5)
    assert stash.old_seeds() == []
    assert len(stash.in_stock()) == 2


async def test_delete_and_persistence(
    hass: HomeAssistant, stash: SeedStash, setup_entry: MockConfigEntry
) -> None:
    await stash.async_delete_seed(stash.resolve("BC")["id"])
    with pytest.raises(ServiceValidationError):
        await stash.async_delete_seed("unknown")

    assert await hass.config_entries.async_reload(setup_entry.entry_id)
    await hass.async_block_till_done()
    reloaded: SeedStash = setup_entry.runtime_data
    assert reloaded is not stash
    assert sorted(s["code"] for s in reloaded.seeds.values()) == ["HK", "LA"]
    assert reloaded.resolve("LA")["total_runtime"] is True


async def test_import_append_renumbers_duplicates(stash: SeedStash) -> None:
    count = await stash.async_import(
        [{"nr": 1, "name": "Doppelt", "code": "BC", "quantity": 3}, {"name": "Ohne Nr."}],
        replace=False,
    )
    assert count == 2
    imported = stash.resolve("Doppelt")
    assert imported["nr"] == 8
    assert imported["code"] is None
    assert imported["log"][0]["kind"] == "import"
    assert stash.resolve("Ohne Nr.")["nr"] == 9


async def test_import_replace_and_rollback(stash: SeedStash) -> None:
    await stash.async_import([{"nr": 5, "name": "Einzig"}], replace=True)
    assert [s["name"] for s in stash.seeds.values()] == ["Einzig"]

    with pytest.raises(ServiceValidationError):
        await stash.async_import([{"name": "Gut"}, {"name": ""}], replace=True)
    assert [s["name"] for s in stash.seeds.values()] == ["Einzig"]


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("C99F2", "C99"),
        ("XD-F3", "XD"),
        ("PB_S1", "PB"),
        ("AB BX2", "AB"),
        ("CD IBL", "CD"),
        ("sm f10", "sm"),
        # Kein Generationszusatz
        ("S60", "S60"),
        ("S#1", "S#1"),
        ("AK47", "AK47"),
        ("UES-OG", "UES-OG"),
        ("F2", "F2"),
    ],
)
def test_validate_strips_generation_from_code(code: str, expected: str) -> None:
    assert validate_seed({"name": "X", "code": code})["code"] == expected


async def test_load_strips_stored_generations(
    hass: HomeAssistant, hass_storage: dict, mock_entry: MockConfigEntry
) -> None:
    def stored(nr: int, code: str) -> dict:
        return {
            **validate_seed({"name": f"Sorte {nr}", "nr": nr}),
            "id": f"s{nr}",
            "code": code,
            "log": [],
        }

    hass_storage["seed_stash"] = {
        "version": 1,
        "key": "seed_stash",
        "data": {"seeds": [stored(1, "C99F2"), stored(2, "XD"), stored(3, "XD-F3")]},
    }
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    stash: SeedStash = mock_entry.runtime_data
    # XD ist schon vergeben, deshalb bleibt XD-F3 stehen
    assert [stash.seeds[f"s{nr}"]["code"] for nr in (1, 2, 3)] == ["C99", "XD", "XD-F3"]
    assert hass_storage["seed_stash"]["data"]["seeds"][0]["code"] == "C99"


async def test_load_recovers_received_from_notes(
    hass: HomeAssistant, hass_storage: dict, mock_entry: MockConfigEntry
) -> None:
    def stored(nr: int, received: str | None, notes: str | None) -> dict:
        seed = validate_seed({"name": f"Sorte {nr}", "nr": nr})
        return {**seed, "id": f"s{nr}", "received": received, "notes": notes, "log": []}

    hass_storage["seed_stash"] = {
        "version": 1,
        "key": "seed_stash",
        "data": {
            "seeds": [
                stored(1, None, "Eingang: 11 2024"),
                stored(2, None, "Lange Keimzeit\nEingang: 02 2025"),
                stored(3, None, "Eingang: irgendwann"),
                stored(4, "2024-05", "Eingang: 11 2024"),
            ]
        },
    }
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    seeds = mock_entry.runtime_data.seeds
    assert (seeds["s1"]["received"], seeds["s1"]["notes"]) == ("2024-11", None)
    assert (seeds["s2"]["received"], seeds["s2"]["notes"]) == ("2025-02", "Lange Keimzeit")
    # Nicht erkannt oder schon gesetzt: unverändert
    assert (seeds["s3"]["received"], seeds["s3"]["notes"]) == (None, "Eingang: irgendwann")
    assert (seeds["s4"]["received"], seeds["s4"]["notes"]) == ("2024-05", "Eingang: 11 2024")
