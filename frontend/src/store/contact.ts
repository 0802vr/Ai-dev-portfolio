import { create } from "zustand";
export type ContactField = "name" | "phone" | "email" | "comment";
export type ContactFields = Record<ContactField, string>;
type Status = "idle" | "loading" | "success" | "error";
type Store = ContactFields & { status: Status; message: string; fieldErrors: Partial<Record<ContactField, string>>;
  setField: (field: ContactField, value: string) => void; submit: () => Promise<void> };
const initial: ContactFields = { name: "", phone: "", email: "", comment: "" };
export const useContactStore = create<Store>((set, get) => ({ ...initial, status: "idle", message: "", fieldErrors: {},
  setField: (field, value) => set((state) => ({ [field]: value, status: "idle", message: "",
    fieldErrors: { ...state.fieldErrors, [field]: undefined } })),
  submit: async () => { set({ status: "loading", message: "", fieldErrors: {} });
    const { name, phone, email, comment } = get();
    try { const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/contact`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, phone, email, comment }) });
      const data = await response.json();
      if (!response.ok) {
        const fieldErrors: Partial<Record<ContactField, string>> = {};
        for (const detail of data?.error?.details ?? []) {
          const field = detail?.loc?.at(-1) as ContactField;
          if (field in initial) fieldErrors[field] = detail.msg;
        }
        set({ status: "error", message: data?.error?.message ?? "Не удалось отправить заявку", fieldErrors });
        return;
      }
      set({ ...initial, status: "success", message: "Спасибо! Обращение принято.", fieldErrors: {} });
    } catch (error) { set({ status: "error", message: error instanceof Error ? error.message : "Ошибка соединения" }); }
  }
}));
