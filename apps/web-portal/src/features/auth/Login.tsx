import { useState } from "react";
import { useAuth } from "../../store/authStore";

/** Connexion JWT + champ MFA TOTP optionnel (428 → demande le code). */
export default function Login() {
  const login = useAuth((s) => s.login);
  const [email, setEmail] = useState("medecin@chu-cocody.ci");
  const [password, setPassword] = useState("MediSuite2026!");
  const [totp, setTotp] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const res = await fetch("/api/auth/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, totp_code: totp || undefined }),
    });
    if (!res.ok) {
      const b = await res.json().catch(() => ({}));
      setError(b.detail ?? `erreur ${res.status}`);
      return;
    }
    const b = await res.json();
    login(b.access_token, b.role, email.split("@")[0]);
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h1>🏥 MEDISUITE</h1>
        <p>Plateforme clinique multimodale — Côte d'Ivoire</p>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email professionnel" />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Mot de passe" />
        <input value={totp} onChange={(e) => setTotp(e.target.value)} placeholder="Code MFA (si activé)" />
        {error && <p className="error">{error}</p>}
        <button type="submit" style={{ width: "100%" }}>Se connecter</button>
        <p className="note" style={{ marginTop: 12 }}>
          Démo : medecin@chu-cocody.ci · biologiste@… · radiologue@… ·
          admin@medisuite.ci · datamanager@medisuite.ci (écran Promoteur) —
          mot de passe MediSuite2026!
        </p>
      </form>
    </div>
  );
}
