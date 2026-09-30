// Experiment 2, condition H: human-only recording UI.
// Records exactly what the human enters. It never classifies, suggests, infers,
// sorts by relevance or pre-fills anything. All requests go to this local server.
"use strict";

let UNITS = null;          // scored paths and allowed option lists (from /api/units)
let CASE = null;           // current case id
let CASEINFO = null;       // request/question/ids for the current case only
let STATE = null;          // the human's record for the current case
let SELECTED = null;       // {kind: "asset"|"code", path}
let saveTimer = null;
let savePending = false;
const srcCache = new Map();

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
function localKey(c) { return `experiment-02-h-state-${c}`; }

// ------------------------------------------------------------------ persistence
function changed() {
  STATE.updated_at = isoNow();
  try { localStorage.setItem(localKey(CASE), JSON.stringify(STATE)); } catch (e) { /* storage full */ }
  savePending = true;
  status("Unsaved changes…");
  clearTimeout(saveTimer);
  saveTimer = setTimeout(flushSave, 600);
}

async function flushSave() {
  clearTimeout(saveTimer);
  if (!savePending || !STATE) return;
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

async function loadCase(c) {
  await flushSave();
  const [info, server] = await Promise.all([api("GET", `/api/case/${c}`), api("GET", `/api/state/${c}`)]);
  let st = server;
  const raw = localStorage.getItem(localKey(c));
  if (raw) {
    try {
      const local = JSON.parse(raw);
      const lt = local.updated_at ? Date.parse(local.updated_at) : 0;
      const stt = server.updated_at ? Date.parse(server.updated_at) : 0;
      if (local.case === c && lt > stt) { st = local; }
    } catch (e) { /* ignore unreadable local copy */ }
  }
  CASE = c; CASEINFO = info; STATE = st; SELECTED = null;
  localStorage.setItem("experiment-02-h-last-case", c);
  if (st !== server) { savePending = true; await flushSave(); }
  render();
}

// ------------------------------------------------------------------ timers
function running(segs) { return segs.length > 0 && segs[segs.length - 1].end === null; }
function total(segs) {
  let t = 0;
  for (const s of segs) t += (s.end ? Date.parse(s.end) : Date.now()) - Date.parse(s.start);
  return t;
}
function timerBox(label, key) {
  const segs = () => STATE[key];
  const clock = el("span", { class: "clock" });
  const list = el("pre");
  const start = el("button", { text: "Start", onclick: () => { segs().push({ start: isoNow(), end: null }); changed(); upd(); } });
  const stop = el("button", { text: "Stop", onclick: () => { segs()[segs().length - 1].end = isoNow(); changed(); upd(); } });
  function upd() {
    const r = running(segs());
    start.disabled = r; stop.disabled = !r;
    clock.textContent = hms(total(segs())) + (r ? " (running)" : "");
    list.textContent = segs().map((s, i) => `${i + 1}. ${s.start} → ${s.end || "…"}`).join("\n") || "(none)";
  }
  upd();
  const box = el("div", { class: "timer" }, el("span", { class: "label", text: label }), start, stop, clock,
    el("details", {}, el("summary", { text: "segments" }), list));
  box._upd = upd;
  return box;
}

// ------------------------------------------------------------------ small editors
function optionSelect(options, value, onchange) {
  const s = el("select", {}, el("option", { value: "", text: "" }), options.map(o => el("option", { value: o, text: o })));
  s.value = value;
  s.addEventListener("change", () => { onchange(s.value); });
  return s;
}
function textInput(obj, key, multiline) {
  const i = multiline ? el("textarea") : el("input", { type: "text" });
  i.value = obj[key];
  i.addEventListener("input", () => { obj[key] = i.value; changed(); });
  return i;
}
function field(label, control) { return el("div", { class: "field" }, el("span", { class: "label", text: label }), control); }

function evidenceEditor(list, rerender) {
  const rows = el("div", { class: "rows" });
  list.forEach((e, i) => {
    rows.append(el("div", { class: "row" },
      el("div", { class: "rowhead" }, el("span", { text: `evidence ${i + 1}` }),
        el("button", { text: "Delete", onclick: () => { list.splice(i, 1); changed(); rerender(); } })),
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
  return el("div", {}, rows, el("button", { text: "Add evidence item", onclick: () => { list.push(blankEvidence()); changed(); rerender(); } }));
}

function stringListEditor(list, label, rerender, multiline) {
  const rows = el("div", { class: "rows" });
  list.forEach((v, i) => {
    const inp = multiline ? el("textarea") : el("input", { type: "text" });
    inp.value = v;
    inp.addEventListener("input", () => { list[i] = inp.value; changed(); });
    rows.append(el("div", { class: "row" },
      el("div", { class: "rowhead" }, el("span", { text: `${label} ${i + 1}` }),
        el("button", { text: "Delete", onclick: () => { list.splice(i, 1); changed(); rerender(); } })), inp));
  });
  return el("div", {}, rows, el("button", { text: `Add ${label}`, onclick: () => { list.push(""); changed(); rerender(); } }));
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
          el("button", { text: "Delete", onclick: () => { rec.relationships.splice(j, 1); changed(); rer(); } })),
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
      field("relationships", el("div", {}, rels, el("button", {
        text: "Add relationship",
        onclick: () => { rec.relationships.push({ related_asset: "", relationship_status: "", reason: "", evidence: [] }); changed(); rer(); }
      })))));
  }
}

// ------------------------------------------------------------------ viewer (middle)
async function renderViewer(host) {
  host.replaceChildren();
  if (!SELECTED) return;
  const p = SELECTED.path, url = "/fixture/" + p.split("/").map(encodeURIComponent).join("/");
  host.append(el("div", { class: "path", text: p }));
  if (SELECTED.kind === "asset") {
    const dims = el("span", { class: "muted" });
    const img = el("img", { src: url, alt: p });
    img.addEventListener("load", () => { dims.textContent = `${img.naturalWidth}×${img.naturalHeight} px · `; });
    host.append(el("div", { class: "label" }, dims, el("a", { href: url, target: "_blank", rel: "noopener", text: "open original" })), img);
    return;
  }
  let text = srcCache.get(p);
  if (text === undefined) {
    const r = await fetch(url);
    text = await r.text();
    srcCache.set(p, text);
  }
  if (!SELECTED || SELECTED.path !== p) return;
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
    onclick: () => { SELECTED = { kind, path: p }; renderFiles(); renderViewer(viewerHost); renderLedger(ledgerHost); }
  }, p, entered ? el("span", { class: "entered", text: `[${entered}]` }) : null));
  filesHost.append(
    el("h2", { text: "ASSET units (15)" }), el("ul", {}, UNITS.assets.map(p => item("asset", p, STATE.assets[p].status))),
    el("h2", { text: "CODE units (8)" }), el("ul", {}, UNITS.code.map(p => item("code", p, STATE.code[p].file_status))));
}

