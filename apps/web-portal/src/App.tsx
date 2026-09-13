import { NavLink, Route, Routes } from "react-router-dom";
import Login from "./features/auth/Login";
import Dashboard from "./features/dashboard/MainDashboard";
import Patients from "./features/patients/PatientList";
import Laboratory from "./features/laboratory/Results";
import Imaging from "./features/imaging/StudyList";
import BiRadsViewer from "./features/imaging/BiRadsViewer";
import TriageBoard from "./features/emergency/TriageBoard";
import StrokeCode from "./features/neurology/StrokeCode";
import FusionViewer from "./features/multimodal/FusionViewer";
import AuditLog from "./features/admin/AuditLog";
import About from "./features/about/About";
import Ecrf from "./features/ecrf/Ecrf";
import OfflineBanner from "./components/OfflineBanner";
import { useAuth } from "./store/authStore";
import ClinicalPanel from "./components/ClinicalPanel";
import { MODULE_NAV } from "./features/modules-nav";

const NAV_MAIN = [
  { to: "/", label: "🏠 Tableau de bord" },
  { to: "/patients", label: "🧑‍⚕️ Dossiers patients" },
  { to: "/imaging", label: "🩻 Imagerie (DICOMweb)" },
  { to: "/birads", label: "🎗️ Lecteur BI-RADS" },
  { to: "/laboratory", label: "🧪 Laboratoire" },
  { to: "/emergency", label: "🚨 Urgences — Triage" },
  { to: "/code-avc", label: "🧠 Code AVC (stroke)" },
  { to: "/multimodal", label: "🧠 Fusion multimodale" },
  { to: "/audit", label: "🔐 Audit (chaîné)" },
  { to: "/ecrf", label: "📋 eCRF (CI-01)" },
  { to: "/about", label: "ℹ️ À propos (UDI)" },
];

export default function App() {
  const { token, role, nom, logout } = useAuth();
  if (!token) return <Login />;

  return (
    <div className="layout">
      <OfflineBanner />
      <aside className="sidebar">
        <h2>🏥 MEDISUITE</h2>
        {NAV_MAIN.map((n) => (
          <NavLink key={n.to} to={n.to} className={({ isActive }) => (isActive ? "active" : "")}>
            {n.label}
          </NavLink>
        ))}
        <p style={{ borderTop: "1px solid rgba(255,255,255,.25)", margin: "14px 0 6px" }} />
        {MODULE_NAV.map((n) => (
          <NavLink key={n.to} to={n.to} className={({ isActive }) => (isActive ? "active" : "")}>
            {n.label}
          </NavLink>
        ))}
        <p style={{ borderTop: "1px solid rgba(255,255,255,.25)", margin: "14px 0 6px" }} />
        <span style={{ fontSize: 13, color: "#a8c4dc" }}>
          Connecté : {nom} ({role})
        </span>
        <button onClick={logout} style={{ marginTop: 10, background: "rgba(255,255,255,.15)" }}>
          Déconnexion
        </button>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/imaging" element={<Imaging />} />
          <Route path="/birads" element={<BiRadsViewer />} />
          <Route path="/laboratory" element={<Laboratory />} />
          <Route path="/emergency" element={<TriageBoard />} />
          <Route path="/code-avc" element={<StrokeCode />} />
          <Route path="/multimodal" element={<FusionViewer />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/ecrf" element={<Ecrf />} />
          <Route path="/about" element={<About />} />
          {MODULE_NAV.map((n) => (
            <Route
              key={n.to}
              path={n.to}
              element={<ClinicalPanel title={n.label} servicePath={n.to.slice(1)} />}
            />
          ))}
        </Routes>
      </main>
    </div>
  );
}
