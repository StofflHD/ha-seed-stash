"""Sensoren für Bestand, Sorten, Nachkauf und Alter der Samen."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SeedStashConfigEntry
from .const import (
    DOMAIN,
    FIELD_CODE,
    FIELD_NAME,
    FIELD_NR,
    FIELD_QUANTITY,
    FIELD_RECEIVED,
    SIGNAL_UPDATE,
)
from .hub import SeedStash


def _summary(seeds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "nr": seed[FIELD_NR],
            "name": seed[FIELD_NAME],
            "code": seed[FIELD_CODE],
            "quantity": seed[FIELD_QUANTITY],
            "received": seed[FIELD_RECEIVED],
        }
        for seed in seeds
    ]


@dataclass(frozen=True, kw_only=True)
class SeedSensorDescription(SensorEntityDescription):
    value_fn: Callable[[SeedStash], int]
    attrs_fn: Callable[[SeedStash], dict[str, Any]] | None = None


SENSORS: tuple[SeedSensorDescription, ...] = (
    SeedSensorDescription(
        key="total_seeds",
        icon="mdi:seed",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.total,
    ),
    SeedSensorDescription(
        key="strains",
        icon="mdi:sprout",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: len(s.in_stock()),
        attrs_fn=lambda s: {"empty": len(s.seeds) - len(s.in_stock())},
    ),
    SeedSensorDescription(
        key="low_stock",
        icon="mdi:seed-outline",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: len(s.low_stock_seeds()),
        attrs_fn=lambda s: {"threshold": s.low_stock, "seeds": _summary(s.low_stock_seeds())},
    ),
    SeedSensorDescription(
        key="old_seeds",
        icon="mdi:timer-sand",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: len(s.old_seeds()),
        attrs_fn=lambda s: {"max_age_years": s.max_age, "seeds": _summary(s.old_seeds())},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SeedStashConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(SeedSensor(entry.runtime_data, desc) for desc in SENSORS)


class SeedSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: SeedSensorDescription

    def __init__(self, stash: SeedStash, description: SeedSensorDescription) -> None:
        self.stash = stash
        self.entity_description = description
        entry_id = stash.entry.entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=stash.entry.title,
            manufacturer="Seed Stash",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self.async_write_ha_state)
        )

    @property
    def native_value(self) -> int:
        return self.entity_description.value_fn(self.stash)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.stash)
