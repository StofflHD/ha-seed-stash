"""CSV-Import (z. B. aus der bisherigen Excel-Samenkiste) und CSV-Export."""

from __future__ import annotations

import csv
import io
import re
from typing import Any

from homeassistant.exceptions import ServiceValidationError

from .const import (
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
    SOURCE_TYPE_OTHER,
    SOURCE_TYPE_OWN,
    SOURCE_TYPE_SHOP,
    SOURCE_TYPE_TRADE,
)
from .hub import validate_seed

# Spaltenköpfe (normalisiert) → Feld. Flower steht für beide Blütetage-Felder.
_FLOWER = "flower"
_HEADERS = {
    FIELD_NR: ("nr", "nummer", "no"),
    FIELD_NAME: ("sorte", "name", "strain"),
    FIELD_LINEAGE: ("kreuzung", "genetik", "lineage"),
    FIELD_BREEDER: ("zuechter", "breeder"),
    FIELD_SOURCE: ("quelle", "herkunft", "source"),
    FIELD_SOURCE_TYPE: ("quellentyp", "sourcetype"),
    FIELD_TYPE: ("art", "type"),
    FIELD_CODE: ("kuerzel", "code"),
    FIELD_GENOTYPE: ("genotyp", "genotype"),
    _FLOWER: ("bluetetage", "bluete", "floweringdays", "flowering"),
    FIELD_QUANTITY: ("menge", "anzahl", "quantity", "count"),
    FIELD_RECEIVED: ("eingang", "received"),
    FIELD_NOTES: ("anmerkung", "anmerkungen", "notizen", "notes"),
}

_TYPES = {
    "reg": "reg",
    "regulaer": "reg",
    "regular": "reg",
    "fem": "fem",
    "feminisiert": "fem",
    "feminized": "fem",
    "autoreg": "auto_reg",
    "autoregulaer": "auto_reg",
    "autoregular": "auto_reg",
    "autofem": "auto_fem",
    "autofeminisiert": "auto_fem",
    "autofeminized": "auto_fem",
}

_GENOTYPES = {
    "indica": "indica",
    "100indica": "indica",
    "sativa": "sativa",
    "100sativa": "sativa",
    "hybrid": "hybrid",
    "hybride": "hybrid",
    "indicadominant": "indica_dominant",
    "sativadominant": "sativa_dominant",
}

_SOURCE_TYPES = {
    "shop": SOURCE_TYPE_SHOP,
    "seedbank": SOURCE_TYPE_SHOP,
    "tausch": SOURCE_TYPE_TRADE,
    "forum": SOURCE_TYPE_TRADE,
    "trade": SOURCE_TYPE_TRADE,
    "geschenk": SOURCE_TYPE_TRADE,
    "eigenezucht": SOURCE_TYPE_OWN,
    "eigen": SOURCE_TYPE_OWN,
    "own": SOURCE_TYPE_OWN,
    "sonstiges": SOURCE_TYPE_OTHER,
    "other": SOURCE_TYPE_OTHER,
}

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "mrz": 3, "maer": 3, "apr": 4, "mai": 5, "may": 5,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dez": 12,
    "dec": 12,
}  # fmt: skip

# Kennzeichnet Züchter-Angaben, die getauscht/geschenkt wurden: "Name (Forum)"
_TRADE_RE = re.compile(r"^(.*?)\s*\((forum|tausch|trade)\)$", re.IGNORECASE)
_SUM_WORDS = ("gesamt", "summe", "total")

