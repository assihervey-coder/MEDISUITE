/** Administration (BEST TO HAVE) — deux volets :
 *  1. Mon compte : enrôlement MFA TOTP (secret + URI otpauth copiables).
 *  2. Administrateurs : gestion des comptes + matrice de permissions RBAC. */
import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { useAuth } from "../../store/authStore";
import { toast } from "../../store/toastStore";

interface User {
  id: string; email: string; nom: string; prenoms: string;
  role: string; mfa_enabled: boolean; active: boolean;
}

interface Permissions {
  permissions: string[];
  roles: Record<string, string[]>;
}

interface MfaEnroll {
  secret_base32: string;
  otpauth: string;
  note: string;
}

/** Décode le payload JWT (claims : email, role, nom) — sans dépendance. */
function jwtEmail(token: string): string {
  try {
    const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    return typeof payload.email === "string" ? payload.email : "";
  } catch {
    return "";
  }
}

const ROLE_BADGE: Record<string, string> = {
  administrateur: "critical",
  medecin: "ok",
  biologiste: "ok",
  radiologue: "ok",
  infirmier: "warn",
  data_manager: "",
};

export default function Admin() {
  const { nom, role, token } = useAuth();
  const email = token ? jwtEmail(token) : "";
  const [users, setUsers] = useState<User[] | null>(null);
  const [usersErr, setUsersErr] = useState("");
  const [perms, setPerms] = useState<Permissions | null>(null);
  const [mfa, setMfa] = useState<MfaEnroll | null>(null);
  const [showSecret, setShowSecret] = useState(false);
  const isAdmin = role === "administrateur";

  useEffect(() => {
    if (!isAdmin) return;
    api
      .get<User[]>("/api/auth/api/v1/users")
      .then(setUsers)
      .catch((e) => setUsersErr(e.message));
    api
      .get<Permissions>("/api/auth/api/v1/permissions")
      .then(setPerms)
      .catch(() => {});
  }, [isAdmin]);

  async function enrollMfa() {
    try {
      const res = await api.post<MfaEnroll>("/api/auth/api/v1/auth/mfa/enroll");
      setMfa(res);
      setShowSecret(false);
      toast.ok("Enrôlement MFA initié — enregistrez le secret dans votre app TOTP");
    } catch (e) {
      toast.error(`MFA : ${(e as Error).message}`);
    }
  }

  async function copy(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text);
      toast.ok(`${label} copié dans le presse-papiers`);
    } catch {
      toast.warn("Copie impossible — sélectionnez le texte manuellement");
    }
  }

  const roleList = perms ? Object.keys(perms.roles).sort() : [];

  return (
    <div>
      <h2>Administration &amp; sécurité</h2>

      <div className="detail-grid">
        <div className="card">
          <h3>🔐 Mon compte — authentification à deux facteurs</h3>
          <p style={{ fontSize: 13.5 }}>
            Connecté : <strong>{nom}</strong> ({role}) — <code>{email}</code>
          </p>
          <p style={{ fontSize: 13 }}>
            Le MFA TOTP (Google Authenticator, FreeOTP…) protège l'accès aux
            données cliniques — requis en production (ISO 27001 A.9.4.3).
            Générez votre secret, puis enregistrez-le dans votre app TOTP :
            le code à 6 chiffres sera demandé à la prochaine connexion.
          </p>
          {!mfa ? (
            <button type="button" onClick={enrollMfa}>Activer le MFA (TOTP)</button>
          ) : (
            <div>
              <p style={{ marginBottom: 6 }}>
                <strong>Secret base32 :</strong>{" "}
                <code className="mfa-secret">{showSecret ? mfa.secret_base32 : "•".repeat(mfa.secret_base32.length)}</code>{" "}
                <button type="button" style={{ fontSize: 12, padding: "3px 8px" }} onClick={() => setShowSecret(!showSecret)}>
                  {showSecret ? "masquer" : "afficher"}
                </button>{" "}
                <button type="button" style={{ fontSize: 12, padding: "3px 8px" }} onClick={() => copy(mfa.secret_base32, "Secret")}>
                  copier
                </button>
              </p>
              <p style={{ fontSize: 12.5 }}>
                URI otpauth (configuration manuelle) :{" "}
                <code style={{ fontSize: 11 }}>{mfa.otpauth}</code>{" "}
                <button type="button" style={{ fontSize: 12, padding: "3px 8px" }} onClick={() => copy(mfa.otpauth, "URI otpauth")}>
                  copier
                </button>
              </p>
              <p className="note">{mfa.note}</p>
            </div>
          )}
        </div>

        {isAdmin && (
          <div className="card">
            <h3>🛡️ Matrice RBAC — permissions par rôle</h3>
            {!perms && <p className="note">Chargement…</p>}
            {perms && (
              <div className="role-grid">
                {roleList.map((r) => (
                  <details key={r} className="role-block">
                    <summary>
                      <span className={`badge ${ROLE_BADGE[r] ?? ""}`}>{r}</span>{" "}
                      {perms.roles[r].length} permission(s)
                    </summary>
                    <ul className="perm-list">
                      {perms.roles[r].sort().map((p) => (
                        <li key={p}><code>{p}</code></li>
                      ))}
                    </ul>
                  </details>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isAdmin && (
        <>
          <h3 style={{ marginTop: 24 }}>Comptes utilisateurs ({users?.length ?? "…"})</h3>
          {usersErr && <p className="error">{usersErr}</p>}
          {users && (
            <table>
              <thead>
                <tr><th>Email</th><th>Nom & prénoms</th><th>Rôle</th><th>MFA</th><th>Actif</th></tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td><code>{u.email}</code></td>
                    <td>{u.nom} {u.prenoms}</td>
                    <td><span className={`badge ${ROLE_BADGE[u.role] ?? ""}`}>{u.role}</span></td>
                    <td>
                      <span className={`badge ${u.mfa_enabled ? "ok" : "warn"}`}>
                        {u.mfa_enabled ? "activé" : "non activé"}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.active ? "ok" : "critical"}`}>
                        {u.active ? "oui" : "non"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p className="note" style={{ marginTop: 8 }}>
            RBAC centralisé (auth-service) — 29 permissions affinées, 7 rôles.
            La création de comptes passe par le provisioning hospitalier (annuaire CHU).
          </p>
        </>
      )}
    </div>
  );
}
