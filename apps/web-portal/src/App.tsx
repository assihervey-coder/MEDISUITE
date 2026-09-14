import { useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import Login from "./features/auth/Login";
import Dashboard from "./features/dashboard/MainDashboard";
import Patients from "./features/patients/PatientList";
import PatientDetail from "./features/patients/PatientDetail";
import Laboratory from "./features/laboratory/Results";
import Imaging from "./features/imaging/StudyList";
import BiRadsViewer from "./features/imaging/BiRadsViewer";
import TriageBoard from "./features/emergency/TriageBoard";
import StrokeCode from "./features/neurology/StrokeCode";
import FusionViewer from "./features/multimodal/FusionViewer";
import TropiRagConsult from "./features/decision/TropiRagConsult";
import AuditLog from "./features/admin/AuditLog";
import Admin from "./features/admin/Admin";
import About from "./features/about/About";
import Ecrf from "./features/ecrf/Ecrf";
import StudyStatus from "./features/study/StudyStatus";
import Epidemiology from "./features/epidemiology/Epidemiology";
import OfflineBanner from "./components/OfflineBanner";
import Toasts from "./components/Toasts";
import ThemeToggle from "./components/ThemeToggle";
import CommandPalette from "./components/CommandPalette";
import { useAuth } from "./store/authStore";
import { MODULE_NAV } from "./features/modules-nav";
import { LanguageProvider, useI18n } from "./i18n/i18n";
import type { Lang, MsgKey } from "./i18n/resolve";
import { LANGS } from "./i18n/resolve";
import { SCREEN_ROUTES } from "./screens/routes.generated";

/** Libellés de langue pour le sélecteur (chaque langue s'affiche dans sa
 * propre écriture — volontairement hors i18n). */
const LANG_LABELS: Record<Lang, string> = {
  fr: "Français",
  en: "English",
  ar: "العربية",
  es: "Español",
};

/** Navigation principale : `key` = clé de traduction (i18n v0.11). */
const NAV_MAIN: Array<{ to: string; icon: string; key: MsgKey }> = [
  { to: "/", icon: "🏠", key: "dashboard" },
  { to: "/patients", icon: "🧑‍⚕️", key: "patients" },
  { to: "/imaging", icon: "🩻", key: "imaging" },
  { to: "/birads", icon: "🎗️", key: "nav.birads" },
  { to: "/laboratory", icon: "🧪", key: "laboratory" },
  { to: "/emergency", icon: "🚨", key: "emergency" },
  { to: "/code-avc", icon: "🧠", key: "nav.code_avc" },
  { to: "/decision", icon: "🧭", key: "nav.tropirag" },
  { to: "/multimodal", icon: "🧠", key: "nav.multimodal" },
  { to: "/epidemiologie", icon: "🌍", key: "nav.epidemiologie" },
  { to: "/audit", icon: "🔐", key: "nav.audit" },
  { to: "/ecrf", icon: "📋", key: "nav.ecrf" },
  { to: "/study", icon: "📈", key: "nav.study" },
  { to: "/admin", icon: "🛡️", key: "nav.administration" },
  { to: "/about", icon: "ℹ️", key: "about" },
];

export default function App() {
  return (
    <LanguageProvider>
      <AppShell />
    </LanguageProvider>
  );
}

function AppShell() {
  const { token, role, nom, logout } = useAuth();
  const { t, lang, setLang } = useI18n();
  const [paletteOpen, setPaletteOpen] = useState(false);

  // Recherche globale ⌘K / Ctrl-K (nice-to-have).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  if (!token) return <Login />;

  return (
    <div className="layout">
      <OfflineBanner />
      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
      <aside className="sidebar">
        <h2>🏥 MEDISUITE</h2>
        <button
          type="button"
          className="palette-trigger"
          onClick={() => setPaletteOpen(true)}
          title="Recherche globale (Ctrl+K)"
        >
          🔎 {t("nav.search")} <kbd>Ctrl K</kbd>
        </button>
        {NAV_MAIN.map((n) => (
          <NavLink key={n.to} to={n.to} className={({ isActive }) => (isActive ? "active" : "")}>
            {n.icon} {t(n.key)}
          </NavLink>
        ))}
        <p style={{ borderTop: "1px solid rgba(255,255,255,.25)", margin: "14px 0 6px" }} />
        {MODULE_NAV.map((n) => (
          <NavLink key={n.to} to={n.to} className={({ isActive }) => (isActive ? "active" : "")}>
            {n.icon} {t(`mod.${n.slug}` as MsgKey)}
          </NavLink>
        ))}
        <p style={{ borderTop: "1px solid rgba(255,255,255,.25)", margin: "14px 0 6px" }} />
        <span style={{ fontSize: 13, color: "#a8c4dc" }}>
          {t("connected")} : {nom} ({role})
        </span>
        <label style={{ display: "block", marginTop: 10, fontSize: 13 }}>
          <span style={{ color: "#a8c4dc" }}>{t("language")}</span>
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as Lang)}
            aria-label={t("language")}
            style={{ width: "100%", marginTop: 4, color: "#0d1b2a" }}
          >
            {LANGS.map((l) => (
              <option key={l} value={l}>
                {LANG_LABELS[l]}
              </option>
            ))}
          </select>
        </label>
        <button onClick={logout} style={{ marginTop: 10, background: "rgba(255,255,255,.15)" }}>
          {t("logout")}
        </button>
        <ThemeToggle />
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route path="/imaging" element={<Imaging />} />
          <Route path="/birads" element={<BiRadsViewer />} />
          <Route path="/laboratory" element={<Laboratory />} />
          <Route path="/emergency" element={<TriageBoard />} />
          <Route path="/code-avc" element={<StrokeCode />} />
          <Route path="/decision" element={<TropiRagConsult />} />
          <Route path="/multimodal" element={<FusionViewer />} />
          <Route path="/epidemiologie" element={<Epidemiology />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/ecrf" element={<Ecrf />} />
          <Route path="/study" element={<StudyStatus />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/about" element={<About />} />
          {/* 96 écrans fins générés (24 modules × 4 types — v0.14) : vue
              d'ensemble, liste des cas, fiche détail, assistance IA. */}
          {SCREEN_ROUTES.map((r) => (
            <Route key={r.path} path={r.path} element={r.element} />
          ))}
        </Routes>
      </main>
      <Toasts />
    </div>
  );
}
