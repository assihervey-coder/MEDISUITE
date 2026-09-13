/** Noyau i18n PUR (testable sans React) — v0.11.
 *
 * Invariants :
 * - PARITÉ des clés entre fr/en/ar/es : garantie à la compilation
 *   (Record<Lang, Dictionary>) ET au runtime (test vitest) ;
 * - repli gracieux : langue inconnue → fr, clé manquante → fr → clé brute ;
 * - RTL : l'arabe est la seule langue de droite à gauche (dirFor).
 */
import translations from "./translations.json";

export const LANGS = ["fr", "en", "ar", "es"] as const;
export type Lang = (typeof LANGS)[number];
/** Le dictionnaire fr sert de référence de clés (compile-time parity). */
export type Dictionary = typeof translations.fr;
export type MsgKey = keyof Dictionary;

/** Échoue à la compilation si une langue manque d'une clé fr. */
export const dictionaries = translations as Record<Lang, Dictionary>;

export function isLang(value: string | null): value is Lang {
  return value !== null && (LANGS as readonly string[]).includes(value);
}

/** Normalisation fail-soft : tout ce qui n'est pas une langue connue → fr. */
export function storageKeyOf(value: string | null): Lang {
  return isLang(value) ? value : "fr";
}

export function dirFor(lang: Lang): "ltr" | "rtl" {
  return lang === "ar" ? "rtl" : "ltr";
}

/** Résolveur : dict courant → dict fr (repli) → clé brute (jamais undefined). */
export function createT(lang: Lang): (key: MsgKey) => string {
  const dict = dictionaries[lang] ?? dictionaries.fr;
  return (key) => dict[key] ?? dictionaries.fr[key] ?? String(key);
}
