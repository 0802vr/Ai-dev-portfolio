"use client";
import { FormEvent } from "react";
import { useContactStore, type ContactFields } from "@/store/contact";

const fields: { key: keyof ContactFields; label: string; type?: string; placeholder: string }[] = [
  { key: "name", label: "Ваше имя", placeholder: "Александр" },
  { key: "phone", label: "Телефон", type: "tel", placeholder: "+7 999 000-00-00" },
  { key: "email", label: "Email", type: "email", placeholder: "hello@company.ru" },
];
export function ContactForm() {
  const store = useContactStore();
  const submit = (event: FormEvent) => { event.preventDefault(); void store.submit(); };
  return <form className="contact-form" onSubmit={submit} aria-label="Форма обратной связи">
    <div className="form-grid">{fields.map(({ key, label, type = "text", placeholder }) =>
      <label key={key}>{label}<input required minLength={key === "name" ? 2 : undefined}
        type={type} value={store[key]} placeholder={placeholder} autoComplete={key}
        onChange={(event) => store.setField(key, event.target.value)} /></label>)}</div>
    <label>Расскажите о задаче<textarea required minLength={10} maxLength={3000}
      value={store.comment} placeholder="Что нужно разработать и какую задачу это решит?"
      onChange={(event) => store.setField("comment", event.target.value)} /></label>
    <div className="form-footer"><button className="button" disabled={store.status === "loading"}>
      {store.status === "loading" ? "Отправляем…" : "Обсудить проект"}</button>
      <p className={`form-message ${store.status}`} role="status">{store.message}</p></div>
  </form>;
}