# Export: Spalten und Beschriftungen (werden beim Import wieder erkannt)
EXPORT_HEADERS = [
    "Nr.", "Sorte", "Kreuzung", "Züchter", "Quelle", "Quellentyp", "Art", "Kürzel",
    "Genotyp", "Blütetage", "Menge", "Eingang", "Anmerkung",
]  # fmt: skip
_TYPE_LABELS = {"reg": "Reg", "fem": "Fem", "auto_reg": "Auto Reg", "auto_fem": "Auto Fem"}
_GENOTYPE_LABELS = {
    "indica": "100% Indica",
    "sativa": "100% Sativa",
    "hybrid": "Hybrid",
    "indica_dominant": "Indica dominant",
    "sativa_dominant": "Sativa dominant",
}
_SOURCE_TYPE_LABELS = {
    SOURCE_TYPE_SHOP: "Shop",
    SOURCE_TYPE_TRADE: "Tausch",
    SOURCE_TYPE_OWN: "Eigene Zucht",
    SOURCE_TYPE_OTHER: "Sonstiges",
}


class _ExcelSemicolon(csv.excel):
    """Standard von Excel mit deutscher Ländereinstellung."""

    delimiter = ";"


def _norm(value: str) -> str:
    """Vergleichsschlüssel: klein, Umlaute ausgeschrieben, nur Buchstaben/Ziffern."""
    value = value.casefold()
    for old, new in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        value = value.replace(old, new)
    return re.sub(r"[^a-z0-9]", "", value)


def _int(value: str) -> int | None:
    value = value.strip().replace(",", ".")
    try:
        number = float(value)
    except ValueError:
        return None
    return int(number) if number.is_integer() else None


def parse_type(value: str) -> str | None:
    return _TYPES.get(_norm(value))


def parse_genotype(value: str) -> str | None:
    return _GENOTYPES.get(_norm(value))


def parse_source_type(value: str) -> str | None:
    return _SOURCE_TYPES.get(_norm(value))


def parse_flower(value: str) -> tuple[int | None, int | None, bool] | None:
    """'56', '53-60', '8-9 Wochen', '70-75 (fertig)' → (von, bis, Gesamtlaufzeit)."""
    numbers = [int(n) for n in re.findall(r"\d+", value)]
    if not numbers or len(numbers) > 2:
        return None
    lowered = value.casefold()
    factor = 7 if re.search(r"\d\s*(w|wo|woche|wochen|weeks?)\b", lowered) else 1
    low, high = numbers[0] * factor, numbers[-1] * factor
    if low > high:
        return None
    total = any(word in lowered for word in ("fertig", "gesamt", "total", "seed to"))
    return low, high, total


def parse_received(value: str) -> str | None:
    """Eingang in 'JJJJ-MM', 'JJJJ' oder 'JJJJ-JJJJ' umwandeln (None = unbekanntes Format)."""
    value = value.strip()

    def month(y: int, m: int) -> str | None:
        return f"{y:04d}-{m:02d}" if 1 <= m <= 12 and 1900 <= y <= 2100 else None

    if m := re.fullmatch(r"(\d{4})\s*[-–/]\s*(\d{4})", value):
        first, last = int(m[1]), int(m[2])
        return f"{first}-{last}" if last > first else str(first)
    if m := re.fullmatch(r"(\d{4})-(\d{1,2})(-\d{1,2}([ T].*)?)?", value):
        return month(int(m[1]), int(m[2]))
    if m := re.fullmatch(r"\d{1,2}\.(\d{1,2})\.(\d{2}|\d{4})", value):
        year = int(m[2])
        return month(year + 2000 if year < 100 else year, int(m[1]))
    if m := re.fullmatch(r"(\d{1,2})/\d{1,2}/(\d{4})", value):
        return month(int(m[2]), int(m[1]))
    if m := re.fullmatch(r"(\d{1,2})[./](\d{4})", value):
        return month(int(m[2]), int(m[1]))
    if re.fullmatch(r"\d{4}", value):
        return value if 1900 <= int(value) <= 2100 else None
    if m := re.fullmatch(r"([^\W\d_]+)\.?\s*'?(\d{2}|\d{4})", value):
        number = _MONTHS.get(_norm(m[1])[:3]) or _MONTHS.get(_norm(m[1])[:4])
        year = int(m[2])
        if number:
            return month(year + 2000 if year < 100 else year, number)
    return None


