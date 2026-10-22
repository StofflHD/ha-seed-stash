"""Freie Eingaben (Excel, Panel) in die gespeicherten Formate umwandeln."""

from __future__ import annotations

import re

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "mrz": 3, "maer": 3, "apr": 4, "mai": 5, "may": 5,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dez": 12,
    "dec": 12,
}  # fmt: skip


def norm(value: str) -> str:
    """Vergleichsschlüssel: klein, Umlaute ausgeschrieben, nur Buchstaben/Ziffern."""
    value = value.casefold()
    for old, new in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        value = value.replace(old, new)
    return re.sub(r"[^a-z0-9]", "", value)


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
    if m := re.fullmatch(r"(\d{1,2})\s*[./-]\s*(\d{4})", value):
        return month(int(m[2]), int(m[1]))
    if re.fullmatch(r"\d{4}", value):
        return value if 1900 <= int(value) <= 2100 else None
    if m := re.fullmatch(r"([^\W\d_]+)[\s.'-]*(\d{2}|\d{4})", value):
        number = _MONTHS.get(norm(m[1])[:3]) or _MONTHS.get(norm(m[1])[:4])
        year = int(m[2])
        if number:
            return month(year + 2000 if year < 100 else year, number)
    return None
