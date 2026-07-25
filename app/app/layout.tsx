import type { Metadata } from "next";
import {  JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "EduPilot — Student Success AI Copilot",
  description:
    "Scholarships, eligibility checks, document analysis, and career roadmaps powered by multi-agent AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${jetbrainsMono.variable} antialiased `}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
