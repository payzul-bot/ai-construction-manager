"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { getApiConfig } from "../src/lib/api";

const examples = [
  "Покрасить стены в квартире 60 м²",
  "Смета на ремонт офиса под ключ",
  "Демонтаж перегородок и вывоз мусора",
  "Коммерческая смета для подрядчика"
];

export default function HomePage() {
  const apiConfig = useMemo(() => getApiConfig(), []);
  const [prompt, setPrompt] = useState("");

  return (
    <main>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>AI Construction Platform</h1>
          <p style={{ marginTop: 0, color: "#4b5563" }}>
            API: {apiConfig.apiBase} | Tenant: {apiConfig.tenantId}
          </p>
        </div>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link href="/projects" style={{ color: "#2563eb", textDecoration: "none" }}>
            Projects
          </Link>
          <Link href="/projects/new" style={{ color: "#2563eb", textDecoration: "none" }}>
            Create project
          </Link>
        </nav>
      </header>

      <section
        style={{
          background: "white",
          padding: 24,
          marginTop: 24,
          borderRadius: 16,
          boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)"
        }}
      >
        <h2 style={{ marginTop: 0 }}>Entry Point — Свободный запрос</h2>
        <p style={{ color: "#4b5563" }}>
          В текущей версии запрос фиксируется как UI-ввод. Документация не описывает
          API-эндпоинт для свободного текста, поэтому поле только для чернового ввода.
        </p>
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Опишите задачу обычным языком"
          rows={4}
          style={{
            width: "100%",
            padding: 12,
            borderRadius: 12,
            border: "1px solid #e2e8f0",
            marginTop: 12,
            resize: "vertical"
          }}
        />
        <div style={{ marginTop: 16 }}>
          <p style={{ marginBottom: 8, fontWeight: 600 }}>Примеры запросов</p>
          <ul style={{ margin: 0, paddingLeft: 20, color: "#4b5563" }}>
            {examples.map((text) => (
              <li key={text} style={{ marginBottom: 4 }}>
                {text}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section
        style={{
          marginTop: 24,
          background: "white",
          padding: 24,
          borderRadius: 16,
          border: "1px solid #e2e8f0"
        }}
      >
        <h2 style={{ marginTop: 0 }}>Flow B — Создать проект</h2>
        <p style={{ color: "#4b5563" }}>
          Создание проекта запускает сбор Project Passport и подбор графа работ.
        </p>
        <Link
          href="/projects/new"
          style={{
            display: "inline-flex",
            padding: "10px 16px",
            borderRadius: 12,
            background: "#2563eb",
            color: "white",
            textDecoration: "none",
            fontWeight: 600
          }}
        >
          Перейти к созданию проекта
        </Link>
      </section>
    </main>
  );
}
