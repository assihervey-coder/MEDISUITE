/** Palette de commandes ⌘K / Ctrl-K (nice-to-have) — recherche globale :
 *  navigation (écrans + modules), patients (requête live backend), actions. */
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../store/authStore";
import { MODULE_NAV } from "../features/modules-nav";
import type { MsgKey } from "../i18n/resolve";
import { useI18n } from "../i18n/i18n";

interface PatientHit {
  id: string;
  numero_dossier: string;
  nom: string;
  prenoms: string;
  age: number;
}

interface Item {
  key: string;
  icon: string;
  label: string;
  hint: string;
  go: () => void;
}

export default function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [q, setQ] = useState("");
  const [patients, setPatients] = useState<PatientHit[]>([]);
  const [sel, setSel] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { t } = useI18n();
  const role = useAuth((s) => s.role);

  // focus + reset à l'ouverture ; Escape ferme
  useEffect(() => {
    if (open) {
      setQ("");
      setSel(0);
      window.setTimeout(() => inputRef.current?.focus(), 10);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  // patients : requête live dès 2 caractères (debounce 180 ms)
  useEffect(() => {
    if (!open || q.trim().length < 2) {
      setPatients([]);
      return;
    }
    const timer = window.setTimeout(() => {
      api
        .get<PatientHit[]>(`/api/patients/api/v1/patients?q=${encodeURIComponent(q.trim())}&limit=6`)
        .then(setPatients)
        .catch(() => setPatients([]));
    }, 180);
    return () => window.clearTimeout(timer);
  }, [q, open]);

  const items = useMemo<Item[]>(() => {
    const nav: Item[] = [
      { key: "dash", icon: "🏠", label: t("dashboard"), hint: "/", go: () => navigate("/") },
      { key: "pat", icon: "🧑‍⚕️", label: t("patients"), hint: "/patients", go: () => navigate("/patients") },
      { key: "img", icon: "🩻", label: t("imaging"), hint: "/imaging", go: () => navigate("/imaging") },
      { key: "lab", icon: "🧪", label: t("laboratory"), hint: "/laboratory", go: () => navigate("/laboratory") },
      { key: "urg", icon: "🚨", label: t("emergency"), hint: "/emergency", go: () => navigate("/emergency") },
      { key: "avc", icon: "🧠", label: t("nav.code_avc"), hint: "/code-avc", go: () => navigate("/code-avc") },
      { key: "fus", icon: "🧠", label: t("nav.multimodal"), hint: "/multimodal", go: () => navigate("/multimodal") },
      { key: "ecrf", icon: "📋", label: t("nav.ecrf"), hint: "/ecrf", go: () => navigate("/ecrf") },
      { key: "study", icon: "📈", label: t("nav.study"), hint: "/study", go: () => navigate("/study") },
      { key: "audit", icon: "🔐", label: t("nav.audit"), hint: "/audit", go: () => navigate("/audit") },
      { key: "epi", icon: "🌍", label: t("nav.epidemiologie"), hint: "/epidemiologie", go: () => navigate("/epidemiologie") },
    ];
    if (role === "administrateur")
      nav.push({ key: "admin", icon: "🛡️", label: t("nav.administration"), hint: "/admin", go: () => navigate("/admin") });
    const modules: Item[] = MODULE_NAV.map((m) => ({
      key: `mod-${m.slug}`,
      icon: m.icon,
      label: t(`mod.${m.slug}` as MsgKey),
      hint: `/${m.slug}`,
      go: () => navigate(`/${m.slug}`),
    }));
    const all = [...nav, ...modules];
    const needle = q.trim().toLowerCase();
    return needle ? all.filter((i) => i.label.toLowerCase().includes(needle)) : all.slice(0, 8);
  }, [q, navigate, role, t]);

  const patientHits = patients.map((p): Item => ({
    key: `pat-${p.id}`,
    icon: "📄",
    label: `${p.nom} ${p.prenoms}`,
    hint: `${p.numero_dossier} · ${p.age} ans`,
    go: () => navigate(`/patients/${p.id}`),
  }));

  const flat = [...patientHits, ...items];
  const active = Math.min(sel, flat.length - 1);

  if (!open) return null;

  return (
    <div className="palette-backdrop" onClick={onClose}>
      <div className="palette" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Recherche globale">
        <input
          ref={inputRef}
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setSel(0);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") { e.preventDefault(); setSel((s) => Math.min(s + 1, flat.length - 1)); }
            if (e.key === "ArrowUp") { e.preventDefault(); setSel((s) => Math.max(s - 1, 0)); }
            if (e.key === "Enter" && flat[active]) { flat[active].go(); onClose(); }
          }}
          placeholder="Rechercher un écran, un patient… (↑↓ naviguer, ↵ ouvrir, Échap fermer)"
          aria-label="Recherche globale"
        />
        <ul className="palette-list">
          {patientHits.length > 0 && (
            <li className="palette-group">Patients</li>
          )}
          {patientHits.map((it, i) => (
            <li
              key={it.key}
              className={i === active ? "on" : ""}
              onMouseEnter={() => setSel(i)}
              onClick={() => { it.go(); onClose(); }}
            >
              <span aria-hidden>{it.icon}</span> {it.label}
              <span className="hint">{it.hint}</span>
            </li>
          ))}
          {items.length > 0 && (
            <li className="palette-group">Écrans &amp; modules</li>
          )}
          {items.map((it, i) => {
            const idx = patientHits.length + i;
            return (
              <li
                key={it.key}
                className={idx === active ? "on" : ""}
                onMouseEnter={() => setSel(idx)}
                onClick={() => { it.go(); onClose(); }}
              >
                <span aria-hidden>{it.icon}</span> {it.label}
                <span className="hint">{it.hint}</span>
              </li>
            );
          })}
          {flat.length === 0 && <li className="palette-empty">Aucun résultat</li>}
        </ul>
      </div>
    </div>
  );
}