// ------------------------------------------------------------------ page
let tick = null;
function render() {
  const main = document.getElementById("main");
  main.replaceChildren();
  renderNav();
  const inv = timerBox("Investigation", "investigation_segments");
  const doc = timerBox("Documentation (separate; never added to investigation)", "documentation_segments");
  clearInterval(tick);
  tick = setInterval(() => { inv._upd(); doc._upd(); }, 1000);

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
  const exportBtn = el("button", {
    text: `Export H-${CASE}.yaml`, onclick: async () => {
      if (running(STATE.investigation_segments) || running(STATE.documentation_segments)) {
        if (!confirm("A timer is still running. The open segment is exported without an end time and is not counted. Export anyway?")) return;
      }
      savePending = true;
      await flushSave();
      try {
        const r = await api("POST", `/api/export/${CASE}`, {});
        exportMsg.textContent = `Written: ${r.written}`;
        out.textContent = r.yaml; out.hidden = false;
      } catch (e) { exportMsg.textContent = `Export failed: ${e.message}`; }
    }
  });
  const exportMsg = el("span", { class: "muted" });
  const next = { A: "B", B: "C" }[CASE];

  main.append(
    el("section", { class: "case" },
      el("h1", { text: `Test ${CASE}: ${CASEINFO.title}` }),
      el("div", { class: "label", text: "Exact request:" }), el("blockquote", { text: CASEINFO.request }),
      el("div", { class: "label", text: "Question:" }), el("blockquote", { text: CASEINFO.question })),
    el("div", { class: "timers" }, inv, doc),
    el("div", { class: "work" }, filesHost, viewerHost, ledgerHost),
    extra,
    el("div", { class: "exportbar" }, exportBtn, exportMsg,
      next ? el("button", { text: `Go to Test ${next}`, onclick: () => loadCase(next) }) : null),
    out);
  renderFiles();
  renderLedger(ledgerHost);
}

function renderNav() {
  const nav = document.getElementById("casenav");
  nav.replaceChildren(...UNITS.cases.map(c => el("button", { class: c === CASE ? "on" : "", text: `Test ${c}`, onclick: () => loadCase(c) })));
}

window.addEventListener("beforeunload", () => { if (savePending) flushSave(); });

(async function init() {
  try {
    UNITS = await api("GET", "/api/units");
    CASE = null;
    renderNav();
    const last = localStorage.getItem("experiment-02-h-last-case");
    await loadCase(UNITS.cases.includes(last) ? last : "A");
  } catch (e) { status(`Could not load: ${e.message}`); }
})();
