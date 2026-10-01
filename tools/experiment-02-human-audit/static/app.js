// Experiment 2, condition H: human-only recording UI.
// Records exactly what the human enters. It never classifies, suggests, infers,
// sorts by relevance or pre-fills anything. All requests go to this local server.
"use strict";

let UNITS = null;          // scored paths and allowed option lists (from /api/units)
let STATUS = null;         // run id and per-case unlocked/finalized flags (from /api/status)
let VIEW = "record";       // "record" | "evidence"
let CASE = null;           // current case id
let CASEINFO = null;       // request/question/ids for the current case only
let STATE = null;          // the human's record for the current case
let READONLY = false;      // true once the current case is finalized
let SELECTED = null;       // {kind: "asset"|"code", path}
let EVIDENCE = null;       // fixture evidence whitelist (from /api/evidence)
let EVSEL = null;          // selected evidence path
let saveTimer = null;
let savePending = false;
const textCache = new Map();

function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (v === true) e.setAttribute(k, "");
    else if (v !== false && v != null) e.setAttribute(k, v);
  }
  for (const c of kids.flat()) if (c != null) e.append(c);
  return e;
}

function pad(n) { return String(n).padStart(2, "0"); }
function isoNow() {
  const d = new Date();
  const off = -d.getTimezoneOffset(), a = Math.abs(off);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
    `${off >= 0 ? "+" : "-"}${pad(Math.floor(a / 60))}:${pad(a % 60)}`;
}
function hms(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  return `${pad(Math.floor(s / 3600))}:${pad(Math.floor(s % 3600 / 60))}:${pad(s % 60)}`;
}

async function api(method, url, body) {
  const opt = { method, headers: {} };
  if (body !== undefined) { opt.headers["Content-Type"] = "application/json"; opt.body = JSON.stringify(body); }
  const r = await fetch(url, opt);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
  return j;
}

function status(text) { document.getElementById("savestatus").textContent = text; }
function localKey(c) { return `experiment-02-h-${STATUS.run_id}-state-${c}`; }
function fileUrl(prefix, p) { return prefix + p.split("/").map(encodeURIComponent).join("/"); }

// ------------------------------------------------------------------ persistence
function changed() {
  if (READONLY) return;
  STATE.updated_at = isoNow();
  try { localStorage.setItem(localKey(CASE), JSON.stringify(STATE)); } catch (e) { /* storage full */ }
  savePending = true;
  status("Unsaved changes…");
  clearTimeout(saveTimer);
  saveTimer = setTimeout(flushSave, 600);
}

async function flushSave() {
  clearTimeout(saveTimer);
  if (!savePending || !STATE || READONLY) return;
  savePending = false;
  const c = CASE, snapshot = JSON.parse(JSON.stringify(STATE));
  try {
    await api("POST", `/api/state/${c}`, snapshot);
    status(`Saved Test ${c} at ${snapshot.updated_at}`);
  } catch (e) {
    savePending = true;
    status(`Save failed (kept in this browser): ${e.message}`);
  }
}

async function refreshStatus() { STATUS = await api("GET", "/api/status"); }

async function loadCase(c) {
  await flushSave();
  await refreshStatus();
  if (!STATUS.cases[c].unlocked) { status(`Test ${c} is locked.`); renderNav(); return; }
  const [info, server] = await Promise.all([api("GET", `/api/case/${c}`), api("GET", `/api/state/${c}`)]);
  let st = server;
  const ro = !!info.finalized;
  if (ro) {
    localStorage.removeItem(localKey(c));
  } else {
    const raw = localStorage.getItem(localKey(c));
    if (raw) {
      try {
        const local = JSON.parse(raw);
        const lt = local.updated_at ? Date.parse(local.updated_at) : 0;
        const stt = server.updated_at ? Date.parse(server.updated_at) : 0;
        if (local.case === c && lt > stt) { st = local; }
      } catch (e) { /* ignore unreadable local copy */ }
    }
  }
  CASE = c; CASEINFO = info; STATE = st; READONLY = ro; SELECTED = null; VIEW = "record";
  if (st !== server) { savePending = true; await flushSave(); }
  render();
}

