/** Provider React i18n : persistance localStorage, lang/dir du document,
 * repli fail-soft. Logique pure dans resolve.ts (testée), ce fichier est
 * l'enveloppe minime. */
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  createT,
  dirFor,
  storageKeyOf,
  type Lang,
  type MsgKey,
} from "./resolve";

const STORAGE_KEY = "medisuite.lang";

type I18nContext = {
  lang: Lang;
  dir: "ltr" | "rtl";
  setLang: (lang: Lang) => void;
  t: (key: MsgKey) => string;
};

const Ctx = createContext<I18nContext | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() =>
    storageKeyOf(localStorage.getItem(STORAGE_KEY)),
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = dirFor(lang);
  }, [lang]);

  const value = useMemo<I18nContext>(
    () => ({ lang, dir: dirFor(lang), setLang, t: createT(lang) }),
    [lang],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n(): I18nContext {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useI18n : hors LanguageProvider");
  return ctx;
}
