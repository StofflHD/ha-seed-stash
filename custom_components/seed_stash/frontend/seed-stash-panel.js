/**
 * Seed Stash – Seitenleisten-Panel für Home Assistant.
 * Eigenständige Web-Komponente ohne Build-Schritt.
 */

const SEED_TYPES = ["reg", "fem", "auto_reg", "auto_fem"];
const GENOTYPES = ["indica", "indica_dominant", "hybrid", "sativa_dominant", "sativa"];
const SOURCE_TYPES = ["shop", "trade", "own", "other"];
const QUANTITY_KINDS = ["germinated", "removed", "added", "correction"];

const TYPE_COLORS = {
  reg: "#43a047",
  fem: "#ab47bc",
  auto_reg: "#fb8c00",
  auto_fem: "#e53935",
};

const I18N = {
  en: {
    title: "Seed Stash",
    settings: "Settings",
    not_loaded: "Seed Stash is not set up or not loaded.",
    empty: "Your stash is empty. Add an entry or import your spreadsheet as CSV.",
    no_match: "No entries match the filter.",
    seeds: "seeds",
    strains: "strains in stock",
    low: "low stock",
    old: "old",
    search: "Search name, code, lineage …",
    all_types: "All types",
    all_genotypes: "All genotypes",
    all_breeders: "All breeders",
    hide_empty: "Hide empty",
    add: "New entry",
    import: "Import",
    export: "Export",
    nr: "No.",
    name: "Strain",
    lineage: "Lineage",
    breeder: "Breeder",
    source: "Source",
    source_type: "Source type",
    type: "Type",
    code: "Code",
    genotype: "Genotype",
    flower: "Flowering days",
    flower_min: "Flowering from",
    flower_max: "to (days)",
    total_runtime: "Total runtime (seed to harvest)",
    total_short: "total",
    quantity: "Quantity",
    received: "Received",
    received_hint: "e.g. 2024-11, 11.2024 or 2018-2019",
    invalid_number: "“{field}” needs a whole number.",
    notes: "Notes",
    none: "–",
    save: "Save",
    saved: "Saved",
    saving: "Saving …",
    close: "Close",
    cancel: "Cancel",
    delete: "Delete entry",
    delete_confirm: "Really delete “{name}”?",
    delete_warning: "The entry and its log will be lost. This cannot be undone.",
    delete_final: "Delete permanently",
    edit: "Edit",
    new_entry: "New entry",
    auto_nr: "automatic",
    stock: "Stock",
    change_stock: "Change stock",
    kind: "Kind",
    count: "Count",
    new_quantity: "New quantity",
    date: "Date",
    note: "Note",
    apply: "Apply",
    log: "Log",
    log_empty: "No entries yet",
    import_title: "Import CSV",
    import_help:
      "In Excel use “Save as → CSV (semicolon separated)”. Columns are detected by their header: No., Strain, Lineage, Breeder, Type, Code, Genotype, Flowering days, Quantity, Received, Notes.",
    file: "File",
    mode: "Mode",
    mode_append: "Add to stash",
    mode_replace: "Replace stash",
    replace_warning: "All existing entries and their logs will be deleted.",
    preview: "Preview",
    warnings: "Notes",
    errors: "Skipped rows",
    line: "Row",
    import_n: "Import {n} entries",
    imported: "{n} entries imported",
    low_badge: "low",
    old_badge: "old",
    kinds: {
      added: "Added",
      germinated: "Germinated",
      removed: "Given away/other",
      correction: "Correction",
      import: "Import",
    },
    types: { reg: "Reg", fem: "Fem", auto_reg: "Auto Reg", auto_fem: "Auto Fem" },
    genotypes: {
      indica: "100% Indica",
      sativa: "100% Sativa",
      hybrid: "Hybrid",
      indica_dominant: "Indica dominant",
      sativa_dominant: "Sativa dominant",
    },
    source_types: { shop: "Shop", trade: "Trade/forum", own: "Own breeding", other: "Other" },
  },
  de: {
    title: "Seed Stash",
    settings: "Einstellungen",
    not_loaded: "Seed Stash ist nicht eingerichtet oder nicht geladen.",
    empty: "Deine Samenkiste ist leer. Lege einen Eintrag an oder importiere deine Excel-Liste als CSV.",
    no_match: "Keine Einträge passen zum Filter.",
    seeds: "Samen",
    strains: "Sorten vorrätig",
    low: "wenig Samen",
    old: "alt",
    search: "Sorte, Kürzel, Kreuzung suchen …",
    all_types: "Alle Arten",
    all_genotypes: "Alle Genotypen",
    all_breeders: "Alle Züchter",
    hide_empty: "Leere ausblenden",
    add: "Neuer Eintrag",
    import: "Import",
    export: "Export",
    nr: "Nr.",
    name: "Sorte",
    lineage: "Kreuzung",
    breeder: "Züchter",
    source: "Quelle",
    source_type: "Quellentyp",
    type: "Art",
    code: "Kürzel",
    genotype: "Genotyp",
    flower: "Blütetage",
    flower_min: "Blütetage von",
    flower_max: "bis",
    total_runtime: "Gesamtlaufzeit (Samen bis Ernte)",
    total_short: "gesamt",
    quantity: "Menge",
    received: "Eingang",
    received_hint: "z. B. 2024-11, 11.2024 oder 2018-2019",
    invalid_number: "„{field}“ braucht eine ganze Zahl.",
    notes: "Anmerkung",
    none: "–",
    save: "Speichern",
    saved: "Gespeichert",
    saving: "Speichere …",
    close: "Schließen",
    cancel: "Abbrechen",
    delete: "Eintrag löschen",
    delete_confirm: "„{name}“ wirklich löschen?",
    delete_warning: "Der Eintrag und sein Protokoll gehen verloren. Das lässt sich nicht rückgängig machen.",
    delete_final: "Endgültig löschen",
    edit: "Bearbeiten",
    new_entry: "Neuer Eintrag",
    auto_nr: "automatisch",
    stock: "Bestand",
    change_stock: "Bestand ändern",
    kind: "Art",
    count: "Anzahl",
    new_quantity: "Neue Menge",
    date: "Datum",
    note: "Notiz",
    apply: "Übernehmen",
    log: "Protokoll",
    log_empty: "Noch keine Einträge",
    import_title: "CSV importieren",
    import_help:
      "In Excel „Speichern unter → CSV (Trennzeichen-getrennt)“ wählen. Die Spalten werden an der Kopfzeile erkannt: Nr., Sorte, Kreuzung, Züchter, Art, Kürzel, Genotyp, Blütetage, Menge, Eingang, Anmerkung.",
    file: "Datei",
    mode: "Modus",
    mode_append: "Zur Samenkiste hinzufügen",
    mode_replace: "Samenkiste ersetzen",
    replace_warning: "Alle bisherigen Einträge und ihre Protokolle werden gelöscht.",
    preview: "Vorschau",
    warnings: "Hinweise",
    errors: "Übersprungene Zeilen",
    line: "Zeile",
    import_n: "{n} Einträge importieren",
    imported: "{n} Einträge importiert",
    low_badge: "wenig",
    old_badge: "alt",
    kinds: {
      added: "Hinzugefügt",
      germinated: "Gekeimt",
      removed: "Abgegeben/sonstiges",
      correction: "Korrektur",
      import: "Import",
    },
    types: { reg: "Reg", fem: "Fem", auto_reg: "Auto Reg", auto_fem: "Auto Fem" },
    genotypes: {
      indica: "100% Indica",
      sativa: "100% Sativa",
      hybrid: "Hybrid",
      indica_dominant: "Indica dominant",
      sativa_dominant: "Sativa dominant",
    },
    source_types: { shop: "Shop", trade: "Tausch/Forum", own: "Eigene Zucht", other: "Sonstiges" },
  },
};

