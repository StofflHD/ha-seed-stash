"""Tests für CSV-Import und -Export."""

from __future__ import annotations

import pytest

from custom_components.seed_stash.csv_io import (
    export_csv,
    parse_csv,
    parse_flower,
    parse_genotype,
    parse_received,
    parse_type,
    split_breeder,
)
from homeassistant.exceptions import ServiceValidationError

# Aufbau wie die Excel-Samenkiste: Titelzeile, Kopfzeile, Leerzeile, Summenzeile
EXCEL_CSV = """SAMENKISTE;;;;;;;;;;
Nr.;Sorte;Kreuzung;Züchter;Art;Kürzel;Genotyp;Blütetage;Menge;Eingang;Anmerkung
1;Bubble Cross F2;Bubble Gum x Sour Gum;Gärtner42 (Forum);Reg;BC;;;15;01.11.2024;
2;Lemon Auto;;Beispiel Seeds;Auto Fem;LA;Indica dominant;70-75 (fertig);10;01.05.2024;CBD-THC ausgeglichen
3;Haze Klassiker;;Altbestand Seeds;Fem;HK;Sativa dominant;77-84;5;2018-2019;
4;;;;;;;;;;
5;Dank F5;G13 x OG;Tauschpartner (Forum) / Bodhi Seeds;Reg;DF;Indica;;12;Jan 25;
6;Ohne Menge;;Beispiel Seeds;Reg;OM;100% Sativa;56;;Feb. 2025;
7;Komisch;;Beispiel Seeds;Superfem;KO;Mostly Indica;irgendwann;3;letztes Jahr;
8;Doppelt;;Beispiel Seeds;Reg;BC;Hybrid;9 Wochen;1;2025;
;Gesamtmenge;46;;;;;;;;
"""


def test_parse_excel_layout() -> None:
    result = parse_csv(EXCEL_CSV)
    assert result["errors"] == []
    rows = {row["seed"]["nr"]: row for row in result["rows"]}
    # Leerzeile und Summenzeile fehlen
    assert sorted(rows) == [1, 2, 3, 5, 6, 7, 8]
    assert rows[1]["line"] == 3

    bc = rows[1]["seed"]
    assert bc["breeder"] == "Gärtner42"
    assert bc["source"] is None
    assert bc["source_type"] == "trade"
    assert bc["type"] == "reg"
    assert bc["received"] == "2024-11"
    assert bc["quantity"] == 15
    assert rows[1]["warnings"] == []

    la = rows[2]["seed"]
    assert la["type"] == "auto_fem"
    assert la["genotype"] == "indica_dominant"
    assert (la["flower_min"], la["flower_max"], la["total_runtime"]) == (70, 75, True)
    assert la["notes"] == "CBD-THC ausgeglichen"

    assert rows[3]["seed"]["received"] == "2018-2019"

    df = rows[5]["seed"]
    assert (df["breeder"], df["source"], df["source_type"]) == (
        "Bodhi Seeds",
        "Tauschpartner",
        "trade",
    )
    assert df["genotype"] == "indica"
    assert df["received"] == "2025-01"

    om = rows[6]
    assert om["seed"]["quantity"] == 0
    assert om["seed"]["received"] == "2025-02"
    assert om["seed"]["genotype"] == "sativa"
    assert om["warnings"] == ["Menge fehlt – 0 übernommen"]

    ko = rows[7]
    assert ko["seed"]["type"] is None
    assert ko["seed"]["genotype"] is None
    assert ko["seed"]["received"] is None
    assert ko["seed"]["notes"] == "Blütetage: irgendwann\nEingang: letztes Jahr"
    assert len(ko["warnings"]) == 4

    doppelt = rows[8]
    assert (doppelt["seed"]["flower_min"], doppelt["seed"]["flower_max"]) == (63, 63)
    assert doppelt["warnings"] == ["Kürzel „BC“ doppelt – wird geleert"]


def test_parse_comma_csv_without_nr_and_errors() -> None:
    text = "Sorte,Art,Menge,Blütetage\nA,Fem,3,56-63\nB,Reg,2,400\n"
    result = parse_csv(text)
    assert [row["seed"]["name"] for row in result["rows"]] == ["A"]
    assert result["rows"][0]["seed"]["nr"] is None
    assert result["errors"][0]["line"] == 3
    assert result["errors"][0]["name"] == "B"


def test_parse_without_header() -> None:
    with pytest.raises(ServiceValidationError, match="Kopfzeile"):
        parse_csv("a;b;c\n1;2;3\n")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("01.11.2024", "2024-11"),
        ("1.3.24", "2024-03"),
        ("11.2024", "2024-11"),
        ("11/2024", "2024-11"),
        ("11/1/2024", "2024-11"),
        ("2024-11-01 00:00:00", "2024-11"),
        ("2024-11", "2024-11"),
        ("2024", "2024"),
        ("2018-2019", "2018-2019"),
        ("2018 – 2019", "2018-2019"),
        ("Nov 24", "2024-11"),
        ("März 2025", "2025-03"),
        ("Dez. 2023", "2023-12"),
        ("2024-13", None),
        ("irgendwann", None),
    ],
)
def test_parse_received(value: str, expected: str | None) -> None:
    assert parse_received(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("56", (56, 56, False)),
        ("53-60", (53, 60, False)),
        ("70-75 (fertig)", (70, 75, True)),
        ("8-9 Wochen", (56, 63, False)),
        ("9w", (63, 63, False)),
        ("60-50", None),
        ("bald", None),
    ],
)
def test_parse_flower(value: str, expected: tuple | None) -> None:
    assert parse_flower(value) == expected


def test_parse_type_and_genotype() -> None:
    assert parse_type("Auto Reg") == "auto_reg"
    assert parse_type("feminisiert") == "fem"
    assert parse_type("auto") is None
    assert parse_genotype("100% Indica") == "indica"
    assert parse_genotype("Sativa-dominant") == "sativa_dominant"


def test_split_breeder() -> None:
    assert split_breeder("Sensi Seeds") == ("Sensi Seeds", None, None)
    assert split_breeder("Terpene Titan (Kwik seeds)") == ("Terpene Titan (Kwik seeds)", None, None)
    assert split_breeder("Philosopher Seeds (Forum)") == ("Philosopher Seeds", None, "trade")
    assert split_breeder("Hans (Forum) / Alpine Seeds") == ("Alpine Seeds", "Hans", "trade")


def test_export_roundtrip() -> None:
    seeds = [row["seed"] for row in parse_csv(EXCEL_CSV)["rows"]]
    text = export_csv(seeds)
    assert text.startswith("﻿Nr.;Sorte;")
    assert (
        "2;Lemon Auto;;Beispiel Seeds;;;Auto Fem;LA;Indica dominant;70-75 (fertig);10;2024-05;"
        in text
    )

    again = [row["seed"] for row in parse_csv(text)["rows"]]
    assert again == seeds