// ------------------------------------------------------------------ timers (never overlap)
function running(segs) { return segs.length > 0 && segs[segs.length - 1].end === null; }
function total(segs) {
  let t = 0;
  for (const s of segs) t += (s.end ? Date.parse(s.end) : Date.now()) - Date.parse(s.start);
  return t;
}
const TIMERS = [
  { key: "investigation_segments", label: "Investigation" },
  { key: "documentation_segments", label: "Documentation (separate; never added to investigation)" },
];
function anyRunning() { return TIMERS.some(t => running(STATE[t.key])); }
function timerBox(t, other) {
  const segs = () => STATE[t.key];
  const clock = el("span", { class: "clock" });
  const note = el("span", { class: "blocked" });
  const list = el("pre");
  const start = el("button", { text: "Start", onclick: () => {
    if (running(STATE[other.key]) || running(segs()) || READONLY) return;
    segs().push({ start: isoNow(), end: null }); changed(); updAll();
  } });
  const stop = el("button", { text: "Stop", onclick: () => {
    if (!running(segs()) || READONLY) return;
    segs()[segs().length - 1].end = isoNow(); changed(); updAll();
  } });
  function upd() {
    const mine = running(segs()), theirs = running(STATE[other.key]);
    start.disabled = READONLY || mine || theirs;
    stop.disabled = READONLY || !mine;
    note.textContent = theirs && !READONLY ? `Start blocked: ${other.label.split(" ")[0]} is running` : "";
    clock.textContent = hms(total(segs())) + (mine ? " (running)" : "");
    list.textContent = segs().map((s, i) => `${i + 1}. ${s.start} → ${s.end || "…"}`).join("\n") || "(none)";
  }
  const box = el("div", { class: "timer" }, el("span", { class: "label", text: t.label }), start, stop, clock, note,
    el("details", {}, el("summary", { text: "segments" }), list));
  box._upd = upd;
  return box;
}
let timerBoxes = [];
function updAll() { timerBoxes.forEach(b => b._upd()); if (exportBtnUpd) exportBtnUpd(); }

// ------------------------------------------------------------------ small editors
function optionSelect(options, value, onchange) {
  const s = el("select", { disabled: READONLY }, el("option", { value: "", text: "" }), options.map(o => el("option", { value: o, text: o })));
  s.value = value;
  s.addEventListener("change", () => { onchange(s.value); });
  return s;
}
function textInput(obj, key, multiline) {
  const i = multiline ? el("textarea", { readonly: READONLY }) : el("input", { type: "text", readonly: READONLY });
  i.value = obj[key];
  i.addEventListener("input", () => { if (READONLY) return; obj[key] = i.value; changed(); });
  return i;
}
function field(label, control) { return el("div", { class: "field" }, el("span", { class: "label", text: label }), control); }
function editButton(text, fn) { return READONLY ? null : el("button", { text, onclick: fn }); }

function evidenceEditor(list, rerender) {
  const rows = el("div", { class: "rows" });
  list.forEach((e, i) => {
    rows.append(el("div", { class: "row" },
      el("div", { class: "rowhead" }, el("span", { text: `evidence ${i + 1}` }),
        editButton("Delete", () => { list.splice(i, 1); changed(); rerender(); })),
      el("div", { class: "grid2" },
        field("source_path", textInput(e, "source_path")),
        field("anchor_type", optionSelect(UNITS.anchor_types, e.anchor_type, v => { e.anchor_type = v; changed(); })),
        field("anchor", textInput(e, "anchor")),
        field("context (optional)", textInput(e, "context")),
        field("locator (optional)", textInput(e, "locator")),
        field("fingerprint (optional)", textInput(e, "fingerprint"))),
      field("fact", textInput(e, "fact", true))));
  });
  const blankEvidence = () => Object.fromEntries(UNITS.evidence_fields.map(k => [k, ""]));
  return el("div", {}, rows, editButton("Add evidence item", () => { list.push(blankEvidence()); changed(); rerender(); }));
}

