"use client";
import { MoveRight, Sun, Moon, Menu, X } from "lucide-react";
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
  const [menuOpen, setMenuOpen] = useState(false);

  const scrollTo = (section: string) => {
    document
      .getElementById(section.toLowerCase().replace(/\s/g, "-"))
      ?.scrollIntoView({ behavior: "smooth" });
    setMenuOpen(false);
  };

  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  return (
    <nav className="w-full sticky top-0 bg-white/90 dark:bg-[#08090E]/85 backdrop-blur-md z-50 border-b border-black/10 dark:border-white/8 transition-all duration-500">
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-10 py-3">
        <div
          className="flex items-center gap-2 hover:cursor-pointer"
          onClick={() => redirect("/")}
        >
          <Image
            className="transition-all duration-500"
            src={"/LogoDark-t.png"}
            width={50}
            height={50}
            loading="eager"
            alt="EduPilot Logo"
          />
          <span className="font-syne text-2xl sm:text-3xl font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
            Edu<span className="text-[#0C65D2]">Pilot</span>
          </span>
        </div>

        {!isAuth && (
          <div className="hidden lg:flex items-center gap-8 xl:gap-16">
            {NAV_LINKS.map((link) => (
              <span
                key={link}
                onClick={() => scrollTo(link)}
                className="font-mono text-sm xl:text-base text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-colors duration-500 cursor-pointer"
              >
                {link}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 sm:gap-3">
          {!isAuth && (
            <>
              <button
                className="hidden sm:block px-4 py-2 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] font-mono text-xs sm:text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer"
                onClick={() => redirect("/auth/login")}
              >
                Log in
              </button>
              <button
                className="hidden sm:flex px-4 py-2 bg-[#0C65D2] text-white font-mono text-xs sm:text-sm hover:bg-[#0a52b0] transition-colors duration-500 cursor-pointer items-center gap-2 group"
                onClick={() => redirect("/auth/signup")}
              >
                Get started
                <MoveRight
                  size={14}
                  className="group-hover:translate-x-0.5 transition-transform duration-500"
                />
              </button>
            </>
          )}

          <button
            onClick={() =>
              setTheme(resolvedTheme === "dark" ? "light" : "dark")
            }
            className="p-2 sm:p-2.5 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer rounded-full"
          >
            {resolvedTheme === "dark" ? (
              <Sun size={15} />
            ) : (
              <Moon size={15} />
            )}
          </button>

          {!isAuth && (
            <button
              onClick={() => setMenuOpen((prev) => !prev)}
              className="lg:hidden p-2 border border-black/10 dark:border-white/8 text-gray-500 dark:text-[#6B7280] hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer"
            >
              {menuOpen ? <X size={16} /> : <Menu size={16} />}
            </button>
          )}
        </div>
      </div>

      {!isAuth && menuOpen && (
        <div className="lg:hidden border-t border-black/10 dark:border-white/8 bg-white/95 dark:bg-[#08090E]/95 backdrop-blur-md">
          <div className="flex flex-col px-4 sm:px-6 py-4 gap-1">
            {NAV_LINKS.map((link) => (
              <span
                key={link}
                onClick={() => scrollTo(link)}
                className="font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-colors duration-500 cursor-pointer py-2.5 border-b border-black/5 dark:border-white/5 last:border-0"
              >
                {link}
              </span>
            ))}
            <div className="flex gap-3 pt-3">
              <button
                className="flex-1 px-4 py-2.5 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] font-mono text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer"
                onClick={() => redirect("/auth/login")}
              >
                Log in
              </button>
              <button
                className="flex-1 px-4 py-2.5 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] transition-colors duration-500 cursor-pointer flex items-center justify-center gap-2 group"
                onClick={() => redirect("/auth/signup")}
              >
                Get started
                <MoveRight
                  size={14}
                  className="group-hover:translate-x-0.5 transition-transform duration-500"
                />
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;