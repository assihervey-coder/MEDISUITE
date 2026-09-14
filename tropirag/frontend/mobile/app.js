/* TropiRAG Terrain — logique applicative mobile (offline-first). */
"use strict";

/* ============ Configuration locale ============ */
const LS = {
  settings: "tropirag.settings",
  queue: "tropirag.queue",
  lastCase: "tropirag.lastCase",
};

const SETTINGS = load(LS.settings, { server: "", key: "tropirag-local-key" });

function load(k, d) {
  try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; }
}
function save(k, v) { localStorage.setItem(k, JSON.stringify(v)); }

/* ============ Vocabulaire embarqué (fonctionne hors-ligne) ============ */
const CONDITIONS = [
  ["Drépanocytose", "drépanocytose SS"],
  ["VIH", "VIH"],
  ["Diabète", "diabète"],
  ["Déficit G6PD", "déficit en G6PD"],
  ["Épilepsie", "épilepsie"],
  ["Insuffisance rénale", "insuffisance rénale"],
];

const SYMPTOM_GROUPS = {
  general: [
    ["fever", "Fièvre"], ["high_fever", "Fièvre ≥ 39,5°"], ["chills", "Frissons"],
    ["sweats", "Sueurs"], ["fatigue", "Asthenie"], ["pallor", "Pâleur"],
    ["prostration", "Prostration"],
  ],
  neuro: [
    ["headache", "Céphalées"], ["confusion", "Confusion"], ["convulsions", "Convulsions"],
    ["coma", "Coma"], ["neck_stiffness", "Raideur nuque"], ["focal_deficit", "Déficit focal"],
    ["dizziness", "Vertiges"], ["photophobia", "Photophobie"],
  ],
  gastro: [
    ["nausea", "Nausées"], ["vomiting", "Vomissements"], ["diarrhea", "Diarrhée"],
    ["abdominal_pain", "Douleur abdom."], ["jaundice", "Ictère"], ["dark_urine", "Urines foncées"],
    ["petechiae", "Pétéchies"], ["bleeding_gums", "Saign. gencives"],
    ["abnormal_bleeding", "Saign. anormaux"], ["vaginal_bleeding", "Métrorragies"],
  ],
  resp: [
    ["cough", "Toux"], ["dyspnea", "Dyspnée"], ["chest_pain", "Douleur thoracique"],
    ["sore_throat", "Angine"], ["myalgia", "Myalgies"], ["arthralgia", "Arthralgies"],
    ["rash", "Éruption"], ["retro_orbital_pain", "Douille rétro-orbit."],
    ["edema", "Œdèmes"], ["oliguria", "Oligurie"],
  ],
  scd: [
    ["bone_pain", "Douleurs osseuses"], ["decreased_fetal_movements", "MAF ↓"],
    ["hematuria", "Hématurie"], ["splenomegaly", "Splénomégalie"],
  ],
};

const COUNTRIES = [
  ["CI", "Côte d'Ivoire"], ["BF", "Burkina Faso"], ["GH", "Ghana"],
  ["ML", "Mali"], ["SN", "Sénégal"], ["GN", "Guinée"], ["NE", "Niger"],
  ["BJ", "Bénin"], ["TG", "Togo"], ["NG", "Nigeria"], ["LR", "Libéria"],
  ["SL", "Sierra Leone"], ["CM", "Cameroun"], ["MR", "Mauritanie"],
  ["GM", "Gambie"], ["GW", "Guinée-Bissau"],
];

/* ============ État de saisie ============ */
const S = { symptoms: new Set(), countries: new Set(), photo: null };

/* ============ UI helpers ============ */
const $ = (id) => document.getElementById(id);

function toast(msg, ms = 2600) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove("show"), ms);
}

function goStep(n) {
  document.querySelectorAll(".step").forEach((s) => s.classList.remove("active"));
  const el = n === "result" ? $("step-result") : $(`step-${n}`);
  el.classList.add("active");
  window.scrollTo({ top: 0 });
}