function stringListEditor(list, label, rerender, multiline) {
  const rows = el("div", { class: "rows" });
  list.forEach((v, i) => {
    const inp = multiline ? el("textarea", { readonly: READONLY }) : el("input", { type: "text", readonly: READONLY });
    inp.value = v;
    inp.addEventListener("input", () => { if (READONLY) return; list[i] = inp.value; changed(); });
    rows.append(el("div", { class: "row" },
      el("div", { class: "rowhead" }, el("span", { text: `${label} ${i + 1}` }),
        editButton("Delete", () => { list.splice(i, 1); changed(); rerender(); })), inp));
  });
  return el("div", {}, rows, editButton(`Add ${label}`, () => { list.push(""); changed(); rerender(); }));
}

// ------------------------------------------------------------------ ledger (right)
function renderLedger(host) {
  host.replaceChildren();
  if (!SELECTED) { host.append(el("p", { class: "muted rec", text: "Select a file on the left." })); return; }
  const rer = () => { renderLedger(host); renderFiles(); };
  const p = SELECTED.path;
  if (SELECTED.kind === "asset") {
    const i = UNITS.assets.indexOf(p), rec = STATE.assets[p];
    host.append(el("h2", { text: `${CASEINFO.asset_ids[i]} · ASSET` }), el("div", { class: "rec" },
      field("asset_path", el("div", { class: "path", text: p })),
      field("status", optionSelect(UNITS.asset_status, rec.status, v => { rec.status = v; changed(); renderFiles(); })),
      field("reason", textInput(rec, "reason", true)),
      field("evidence", evidenceEditor(rec.evidence, rer)),
      field("game_usage", stringListEditor(rec.game_usage, "game_usage entry", rer))));
  } else {
    const i = UNITS.code.indexOf(p), rec = STATE.code[p];
    const rels = el("div", { class: "rows" });
    rec.relationships.forEach((r, j) => {
      rels.append(el("div", { class: "row" },
        el("div", { class: "rowhead" }, el("span", { text: `relationship ${j + 1}` }),
          editButton("Delete", () => { rec.relationships.splice(j, 1); changed(); rer(); })),
        field("related_asset", optionSelect(UNITS.assets, r.related_asset, v => { r.related_asset = v; changed(); })),
        field("relationship_status", optionSelect(UNITS.code_status, r.relationship_status, v => { r.relationship_status = v; changed(); })),
        field("reason", textInput(r, "reason", true)),
        field("evidence", evidenceEditor(r.evidence, rer))));
    });
    host.append(el("h2", { text: `${CASEINFO.code_ids[i]} · CODE` }), el("div", { class: "rec" },
      field("source_path", el("div", { class: "path", text: p })),
      field("file_status", optionSelect(UNITS.code_status, rec.file_status, v => { rec.file_status = v; changed(); renderFiles(); })),
      field("reason", textInput(rec, "reason", true)),
      field("evidence", evidenceEditor(rec.evidence, rer)),
      field("relationships", el("div", {}, rels, editButton("Add relationship", () => {
        rec.relationships.push({ related_asset: "", relationship_status: "", reason: "", evidence: [] }); changed(); rer();
      })))));
  }
}

// ------------------------------------------------------------------ file viewer (shared)
async function showFile(host, prefix, p, kind, isCurrent) {
  host.replaceChildren();
  const url = fileUrl(prefix, p);
  host.append(el("div", { class: "path", text: p }));
  if (kind === "image") {
    const dims = el("span", { class: "muted" });
    const img = el("img", { src: url, alt: p });
    img.addEventListener("load", () => { dims.textContent = `${img.naturalWidth}×${img.naturalHeight} px · `; });
    host.append(el("div", { class: "label" }, dims, el("a", { href: url, target: "_blank", rel: "noopener", text: "open original" })), img);
    return;
  }
  let text = textCache.get(url);
  if (text === undefined) {
    const r = await fetch(url);
    text = await r.text();
    textCache.set(url, text);
  }
  if (!isCurrent()) return;
  const pre = el("pre", { class: "src" });
  const lines = text.split("\n");
  if (lines.length && lines[lines.length - 1] === "") lines.pop();
  const frag = document.createDocumentFragment();
  lines.forEach((l, i) => { frag.append(el("span", { class: "ln", text: String(i + 1) }), l + "\n"); });
  pre.append(frag);
  host.append(el("div", { class: "label", text: `${lines.length} lines (raw fixture text)` }), pre);
}

