/** Store d'authentification (zustand) : JWT + claims décodés côté client. */
import { create } from "zustand";

interface AuthState {
  token: string | null;
  role: string;
  nom: string;
  login: (token: string, role: string, nom: string) => void;
  logout: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  token: sessionStorage.getItem("msk_token"),
  role: sessionStorage.getItem("msk_role") ?? "",
  nom: sessionStorage.getItem("msk_nom") ?? "",
  login: (token, role, nom) => {
    sessionStorage.setItem("msk_token", token);
    sessionStorage.setItem("msk_role", role);
    sessionStorage.setItem("msk_nom", nom);
    set({ token, role, nom });
  },
  logout: () => {
    ["msk_token", "msk_role", "msk_nom"].forEach((k) => sessionStorage.removeItem(k));
    set({ token: null, role: "", nom: "" });
  },
}));