def split_breeder(value: str) -> tuple[str | None, str | None, str | None]:
    """'Tauschpartner (Forum) / Züchter' → (Züchter, Quelle, Quellentyp)."""
    parts = [part.strip() for part in re.split(r"\s+/\s+", value) if part.strip()]
    if len(parts) == 2 and (m := _TRADE_RE.match(parts[0])):
        breeder = _TRADE_RE.match(parts[1])
        return (breeder[1] if breeder else parts[1]), m[1], SOURCE_TYPE_TRADE
    if len(parts) == 1 and (m := _TRADE_RE.match(parts[0])):
        return m[1], None, SOURCE_TYPE_TRADE
    return value.strip() or None, None, None


def _find_header(rows: list[list[str]]) -> tuple[int, dict[str, int]]:
    lookup = {alias: field for field, aliases in _HEADERS.items() for alias in aliases}
    for index, row in enumerate(rows[:15]):
        columns: dict[str, int] = {}
        for col, cell in enumerate(row):
            field = lookup.get(_norm(cell))
            if field and field not in columns:
                columns[field] = col
        if FIELD_NAME in columns and len(columns) >= 3:
            return index, columns
    raise ServiceValidationError(
        "Keine Kopfzeile gefunden. Die CSV braucht mindestens die Spalten Sorte, Art und Menge."
    )


def parse_csv(text: str) -> dict[str, Any]:
    """CSV lesen und jede Zeile in einen Samen-Eintrag umwandeln.

    Ergebnis: {"rows": [{"line", "seed", "warnings"}], "errors": [{"line", "error"}]}.
    Leere Zeilen und Summenzeilen werden übersprungen.
    """
    text = text.lstrip("﻿")
    try:
        dialect: Any = csv.Sniffer().sniff(text[:4096], delimiters=";,\t")
    except csv.Error:
        dialect = _ExcelSemicolon
    rows = list(csv.reader(io.StringIO(text), dialect))
    header, columns = _find_header(rows)

    result: dict[str, Any] = {"rows": [], "errors": []}
    for line, row in enumerate(rows[header + 1 :], start=header + 2):

        def cell(field: str, row: list[str] = row) -> str:
            col = columns.get(field)
            return row[col].strip() if col is not None and col < len(row) else ""

        name = cell(FIELD_NAME)
        if not name:
            continue
        if _norm(name).startswith(_SUM_WORDS) and not cell(FIELD_TYPE) and not cell(FIELD_QUANTITY):
            continue

        seed, warnings = _parse_row(cell, FIELD_SOURCE in columns)
        try:
            seed = validate_seed(seed)
        except ServiceValidationError as err:
            result["errors"].append({"line": line, "name": name, "error": str(err)})
            continue
        result["rows"].append({"line": line, "seed": seed, "warnings": warnings})

    _warn_duplicates(result["rows"])
    return result


