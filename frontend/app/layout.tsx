import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "Datacruit PoC — AI Recruitment Platform",
  description:
    "Proof of concept recreating Datacruit's core ATS workflow: job postings, AI candidate matching, pipelines, interview scheduling and hiring analytics.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen text-slate-900 antialiased">
        <Nav />
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
        <footer className="mx-auto max-w-6xl px-6 py-10 text-center text-xs text-slate-400">
          Unofficial proof-of-concept inspired by datacruit.com — not affiliated with Datacruit.
        </footer>
      </body>
    </html>
  );
}