// ------------------------------------------------------------------ file list (left)
let filesHost = null, viewerHost = null, ledgerHost = null;
function renderFiles() {
  if (!filesHost) return;
  filesHost.replaceChildren();
  const item = (kind, p, entered) => el("li", {}, el("button", {
    class: SELECTED && SELECTED.path === p ? "on" : "",
    onclick: () => {
      SELECTED = { kind, path: p }; renderFiles(); renderLedger(ledgerHost);
      showFile(viewerHost, "/fixture/", p, kind === "asset" ? "image" : "text", () => SELECTED && SELECTED.path === p);
    }
  }, p, entered ? el("span", { class: "entered", text: `[${entered}]` }) : null));
  filesHost.append(
    el("h2", { text: "ASSET units (15)" }), el("ul", {}, UNITS.assets.map(p => item("asset", p, STATE.assets[p].status))),
    el("h2", { text: "CODE units (8)" }), el("ul", {}, UNITS.code.map(p => item("code", p, STATE.code[p].file_status))));
}

// ------------------------------------------------------------------ evidence view
async function renderEvidence(main) {
  if (!EVIDENCE) EVIDENCE = await api("GET", "/api/evidence");
  const list = el("div", { class: "files" });
  const viewer = el("div", { class: "viewer" });
  const draw = () => {
    list.replaceChildren(el("h2", { text: `Fixture evidence (${EVIDENCE.files.length} files, fixtures/kite-production/, path order)` }),
      el("ul", {}, EVIDENCE.files.map(f => el("li", {}, el("button", {
        class: EVSEL === f.path ? "on" : "",
        onclick: () => { EVSEL = f.path; draw(); showFile(viewer, "/evidence/", f.path, f.type, () => EVSEL === f.path && VIEW === "evidence"); }
      }, f.path, el("span", { class: "entered", text: f.type }))))));
  };
  draw();
  main.append(el("section", { class: "case" }, el("h1", { text: "Fixture evidence (read-only)" }),
    el("div", { class: "label", text: "The evidence browser exposes the permitted static-production evidence. metadata/fixture-manifest.json is intentionally not exposed because it contains precomputed relationship/game-usage information. metadata/KITE_ASSET_MASTERLIST.md is intentionally not exposed because it describes excluded video material. These exclusions are experiment-interface protections and do not modify the frozen fixture. Timers keep their state while this view is open." })),
    el("div", { class: "work evidence" }, list, viewer));
  if (EVSEL) {
    const f = EVIDENCE.files.find(x => x.path === EVSEL);
    if (f) showFile(viewer, "/evidence/", f.path, f.type, () => EVSEL === f.path && VIEW === "evidence");
  }
}

