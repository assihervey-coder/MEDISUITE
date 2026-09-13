/**
 * patient-portal — portail patient : résultats, RDV et CONSENTEMENTS RGPD.
 * (Shell minimal — les écrans complets sont dans web-portal/features.)
 *
 * Écrans clés :
 *  - /consents  : consent_ia, consent_recherche (révocables à tout moment, art. 7 RGPD)
 *  - /results   : LabResults, ImagingReports, Trends
 *  - /appointments / messages / education (cancer-awareness, diabète, santé oculaire…)
 */
export const SCREENS = [
  "consents", "results/LabResults", "results/ImagingReports", "results/Trends",
  "appointments", "messages",
  "education/cancer-awareness", "education/diabetes-management",
  "education/eye-health", "education/lifestyle", "education/cardiac-health",
  "education/mental-health",
] as const;

export async function setConsent(patientId: string, consent: { consent_ia?: boolean; consent_recherche?: boolean }) {
  const res = await fetch(`http://localhost:8002/api/v1/patients/${patientId}/consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(consent),
  });
  if (!res.ok) throw new Error(`consentement refusé : ${res.status}`);
  return res.json();
}
