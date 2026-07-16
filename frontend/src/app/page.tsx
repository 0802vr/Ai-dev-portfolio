import { ContactForm } from "@/components/contact-form";
import { Reveal } from "@/components/reveal";
const projects = [
  ["01", "Pulse CRM", "SaaS-платформа", "Единый контур продаж с аналитикой и AI-подсказками."],
  ["02", "North Logistics", "B2B-сервис", "Управление маршрутами и документами в реальном времени."],
  ["03", "Form AI", "AI-интеграция", "Классификация обращений и автоматизация первого ответа."]];
const stack = ["Python", "FastAPI", "PostgreSQL", "Next.js", "TypeScript", "Docker", "AI API", "CI/CD"];
export default function Home() { return <><header className="header"><a className="logo" href="#top">AV<span>.</span></a>
  <nav aria-label="Основная навигация"><a href="#about">Подход</a><a href="#work">Проекты</a><a href="#contact">Контакты</a></nav><a className="header-link" href="#contact">Начать проект ↗</a></header>
  <main id="top"><section className="hero" aria-labelledby="hero-title"><div className="hero-kicker"><span>Full-stack developer</span><span>Самара · 2026</span></div>
    <Reveal><h1 id="hero-title">Создаю цифровые<br/><em>продукты</em>, которые<br/>работают.</h1></Reveal>
    <div className="hero-bottom"><p>Проектирую backend-системы, интерфейсы и AI-интеграции — от идеи до стабильного запуска.</p><a className="circle-link" href="#about">↓</a></div><div className="orb" aria-hidden="true"/></section>
  <section className="about section" id="about"><Reveal className="section-label">01 / Подход</Reveal><Reveal><h2>Сложное внутри.<br/><span>Простое снаружи.</span></h2></Reveal>
    <div className="about-grid"><Reveal><p className="lead">Помогаю бизнесу превращать процессы и идеи в понятные, быстрые и поддерживаемые продукты.</p></Reveal>
    <Reveal><div className="principles">{[["01","Архитектура","Система растёт без болезненных переделок."],["02","Надёжность","Ошибки видны, данные защищены, сервис доступен."],["03","Результат","Технология решает задачу, а не усложняет её."]].map(x=><article key={x[0]}><b>{x[0]}</b><h3>{x[1]}</h3><p>{x[2]}</p></article>)}</div></Reveal></div>
    <Reveal><ul className="stack">{stack.map(x=><li key={x}>{x}</li>)}</ul></Reveal></section>
  <section className="work section" id="work"><Reveal className="section-label">02 / Избранные проекты</Reveal><Reveal><h2>От задачи<br/>до <span>результата.</span></h2></Reveal>
    <div className="projects">{projects.map(x=><Reveal key={x[0]}><article className="project"><span>{x[0]}</span><div><small>{x[2]}</small><h3>{x[1]}</h3><p>{x[3]}</p></div><i>↗</i></article></Reveal>)}</div></section>
  <section className="contact section" id="contact"><Reveal className="section-label">03 / Контакты</Reveal><div className="contact-head"><Reveal><h2>Есть задача?<br/><span>Давайте обсудим.</span></h2></Reveal><Reveal><p>AI проанализирует обращение, а я лично отвечу и предложу следующий шаг.</p></Reveal></div><Reveal><ContactForm/></Reveal></section></main>
  <footer><a className="logo" href="#top">AV<span>.</span></a><p>© 2026 Алексей Волков</p><a href="mailto:hello@example.com">hello@example.com</a></footer></> }
