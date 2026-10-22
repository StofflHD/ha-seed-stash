# Seed Stash for Home Assistant

Keep track of your seed stash in Home Assistant – strains, stock and every seed you take out.

*The user interface is available in English and German.*

## Features

- **Sidebar panel** – sortable table with search and filters (type, genotype, breeder), entry details and editing
- **Stock log** – germinated, given away, added or corrected, each with date and note
- **CSV import** – bring over your existing spreadsheet (Excel “Save as CSV”); breeder/source, flowering days and dates are recognised automatically, with a preview before anything is saved
- **CSV export** – back to Excel at any time
- **Entities** – total seeds, strains in stock, low stock and old seeds for dashboards and automations
- **Actions** – `seed_stash.take_seeds` and `seed_stash.add_seeds` (by number, code or strain)

## Installation

Requires Home Assistant **2025.6** or newer.

1. HACS → **⋮ → Custom repositories**
2. Repository `https://github.com/StofflHD/ha-seed-stash`, type **Integration**
3. Download **Seed Stash** and restart Home Assistant
4. *Settings → Devices & services → Add integration → Seed Stash*

## License

[GNU General Public License v3.0](LICENSE)
