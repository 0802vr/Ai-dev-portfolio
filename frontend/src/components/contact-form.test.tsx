import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { useContactStore } from "@/store/contact";
import { ContactForm } from "./contact-form";

beforeEach(() => {
  useContactStore.setState({ name: "", phone: "", email: "", comment: "", status: "idle",
    message: "", fieldErrors: {} });
  vi.restoreAllMocks();
});

test("отправляет валидное обращение после согласия", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ message: "ok" }) }));
  render(<ContactForm />);
  fireEvent.change(screen.getByLabelText("Ваше имя"), { target: { value: "Анна" } });
  fireEvent.change(screen.getByLabelText("Телефон"), { target: { value: "+79990000000" } });
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "anna@example.com" } });
  fireEvent.change(screen.getByLabelText("Расскажите о задаче"), { target: { value: "Нужен корпоративный сайт" } });
  fireEvent.click(screen.getByRole("checkbox"));
  fireEvent.click(screen.getByRole("button", { name: "Обсудить проект" }));
  await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Обращение принято"));
});

