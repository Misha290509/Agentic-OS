/* AIOS dashboard — vanilla JS, polls /api/overview. Panels + theme + refresh
   interval all come from config/ui.json (served inside the overview blob). */
"use strict";

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function applyTheme(theme) {
  if (!theme) return;
  const r = document.documentElement.style;
  const map = { page: "--page", surface: "--surface", ink: "--ink",
    ink_secondary: "--ink-2", ink_muted: "--ink-3", hairline: "--hairline",
    border: "--border", accent: "--accent" };
  for (const [k, v] of Object.entries(map)) if (theme[k]) r.setProperty(v, theme[k]);
  for (const [k, v] of Object.entries(theme.status || {})) r.setProperty(`--${k}`, v);
}

/* Minimal markdown: headings, bullets, paragraphs. Input is escaped first. */
function md(text) {
  const lines = esc(text).replace(/^---[\s\S]*?---\n/, "").split("\n");
  let out = "", inList = false;
  for (const line of lines) {
    if (/^#{1,3} /.test(line)) {
      if (inList) { out += "</ul>"; inList = false; }
      out += `<h3>${line.replace(/^#+ /, "")}</h3>`;
    } else if (/^- /.test(line)) {
      if (!inList) { out += "<ul>"; inList = true; }
      out += `<li>${line.slice(2)}</li>`;
    } else if (line.trim()) {
      if (inList) { out += "</ul>"; inList = false; }
      out += `<p>${line}</p>`;
    }
  }
  return out + (inList ? "</ul>" : "");
}

function tbl(rows, cols) {
  if (!rows || !rows.length) return `<div class="empty">nothing here</div>`;
  const head = cols.map((c) => `<th>${esc(c.h)}</th>`).join("");
  const body = rows.map((r) =>
    `<tr>${cols.map((c) => `<td class="${c.cls || ""}">${c.f(r)}</td>`).join("")}</tr>`).join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}
const status = (s) => `<span class="status ${esc(s)}">${esc(s)}</span>`;

function tiles(d) {
  const c = d.counts || {};
  const t = [
    { v: c.open_tasks, l: "open tasks" },
    { v: c.open_bugs_s1s2, l: "S1/S2 bugs", alert: c.open_bugs_s1s2 > 0 },
    { v: c.open_bugs, l: "open bugs" },
    { v: c.open_loops, l: "open loops" },
    { v: c.failed_runs_7d, l: "failed runs (7d)", alert: c.failed_runs_7d > 0 },
    { v: c.queue, l: "queued triggers" },
  ];
  $("stats").innerHTML = t.map((x) =>
    `<div class="tile${x.alert ? " alert" : ""}"><div class="v">${x.v ?? "–"}</div><div class="l">${esc(x.l)}</div></div>`).join("");
}

async function trigger(id, btn) {
  btn.disabled = true;
  try {
    const res = await fetch("/api/action", { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: id }) });
    if ((await res.json()).ok) { btn.classList.add("sent"); setTimeout(() => btn.classList.remove("sent"), 2000); }
  } finally { btn.disabled = false; refresh(); }
}

function actions(ui) {
  const box = $("actions");
  if (box.childElementCount) return; // build once
  for (const a of ui.quick_actions || []) {
    const b = document.createElement("button");
    b.textContent = a.label;
    b.title = a.hint || "";
    b.onclick = () => trigger(a.id, b);
    box.appendChild(b);
  }
}

function render(d) {
  const ui = d.ui || {}, p = ui.panels || {};
  $("meta").textContent = `updated ${d.generated}`;
  applyTheme(ui.theme);

  $("stats").hidden = !p.stats; if (p.stats) tiles(d);
  $("actions").hidden = !(ui.quick_actions || []).length; actions(ui);

  const show = (name, fn) => { const el = $(`panel-${name}`); el.hidden = !p[name]; if (p[name]) fn(); };

  show("focus", () => $("focus").innerHTML = d.focus ? md(d.focus) : `<div class="empty">state/current-focus.md is empty</div>`);

  show("open_loops", () => $("open_loops").innerHTML = tbl(d.open_loops, [
    { h: "loop", f: (r) => esc(r.loop), cls: "t" },
    { h: "status", f: (r) => status(r.status) },
    { h: "iter", f: (r) => esc(r.iteration) },
    { h: "next action", f: (r) => esc(r.next_action) },
  ]));

  show("tasks", () => $("tasks").innerHTML = tbl(d.tasks, [
    { h: "#", f: (r) => r.id },
    { h: "p", f: (r) => r.priority },
    { h: "task", f: (r) => esc(r.title), cls: "t" },
    { h: "status", f: (r) => status(r.status) },
    { h: "project", f: (r) => esc(r.project) },
  ]));

  show("bugs", () => $("bugs").innerHTML = tbl(d.bugs, [
    { h: "#", f: (r) => r.id },
    { h: "sev", f: (r) => status(r.severity) },
    { h: "bug", f: (r) => esc(r.title), cls: "t" },
    { h: "area", f: (r) => esc(r.area) },
    { h: "reports", f: (r) => r.report_count },
  ]));

  show("runs", () => $("runs").innerHTML = tbl(d.runs, [
    { h: "automation", f: (r) => esc(r.automation), cls: "t" },
    { h: "status", f: (r) => status(r.status) },
    { h: "started", f: (r) => esc((r.started_at || "").slice(5, 16)) },
    { h: "detail", f: (r) => esc(r.detail) },
  ]));

  show("sessions", () => $("sessions").innerHTML = tbl(d.sessions, [
    { h: "started", f: (r) => esc((r.started_at || "").slice(0, 16)) },
    { h: "focus", f: (r) => esc(r.focus), cls: "t" },
    { h: "summary", f: (r) => esc(r.summary) },
  ]));

  show("metrics", () => $("metrics").innerHTML = tbl(d.metrics, [
    { h: "metric", f: (r) => esc(r.label || r.name), cls: "t" },
    { h: "latest", f: (r) => r.latest ? `${r.latest.value}${esc(r.unit)}` : "–" },
    { h: "recorded", f: (r) => esc(r.latest ? r.latest.recorded_at.slice(5, 16) : "") },
    { h: "history", f: (r) => esc((r.history || []).map((x) => x.value).join(" · ")) },
  ]));

  show("queue", () => $("queue").innerHTML = tbl(d.queue, [
    { h: "trigger", f: (r) => esc(r.action), cls: "t" },
    { h: "requested", f: (r) => esc(r.requested_at) },
    { h: "via", f: (r) => esc(r.via) },
  ]));

  const entries = (d.session_log || "").split(/\n(?=## )/).filter((s) => s.startsWith("## "));
  $("panel-log").hidden = false;
  $("session_log").innerHTML = entries.length
    ? md(entries.slice(0, (ui.limits || {}).log_entries || 3).join("\n"))
    : `<div class="empty">no session log yet</div>`;
}

async function refresh() {
  try {
    const d = await (await fetch("/api/overview")).json();
    render(d);
    if (!refresh.timer) refresh.timer = setInterval(refresh, ((d.ui || {}).refresh_seconds || 10) * 1000);
  } catch (e) {
    $("meta").textContent = `connection lost — is serve_dashboard.py running? (${e.message})`;
  }
}
refresh();