// ------------------------------------------------------------------ page
let tick = null, exportBtnUpd = null;
function render() {
  const main = document.getElementById("main");
  main.replaceChildren();
  renderNav();
  clearInterval(tick);
  exportBtnUpd = null;
  if (VIEW === "evidence") { timerBoxes = []; renderEvidence(main); return; }
  if (!STATE) return;
  timerBoxes = [timerBox(TIMERS[0], TIMERS[1]), timerBox(TIMERS[1], TIMERS[0])];
  updAll();
  tick = setInterval(updAll, 1000);

  filesHost = el("div", { class: "files" });
  viewerHost = el("div", { class: "viewer" });
  ledgerHost = el("div", { class: "ledger" });

  const rerExtra = () => renderExtra(extra);
  const extra = el("div", { class: "extra" });
  function renderExtra(host) {
    host.replaceChildren(
      el("div", {}, el("h2", { text: "Unresolved items" }), stringListEditor(STATE.unresolved_items, "unresolved item", rerExtra, true)),
      el("div", {}, el("h2", { text: "Notes on work performed (optional)" }), textInput(STATE, "work_notes", true)));
  }
  renderExtra(extra);

  const out = el("pre", { class: "exported", hidden: true });
  const exportMsg = el("span", { class: "muted" });
  const next = { A: "B", B: "C" }[CASE];
  const bar = el("div", { class: "exportbar" });
  if (READONLY) {
    bar.append(el("span", { text: `Test ${CASE} finalized at ${CASEINFO.finalized.finalized_at}; exported to ${CASEINFO.finalized.export_file}. Read-only.` }));
  } else {
    const exportBtn = el("button", {
      text: `Export and finalize Test ${CASE}`, onclick: async () => {
        if (anyRunning()) return;
        if (!confirm(`Export and finalize Test ${CASE}? Test ${CASE} becomes read-only${next ? ` and Test ${next} unlocks` : ""}.`)) return;
        savePending = true;
        await flushSave();
        try {
          const r = await api("POST", `/api/finalize/${CASE}`, {});
          localStorage.removeItem(localKey(CASE));
          await loadCase(CASE);
          const o = document.querySelector("pre.exported");
          if (o) { o.textContent = r.yaml; o.hidden = false; }
          status(`Test ${CASE} exported and finalized: ${r.written}`);
        } catch (e) { exportMsg.textContent = `Export failed: ${e.message}`; }
      }
    });
    exportBtnUpd = () => {
      exportBtn.disabled = anyRunning();
      exportMsg.textContent = anyRunning() ? "Stop the running timer to export and finalize." : "";
    };
    exportBtnUpd();
    bar.append(exportBtn, exportMsg);
  }
  if (next) {
    const unlocked = STATUS.cases[next].unlocked;
    bar.append(el("button", { text: unlocked ? `Go to Test ${next}` : `Test ${next} locked until Test ${CASE} is finalized`,
      disabled: !unlocked, onclick: () => loadCase(next) }));
  }

  main.append(
    el("section", { class: "case" },
      el("h1", { text: `Test ${CASE}: ${CASEINFO.title}` + (READONLY ? " (finalized, read-only)" : "") }),
      el("div", { class: "label", text: "Exact request:" }), el("blockquote", { text: CASEINFO.request }),
      el("div", { class: "label", text: "Question:" }), el("blockquote", { text: CASEINFO.question })),
    el("div", { class: "timers" }, timerBoxes),
    el("div", { class: "work" }, filesHost, viewerHost, ledgerHost),
    extra, bar, out);
  renderFiles();
  renderLedger(ledgerHost);
}

function renderNav() {
  const nav = document.getElementById("casenav");
  const caseBtns = UNITS.cases.map(c => {
    const s = STATUS.cases[c];
    const word = s.finalized ? "finalized" : s.unlocked ? "open" : "locked";
    return el("button", { class: VIEW === "record" && c === CASE ? "on" : "", disabled: !s.unlocked,
      text: `Test ${c} · ${word}`, onclick: () => loadCase(c) });
  });
  nav.replaceChildren(...caseBtns, el("span", { class: "sep" }),
    el("button", { class: VIEW === "evidence" ? "on" : "", text: "Fixture evidence",
      onclick: async () => { await flushSave(); VIEW = "evidence"; render(); } }),
    VIEW === "evidence" && CASE ? el("button", { text: `Back to Test ${CASE}`, onclick: () => { VIEW = "record"; render(); } }) : null);
}

window.addEventListener("beforeunload", () => { if (savePending) flushSave(); });

(async function init() {
  try {
    UNITS = await api("GET", "/api/units");
    await refreshStatus();
    renderNav();
    await loadCase(STATUS.resume);   // always the earliest unlocked, not-finalized case
  } catch (e) { status(`Could not load: ${e.message}`); }
})();
