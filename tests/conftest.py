"""Gemeinsame Fixtures."""

from __future__ import annotations

from collections.abc import Generator
import sys

from freezegun.api import FrozenDateTimeFactory
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import pytest_socket

from custom_components.seed_stash.const import DOMAIN
from homeassistant.core import HomeAssistant

if sys.platform == "win32":
    # Die Windows-Event-Loop braucht ein lokales TCP-Socket-Paar (Linux nutzt Unix-Sockets),
    # das pytest-socket sonst blockiert. Unter Linux/CI bleibt der Schutz aktiv.
    pytest_socket.disable_socket = lambda *args, **kwargs: None


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> Generator[None]:
    yield


@pytest.fixture(autouse=True)
async def frozen_today(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> FrozenDateTimeFactory:
    """Fester „Heute“-Wert: 15.09.2026, 12:00 Uhr in Berlin."""
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to("2026-09-15 12:00:00+02:00")
    return freezer


@pytest.fixture
def mock_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        version=1,
        title="Samenkiste",
        data={},
        options={"low_stock": 3, "max_age_years": 5},
    )


@pytest.fixture
async def setup_entry(hass: HomeAssistant, mock_entry: MockConfigEntry) -> MockConfigEntry:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()
    return mock_entry


SAMPLE_SEEDS = [
    {
        "nr": 1,
        "name": "Bubble Cross F2",
        "lineage": "Bubble Gum x Sour Gum",
        "breeder": "Gärtner42",
        "source_type": "trade",
        "type": "reg",
        "code": "BC",
        "quantity": 15,
        "received": "2024-11",
    },
    {
        "nr": 2,
        "name": "Lemon Auto",
        "breeder": "Beispiel Seeds",
        "type": "auto_fem",
        "code": "LA",
        "genotype": "indica_dominant",
        "flower_min": 70,
        "flower_max": 75,
        "total_runtime": True,
        "quantity": 2,
        "received": "2024-05",
    },
    {
        "nr": 7,
        "name": "Haze Klassiker",
        "breeder": "Altbestand Seeds",
        "type": "fem",
        "code": "HK",
        "genotype": "sativa_dominant",
        "flower_min": 77,
        "flower_max": 84,
        "quantity": 5,
        "received": "2018-2019",
    },
]


@pytest.fixture
async def stash(hass: HomeAssistant, setup_entry: MockConfigEntry):
    """Samenkiste mit drei Beispiel-Einträgen."""
    hub = setup_entry.runtime_data
    for seed in SAMPLE_SEEDS:
        await hub.async_add_seed(seed)
    await hass.async_block_till_done()
    return hub
