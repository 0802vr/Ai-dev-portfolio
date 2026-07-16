import { create } from "zustand";
export type ContactField = "name" | "phone" | "email" | "comment";
export type ContactFields = Record<ContactField, string>;
type Status = "idle" | "loading" | "success" | "error";
type Store = ContactFields & { status: Status; message: string;
  setField: (field: ContactField, value: string) => void; submit: () => Promise<void> };
const initial: ContactFields = { name: "", phone: "", email: "", comment: "" };
export const useContactStore = create<Store>((set, get) => ({ ...initial, status: "idle", message: "",
  setField: (field, value) => set({ [field]: value, status: "idle", message: "" }),
  submit: async () => { set({ status: "loading", message: "" });
    const { name, phone, email, comment } = get();
    try { const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/contact`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, phone, email, comment }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.error?.message ?? "Не удалось отправить заявку");
      set({ ...initial, status: "success", message: "Спасибо! Обращение принято." });
    } catch (error) { set({ status: "error", message: error instanceof Error ? error.message : "Ошибка соединения" }); }
  }
}));