/* ============ Chips dynamiques ============ */
function buildChips() {
  // comorbidités
  $("condChips").innerHTML = CONDITIONS.map(
    ([label, val]) => `<div class="chip" data-cond="${val}">${label}</div>`
  ).join("");
  // symptômes par groupe
  for (const [grp, items] of Object.entries(SYMPTOM_GROUPS)) {
    const host = document.querySelector(`.chips[data-group="${grp}"]`);
    host.innerHTML = items.map(
      ([code, label]) => `<div class="chip" data-sym="${code}">${label}</div>`
    ).join("");
  }
  // pays
  $("countryChips").innerHTML = COUNTRIES.map(
    ([iso, name]) => `<div class="chip" data-cty="${iso}">${name}</div>`
  ).join("");

  // interactions
  document.addEventListener("click", (e) => {
    const c = e.target.closest(".chip");
    if (!c) return;
    if (c.dataset.cond) {
      c.classList.toggle("on");
      if (c.dataset.cond.includes("G6PD")) {
        toast("Déficit G6PD : la primaquine sera interdite automatiquement.");
      }
      if (c.dataset.cond.includes("drépano")) {
        toast("Drépanocytose détectée : toute fièvre sera traitée comme urgence.");
      }
    } else if (c.dataset.sym) {
      c.classList.toggle("on");
      if (c.classList.contains("on")) S.symptoms.add(c.dataset.sym);
      else S.symptoms.delete(c.dataset.sym);
    } else if (c.dataset.cty) {
      c.classList.toggle("on");
      if (c.classList.contains("on")) S.countries.add(c.dataset.cty);
      else S.countries.delete(c.dataset.cty);
    }
  });

  $("pregnant").addEventListener("change", (e) => {
    $("pregFields").classList.toggle("hidden", !e.target.checked);
  });
}

/* ============ Grossesse : age gestationnel ============ */
function pregPayload() {
  if (!$("pregnant").checked) return {};
  const ga = $("gaWeeks").value ? parseInt($("gaWeeks").value, 10) : null;
  return { pregnant: $("pregStatus").value, gestational_age_weeks: ga };
}

/* ============ Dictée vocale (Web Speech, local) ============ */
let recognition = null;
function toggleMic() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { toast("Dictée non supportée sur ce navigateur — tapez le texte."); return; }
  if (recognition) { recognition.stop(); return; }
  recognition = new SR();
  recognition.lang = "fr-FR";
  recognition.continuous = true;
  recognition.interimResults = false;
  recognition.onresult = (ev) => {
    let t = "";
    for (let i = ev.resultIndex; i < ev.results.length; i++) t += ev.results[i][0].transcript;
    $("freeText").value += ($("freeText").value ? " " : "") + t.trim();
  };
  recognition.onend = () => { recognition = null; $("micBtn").parentElement.classList.remove("rec"); };
  recognition.onerror = () => { recognition = null; $("micBtn").parentElement.classList.remove("rec"); toast("Dictée interrompue."); };
  recognition.start();
  $("micBtn").parentElement.classList.add("rec");
  $("micState").textContent = "Micro actif — parlez en français";
}

/* ============ Normalisation du texte libre ============ */
async function normalizeText() {
  const text = $("freeText").value.trim();
  if (!text) return;
  if (isOnline() && SETTINGS.server) {
    try {
      const r = await api("POST", "/api/v1/symptoms/normalize", { text });
      renderDetected(r.symptoms.map((s) => s.code));
      return;
    } catch { /* fallback local silencieux */ }
  }
  renderDetected(localNormalize(text));
  toast("Détection locale (hors-ligne) — vérifiez les puces.");
}

