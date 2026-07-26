"use client";
import { Bell, Search, Sun, Moon } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

type Props = {
  userName?: string;
};

export default function DashboardHeader({ userName }: Props) {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <header className="sticky top-0 z-40 bg-white/90 dark:bg-[#08090E]/90 backdrop-blur-md border-b border-black/10 dark:border-white/8 px-6 py-5 flex items-center justify-between gap-4 transition-all duration-500">
      <div>
        <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-lg transition-all duration-500">
          {greeting},{" "}
          <span className="text-[#0C65D2]">{userName ?? "Student"}</span> 👋
        </p>
        <p className="font-mono text-base text-gray-400 dark:text-[#6B7280]">
          Here's what's happening with your applications today.
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button className="flex items-center gap-2 px-3 py-2 border border-black/10 dark:border-white/8 font-mono text-[12px] text-gray-400 dark:text-[#6B7280] hover:border-black/20 dark:hover:border-white/20 hover:text-gray-700 dark:hover:text-[#F0F4FF] cursor-pointer transition-all duration-500">
          <Search size={14} />
          <span className="hidden sm:inline">Search...</span>
        </button>
        <button className="relative p-2 border border-black/10 dark:border-white/8 text-gray-400 dark:text-[#6B7280] hover:border-black/20 dark:hover:border-white/20 hover:text-gray-700 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer">
          <Bell size={16} />
          <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-[#0C65D2]" />
        </button>
        {mounted && (
          <button
            onClick={() =>
              setTheme(resolvedTheme === "dark" ? "light" : "dark")
            }
            className="p-2 border border-black/10 dark:border-white/8 text-gray-400 dark:text-[#6B7280] hover:border-black/20 dark:hover:border-white/20 hover:text-gray-700 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer rounded-full"
          >
            {resolvedTheme === "dark" ? <Moon size={15} /> : <Sun size={15} />}
          </button>
        )}
      </div>
    </header>
  );
}
