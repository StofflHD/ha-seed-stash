"""Zentrale Verwaltung der Samenkiste und persistente Speicherung."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
import re
from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_LOW_STOCK,
    CONF_MAX_AGE,
    DEFAULT_LOW_STOCK,
    DEFAULT_MAX_AGE,
    EVENT_QUANTITY_CHANGED,
    FIELD_BREEDER,
    FIELD_CODE,
    FIELD_FLOWER_MAX,
    FIELD_FLOWER_MIN,
    FIELD_GENOTYPE,
    FIELD_LINEAGE,
    FIELD_NAME,
    FIELD_NOTES,
    FIELD_NR,
    FIELD_QUANTITY,
    FIELD_RECEIVED,
    FIELD_SOURCE,
    FIELD_SOURCE_TYPE,
    FIELD_TOTAL_RUNTIME,
    FIELD_TYPE,
    GENOTYPES,
    LOG_ADDED,
    LOG_CORRECTION,
    LOG_GERMINATED,
    LOG_IMPORT,
    LOG_REMOVED,
    MAX_LOG,
    SEED_TYPES,
    SIGNAL_UPDATE,
    SOURCE_TYPES,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .formats import parse_received

# Jahr-Monat, nur Jahr oder Zeitraum zweier Jahre
RECEIVED_RE = re.compile(r"^\d{4}(-(0[1-9]|1[0-2]))?$|^\d{4}-\d{4}$")
# Generation am Ende eines Kürzels (C99F2, XD-F3, PB_S1, AB BX2, CD IBL)
GENERATION_RE = re.compile(r"^(.+?)[-_ ]?(F\d{1,2}|S\d|BX\d?|IBL)$", re.IGNORECASE)


def strip_generation(code: str | None) -> str | None:
    """Die Generation gehört in die Sorte, nicht ins Kürzel."""
    if code and (match := GENERATION_RE.match(code)):
        return match[1]
    return code


def _text(max_len: int) -> Callable[[Any], str | None]:
    """Freitext: getrimmt, leer wird zu None."""

    def validate(value: Any) -> str | None:
        if value is None:
            return None
        value = str(value).strip()
        if len(value) > max_len:
            raise vol.Invalid(f"Höchstens {max_len} Zeichen")
        return value or None

    return validate


def _optional(validator: Any) -> Any:
    """None und leere Werte erlauben (leer wird zu None)."""
    return vol.Any(None, vol.All("", lambda _: None), validator)


def _received(value: Any) -> str | None:
    """Eingang wie beim Import auch als 03.2025, Mär 25 usw. annehmen."""
    text = str(value).strip() if value is not None else ""
    if not text or RECEIVED_RE.match(text):
        return text or None
    if (parsed := parse_received(text)) is None:
        raise vol.Invalid("nicht erkannt – z. B. 2024-11, 11.2024 oder 2018-2019")
    return parsed


# Feldnamen für Fehlermeldungen
FIELD_LABELS = {
    FIELD_NR: "Nr.",
    FIELD_NAME: "Sorte",
    FIELD_LINEAGE: "Kreuzung",
    FIELD_BREEDER: "Züchter",
    FIELD_SOURCE: "Quelle",
    FIELD_SOURCE_TYPE: "Quellentyp",
    FIELD_TYPE: "Art",
    FIELD_CODE: "Kürzel",
    FIELD_GENOTYPE: "Genotyp",
    FIELD_FLOWER_MIN: "Blütetage von",
    FIELD_FLOWER_MAX: "Blütetage bis",
    FIELD_TOTAL_RUNTIME: "Gesamtlaufzeit",
    FIELD_QUANTITY: "Menge",
    FIELD_RECEIVED: "Eingang",
    FIELD_NOTES: "Anmerkung",
}


SEED_SCHEMA = vol.Schema(
    {
        vol.Optional(FIELD_NR): _optional(vol.All(vol.Coerce(int), vol.Range(min=1, max=99999))),
        vol.Required(FIELD_NAME): vol.All(_text(200), vol.Length(min=1)),
        vol.Optional(FIELD_LINEAGE): _text(500),
        vol.Optional(FIELD_BREEDER): _text(200),
        vol.Optional(FIELD_SOURCE): _text(200),
        vol.Optional(FIELD_SOURCE_TYPE): _optional(vol.In(SOURCE_TYPES)),
        vol.Optional(FIELD_TYPE): _optional(vol.In(SEED_TYPES)),
        vol.Optional(FIELD_CODE): _text(20),
        vol.Optional(FIELD_GENOTYPE): _optional(vol.In(GENOTYPES)),
        vol.Optional(FIELD_FLOWER_MIN): _optional(
            vol.All(vol.Coerce(int), vol.Range(min=1, max=365))
        ),
        vol.Optional(FIELD_FLOWER_MAX): _optional(
            vol.All(vol.Coerce(int), vol.Range(min=1, max=365))
        ),
        vol.Optional(FIELD_TOTAL_RUNTIME, default=False): bool,
        vol.Optional(FIELD_QUANTITY, default=0): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100000)
        ),
        vol.Optional(FIELD_RECEIVED): _received,
        vol.Optional(FIELD_NOTES): _text(5000),
    }
)

SEED_FIELDS = tuple(str(key) for key in SEED_SCHEMA.schema)


def validate_seed(data: dict[str, Any]) -> dict[str, Any]:
    """Eingaben prüfen und vereinheitlichen; alle Felder sind danach vorhanden."""
    try:
        seed = SEED_SCHEMA(data)
    except vol.Invalid as err:
        field = str(err.path[0]) if err.path else ""
        if field == FIELD_NAME:
            raise ServiceValidationError("Bitte eine Sorte angeben") from err
        label = FIELD_LABELS.get(field, field)
        # Eigene Meldungen sind deutsch und werden mit angezeigt
        detail = (
            err.error_message if field == FIELD_RECEIVED or "Zeichen" in err.error_message else ""
        )
        raise ServiceValidationError(
            f"Ungültige Angabe bei „{label}“" + (f": {detail}" if detail else "")
        ) from err
    for key in SEED_FIELDS:
        seed.setdefault(key, None)
    seed[FIELD_CODE] = strip_generation(seed[FIELD_CODE])

    low, high = seed[FIELD_FLOWER_MIN], seed[FIELD_FLOWER_MAX]
    if low is None or high is None:
        seed[FIELD_FLOWER_MIN] = seed[FIELD_FLOWER_MAX] = low if high is None else high
    elif low > high:
        raise ServiceValidationError("Blütetage: „von“ ist größer als „bis“")
    return seed


def received_year(value: str | None) -> int | None:
    """Erstes Jahr des Eingangs (bei Zeiträumen das ältere)."""
    return int(value[:4]) if value else None


class SeedStash:
    """Hält alle Einträge der Samenkiste eines Config Entries."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.seeds: dict[str, dict[str, Any]] = {}

    # --- Speicher ---------------------------------------------------------

    async def async_load(self) -> None:
        stored = await self._store.async_load() or {}
        self.seeds = {seed["id"]: seed for seed in stored.get("seeds", [])}
        if self._strip_stored_generations():
            await self.async_save()

    def _strip_stored_generations(self) -> bool:
        """Generation aus Kürzeln entfernen, die vor 0.1.1 gespeichert wurden.

        Ein Kürzel bleibt unverändert, wenn das gekürzte schon vergeben ist.
        """
        changed = False
        for seed in self.seeds.values():
            code = strip_generation(seed[FIELD_CODE])
            if code == seed[FIELD_CODE]:
                continue
            taken = {(s[FIELD_CODE] or "").casefold() for s in self.seeds.values() if s is not seed}
            if code.casefold() not in taken:
                seed[FIELD_CODE] = code
                changed = True
        return changed

    async def async_save(self) -> None:
        await self._store.async_save({"seeds": list(self.seeds.values())})

    async def async_save_and_notify(self) -> None:
        await self.async_save()
        self.async_notify()

    @callback
    def async_notify(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_UPDATE)

    async def async_remove(self) -> None:
        await self._store.async_remove()

    # --- Optionen und Auswertung ------------------------------------------

    @property
    def low_stock(self) -> int:
        return int(self.entry.options.get(CONF_LOW_STOCK, DEFAULT_LOW_STOCK))

    @property
    def max_age(self) -> int:
        return int(self.entry.options.get(CONF_MAX_AGE, DEFAULT_MAX_AGE))

    def sorted_seeds(self) -> list[dict[str, Any]]:
        return sorted(self.seeds.values(), key=lambda s: s[FIELD_NR])

    @property
    def total(self) -> int:
        return sum(seed[FIELD_QUANTITY] for seed in self.seeds.values())

    def in_stock(self) -> list[dict[str, Any]]:
        return [seed for seed in self.sorted_seeds() if seed[FIELD_QUANTITY] > 0]

    def low_stock_seeds(self) -> list[dict[str, Any]]:
        return [s for s in self.in_stock() if s[FIELD_QUANTITY] <= self.low_stock]

    def old_seeds(self) -> list[dict[str, Any]]:
        limit = dt_util.now().year - self.max_age
        return [
            seed
            for seed in self.in_stock()
            if (year := received_year(seed[FIELD_RECEIVED])) is not None and year <= limit
        ]

    # --- Suchen -----------------------------------------------------------

    def get(self, seed_id: str) -> dict[str, Any]:
        if (seed := self.seeds.get(seed_id)) is None:
            raise ServiceValidationError("Unbekannter Eintrag")
        return seed

    def resolve(self, value: str | int) -> dict[str, Any]:
        """Eintrag per ID, Nr., Kürzel oder Sorte (Groß-/Kleinschreibung egal) finden."""
        text = str(value).strip()
        if text in self.seeds:
            return self.seeds[text]
        if text.isdigit():
            for seed in self.seeds.values():
                if seed[FIELD_NR] == int(text):
                    return seed
        wanted = text.casefold()
        for field in (FIELD_CODE, FIELD_NAME):
            for seed in self.seeds.values():
                if (seed[field] or "").casefold() == wanted:
                    return seed
        raise ServiceValidationError(f"Unbekannter Eintrag: {value}")

    def next_nr(self) -> int:
        return max((seed[FIELD_NR] for seed in self.seeds.values()), default=0) + 1

    def _check_unique(self, seed: dict[str, Any], own_id: str | None = None) -> None:
        for other in self.seeds.values():
            if other["id"] == own_id:
                continue
            if other[FIELD_NR] == seed[FIELD_NR]:
                raise ServiceValidationError(f"Nr. {seed[FIELD_NR]} ist bereits vergeben")
            code = seed[FIELD_CODE]
            if code and (other[FIELD_CODE] or "").casefold() == code.casefold():
                raise ServiceValidationError(f"Kürzel „{code}“ ist bereits vergeben")

    # --- Ändern -----------------------------------------------------------

    @staticmethod
    def _log(
        seed: dict[str, Any], kind: str, delta: int, day: date, note: str | None = None
    ) -> None:
        seed["log"].append(
            {
                "id": uuid4().hex,
                "date": day.isoformat(),
                "kind": kind,
                "delta": delta,
                "quantity": seed[FIELD_QUANTITY],
                "note": note,
            }
        )
        seed["log"].sort(key=lambda item: item["date"])
        del seed["log"][:-MAX_LOG]

    def _new_seed(self, data: dict[str, Any], log_kind: str) -> dict[str, Any]:
        seed = validate_seed(data)
        if seed[FIELD_NR] is None:
            seed[FIELD_NR] = self.next_nr()
        self._check_unique(seed)
        today = dt_util.now().date()
        seed.update(id=uuid4().hex, created=today.isoformat(), log=[])
        if seed[FIELD_QUANTITY]:
            self._log(seed, log_kind, seed[FIELD_QUANTITY], today)
        return seed

    async def async_add_seed(self, data: dict[str, Any]) -> dict[str, Any]:
        seed = self._new_seed(data, LOG_ADDED)
        self.seeds[seed["id"]] = seed
        await self.async_save_and_notify()
        return seed

    async def async_update_seed(self, seed_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Stammdaten ändern. Ohne Menge bleibt der Bestand unverändert, eine geänderte
        Menge wird als Korrektur protokolliert."""
        seed = self.get(seed_id)
        new = validate_seed({FIELD_QUANTITY: seed[FIELD_QUANTITY], **data})
        if new[FIELD_NR] is None:
            new[FIELD_NR] = seed[FIELD_NR]
        self._check_unique(new, seed_id)
        delta = new[FIELD_QUANTITY] - seed[FIELD_QUANTITY]
        seed.update(new)
        if delta:
            self._log(seed, LOG_CORRECTION, delta, dt_util.now().date())
        await self.async_save_and_notify()
        return seed

    async def async_delete_seed(self, seed_id: str) -> None:
        self.get(seed_id)
        del self.seeds[seed_id]
        await self.async_save_and_notify()

    async def async_change_quantity(
        self,
        seed_id: str,
        kind: str,
        count: int,
        day: date | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        """Bestand ändern: hinzufügen, keimen, abgeben oder auf einen Wert korrigieren."""
        seed = self.get(seed_id)
        day = day or dt_util.now().date()
        if day > dt_util.now().date():
            raise ServiceValidationError("Das Datum darf nicht in der Zukunft liegen")
        if count < 0 or (count == 0 and kind != LOG_CORRECTION):
            raise ServiceValidationError("Die Anzahl muss mindestens 1 sein")

        old = seed[FIELD_QUANTITY]
        if kind == LOG_ADDED:
            new = old + count
        elif kind in (LOG_GERMINATED, LOG_REMOVED):
            if count > old:
                raise ServiceValidationError(
                    f"Von „{seed[FIELD_NAME]}“ sind nur noch {old} Samen da"
                )
            new = old - count
        elif kind == LOG_CORRECTION:
            new = count
        else:
            raise ServiceValidationError(f"Unbekannte Art: {kind}")
        if new == old:
            return seed

        seed[FIELD_QUANTITY] = new
        self._log(seed, kind, new - old, day, _text(500)(note))
        await self.async_save_and_notify()
        self.hass.bus.async_fire(
            EVENT_QUANTITY_CHANGED,
            {
                "seed_id": seed_id,
                "nr": seed[FIELD_NR],
                "name": seed[FIELD_NAME],
                "code": seed[FIELD_CODE],
                "kind": kind,
                "delta": new - old,
                "quantity": new,
            },
        )
        return seed

    async def async_import(self, entries: list[dict[str, Any]], replace: bool) -> int:
        """Importierte Einträge übernehmen; bei replace wird die Kiste vorher geleert.

        Erst werden alle Einträge geprüft, damit ein Fehler nichts halb übernimmt.
        Belegte Nummern und Kürzel werden beim Anhängen neu vergeben bzw. geleert.
        """
        previous = self.seeds
        self.seeds = {} if replace else dict(previous)
        try:
            for data in entries:
                data = dict(data)
                if data.get(FIELD_NR) in {s[FIELD_NR] for s in self.seeds.values()}:
                    data[FIELD_NR] = None
                code = (data.get(FIELD_CODE) or "").casefold()
                if code and code in {(s[FIELD_CODE] or "").casefold() for s in self.seeds.values()}:
                    data[FIELD_CODE] = None
                seed = self._new_seed(data, LOG_IMPORT)
                self.seeds[seed["id"]] = seed
        except ServiceValidationError:
            self.seeds = previous
            raise
        await self.async_save_and_notify()
        return len(entries)