/* repli local minimal : fièvre, chiffres, mots-clés fréquents */
function localNormalize(t) {
  const s = t.toLowerCase().replace(/[’']/g, " ");
  const out = new Set();
  if (/\b(fievre|fièvre|fever|corps chaud|temperature)\b/.test(s)) out.add("fever");
  const m = s.match(/(\d{2}[.,]\d)\s*(°|deg)?/);
  if (m && parseFloat(m[1].replace(",", ".")) >= 39.5) out.add("high_fever");
  if (/\b(39|40|41)\b/.test(s)) out.add("high_fever");
  if (/frisson/.test(s)) out.add("chills");
  if (/cephal|mal de tete|tete/.test(s)) out.add("headache");
  if (/vomi/.test(s)) out.add("vomiting");
  if (/diarrh/.test(s)) out.add("diarrhea");
  if (/toux/.test(s)) out.add("cough");
  if (/paleur|pale/.test(s)) out.add("pallor");
  if (/os|crise/.test(s) && /douleur/.test(s)) out.add("bone_pain");
  if (/bebe|foetus|fetal/.test(s) && /bouge/.test(s)) out.add("decreased_fetal_movements");
  return [...out];
}

function renderDetected(codes) {
  if (!codes.length) { $("textDetected").innerHTML = '<div class="empty-note">Aucun symptôme reconnu</div>'; return; }
  codes.forEach((c) => S.symptoms.add(c));
  $("textDetected").innerHTML = codes.map((c) => {
    const label = labelOf(c);
    return `<div class="chip on" data-sym="${c}" onclick="this.classList.remove('on');S.symptoms.delete('${c}')">${label} ✕</div>`;
  }).join("");
  // synchroniser les puces principales
  document.querySelectorAll("[data-sym]").forEach((el) => {
    if (el.closest("#textDetected")) return;
    el.classList.toggle("on", S.symptoms.has(el.dataset.sym));
  });
}

function labelOf(code) {
  for (const items of Object.values(SYMPTOM_GROUPS))
    for (const [c, l] of items) if (c === code) return l;
  return code;
}

/* ============ Photo ============ */
document.addEventListener("DOMContentLoaded", () => {
  $("photoInput").addEventListener("change", (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const rd = new FileReader();
    rd.onload = () => {
      S.photo = rd.result; // dataURL base64
      $("photoThumb").src = S.photo;
    };
    rd.readAsDataURL(f);
  });
});

/* ============ Construction du cas ============ */
function buildCase() {
  const patient = {
    age_years: $("age").value ? parseInt($("age").value, 10) : null,
    age_months: $("ageMonths").value ? parseInt($("ageMonths").value, 10) : null,
    sex: $("sex").value,
    weight_kg: $("weight").value ? parseFloat($("weight").value) : null,
    ...pregPayload(),
    chronic_conditions: [...document.querySelectorAll("[data-cond].on")].map((c) => c.dataset.cond),
  };

  const vitals = {};
  if ($("temp").value) vitals.temperature_c = parseFloat($("temp").value);
  if ($("hr").value) vitals.heart_rate = parseInt($("hr").value, 10);
  if ($("rr").value) vitals.respiratory_rate = parseInt($("rr").value, 10);
  if ($("spo2").value) vitals.spo2 = parseInt($("spo2").value, 10);
  if ($("sbp").value && $("dbp").value) {
    vitals.systolic_bp = parseInt($("sbp").value, 10);
    vitals.diastolic_bp = parseInt($("dbp").value, 10);
  }

  const today = new Date();
  const stay = $("stayDays").value ? parseInt($("stayDays").value, 10) : 14;
  const dep = $("returnDate").value ? new Date($("returnDate").value) : new Date(today.getTime() - stay * 864e5);
  const depStr = dep.toISOString().slice(0, 10);

  const travel = { segments: [...S.countries].map((iso) => ({
    country: iso, departure: depStr,
    region: iso === "CI" ? ($("ciRegion").value.trim() || undefined) : undefined,
    rural_stay: $("rural").checked || undefined,
    prophylaxis_taken: $("prophylaxis").checked || undefined,
    burial_attended: $("burial").checked || undefined,
    sick_contact: $("sickContact").checked || undefined,
  })) };

  const lab_results = [];
  if ($("rdt").value) lab_results.push({ test: "rdt_malaria", value: $("rdt").value });
  if ($("hb").value) lab_results.push({ test: "cbc", component: "hb", numeric: parseFloat($("hb").value), unit: "g/dL" });
  if ($("plt").value) lab_results.push({ test: "cbc", component: "plt", numeric: parseInt($("plt").value, 10), unit: "/µL" });
  if ($("glucose").value) lab_results.push({ test: "glucose", numeric: parseFloat($("glucose").value), unit: "mmol/L" });
  if ($("crea").value) lab_results.push({ test: "creatinine", numeric: parseInt($("crea").value, 10), unit: "µmol/L" });

  return {
    patient,
    free_text: $("freeText").value || null,
    symptom_codes: [...S.symptoms],
    vitals: Object.keys(vitals).length ? vitals : null,
    lab_results,
    travel,
    use_ai: true,
    language: "fr",
    _photo: S.photo, // conservé pour le mesh IA (si branché)
    _captured_at: new Date().toISOString(),
  };
}

/* ============ Soumission (avec file offline) ============ */
async function submitCase() {
  const c = buildCase();
  save(LS.lastCase, c);
  $("analyzeBtn").disabled = true;
  $("analyzeBtn").textContent = "Analyse…";
  try {
    if (isOnline() && SETTINGS.server) {
      const r = await api("POST", "/api/v1/cases", stripLocal(c));
      renderResult(r);
      goStep("result");
    } else {
      enqueue(c);
      toast("Hors-ligne : cas mis en file d'attente (" + queueLength() + ")");
      goStep("result");
      renderOfflineAdvice(c);
    }
  } catch (e) {
    if (e.message.includes("Failed to fetch")) {
      enqueue(c);
      toast("Serveur injoignable : cas mis en file (" + queueLength() + ")");
      goStep("result");
      renderOfflineAdvice(c);
    } else {
      toast("Erreur : " + e.message, 4200);
    }
  } finally {
    $("analyzeBtn").disabled = false;
    $("analyzeBtn").textContent = "⚡ Analyser le cas";
  }
}

function stripLocal(c) { const { _photo, _captured_at, ...rest } = c; return rest; }
function enqueue(c) { const q = load(LS.queue, []); q.push(c); save(LS.queue, q); paintQueue(); }
function queueLength() { return load(LS.queue, []).length; }

function renderOfflineAdvice(c) {
  $("verdict").className = "v-priority";
  $("verdict").textContent = "MODE HORS-LIGNE — case en file d'attente";
  $("resCard").innerHTML = `<div class="rf-item"><b>Case enregistré localement.</b>
    Il sera analysé dès que la connexion au serveur TropiRAG sera rétablie.
    ${c.symptom_codes.length} symptôme(s) saisi(s), ${c.travel.segments.length} destination(s).</div>
    <div class="empty-note">Si urgence visible (coma, convulsions, saignements, enfant pâle et mou) :
    transférer immédiatement, sans attendre l'analyse.</div>`;
}

/* ============ Rendu du résultat ============ */
const SEV_FR = { immediate: "IMMÉDIAT", emergency: "URGENCE", priority: "PRIORITAIRE", routine: "ROUTINE" };

function renderResult(r) {
  const v = $("verdict");
  if (r.urgency === "immediate" || r.urgency === "emergency") {
    v.className = "v-emergency";
  } else if (r.urgency === "priority") {
    v.className = "v-priority";
  } else {
    v.className = "v-routine";
  }
  v.textContent = (SEV_FR[r.urgency] || r.urgency?.toUpperCase()) + " — " +
    (r.severity === "critical" ? "cas critique" : r.severity === "severe" ? "cas sévère" : "cas non sévère");

  $("resRedFlags").innerHTML = (r.red_flags || []).length
    ? r.red_flags.map((f) => `<div class="rf-item"><b>${esc(f.code)}</b> — ${esc(f.message)}</div>`).join("")
    : '<div class="empty-note">Aucun signe d\'alerte détecté</div>';

  $("resDiff").innerHTML = (r.differentials || []).slice(0, 8).map((d, i) =>
    `<div class="diff-item"><span class="diff-rank">${i + 1}</span>
     <span class="diff-name">${esc(d.disease_label || d.disease)}</span>
     <span class="diff-score">${Math.round((d.score || 0) * 100)}%</span></div>`).join("")
    || '<div class="empty-note">—</div>';

  $("resTests").innerHTML = (r.required_tests || []).length
    ? r.required_tests.map((t) => `<div class="test-item">🧪 <b>${esc(t.test_label || t.test)}</b> — ${esc(t.reason || "")}</div>`).join("")
    : '<div class="empty-note">—</div>';

  $("resDrugs").innerHTML = (r.drug_constraints || []).length
    ? r.drug_constraints.map((d) => d.forbidden
        ? `<div class="drug-item forbidden">⛔ <b>${esc(d.drug)}</b> — ${esc(d.reason)}</div>`
        : `<div class="drug-item">✅ <b>${esc(d.drug)}</b> — ${esc(d.reason)}</div>`).join("")
    : '<div class="empty-note">Aucune contrainte particulière</div>';

  const escs = [];
  if (r.escalations) escs.push(...r.escalations.map((e) => e.message));
  if (r.notifications) escs.push(...r.notifications.map((n) => "⚠ " + n.reason));
  $("resEsc").innerHTML = escs.length
    ? escs.map((m) => `<div class="rf-item">${esc(m)}</div>`).join("")
    : '<div class="empty-note">—</div>';

  $("resCits").innerHTML = (r.citations || []).length
    ? r.citations.slice(0, 8).map((c) =>
        `<div class="cit"><b>${esc(c.unit_id || c.source_id)}</b> — ${esc((c.text || c.excerpt || "").slice(0, 150))}…</div>`).join("")
    : '<div class="empty-note">—</div>';

  $("resDisclaimer").textContent = r.disclaimer ||
    "TropiRAG est un compagnon d'aide à la décision — il ne remplace jamais le jugement clinique. " +
    "Toute posologie relève du protocole national et du clinicien responsable.";
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (m) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}

/* ============ File d'attente + synchronisation ============ */
async function syncQueue() {
  const q = load(LS.queue, []);
  if (!q.length) { paintQueue(); return; }
  if (!isOnline() || !SETTINGS.server) { toast("Pas de connexion au serveur."); return; }
  let ok = 0, last = null;
  for (const c of q) {
    try { last = await api("POST", "/api/v1/cases", stripLocal(c)); ok++; }
    catch { break; }
  }
  save(LS.queue, q.slice(ok));
  paintQueue();
  if (last) { renderResult(last); goStep("result"); }
  toast(`${ok} cas synchronisé(s)`);
}

function paintQueue() {
  const n = queueLength();
  const b = $("queueBadge");
  b.style.display = n ? "block" : "none";
  b.textContent = `OFFLINE — ${n} cas en attente · toucher pour synchroniser`;
}

/* ============ Réseau & API ============ */
function isOnline() { return navigator.onLine; }

async function api(method, path, body) {
  const headers = { "Content-Type": "application/json" };
  if (SETTINGS.key) headers["X-API-Key"] = SETTINGS.key;
  const r = await fetch(SETTINGS.server.replace(/\/$/, "") + path, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) {
    const t = await r.text().catch(() => "");
    throw new Error(`HTTP ${r.status} ${t.slice(0, 140)}`);
  }
  return r.json();
}

/* ============ Paramètres ============ */
function openSettings() {
  $("setServer").value = SETTINGS.server;
  $("setKey").value = SETTINGS.key;
  $("settingsMode").textContent = isOnline() && SETTINGS.server
    ? "Connecté : analyses complètes (déterministe + mesh IA)"
    : "Hors-ligne : saisie locale + file d'attente";
  $("settingsSheet").classList.add("open");
}
function closeSettings() { $("settingsSheet").classList.remove("open"); }
function saveSettings() {
  SETTINGS.server = $("setServer").value.trim().replace(/\/$/, "");
  SETTINGS.key = $("setKey").value.trim();
  save(LS.settings, SETTINGS);
  closeSettings();
  toast("Paramètres enregistrés");
}

/* ============ Cycle de vie ============ */
window.addEventListener("online", () => { $("netDot").classList.add("on"); paintQueue(); syncQueue(); });
window.addEventListener("offline", () => { $("netDot").classList.remove("on"); paintQueue(); });

function newCase() {
  S.symptoms.clear(); S.countries.clear(); S.photo = null;
  document.querySelectorAll(".chip.on").forEach((c) => c.classList.remove("on"));
  document.querySelectorAll("input, textarea, select").forEach((el) => {
    if (el.type === "checkbox") el.checked = false; else el.value = "";
  });
  $("pregFields").classList.add("hidden");
  goStep(1);
}

document.addEventListener("DOMContentLoaded", () => {
  buildChips();
  paintQueue();
  if (isOnline() && SETTINGS.server) $("netDot").classList.add("on");
  if (!SETTINGS.server) setTimeout(openSettings, 400);
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
});