def _parse_row(cell: Any, has_source: bool) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    notes = [cell(FIELD_NOTES)] if cell(FIELD_NOTES) else []
    seed: dict[str, Any] = {
        FIELD_NAME: cell(FIELD_NAME),
        FIELD_LINEAGE: cell(FIELD_LINEAGE),
        FIELD_CODE: cell(FIELD_CODE),
    }

    if raw := cell(FIELD_NR):
        seed[FIELD_NR] = _int(raw)
        if seed[FIELD_NR] is None or seed[FIELD_NR] < 1:
            seed[FIELD_NR] = None
            warnings.append(f"Nr. „{raw}“ ungültig – wird neu vergeben")

    breeder = cell(FIELD_BREEDER)
    if has_source:
        seed[FIELD_BREEDER], seed[FIELD_SOURCE] = breeder, cell(FIELD_SOURCE)
        seed[FIELD_SOURCE_TYPE] = parse_source_type(cell(FIELD_SOURCE_TYPE))
    elif breeder:
        seed[FIELD_BREEDER], seed[FIELD_SOURCE], seed[FIELD_SOURCE_TYPE] = split_breeder(breeder)

    if raw := cell(FIELD_TYPE):
        seed[FIELD_TYPE] = parse_type(raw)
        if seed[FIELD_TYPE] is None:
            warnings.append(f"Art „{raw}“ unbekannt")

    if raw := cell(FIELD_GENOTYPE):
        seed[FIELD_GENOTYPE] = parse_genotype(raw)
        if seed[FIELD_GENOTYPE] is None:
            warnings.append(f"Genotyp „{raw}“ unbekannt")

    if raw := cell(_FLOWER):
        if (flower := parse_flower(raw)) is None:
            warnings.append(f"Blütetage „{raw}“ nicht erkannt – in Anmerkung übernommen")
            notes.append(f"Blütetage: {raw}")
        else:
            seed[FIELD_FLOWER_MIN], seed[FIELD_FLOWER_MAX], seed[FIELD_TOTAL_RUNTIME] = flower

    raw = cell(FIELD_QUANTITY)
    quantity = _int(raw) if raw else None
    if quantity is None or quantity < 0:
        warnings.append(
            f"Menge „{raw}“ ungültig – 0 übernommen" if raw else "Menge fehlt – 0 übernommen"
        )
        quantity = 0
    seed[FIELD_QUANTITY] = quantity

    if raw := cell(FIELD_RECEIVED):
        seed[FIELD_RECEIVED] = parse_received(raw)
        if seed[FIELD_RECEIVED] is None:
            warnings.append(f"Eingang „{raw}“ nicht erkannt – in Anmerkung übernommen")
            notes.append(f"Eingang: {raw}")

    seed[FIELD_NOTES] = "\n".join(notes)
    return seed, warnings


def _warn_duplicates(rows: list[dict[str, Any]]) -> None:
    seen_nr: set[int] = set()
    seen_code: set[str] = set()
    for row in rows:
        seed = row["seed"]
        if (nr := seed[FIELD_NR]) is not None:
            if nr in seen_nr:
                row["warnings"].append(f"Nr. {nr} doppelt – wird neu vergeben")
            seen_nr.add(nr)
        if code := (seed[FIELD_CODE] or "").casefold():
            if code in seen_code:
                row["warnings"].append(f"Kürzel „{seed[FIELD_CODE]}“ doppelt – wird geleert")
            seen_code.add(code)


def export_csv(seeds: list[dict[str, Any]]) -> str:
    """Semikolon-CSV mit BOM, damit Excel Umlaute und Spalten richtig erkennt."""

    def flower(seed: dict[str, Any]) -> str:
        low, high = seed[FIELD_FLOWER_MIN], seed[FIELD_FLOWER_MAX]
        if low is None:
            return ""
        text = str(low) if low == high else f"{low}-{high}"
        return f"{text} (fertig)" if seed[FIELD_TOTAL_RUNTIME] else text

    out = io.StringIO()
    writer = csv.writer(out, delimiter=";", lineterminator="\r\n")
    writer.writerow(EXPORT_HEADERS)
    for seed in seeds:
        writer.writerow(
            [
                seed[FIELD_NR],
                seed[FIELD_NAME],
                seed[FIELD_LINEAGE] or "",
                seed[FIELD_BREEDER] or "",
                seed[FIELD_SOURCE] or "",
                _SOURCE_TYPE_LABELS.get(seed[FIELD_SOURCE_TYPE], ""),
                _TYPE_LABELS.get(seed[FIELD_TYPE], ""),
                seed[FIELD_CODE] or "",
                _GENOTYPE_LABELS.get(seed[FIELD_GENOTYPE], ""),
                flower(seed),
                seed[FIELD_QUANTITY],
                seed[FIELD_RECEIVED] or "",
                seed[FIELD_NOTES] or "",
            ]
        )
    return "﻿" + out.getvalue()
