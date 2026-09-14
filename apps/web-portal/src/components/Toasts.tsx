/** Conteneur des notifications toast — coin bas-droite, pile animée. */
import { useToasts } from "../store/toastStore";

const ICON: Record<string, string> = { ok: "✅", warn: "⚠️", error: "⛔" };

export default function Toasts() {
  const { toasts, dismiss } = useToasts();
  if (toasts.length === 0) return null;
  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.kind}`} onClick={() => dismiss(t.id)}>
          <span aria-hidden>{ICON[t.kind]}</span>
          <span>{t.message}</span>
        </div>
      ))}
    </div>
  );
}
