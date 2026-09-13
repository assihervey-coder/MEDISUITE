/** Navigation des 24 modules de spécialités (modules 03-26, ports 8100-8123).
 * v0.11 : le libellé est traduit à l'affichage via la clé `mod.<slug>`
 * (i18n, App.tsx) — le slug est la source de vérité, alignée sur
 * datasets/registry.py et services/registry.py (nuclear-medicine en URL,
 * nuclear_medicine en clé i18n). */
export const MODULE_NAV: Array<{ to: string; slug: string; icon: string }> = [
  { to: "/module/oncology", slug: "oncology", icon: "🎗️" },
  { to: "/module/tumor", slug: "tumor", icon: "🧠" },
  { to: "/module/ophthalmology", slug: "ophthalmology", icon: "👁️" },
  { to: "/module/diabetes", slug: "diabetes", icon: "🩸" },
  { to: "/module/traumatology", slug: "traumatology", icon: "🦴" },
  { to: "/module/cardiology", slug: "cardiology", icon: "❤️" },
  { to: "/module/pneumology", slug: "pneumology", icon: "🫁" },
  { to: "/module/obstetrics", slug: "obstetrics", icon: "🤰" },
  { to: "/module/gynecology", slug: "gynecology", icon: "🌸" },
  { to: "/module/fertility", slug: "fertility", icon: "🧬" },
  { to: "/module/neurology", slug: "neurology", icon: "🧠" },
  { to: "/module/psychiatry", slug: "psychiatry", icon: "🧬" },
  { to: "/module/pediatrics", slug: "pediatrics", icon: "👶" },
  { to: "/module/nephrology", slug: "nephrology", icon: "🫘" },
  { to: "/module/gastroenterology", slug: "gastroenterology", icon: "🫄" },
  { to: "/module/dermatology", slug: "dermatology", icon: "🩹" },
  { to: "/module/ent", slug: "ent", icon: "👂" },
  { to: "/module/rheumatology", slug: "rheumatology", icon: "🦴" },
  { to: "/module/urology", slug: "urology", icon: "🚹" },
  { to: "/module/nuclear-medicine", slug: "nuclear_medicine", icon: "☢️" },
  { to: "/module/radiotherapy", slug: "radiotherapy", icon: "🎯" },
  { to: "/module/anesthesia", slug: "anesthesia", icon: "💉" },
  { to: "/module/geriatrics", slug: "geriatrics", icon: "👴" },
  { to: "/module/emergency", slug: "emergency", icon: "🚨" },
];
