/** Thème clair/sombre (nice-to-have) — persisté, appliqué via data-theme sur
 *  <body> ; les couleurs dérivent des variables CSS existantes. */
import { useEffect, useState } from "react";

const KEY = "msk_theme";
type Theme = "light" | "dark";

function initial(): Theme {
  const saved = localStorage.getItem(KEY);
  if (saved === "dark" || saved === "light") return saved;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(initial);

  useEffect(() => {
    document.body.dataset.theme = theme;
    localStorage.setItem(KEY, theme);
  }, [theme]);

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      title={theme === "dark" ? "Passer en thème clair" : "Passer en thème sombre"}
      aria-label="Basculer le thème clair/sombre"
    >
      {theme === "dark" ? "☀️ Clair" : "🌙 Sombre"}
    </button>
  );
}
