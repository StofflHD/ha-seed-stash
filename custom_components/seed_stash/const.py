"""Konstanten für Seed Stash."""

DOMAIN = "seed_stash"

# Samen-Eintrag (eine Zeile der Samenkiste)
FIELD_NR = "nr"
FIELD_NAME = "name"
FIELD_LINEAGE = "lineage"
FIELD_BREEDER = "breeder"
FIELD_SOURCE = "source"
FIELD_SOURCE_TYPE = "source_type"
FIELD_TYPE = "type"
FIELD_CODE = "code"
FIELD_GENOTYPE = "genotype"
FIELD_FLOWER_MIN = "flower_min"
FIELD_FLOWER_MAX = "flower_max"
# Blütetage sind die Gesamtlaufzeit vom Samen bis zur Ernte (Autoflower)
FIELD_TOTAL_RUNTIME = "total_runtime"
FIELD_QUANTITY = "quantity"
# "2024-11", "2024" oder Zeitraum "2018-2019"
FIELD_RECEIVED = "received"
FIELD_NOTES = "notes"

SEED_TYPE_REG = "reg"
SEED_TYPE_FEM = "fem"
SEED_TYPE_AUTO_REG = "auto_reg"
SEED_TYPE_AUTO_FEM = "auto_fem"
SEED_TYPES = [SEED_TYPE_REG, SEED_TYPE_FEM, SEED_TYPE_AUTO_REG, SEED_TYPE_AUTO_FEM]

GENOTYPES = ["indica", "sativa", "hybrid", "indica_dominant", "sativa_dominant"]

SOURCE_TYPE_SHOP = "shop"
# Getauscht/geschenkt, z. B. über ein Forum
SOURCE_TYPE_TRADE = "trade"
SOURCE_TYPE_OWN = "own"
SOURCE_TYPE_OTHER = "other"
SOURCE_TYPES = [SOURCE_TYPE_SHOP, SOURCE_TYPE_TRADE, SOURCE_TYPE_OWN, SOURCE_TYPE_OTHER]

# Bestandsprotokoll
LOG_ADDED = "added"
LOG_GERMINATED = "germinated"
LOG_REMOVED = "removed"
LOG_CORRECTION = "correction"
LOG_IMPORT = "import"
LOG_KINDS = [LOG_ADDED, LOG_GERMINATED, LOG_REMOVED, LOG_CORRECTION, LOG_IMPORT]
MAX_LOG = 200

# Optionen
CONF_LOW_STOCK = "low_stock"
CONF_MAX_AGE = "max_age_years"
DEFAULT_LOW_STOCK = 3
DEFAULT_MAX_AGE = 5

STORAGE_VERSION = 1
STORAGE_KEY = DOMAIN

SIGNAL_UPDATE = f"{DOMAIN}_update"
# Aktiver Hub für Panel und Aktionen (gesetzt, sobald die Daten bereitstehen)
DATA_HUB = f"{DOMAIN}_hub"

# Seitenleisten-Panel
PANEL_URL_PATH = "seed-stash"
PANEL_COMPONENT = "seed-stash-panel"
PANEL_ICON = "mdi:seed"
PANEL_TITLE = "Seed Stash"
STATIC_URL = "/seed_stash_static"
WS_SUBSCRIBE = f"{DOMAIN}/subscribe"
WS_SAVE_SEED = f"{DOMAIN}/save_seed"
WS_DELETE_SEED = f"{DOMAIN}/delete_seed"
WS_CHANGE_QUANTITY = f"{DOMAIN}/change_quantity"
WS_SET_LOG = f"{DOMAIN}/set_log"
WS_IMPORT_PREVIEW = f"{DOMAIN}/import_preview"
WS_IMPORT = f"{DOMAIN}/import"
WS_EXPORT = f"{DOMAIN}/export"

EVENT_QUANTITY_CHANGED = f"{DOMAIN}_quantity_changed"

SERVICE_TAKE_SEEDS = "take_seeds"
SERVICE_ADD_SEEDS = "add_seeds"

ATTR_SEED = "seed"
ATTR_COUNT = "count"
ATTR_KIND = "kind"
ATTR_NOTE = "note"
ATTR_DATE = "date"
