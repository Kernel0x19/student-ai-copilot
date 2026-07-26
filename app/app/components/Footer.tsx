"use client";
import Image from "next/image";
import { useTheme } from "next-themes";
import { useState, useEffect } from "react";

const NAV_LINKS = [
  "Home",
  "Features",
  "How it works",
  "Workflow",
  "Benefits",
  "FAQ",
];

export default function Footer() {
  const scrollTo = (section: string) => {
    if (typeof window === "undefined") return;
    document
      .getElementById(section.toLowerCase().replace(/\s/g, "-"))
      ?.scrollIntoView({ behavior: "smooth" });
  };

  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  const SOCIAL = [
    {
      icon: (
        <Image
          src={
            !mounted || resolvedTheme === "dark"
              ? "/GithubLogo-dark.svg"
              : "/GithubLogo-light.svg"
          }
          width={20}
          height={20}
          loading="eager"
          alt="Github Logo"
        />
      ),
      href: "https://github.com",
      label: "GitHub",
    },
    {
      icon: (
        <Image
          src={
            !mounted || resolvedTheme === "dark"
              ? "/XLogo-dark.png"
              : "/XLogo.webp"
          }
          width={20}
          height={20}
          loading="eager"
          alt="X Logo"
        />
      ),
      href: "https://x.com",
      label: "X",
    },
    {
      icon: (
        <Image
          src={"/LinkedIn.svg"}
          width={20}
          height={20}
          loading="eager"
          alt="LinkedIn Logo"
        />
      ),
      href: "https://linkedin.com",
      label: "LinkedIn",
    },
    {
      icon: (
        <Image
          src={"/Instagram.svg"}
          width={20}
          height={20}
          loading="eager"
          alt="Instagram Logo"
        />
      ),
      href: "https://instagram.com",
      label: "Instagram",
    },
  ];

  return (
    <footer className="border-t border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
      <div className="max-w-300 mx-auto px-10 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-12 items-start">
          <div className="max-w-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 bg-[#0C65D2] flex items-center justify-center font-mono text-[13px] font-medium text-white transition-all duration-500">
                EP
              </div>
              <span className="font-syne text-xl font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
                Edu<span className="text-[#0C65D2]">Pilot</span>
              </span>
            </div>
            <p className="font-mono text-sm text-gray-500 dark:text-[#6B7280] leading-relaxed mb-6 transition-all duration-500">
              An agentic AI copilot built for Indian students. Find
              scholarships, verify eligibility, analyse documents, and plan your
              career — all in one place.
            </p>
            <div className="flex items-center gap-3">
              {SOCIAL.map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={s.label}
                  className="w-8 h-8 border border-black/10 dark:border-white/8 flex items-center justify-center text-gray-400 dark:text-[#6B7280] hover:border-[#0C65D2]/40 hover:text-[#0C65D2] transition-all duration-500"
                >
                  {s.icon}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="font-mono text-[10px] tracking-widest text-gray-400 dark:text-[#6B7280] mb-4 transition-all duration-500">
              NAVIGATE
            </p>
            <div className="flex flex-col gap-3">
              {NAV_LINKS.map((link) => (
                <span
                  key={link}
                  onClick={() => scrollTo(link)}
                  className="font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] cursor-pointer w-fit transition-all duration-500"
                >
                  {link}
                </span>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-16 pt-6 border-t border-black/10 dark:border-white/8 flex flex-col sm:flex-row items-center justify-between gap-4 transition-all duration-500">
          <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
            © 2026 EduPilot · Built by Team SPHINX for CODEAMBLE 2026
          </p>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
              All systems operational
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