const INTEGRATION_URL = "/config/integrations/integration/seed_stash";

const COLUMNS = [
  { key: "nr", cls: "num" },
  { key: "name" },
  { key: "code" },
  { key: "breeder" },
  { key: "type" },
  { key: "genotype" },
  { key: "flower", cls: "num" },
  { key: "quantity", cls: "num" },
  { key: "received" },
];

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

class SeedStashPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._error = null;
    this._unsub = null;
    this._built = false;
    // Offener Dialog: {mode: "seed" | "new" | "import", id?}
    this._dialog = null;
    this._filter = { text: "", type: "", genotype: "", breeder: "", hideEmpty: false };
    this._sort = { key: "nr", dir: 1 };
    this._import = null;
  }

  // --- Eigenschaften, die Home Assistant setzt ------------------------------

  set hass(hass) {
    const languageChanged = this._hass && this._hass.language !== hass.language;
    this._hass = hass;
    if (!this._built) this._build();
    this._menuButton.hass = hass;
    this.style.colorScheme = hass.themes?.darkMode ? "dark" : "light";
    if (!this._unsub) this._subscribe();
    if (languageChanged) {
      this._renderStatic();
      this._renderAll();
    }
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (this._menuButton) this._menuButton.narrow = narrow;
  }

  set panel(panel) {
    this._panel = panel;
  }

  connectedCallback() {
    if (this._hass && !this._unsub) this._subscribe();
  }

  disconnectedCallback() {
    if (this._unsub) {
      this._unsub.then((unsub) => unsub()).catch(() => {});
      this._unsub = null;
    }
  }

  // --- Daten ------------------------------------------------------------------

  _subscribe() {
    this._unsub = this._hass.connection.subscribeMessage(
      (data) => {
        this._data = data;
        this._error = null;
        this._renderAll();
      },
      { type: "seed_stash/subscribe" }
    );
    this._unsub.catch((err) => {
      this._error = err.message || String(err);
      this._unsub = null;
      this._renderMain();
    });
  }

  _seed(id) {
    return this._data?.seeds.find((s) => s.id === id);
  }

  // --- Hilfen -------------------------------------------------------------------

  get _lang() {
    return (this._hass?.language || "en").startsWith("de") ? "de" : "en";
  }

  _t(key, vars = {}) {
    const dict = I18N[this._lang];
    let text = key.split(".").reduce((obj, part) => obj?.[part], dict);
    if (text === undefined) text = key.split(".").reduce((obj, part) => obj?.[part], I18N.en) ?? key;
    return String(text).replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");
  }

  _date(iso) {
    if (!iso) return this._t("none");
    const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString(this._hass.language, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  }

  _received(value) {
    if (!value) return this._t("none");
    const month = /^(\d{4})-(\d{2})$/.exec(value);
    if (!month) return value.replace("-", "–");
    return new Date(Number(month[1]), Number(month[2]) - 1, 1).toLocaleDateString(
      this._hass.language,
      { month: "short", year: "numeric" }
    );
  }

  _flower(seed) {
    if (seed.flower_min == null) return this._t("none");
    const range =
      seed.flower_min === seed.flower_max ? `${seed.flower_min}` : `${seed.flower_min}–${seed.flower_max}`;
    return seed.total_runtime ? `${range} (${this._t("total_short")})` : range;
  }

  _typeChip(type) {
    if (!type) return this._t("none");
    return `<span class="chip" style="--chip:${TYPE_COLORS[type] || "#888"}">${esc(
      this._t(`types.${type}`)
    )}</span>`;
  }

  _options(values, prefix, selected, emptyLabel = "") {
    const empty = `<option value="">${esc(emptyLabel)}</option>`;
    return (
      empty +
      values
        .map(
          (v) =>
            `<option value="${esc(v)}" ${v === selected ? "selected" : ""}>${esc(
              prefix ? this._t(`${prefix}.${v}`) : v
            )}</option>`
        )
        .join("")
    );
  }

  _navigate(path) {
    history.pushState(null, "", path);
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
  }

  _status(el, text, ok) {
    el.textContent = text;
    el.className = `status ${ok ? "ok" : "error"}`;
  }

  // --- Aufbau -------------------------------------------------------------------

  _build() {
    this._built = true;
    this.shadowRoot.innerHTML = `
      <style>${STYLES}</style>
      <div class="toolbar">
        <span class="menu"></span>
        <div class="title"></div>
        <button class="text-button" id="import"></button>
        <button class="text-button" id="export"></button>
        <button class="text-button" id="settings"></button>
      </div>
      <main>
        <div id="summary" class="summary"></div>
        <div class="filters">
          <input id="f-text" type="search" />
          <select id="f-type"></select>
          <select id="f-genotype"></select>
          <select id="f-breeder"></select>
          <label class="check"><input id="f-empty" type="checkbox" /><span id="f-empty-label"></span></label>
          <span class="spacer"></span>
          <button class="primary" id="add"></button>
        </div>
        <div id="main"></div>
      </main>
      <div class="overlay hidden" id="overlay">
        <div class="dialog" role="dialog" aria-modal="true">
          <div class="dialog-header">
            <div id="dlg-title" class="dlg-name"></div>
            <button class="icon-button" id="dlg-close" aria-label="close">✕</button>
          </div>
          <div class="dialog-body">
            <div id="dlg-info"></div>
            <div id="dlg-forms"></div>
          </div>
        </div>
      </div>
    `;
    const $ = (id) => this.shadowRoot.getElementById(id);
    this._menuButton = document.createElement("ha-menu-button");
    this._menuButton.hass = this._hass;
    this._menuButton.narrow = this._narrow;
    this.shadowRoot.querySelector(".menu").appendChild(this._menuButton);

    $("settings").addEventListener("click", () => this._navigate(INTEGRATION_URL));
    $("export").addEventListener("click", () => this._export());
    $("import").addEventListener("click", () => this._openDialog({ mode: "import" }));
    $("add").addEventListener("click", () => this._openDialog({ mode: "new" }));
    $("f-text").addEventListener("input", (ev) => {
      this._filter.text = ev.target.value;
      this._renderMain();
    });
    for (const [id, key] of [["f-type", "type"], ["f-genotype", "genotype"], ["f-breeder", "breeder"]]) {
      $(id).addEventListener("change", (ev) => {
        this._filter[key] = ev.target.value;
        this._renderMain();
      });
    }
    $("f-empty").addEventListener("change", (ev) => {
      this._filter.hideEmpty = ev.target.checked;
      this._renderMain();
    });
    $("main").addEventListener("click", (ev) => {
      const head = ev.target.closest("[data-sort]");
      if (head) {
        const key = head.dataset.sort;
        this._sort = { key, dir: this._sort.key === key ? -this._sort.dir : 1 };
        this._renderMain();
        return;
      }
      const row = ev.target.closest("[data-seed]");
      if (row) this._openDialog({ mode: "seed", id: row.dataset.seed });
    });
    $("main").addEventListener("keydown", (ev) => {
      const row = ev.target.closest("[data-seed]");
      if (row && ev.key === "Enter") this._openDialog({ mode: "seed", id: row.dataset.seed });
    });
    $("dlg-close").addEventListener("click", () => this._closeDialog());
    $("overlay").addEventListener("click", (ev) => {
      if (ev.target.id === "overlay") this._closeDialog();
    });
    this.shadowRoot.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape") this._closeDialog();
    });
    this._renderStatic();
  }

  _renderStatic() {
    const $ = (id) => this.shadowRoot.getElementById(id);
    this.shadowRoot.querySelector(".title").textContent = this._t("title");
    $("settings").textContent = this._t("settings");
    $("export").textContent = this._t("export");
    $("import").textContent = this._t("import");
    $("add").textContent = `+ ${this._t("add")}`;
    $("f-text").placeholder = this._t("search");
    $("f-type").innerHTML = this._options(SEED_TYPES, "types", this._filter.type, this._t("all_types"));
    $("f-genotype").innerHTML = this._options(
      GENOTYPES,
      "genotypes",
      this._filter.genotype,
      this._t("all_genotypes")
    );
    $("f-empty-label").textContent = this._t("hide_empty");
  }

  _renderAll() {
    if (!this._built) return;
    this._renderSummary();
    this._renderMain();
    if (this._pendingOpen && this._seed(this._pendingOpen)) {
      const id = this._pendingOpen;
      this._pendingOpen = null;
      if (this._dialog?.mode === "new") this._openDialog({ mode: "seed", id });
      return;
    }
    if (!this._dialog) return;
    if (this._dialog.mode === "seed") {
      if (this._seed(this._dialog.id)) this._renderSeedInfo();
      else this._closeDialog();
    }
  }

  // --- Übersicht ----------------------------------------------------------------

  _renderSummary() {
    const el = this.shadowRoot.getElementById("summary");
    const data = this._data;
    if (!data?.loaded) {
      el.innerHTML = "";
      return;
    }
    const item = (n, label, cls = "") =>
      `<span class="summary-item ${cls}"><b>${n}</b> ${esc(this._t(label))}</span>`;
    el.innerHTML = [
      item(data.total, "seeds"),
      item(data.in_stock, "strains"),
      data.low_ids.length ? item(data.low_ids.length, "low", "warn") : "",
      data.old_ids.length ? item(data.old_ids.length, "old", "warn") : "",
    ].join("");

    // Züchter-Filter aus den vorhandenen Einträgen
    const breeders = [...new Set(data.seeds.map((s) => s.breeder).filter(Boolean))].sort((a, b) =>
      a.localeCompare(b)
    );
    if (this._filter.breeder && !breeders.includes(this._filter.breeder)) this._filter.breeder = "";
    this.shadowRoot.getElementById("f-breeder").innerHTML = this._options(
      breeders,
      "",
      this._filter.breeder,
      this._t("all_breeders")
    );
  }

  _filtered() {
    const f = this._filter;
    const text = f.text.trim().toLocaleLowerCase();
    const rows = this._data.seeds.filter((s) => {
      if (f.hideEmpty && !s.quantity) return false;
      if (f.type && s.type !== f.type) return false;
      if (f.genotype && s.genotype !== f.genotype) return false;
      if (f.breeder && s.breeder !== f.breeder) return false;
      if (!text) return true;
      return [s.name, s.code, s.lineage, s.breeder, s.source, s.notes, String(s.nr)].some((v) =>
        (v || "").toLocaleLowerCase().includes(text)
      );
    });
    const { key, dir } = this._sort;
    const value = (s) => {
      if (key === "flower") return s.flower_min;
      if (key === "type") return s.type ? SEED_TYPES.indexOf(s.type) : null;
      if (key === "genotype") return s.genotype ? GENOTYPES.indexOf(s.genotype) : null;
      return s[key];
    };
    return rows.sort((a, b) => {
      const va = value(a);
      const vb = value(b);
      // Leere Werte immer ans Ende
      if (va == null || va === "") return vb == null || vb === "" ? a.nr - b.nr : 1;
      if (vb == null || vb === "") return -1;
      const cmp =
        typeof va === "number" ? va - vb : String(va).localeCompare(String(vb), undefined, { numeric: true });
      return cmp * dir || a.nr - b.nr;
    });
  }

  _renderMain() {
    const main = this.shadowRoot.getElementById("main");
    if (this._error) {
      main.innerHTML = `<div class="empty error">${esc(this._error)}</div>`;
      return;
    }
    if (!this._data) {
      main.innerHTML = `<div class="empty">…</div>`;
      return;
    }
    if (!this._data.loaded) {
      main.innerHTML = `<div class="empty">${esc(this._t("not_loaded"))}</div>`;
      return;
    }
    if (!this._data.seeds.length) {
      main.innerHTML = `<div class="empty">${esc(this._t("empty"))}</div>`;
      return;
    }
    const rows = this._filtered();
    if (!rows.length) {
      main.innerHTML = `<div class="empty">${esc(this._t("no_match"))}</div>`;
      return;
    }
    const low = new Set(this._data.low_ids);
    const old = new Set(this._data.old_ids);
    const head = COLUMNS.map(({ key, cls }) => {
      const arrow = this._sort.key === key ? (this._sort.dir > 0 ? " ▲" : " ▼") : "";
      return `<th class="${cls || ""}" data-sort="${key}">${esc(this._t(key))}${arrow}</th>`;
    }).join("");
    const body = rows
      .map((s) => {
        const badges = [
          low.has(s.id) ? `<span class="badge">${esc(this._t("low_badge"))}</span>` : "",
          old.has(s.id) ? `<span class="badge">${esc(this._t("old_badge"))}</span>` : "",
        ].join("");
        const source = s.source || (s.source_type ? this._t(`source_types.${s.source_type}`) : "");
        return `
          <tr data-seed="${esc(s.id)}" tabindex="0" class="${s.quantity ? "" : "empty-row"}">
            <td class="num">${s.nr}</td>
            <td><div class="strong">${esc(s.name)}</div>${
              s.lineage ? `<div class="secondary small">${esc(s.lineage)}</div>` : ""
            }</td>
            <td>${esc(s.code || this._t("none"))}</td>
            <td><div>${esc(s.breeder || this._t("none"))}</div>${
              source ? `<div class="secondary small">${esc(source)}</div>` : ""
            }</td>
            <td>${this._typeChip(s.type)}</td>
            <td>${esc(s.genotype ? this._t(`genotypes.${s.genotype}`) : this._t("none"))}</td>
            <td class="num">${esc(this._flower(s))}</td>
            <td class="num"><b>${s.quantity}</b>${badges}</td>
            <td>${esc(this._received(s.received))}</td>
          </tr>`;
      })
      .join("");
    main.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead><tr>${head}</tr></thead>
          <tbody>${body}</tbody>
        </table>
      </div>`;
  }

  // --- Dialog -------------------------------------------------------------------

  _openDialog(dialog) {
    this._dialog = dialog;
    this.shadowRoot.getElementById("overlay").classList.remove("hidden");
    const info = this.shadowRoot.getElementById("dlg-info");
    const forms = this.shadowRoot.getElementById("dlg-forms");
    info.innerHTML = "";
    forms.innerHTML = "";
    if (dialog.mode === "import") {
      this._import = null;
      this.shadowRoot.getElementById("dlg-title").textContent = this._t("import_title");
      this._renderImport();
      return;
    }
    if (dialog.mode === "new") {
      this.shadowRoot.getElementById("dlg-title").textContent = this._t("new_entry");
      this._renderEditForm(null);
      return;
    }
    this._renderSeedInfo();
    this._renderEditForm(this._seed(dialog.id));
  }

  _closeDialog() {
    this._dialog = null;
    this._import = null;
    this._pendingOpen = null;
    this.shadowRoot.getElementById("overlay").classList.add("hidden");
  }

  /** Bestand, Bestandsänderung und Protokoll – wird bei Live-Updates neu gezeichnet. */
  _renderSeedInfo() {
    const seed = this._seed(this._dialog.id);
    const info = this.shadowRoot.getElementById("dlg-info");
    this.shadowRoot.getElementById("dlg-title").textContent = `${seed.nr} · ${seed.name}`;

    const log = [...seed.log]
      .reverse()
      .map(
        (item) => `
        <li>
          <span>${esc(this._date(item.date))} · ${esc(this._t(`kinds.${item.kind}`))}${
            item.note ? `<div class="secondary small">${esc(item.note)}</div>` : ""
          }</span>
          <span class="nowrap"><b class="${item.delta < 0 ? "minus" : "plus"}">${
            item.delta > 0 ? "+" : ""
          }${item.delta}</b> → ${item.quantity}</span>
        </li>`
      )
      .join("");

    const keep = info.querySelector("form");
    const kind = keep?.elements.kind.value || "germinated";
    info.innerHTML = `
      <div class="stock">
        <div><div class="secondary small">${esc(this._t("stock"))}</div><div class="big">${seed.quantity}</div></div>
        <div>${this._typeChip(seed.type)}</div>
        ${seed.code ? `<div class="secondary">${esc(this._t("code"))}: <b>${esc(seed.code)}</b></div>` : ""}
      </div>
      <div class="columns">
        <div>
          <h3>${esc(this._t("change_stock"))}</h3>
          <form id="qty-form" novalidate>
            <div class="row">
              <label>${esc(this._t("kind"))}
                <select name="kind">${QUANTITY_KINDS.map(
                  (k) => `<option value="${k}" ${k === kind ? "selected" : ""}>${esc(this._t(`kinds.${k}`))}</option>`
                ).join("")}</select>
              </label>
              <label><span id="count-label"></span>
                <input name="count" type="number" min="0" step="1" value="1" required />
              </label>
              <label>${esc(this._t("date"))}
                <input name="date" type="date" value="${esc(this._data.today)}" max="${esc(this._data.today)}" />
              </label>
            </div>
            <label>${esc(this._t("note"))}<input name="note" type="text" maxlength="500" /></label>
            <button class="primary" type="submit">${esc(this._t("apply"))}</button>
            <div class="status" id="qty-status"></div>
          </form>
        </div>
        <div>
          <h3>${esc(this._t("log"))}</h3>
          ${log ? `<ul class="list log">${log}</ul>` : `<div class="secondary">${esc(this._t("log_empty"))}</div>`}
        </div>
      </div>
    `;
    const form = info.querySelector("#qty-form");
    const updateLabel = () => {
      const isCorrection = form.elements.kind.value === "correction";
      info.querySelector("#count-label").textContent = this._t(isCorrection ? "new_quantity" : "count");
      if (isCorrection) form.elements.count.value = seed.quantity;
    };
    form.elements.kind.addEventListener("change", updateLabel);
    updateLabel();
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const status = info.querySelector("#qty-status");
      const button = form.querySelector("button");
      button.disabled = true;
      try {
        await this._hass.callWS({
          type: "seed_stash/change_quantity",
          seed_id: seed.id,
          kind: form.elements.kind.value,
          count: Number(form.elements.count.value),
          date: form.elements.date.value || undefined,
          note: form.elements.note.value || undefined,
        });
        // Bei einer Änderung zeichnet das Live-Update das Formular neu, ohne Änderung
        // (z. B. Korrektur auf den aktuellen Wert) kommt keins
        status.textContent = "";
      } catch (err) {
        this._status(status, err?.message || String(err), false);
      }
      button.disabled = false;
    });
  }

  _renderEditForm(seed) {
    const forms = this.shadowRoot.getElementById("dlg-forms");
    const v = (key) => esc(seed?.[key] ?? "");
    const text = (key, extra = "") =>
      `<label>${esc(this._t(key))}<input name="${key}" type="text" value="${v(key)}" ${extra} /></label>`;
    const number = (key, extra = "") =>
      `<label>${esc(this._t(key))}<input name="${key}" type="number" step="1" min="0" value="${v(key)}" ${extra} /></label>`;
    const select = (key, values, prefix) =>
      `<label>${esc(this._t(key))}<select name="${key}">${this._options(values, prefix, seed?.[key] ?? "", this._t("none"))}</select></label>`;

    forms.innerHTML = `
      <form id="edit-form" class="${seed ? "edit" : ""}" novalidate>
        ${seed ? `<h3>${esc(this._t("edit"))}</h3>` : ""}
        <div class="row">
          ${number("nr", `min="1" placeholder="${esc(this._t("auto_nr"))}"`)}
          ${text("name", 'required maxlength="200"')}
          ${text("code", 'maxlength="20"')}
        </div>
        <div class="row">${text("lineage", 'maxlength="500"')}</div>
        <div class="row">
          ${text("breeder", 'maxlength="200"')}
          ${text("source", 'maxlength="200"')}
          ${select("source_type", SOURCE_TYPES, "source_types")}
        </div>
        <div class="row">
          ${select("type", SEED_TYPES, "types")}
          ${select("genotype", GENOTYPES, "genotypes")}
        </div>
        <div class="row">
          ${number("flower_min", 'min="1" max="365"')}
          ${number("flower_max", 'min="1" max="365"')}
          <label class="check"><input name="total_runtime" type="checkbox" ${
            seed?.total_runtime ? "checked" : ""
          } />${esc(this._t("total_runtime"))}</label>
        </div>
        <div class="row">
          ${seed ? "" : number("quantity", 'value="0"')}
          ${text("received", `placeholder="${esc(this._t("received_hint"))}"`)}
        </div>
        <label>${esc(this._t("notes"))}<textarea name="notes" rows="3" maxlength="5000">${v("notes")}</textarea></label>
        <div class="footer">
          <button class="primary" type="submit">${esc(this._t("save"))}</button>
          ${seed ? `<button class="text-button danger-text" type="button" id="delete">${esc(this._t("delete"))}</button>` : ""}
        </div>
        <div id="confirm"></div>
        <div class="status" id="edit-status"></div>
      </form>
    `;
    const form = forms.querySelector("form");
    // Eigener Klick-Handler: nicht davon abhängig, dass der Browser das Formular absendet
    form.addEventListener("submit", (ev) => ev.preventDefault());
    form.querySelector("button[type=submit]").addEventListener("click", (ev) => {
      ev.preventDefault();
      this._saveSeed(form, seed);
    });
    form.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && ev.target.tagName === "INPUT") {
        ev.preventDefault();
        this._saveSeed(form, seed);
      }
    });
    forms.querySelector("#delete")?.addEventListener("click", () => this._confirmDelete(seed));
  }

  async _saveSeed(form, seed) {
    const status = form.querySelector("#edit-status");
    const button = form.querySelector("button[type=submit]");
    if (button.disabled) return;
    // Ungültige Zahl (z. B. "56-63") liefert sonst einen leeren Wert und würde das Feld leeren
    const bad = [...form.elements].find((el) => el.validity?.badInput);
    if (bad) {
      this._status(status, this._t("invalid_number", { field: this._t(bad.name) }), false);
      bad.focus();
      return;
    }
    button.disabled = true;
    status.textContent = this._t("saving");
    status.className = "status";
    try {
      const data = {};
      for (const el of form.elements) {
        if (!el.name) continue;
        if (el.type === "checkbox") data[el.name] = el.checked;
        else if (el.type === "number") data[el.name] = el.value === "" ? null : Number(el.value);
        else data[el.name] = String(el.value ?? "").trim() || null;
      }
      if (data.quantity === null) data.quantity = 0;
      const msg = { type: "seed_stash/save_seed", seed: data };
      if (seed) msg.seed_id = seed.id;
      const result = await this._hass.callWS(msg);
      if (seed) {
        this._status(status, this._t("saved"), true);
      } else if (this._seed(result.seed_id)) {
        this._openDialog({ mode: "seed", id: result.seed_id });
      } else {
        // Live-Update mit dem neuen Eintrag ist noch unterwegs
        this._pendingOpen = result.seed_id;
      }
    } catch (err) {
      console.error("Seed Stash: Speichern fehlgeschlagen", err);
      this._status(status, err?.message || String(err), false);
    } finally {
      button.disabled = false;
    }
  }

  _confirmDelete(seed) {
    const box = this.shadowRoot.getElementById("confirm");
    box.innerHTML = `
      <div class="confirm">
        <p><b>${esc(this._t("delete_confirm", { name: seed.name }))}</b></p>
        <p>${esc(this._t("delete_warning"))}</p>
        <div class="confirm-buttons">
          <button class="text-button" type="button" id="del-cancel">${esc(this._t("cancel"))}</button>
          <button class="danger" type="button" id="del-ok">${esc(this._t("delete_final"))}</button>
        </div>
      </div>`;
    box.querySelector("#del-cancel").addEventListener("click", () => (box.innerHTML = ""));
    box.querySelector("#del-ok").addEventListener("click", async () => {
      try {
        await this._hass.callWS({ type: "seed_stash/delete_seed", seed_id: seed.id });
        this._closeDialog();
      } catch (err) {
        this._status(this.shadowRoot.getElementById("edit-status"), err?.message || String(err), false);
      }
    });
  }

  // --- Import / Export ------------------------------------------------------------

  _renderImport() {
    const forms = this.shadowRoot.getElementById("dlg-forms");
    const state = this._import;
    const preview = state?.preview;
    const replace = state?.replace ?? false;

    let previewHtml = "";
    if (preview) {
      const rows = preview.rows
        .map(({ line, seed, warnings }) => {
          const source = [seed.source, seed.source_type ? this._t(`source_types.${seed.source_type}`) : ""]
            .filter(Boolean)
            .join(" · ");
          return `
          <tr class="${warnings.length ? "warn-row" : ""}">
            <td class="num">${line}</td>
            <td class="num">${seed.nr ?? "–"}</td>
            <td><div class="strong">${esc(seed.name)}</div>${
              seed.lineage ? `<div class="secondary small">${esc(seed.lineage)}</div>` : ""
            }</td>
            <td>${esc(seed.code || "–")}</td>
            <td>${esc(seed.breeder || "–")}${source ? `<div class="secondary small">${esc(source)}</div>` : ""}</td>
            <td>${this._typeChip(seed.type)}</td>
            <td>${esc(seed.genotype ? this._t(`genotypes.${seed.genotype}`) : "–")}</td>
            <td class="num">${esc(this._flower(seed))}</td>
            <td class="num">${seed.quantity}</td>
            <td>${esc(this._received(seed.received))}</td>
            <td class="small">${warnings.map((w) => esc(w)).join("<br>")}</td>
          </tr>`;
        })
        .join("");
      const errors = preview.errors
        .map((e) => `<li>${esc(this._t("line"))} ${e.line} (${esc(e.name)}): ${esc(e.error)}</li>`)
        .join("");
      previewHtml = `
        <h3>${esc(this._t("preview"))}</h3>
        <div class="table-wrap">
          <table class="preview">
            <thead><tr>
              <th>${esc(this._t("line"))}</th><th>${esc(this._t("nr"))}</th><th>${esc(this._t("name"))}</th>
              <th>${esc(this._t("code"))}</th><th>${esc(this._t("breeder"))}</th><th>${esc(this._t("type"))}</th>
              <th>${esc(this._t("genotype"))}</th><th>${esc(this._t("flower"))}</th><th>${esc(this._t("quantity"))}</th>
              <th>${esc(this._t("received"))}</th><th>${esc(this._t("warnings"))}</th>
            </tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
        ${errors ? `<h3>${esc(this._t("errors"))}</h3><ul class="errors">${errors}</ul>` : ""}
      `;
    }

    forms.innerHTML = `
      <p class="secondary">${esc(this._t("import_help"))}</p>
      <div class="row">
        <label>${esc(this._t("file"))}<input id="imp-file" type="file" accept=".csv,text/csv" /></label>
        <label>${esc(this._t("mode"))}
          <select id="imp-mode">
            <option value="append" ${replace ? "" : "selected"}>${esc(this._t("mode_append"))}</option>
            <option value="replace" ${replace ? "selected" : ""}>${esc(this._t("mode_replace"))}</option>
          </select>
        </label>
      </div>
      ${replace ? `<div class="confirm small-confirm">${esc(this._t("replace_warning"))}</div>` : ""}
      ${previewHtml}
      <div class="footer">
        ${
          preview?.rows.length
            ? `<button class="${replace ? "danger" : "primary"}" id="imp-go">${esc(
                this._t("import_n", { n: preview.rows.length })
              )}</button>`
            : ""
        }
      </div>
      <div class="status" id="imp-status"></div>
    `;
    const status = forms.querySelector("#imp-status");
    if (state?.error) this._status(status, state.error, false);

    forms.querySelector("#imp-mode").addEventListener("change", (ev) => {
      this._import = { ...(this._import || {}), replace: ev.target.value === "replace" };
      this._renderImport();
    });
    forms.querySelector("#imp-file").addEventListener("change", async (ev) => {
      const file = ev.target.files[0];
      if (!file) return;
      const csv = await this._readText(file);
      try {
        const result = await this._hass.callWS({ type: "seed_stash/import_preview", csv });
        this._import = { replace, csv, preview: result };
      } catch (err) {
        this._import = { replace, error: err?.message || String(err) };
      }
      this._renderImport();
    });
    forms.querySelector("#imp-go")?.addEventListener("click", async (ev) => {
      ev.target.disabled = true;
      try {
        const result = await this._hass.callWS({
          type: "seed_stash/import",
          csv: state.csv,
          replace,
        });
        this._import = null;
        this._renderImport();
        this._status(forms.querySelector("#imp-status"), this._t("imported", { n: result.imported }), true);
      } catch (err) {
        this._status(status, err?.message || String(err), false);
        ev.target.disabled = false;
      }
    });
  }

  /** Excel speichert CSV je nach Version als UTF-8 oder Windows-1252. */
  async _readText(file) {
    const buffer = await file.arrayBuffer();
    try {
      return new TextDecoder("utf-8", { fatal: true }).decode(buffer);
    } catch (_err) {
      return new TextDecoder("windows-1252").decode(buffer);
    }
  }

  async _export() {
    try {
      const result = await this._hass.callWS({ type: "seed_stash/export" });
      const url = URL.createObjectURL(new Blob([result.csv], { type: "text/csv;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = result.filename;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      this._error = err?.message || String(err);
      this._renderMain();
    }
  }
}

const STYLES = `
  :host {
    display: block;
    min-height: 100vh;
    /* Kein Überstand nach rechts, sonst zeigt Home Assistant unten eine Scrollleiste.
       clip statt hidden, damit die Kopfzeile sticky bleibt. */
    overflow-x: clip;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
  }
  .toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
    height: var(--header-height, 56px);
    padding: 0 12px 0 4px;
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, #fff);
    border-bottom: var(--app-header-border-bottom, none);
    position: sticky;
    top: 0;
    z-index: 2;
  }
  .title { flex: 1; font-size: 20px; margin-left: 8px; }
  main { padding: 16px; max-width: 1400px; margin: 0 auto; box-sizing: border-box; }
  .empty { padding: 48px 16px; text-align: center; color: var(--secondary-text-color); }
  .error { color: var(--error-color, #db4437); }
  .summary { display: flex; flex-wrap: wrap; gap: 8px 20px; margin-bottom: 12px; font-size: 15px; }
  .summary-item b { font-size: 20px; }
  .summary-item.warn b { color: var(--warning-color, #ffa600); }
  .filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; }
  .filters input[type=search] { flex: 1 1 240px; }
  .filters .spacer { flex: 1; }
  .secondary { color: var(--secondary-text-color); }
  .small { font-size: 12px; }
  .strong { font-weight: 500; }
  .nowrap { white-space: nowrap; }
  .table-wrap {
    overflow-x: auto;
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border-radius: var(--ha-card-border-radius, 12px);
    border: 1px solid var(--divider-color);
  }
  table { border-collapse: collapse; width: 100%; font-size: 14px; }
  th, td { padding: 8px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--divider-color); }
  th {
    font-size: 12px;
    font-weight: 500;
    color: var(--secondary-text-color);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
    position: sticky;
    top: 0;
    background: var(--ha-card-background, var(--card-background-color, #fff));
  }
  .preview th { cursor: default; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr[data-seed] { cursor: pointer; }
  tbody tr[data-seed]:hover, tbody tr[data-seed]:focus-visible {
    background: var(--secondary-background-color);
    outline: none;
  }
  .empty-row { opacity: 0.55; }
  .warn-row { background: color-mix(in srgb, var(--warning-color, #ffa600) 10%, transparent); }
  .num { text-align: right; white-space: nowrap; }
  .chip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 500;
    color: var(--chip);
    background: color-mix(in srgb, var(--chip) 18%, transparent);
    white-space: nowrap;
  }
  .badge {
    display: inline-block;
    margin-left: 6px;
    padding: 0 6px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 500;
    color: var(--warning-color, #ffa600);
    background: color-mix(in srgb, var(--warning-color, #ffa600) 15%, transparent);
  }
  button { font: inherit; }
  .text-button {
    background: none;
    border: none;
    color: inherit;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    text-transform: uppercase;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.05em;
  }
  .text-button:hover { background: rgba(127, 127, 127, 0.15); }
  .icon-button {
    background: none;
    border: none;
    color: inherit;
    font-size: 18px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
  }
  .icon-button:hover { background: rgba(127, 127, 127, 0.15); }
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    padding: 16px;
  }
  .overlay.hidden { display: none; }
  .dialog {
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color);
    border-radius: var(--ha-dialog-border-radius, 24px);
    width: min(1000px, 100%);
    max-height: calc(100vh - 32px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 20px 16px 12px 24px;
    border-bottom: 1px solid var(--divider-color);
  }
  .dlg-name { font-size: 22px; }
  .dialog-body { overflow-y: auto; padding: 16px 24px 24px; }
  .dialog .table-wrap { border-radius: 8px; }
  .stock { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
  .big { font-size: 32px; font-weight: 500; line-height: 1.1; }
  h3 { font-size: 14px; font-weight: 500; margin: 20px 0 8px; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.05em; }
  .columns { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0 32px; }
  .list { list-style: none; margin: 0; padding: 0; }
  .list li {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 6px 0;
    border-bottom: 1px solid var(--divider-color);
    font-size: 14px;
  }
  .log { max-height: 260px; overflow-y: auto; }
  .plus { color: var(--success-color, #43a047); }
  .minus { color: var(--error-color, #db4437); }
  .errors { margin: 0; padding-left: 20px; color: var(--error-color, #db4437); font-size: 14px; }
  #dlg-forms { border-top: 1px solid var(--divider-color); margin-top: 24px; }
  #dlg-info:empty + #dlg-forms { border-top: none; margin-top: 0; }
  form { display: flex; flex-direction: column; gap: 8px; }
  .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: flex-end; }
  .row > * { flex: 1; min-width: 140px; }
  label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--secondary-text-color); }
  label.check { flex-direction: row; align-items: center; gap: 6px; font-size: 14px; color: var(--primary-text-color); }
  .row label.check { padding-bottom: 8px; }
  select, input, textarea {
    font: inherit;
    font-size: 14px;
    color: var(--primary-text-color);
    background-color: var(--secondary-background-color);
    border: 1px solid var(--divider-color);
    border-radius: 6px;
    padding: 8px;
    box-sizing: border-box;
    min-width: 0;
  }
  input:invalid { border-color: var(--error-color, #db4437); }
  option, optgroup {
    background-color: var(--card-background-color, var(--primary-background-color));
    color: var(--primary-text-color);
  }
  label.check input { width: auto; }
  textarea { resize: vertical; width: 100%; }
  .primary {
    align-self: flex-start;
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    cursor: pointer;
    font-weight: 500;
  }
  .primary:disabled, .danger:disabled { opacity: 0.5; cursor: default; }
  .footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
  }
  .dialog .danger-text { color: var(--error-color, #db4437); }
  .confirm {
    border: 1px solid var(--error-color, #db4437);
    border-radius: 12px;
    padding: 12px 16px;
    max-width: 420px;
    background: color-mix(in srgb, var(--error-color, #db4437) 8%, transparent);
  }
  .small-confirm { margin-top: 8px; font-size: 14px; }
  .confirm p { margin: 0 0 8px; font-size: 14px; }
  .confirm-buttons { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }
  .danger {
    background: var(--error-color, #db4437);
    color: #fff;
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    cursor: pointer;
    font-weight: 500;
  }
  .status { min-height: 20px; margin-top: 8px; font-size: 14px; }
  .status.ok { color: var(--success-color, #43a047); }
  .status.error { color: var(--error-color, #db4437); }
  @media (max-width: 600px) {
    main { padding: 8px; }
    .toolbar .text-button { padding: 8px 6px; font-size: 12px; }
    .overlay { padding: 0; }
    .dialog { border-radius: 0; max-height: 100vh; height: 100vh; }
    .dialog-body { padding: 12px 16px 24px; }
  }
`;

if (!customElements.get("seed-stash-panel")) {
  customElements.define("seed-stash-panel", SeedStashPanel);
}
