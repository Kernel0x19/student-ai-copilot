"use client";
import {
  MoveRight,
  Sun,
  Moon,
  Menu,
  X,
  LogOut,
  LayoutDashboard,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useTheme } from "next-themes";
import { useEffect, useRef, useState } from "react";
import { createClient } from "@/app/lib/supabase/client";

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
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [user, setUser] = useState<{ name: string; email: string } | null>(
    null,
  );
  const [userLoading, setUserLoading] = useState(true);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    window.location.href = "/auth/login";
  };

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data }) => {
      if (data.user) {
        supabase
          .from("profiles")
          .select("full_name")
          .eq("id", data.user.id)
          .single()
          .then(({ data: profile }) => {
            setUser({
              name: profile?.full_name?.split(" ")[0] ?? "Student",
              email: data.user.email ?? "",
            });
            setUserLoading(false);
          });
      } else {
        setUserLoading(false);
      }
    });
  }, []);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const scrollTo = (section: string) => {
    document
      .getElementById(section.toLowerCase().replace(/\s/g, "-"))
      ?.scrollIntoView({ behavior: "smooth" });
    setMenuOpen(false);
  };

  useEffect(() => {
    setMounted(true);
  }, []);
  if (!mounted) return null;

  const initials = user?.name?.[0]?.toUpperCase() ?? "S";

  return (
    <nav className="w-full sticky top-0 bg-white/90 dark:bg-[#08090E]/85 backdrop-blur-md z-50 border-b border-black/10 dark:border-white/8 transition-all duration-500">
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-10 py-4">
        <Link href="/" className="flex items-center gap-2 hover:cursor-pointer">
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
        </Link>
        {!isAuth && (
          <div className="hidden lg:flex items-center gap-8 xl:gap-16">
            {NAV_LINKS.map((link) => (
              <span
                key={link}
                onClick={() => scrollTo(link)}
                className="font-mono text-base xl:text-lg text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-colors duration-500 cursor-pointer"
              >
                {link}
              </span>
            ))}
          </div>
        )}
        <div className="flex items-center gap-2 sm:gap-3">
          {userLoading ? (
            <div className="hidden sm:flex items-center gap-2">
              <div className="w-20 h-9 bg-black/8 dark:bg-white/8 animate-pulse" />
              <div className="w-28 h-9 bg-black/8 dark:bg-white/8 animate-pulse" />
            </div>
          ) : user ? (
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setDropdownOpen((p) => !p)}
                className="flex items-center gap-2.5 px-3 py-2 border border-black/10 dark:border-white/8 hover:border-[#0C65D2]/40 transition-all duration-200 cursor-pointer"
              >
                <div className="w-7 h-7 bg-[#0C65D2] flex items-center justify-center font-mono text-sm font-bold text-white rounded-full shrink-0">
                  {initials}
                </div>
                <span className="font-mono text-base text-gray-700 dark:text-[#F0F4FF] hidden sm:block">
                  {user.name}
                </span>
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 border border-black/10 dark:border-white/8 bg-white dark:bg-[#0F1117] shadow-xl z-50">
                  <div className="px-4 py-3 border-b border-black/10 dark:border-white/8">
                    <p className="font-mono text-sm font-bold text-gray-900 dark:text-[#F0F4FF]">
                      {user.name}
                    </p>
                    <p className="font-mono text-xs text-gray-400 dark:text-[#6B7280] truncate mt-0.5">
                      {user.email}
                    </p>
                  </div>
                  <div className="py-1">
                    <Link
                      href="/dashboard"
                      prefetch={true}
                      onClick={() => setDropdownOpen(false)}
                      className="flex items-center gap-2.5 px-4 py-3 font-mono text-sm text-gray-600 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] hover:bg-gray-50 dark:hover:bg-white/4 transition-colors duration-200"
                    >
                      <LayoutDashboard size={15} />
                      Dashboard
                    </Link>
                    <Link
                      href="/dashboard/profile"
                      onClick={() => setDropdownOpen(false)}
                      className="flex items-center gap-2.5 px-4 py-3 font-mono text-sm text-gray-600 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] hover:bg-gray-50 dark:hover:bg-white/4 transition-colors duration-200"
                    >
                      <div className="w-3.5 h-3.5 rounded-full border border-current" />
                      Profile
                    </Link>
                  </div>
                  <div className="border-t border-black/10 dark:border-white/8 py-1">
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2.5 px-4 py-3 w-full font-mono text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/8 transition-colors duration-200 cursor-pointer"
                    >
                      <LogOut size={15} />
                      Log out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            !isAuth && (
              <>
                <Link
                  href="/auth/login"
                  className="hidden sm:block px-4 py-2.5 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] font-mono text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500"
                >
                  Log in
                </Link>
                <Link
                  href="/auth/signup"
                  className="hidden sm:flex px-4 py-2.5 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] transition-colors duration-500 items-center gap-2 group"
                >
                  Get started
                  <MoveRight
                    size={14}
                    className="group-hover:translate-x-0.5 transition-transform duration-500"
                  />
                </Link>
              </>
            )
          )}
          <button
            onClick={() =>
              setTheme(resolvedTheme === "dark" ? "light" : "dark")
            }
            className="p-2 sm:p-2.5 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer rounded-full"
          >
            {resolvedTheme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          {!isAuth &&
            (userLoading ? (
              <div className="lg:hidden w-9 h-9 bg-black/8 dark:bg-white/8 animate-pulse" />
            ) : (
              <button
                onClick={() => setMenuOpen((prev) => !prev)}
                className="lg:hidden p-2 border border-black/10 dark:border-white/8 text-gray-500 dark:text-[#6B7280] hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer"
              >
                {menuOpen ? <X size={17} /> : <Menu size={17} />}
              </button>
            ))}
        </div>
      </div>
      {!isAuth && menuOpen && (
        <div className="lg:hidden border-t border-black/10 dark:border-white/8 bg-white/95 dark:bg-[#08090E]/95 backdrop-blur-md">
          <div className="flex flex-col px-4 sm:px-6 py-4 gap-1">
            {NAV_LINKS.map((link) => (
              <span
                key={link}
                onClick={() => scrollTo(link)}
                className="font-mono text-base text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-colors duration-500 cursor-pointer py-3 border-b border-black/5 dark:border-white/5 last:border-0"
              >
                {link}
              </span>
            ))}
            {userLoading ? (
              <div className="pt-3 flex gap-3">
                <div className="flex-1 h-11 bg-black/8 dark:bg-white/8 animate-pulse" />
                <div className="flex-1 h-11 bg-black/8 dark:bg-white/8 animate-pulse" />
              </div>
            ) : !user ? (
              <div className="flex gap-3 pt-3">
                <Link
                  href="/auth/login"
                  className="flex-1 px-4 py-3 border border-black/10 dark:border-white/8 bg-transparent text-gray-500 dark:text-[#6B7280] font-mono text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 text-center"
                >
                  Log in
                </Link>
                <Link
                  href="/auth/signup"
                  className="flex-1 px-4 py-3 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] transition-colors duration-500 flex items-center justify-center gap-2 group"
                >
                  Get started
                  <MoveRight
                    size={14}
                    className="group-hover:translate-x-0.5 transition-transform duration-500"
                  />
                </Link>
              </div>
            ) : (
              <div className="pt-3 flex flex-col gap-2">
                <div className="flex items-center gap-3 px-1 py-2 border-b border-black/10 dark:border-white/8 mb-1">
                  <div className="w-9 h-9 bg-[#0C65D2] flex items-center justify-center font-mono text-base font-bold text-white rounded-full shrink-0">
                    {initials}
                  </div>
                  <div>
                    <p className="font-mono text-sm font-bold text-gray-900 dark:text-[#F0F4FF]">
                      {user.name}
                    </p>
                    <p className="font-mono text-xs text-gray-400 dark:text-[#6B7280] truncate">
                      {user.email}
                    </p>
                  </div>
                </div>
                <Link
                  href="/dashboard"
                  prefetch={true}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] transition-colors duration-500"
                >
                  <LayoutDashboard size={15} />
                  Go to Dashboard
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center justify-center gap-2 px-4 py-3 border border-red-500/30 text-red-500 font-mono text-sm hover:bg-red-50 dark:hover:bg-red-500/8 transition-colors duration-200 cursor-pointer"
                >
                  <LogOut size={15} />
                  Log out
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
