"use client";
import { MoveRight, Sun, Moon } from "lucide-react";
import { redirect } from "next/navigation";
import Image from "next/image";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

const NAV_LINKS = [
  "Home",
  "Features",
  "How it works",
  "Workflow",
  "Benefits",
  "FAQ",
];

interface Auth {
  isAuth?: boolean;
}

const Navbar = ({ isAuth }: Auth) => {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  const scrollTo = (section: string) => {
    document
      .getElementById(section.toLowerCase().replace(/\s/g, "-"))
      ?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  return (
    <nav className="w-full flex items-center justify-between px-10 py-3 border-b border-black/10 dark:border-white/8 sticky top-0 bg-white/90 dark:bg-[#08090E]/85 backdrop-blur-md z-50 transition-all duration-500">
      <div className="flex items-center gap-2 hover:cursor-pointer" onClick={() => redirect("/")}>
        <Image
          className="transition-all duration-500"
          src={"/LogoDark-t.png"}
          width={70}
          height={70}
          loading="eager"
          alt="EduPilot Logo"
        />
        <span className="font-syne text-3xl md:text-4xl font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
          Edu<span className="text-[#0C65D2]">Pilot</span>
        </span>
      </div>
      {!isAuth && (
        <>
          <div className="hidden md:flex items-center gap-16">
            {NAV_LINKS.map((link) => (
              <span
                key={link}
                onClick={() => scrollTo(link)}
                className="font-mono text-lg text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-colors duration-500 cursor-pointer"
              >
                {link}
              </span>
            ))}
          </div>
        </>
      )}
      <div className="flex items-center gap-3">
        {!isAuth && (
          <>
            <button
              className="px-5 py-2 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] font-mono text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer"
              onClick={() => redirect("/auth/login")}
            >
              Log in
            </button>
            <button
              className="px-5 py-2 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] transition-colors duration-500 cursor-pointer flex items-center gap-2 group"
              onClick={() => redirect("/auth/signup")}
            >
              Get started
              <MoveRight
                size={15}
                className="group-hover:translate-x-0.5 transition-transform duration-500"
              />
            </button>
          </>
        )}
        <button
          onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
          className="p-2.5 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer rounded-full"
        >
          {resolvedTheme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
