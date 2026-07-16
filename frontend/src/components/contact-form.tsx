"use client";

import { FormEvent, useState } from "react";

import { type ContactField, useContactStore } from "@/store/contact";

const fields: Array<{ key: Exclude<ContactField, "comment">; label: string; type: string; placeholder: string }> = [
  { key: "name", label: "Ваше имя", type: "text", placeholder: "Александр" },
  { key: "phone", label: "Телефон", type: "tel", placeholder: "+7 999 000-00-00" },
  { key: "email", label: "Email", type: "email", placeholder: "hello@company.ru" },
];

export function ContactForm() {
  const store = useContactStore();
  const [consent, setConsent] = useState(false);
  const submit = (event: FormEvent) => {
    event.preventDefault();
    void store.submit();
  };

  return <form className="contact-form" onSubmit={submit} aria-label="Форма обратной связи">
    <div className="form-grid">{fields.map(({ key, label, type, placeholder }) =>
      <label key={key}>{label}<input required minLength={key === "name" ? 2 : undefined}
        aria-invalid={Boolean(store.fieldErrors[key])} aria-describedby={`${key}-error`}
        type={type} value={store[key]} placeholder={placeholder} autoComplete={key}
        onChange={(event) => store.setField(key, event.target.value)} />
        <span className="field-error" id={`${key}-error`}>{store.fieldErrors[key]}</span></label>)}</div>
    <label>Расскажите о задаче<textarea required minLength={10} maxLength={3000}
      aria-invalid={Boolean(store.fieldErrors.comment)} aria-describedby="comment-error"
      value={store.comment} placeholder="Что нужно разработать и какую задачу это решит?"
      onChange={(event) => store.setField("comment", event.target.value)} />
      <span className="field-error" id="comment-error">{store.fieldErrors.comment}</span></label>
    <label className="consent"><input type="checkbox" checked={consent} required
      onChange={(event) => setConsent(event.target.checked)} />
      <span>Я согласен с <a href="/privacy" target="_blank">политикой обработки персональных данных</a></span></label>
    <div className="form-footer"><button className="button" disabled={store.status === "loading"}>
      {store.status === "loading" ? "Отправляем…" : "Обсудить проект"}</button>
      <p className={`form-message ${store.status}`} role="status">{store.message}</p></div>
  </form>;
}

