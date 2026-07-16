import type { Metadata } from "next";
import { Manrope, Unbounded } from "next/font/google";
import "./globals.css";
const manrope = Manrope({ subsets: ["cyrillic", "latin"], variable: "--font-body" });
const display = Unbounded({ subsets: ["cyrillic", "latin"], variable: "--font-display" });
export const metadata: Metadata = { title: "Алексей Волков — full-stack разработчик",
  description: "Разработка быстрых веб-сервисов и AI-интеграций для бизнеса.",
  metadataBase: new URL("https://example.com"),
  openGraph: { title: "Алексей Волков — full-stack разработчик",
    description: "Backend-системы, интерфейсы и AI-интеграции для бизнеса.",
    type: "website", locale: "ru_RU" },
  robots: { index: true, follow: true } };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ru"><body className={`${manrope.variable} ${display.variable}`}>{children}</body></html>;
}
