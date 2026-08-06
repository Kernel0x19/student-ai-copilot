"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import { redirect } from "next/navigation";
import {
  LayoutDashboard,
  GraduationCap,
  Briefcase,
  Code2,
  MessageSquare,
  FileText,
  Bell,
  User,
  LogOut,
  BookOpen,
  Search,
  BarChart3,
  FlaskConical,
} from "lucide-react";
import { logout } from "@/app/auth/actions";

const NAV = [
  {
    href: "/dashboard",
    icon: <LayoutDashboard size={17} />,
    label: "Dashboard",
  },
  {
    href: "/dashboard/scholarships",
    icon: <GraduationCap size={17} />,
    label: "Scholarships",
  },
  {
    href: "/dashboard/internships",
    icon: <Briefcase size={17} />,
    label: "Internships",
  },
  {
    href: "/dashboard/hackathons",
    icon: <Code2 size={17} />,
    label: "Hackathons",
  },
  {
    href: "/dashboard/chat",
    icon: <MessageSquare size={17} />,
    label: "AI Chat",
  },
  {
    href: "/dashboard/search",
    icon: <Search size={17} />,
    label: "Search",
  },
  {
    href: "/dashboard/documents",
    icon: <FileText size={17} />,
    label: "Documents",
  },
  {
    href: "/dashboard/notifications",
    icon: <Bell size={17} />,
    label: "Notifications",
  },
  { href: "/dashboard/profile", icon: <User size={17} />, label: "Profile" },
  { href: "/dashboard/consent", icon: <BookOpen size={17} />, label: "Consent" },
  { href: "/dashboard/admin", icon: <BarChart3 size={17} />, label: "Admin" },
  { href: "/dashboard/eval", icon: <FlaskConical size={17} />, label: "AI Quality" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-60 shrink-0 border-r border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] min-h-screen fixed top-0 left-0 bottom-0 transition-all duration-500">
      <div className="px-6 py-5 border-b border-black/10 dark:border-white/8 transition-all duration-500">
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
          <span className="font-syne text-xl sm:text-2xl font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
            Edu<span className="text-[#0C65D2]">Pilot</span>
          </span>
        </div>
      </div>
      <nav className="flex flex-col gap-1 px-3 py-4 flex-1">
        {NAV.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 font-mono text-sm transition-all duration-500 border-l-2 ${
                isActive
                  ? "border-[#0C65D2] bg-[#0C65D2]/8 dark:bg-[#0C65D2]/10 text-[#0C65D2]"
                  : "border-transparent text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] hover:bg-gray-100 dark:hover:bg-white/4"
              }`}
            >
              {item.icon}
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="px-3 py-4 border-t border-black/10 dark:border-white/8 transition-all duration-500">
        <button
          onClick={() => logout()}
          className="flex items-center gap-3 px-3 py-2.5 w-full font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/8 border-l-2 border-transparent transition-all duration-500 cursor-pointer"
        >
          <LogOut size={17} />
          Log out
        </button>
      </div>
    </aside>
  );
}
