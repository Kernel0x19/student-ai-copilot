import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import {
  GraduationCap,
  Briefcase,
  MessageSquare,
  FileText,
  ArrowRight,
  Clock,
  BookmarkCheck,
  AlertCircle,
  TrendingUp,
  ChevronRight,
} from "lucide-react";

const MOCK_SCHOLARSHIPS = [
  {
    id: 1,
    title: "National Scholarship Portal — CSE",
    amount: "₹50,000",
    deadline: "2026-08-15",
    match: 94,
  },
  {
    id: 2,
    title: "MahaDBT — OBC Engineering",
    amount: "₹25,000",
    deadline: "2026-08-22",
    match: 88,
  },
  {
    id: 3,
    title: "Inspire Scholarship — DOST",
    amount: "₹80,000",
    deadline: "2026-09-01",
    match: 76,
  },
];

const MOCK_DEADLINES = [
  {
    id: 1,
    title: "NSP Scholarship",
    date: "Aug 15",
    daysLeft: 20,
    type: "scholarship",
  },
  {
    id: 2,
    title: "Google STEP Internship",
    date: "Aug 18",
    daysLeft: 23,
    type: "internship",
  },
  {
    id: 3,
    title: "MahaDBT Application",
    date: "Aug 22",
    daysLeft: 27,
    type: "scholarship",
  },
  {
    id: 4,
    title: "Inspire Scholarship",
    date: "Sep 01",
    daysLeft: 37,
    type: "scholarship",
  },
];

const MOCK_CHAT = [
  { id: 1, message: "Am I eligible for the NSP scholarship?", time: "2h ago" },
  {
    id: 2,
    message: "What skills do I need for an ML Engineer role?",
    time: "Yesterday",
  },
  { id: 3, message: "Generate a career roadmap for me", time: "2 days ago" },
];

const MOCK_SAVED = [
  {
    id: 1,
    title: "Google STEP Internship",
    type: "internship",
    saved: "3 days ago",
  },
  {
    id: 2,
    title: "NSP — Top Class Education",
    type: "scholarship",
    saved: "5 days ago",
  },
];

const MOCK_APPLICATIONS = [
  { id: 1, title: "NSP Scholarship", status: "In Progress", pct: 60 },
  { id: 2, title: "MahaDBT", status: "Documents Pending", pct: 30 },
  { id: 3, title: "Google STEP", status: "Submitted", pct: 100 },
];

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  const { data: profile } = await supabase
    .from("profiles")
    .select("full_name, college, stream, year_of_study, cgpa, is_admin")
    .eq("id", user.id)
    .single();

  const profileComplete = !!(
    profile?.college &&
    profile?.stream &&
    profile?.year_of_study
  );

  return (
    <div className="flex flex-col gap-6 max-w-300 transition-all duration-500">
      {!profileComplete && (
        <div className="flex items-center justify-between gap-4 px-5 py-4 border border-yellow-500/30 bg-yellow-500/8 dark:bg-yellow-500/10 transition-all duration-500">
          <div className="flex items-center gap-3">
            <AlertCircle
              size={16}
              className="text-yellow-500 shrink-0 transition-all duration-500"
            />
            <p className="font-mono text-sm text-yellow-700 dark:text-yellow-400 transition-all duration-500">
              Complete your profile to get personalized scholarship matches.
            </p>
          </div>
          <Link
            href="/dashboard/profile"
            className="font-mono text-[12px] text-yellow-600 dark:text-yellow-400 border border-yellow-500/30 px-3 py-1.5 hover:bg-yellow-500/10 shrink-0 transition-all duration-500"
          >
            Complete profile →
          </Link>
        </div>
      )}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          {
            label: "Scholarships matched",
            value: "18",
            icon: <GraduationCap size={16} />,
            color: "text-[#0C65D2]",
          },
          {
            label: "Internships available",
            value: "24",
            icon: <Briefcase size={16} />,
            color: "text-green-500",
          },
          {
            label: "Documents uploaded",
            value: "3",
            icon: <FileText size={16} />,
            color: "text-purple-500",
          },
          {
            label: "Applications tracked",
            value: "3",
            icon: <TrendingUp size={16} />,
            color: "text-orange-500",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 transition-all duration-500"
          >
            <div className={`mb-2 ${stat.color}`}>{stat.icon}</div>
            <p className={`font-syne text-2xl font-extrabold ${stat.color}`}>
              {stat.value}
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] mt-0.5 transition-all duration-500">
              {stat.label}
            </p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          {
            href: "/dashboard/scholarships",
            label: "Search scholarships",
            icon: <GraduationCap size={15} />,
          },
          {
            href: "/dashboard/chat",
            label: "Chat with AI",
            icon: <MessageSquare size={15} />,
          },
          {
            href: "/dashboard/documents",
            label: "Upload document",
            icon: <FileText size={15} />,
          },
          {
            href: "/dashboard/internships",
            label: "Find internships",
            icon: <Briefcase size={15} />,
          },
        ].map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="flex items-center justify-between gap-2 px-4 py-3 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] hover:border-[#0C65D2]/40 hover:bg-[#0C65D2]/4 dark:hover:bg-[#0C65D2]/8 transition-all duration-500 group"
          >
            <div className="flex items-center gap-2 font-mono text-[12px] text-gray-600 dark:text-[#6B7280] group-hover:text-[#0C65D2] transition-all duration-500">
              <span className="text-[#0C65D2]">{action.icon}</span>
              {action.label}
            </div>
            <ArrowRight
              size={13}
              className="text-gray-300 dark:text-white/20 group-hover:text-[#0C65D2] transition-colors duration-500"
            />
          </Link>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
        <div className="lg:col-span-2 border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
                Matched Scholarships
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                Ranked by eligibility fit
              </p>
            </div>
            <Link
              href="/dashboard/scholarships"
              className="font-mono text-[11px] text-[#0C65D2] hover:underline flex items-center gap-1"
            >
              View all <ChevronRight size={12} />
            </Link>
          </div>
          <div className="flex flex-col">
            {MOCK_SCHOLARSHIPS.map((s, i) => (
              <div
                key={s.id}
                className={`flex items-center justify-between gap-4 px-5 py-4 ${i !== MOCK_SCHOLARSHIPS.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
              >
                <div className="flex items-center gap-3 min-w-0 transition-all duration-500">
                  <div className="w-8 h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0">
                    <GraduationCap size={14} />
                  </div>
                  <div className="min-w-0">
                    <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] transition-all duration-500 truncate">
                      {s.title}
                    </p>
                    <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                      {s.amount} · Deadline {s.deadline}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0 transition-all duration-500">
                  <div className="text-right">
                    <p className="font-mono text-[12px] text-[#0C65D2] font-bold">
                      {s.match}%
                    </p>
                    <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                      match
                    </p>
                  </div>
                  <ChevronRight
                    size={14}
                    className="text-gray-300 dark:text-white/20 group-hover:text-[#0C65D2] transition-colors duration-500"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
                Upcoming Deadlines
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                Don't miss these
              </p>
            </div>
            <Clock
              size={14}
              className="text-gray-400 dark:text-[#6B7280] transition-all duration-500"
            />
          </div>
          <div className="flex flex-col">
            {MOCK_DEADLINES.map((d, i) => (
              <div
                key={d.id}
                className={`flex items-center justify-between gap-3 px-5 py-3.5 transition-all duration-500 ${i !== MOCK_DEADLINES.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""}`}
              >
                <div className="min-w-0">
                  <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] transition-all duration-500 truncate">
                    {d.title}
                  </p>
                  <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                    {d.date}
                  </p>
                </div>
                <span
                  className={`font-mono text-[10px] px-2 py-0.5 border shrink-0 transition-all duration-500 ${
                    d.daysLeft <= 14
                      ? "border-red-500/30 bg-red-500/10 text-red-500"
                      : d.daysLeft <= 30
                        ? "border-yellow-500/30 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400"
                        : "border-black/10 dark:border-white/8 text-gray-400 dark:text-[#6B7280]"
                  }`}
                >
                  {d.daysLeft}d left
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Application Progress
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
              Track your active applications
            </p>
          </div>
          <div className="flex flex-col gap-4 p-5">
            {MOCK_APPLICATIONS.map((app) => (
              <div key={app.id}>
                <div className="flex items-center justify-between mb-1.5">
                  <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] truncate transition-all duration-500">
                    {app.title}
                  </p>
                  <span
                    className={`font-mono text-[10px] shrink-0 ml-2 ${
                      app.pct === 100
                        ? "text-green-500"
                        : app.pct < 50
                          ? "text-yellow-500"
                          : "text-[#0C65D2]"
                    }`}
                  >
                    {app.status}
                  </span>
                </div>
                <div className="w-full h-1.5 bg-black/8 dark:bg-white/8 rounded-full overflow-hidden transition-all duration-500">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      app.pct === 100 ? "bg-green-500" : "bg-[#0C65D2]"
                    }`}
                    style={{ width: `${app.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500 text-sm">
                Recent AI Chats
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                Your last conversations
              </p>
            </div>
            <Link
              href="/dashboard/chat"
              className="font-mono text-[11px] text-[#0C65D2] hover:underline flex items-center gap-1"
            >
              Open <ChevronRight size={12} />
            </Link>
          </div>
          <div className="flex flex-col transition-all duration-500">
            {MOCK_CHAT.map((c, i) => (
              <div
                key={c.id}
                className={`flex items-start gap-3 px-5 py-3.5 transition-all duration-500 ${i !== MOCK_CHAT.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer`}
              >
                <div className="w-6 h-6 bg-[#0C65D2]/10 transition-all duration-500 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0 mt-0.5">
                  <MessageSquare size={11} />
                </div>
                <div className="min-w-0">
                  <p className="font-mono text-[12px] text-gray-700 transition-all duration-500 dark:text-[#a8c7fa] truncate">
                    {c.message}
                  </p>
                  <p className="font-mono text-[10px] text-gray-400 transition-all duration-500 dark:text-[#6B7280] mt-0.5">
                    {c.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <div className="px-5 py-3 border-t border-black/10  dark:border-white/8 transition-all duration-500">
            <Link
              href="/dashboard/chat"
              className="flex items-center justify-center gap-2 w-full py-2  bg-[#0C65D2] text-white font-mono text-[12px] hover:bg-[#0a52b0] transition-colors duration-500"
            >
              <MessageSquare size={13} />
              Start new chat
            </Link>
          </div>
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b transition-all duration-500 border-black/10 dark:border-white/8">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
                Saved Opportunities
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                Your bookmarked items
              </p>
            </div>
            <BookmarkCheck
              size={14}
              className="text-gray-400 dark:text-[#6B7280] transition-all duration-500"
            />
          </div>
          <div className="flex flex-col">
            {MOCK_SAVED.map((s, i) => (
              <div
                key={s.id}
                className={`flex items-center gap-3 px-5 py-3.5 transition-all duration-500 ${i !== MOCK_SAVED.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
              >
                <div
                  className={`w-7 h-7 flex items-center justify-center shrink-0 transition-all duration-500 ${
                    s.type === "scholarship"
                      ? "bg-[#0C65D2]/10 border border-[#0C65D2]/20 text-[#0C65D2]"
                      : "bg-green-500/10 border border-green-500/20 text-green-500"
                  }`}
                >
                  {s.type === "scholarship" ? (
                    <GraduationCap size={13} />
                  ) : (
                    <Briefcase size={13} />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] transition-all duration-500 truncate">
                    {s.title}
                  </p>
                  <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                    Saved {s.saved}
                  </p>
                </div>
                <ChevronRight
                  size={13}
                  className="text-gray-300 dark:text-white/20 group-hover:text-[#0C65D2]  shrink-0 transition-colors duration-500"
                />
              </div>
            ))}
          </div>
          {MOCK_SAVED.length === 0 && (
            <div className="px-5 py-8 text-center">
              <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
                No saved opportunities yet.
              </p>
              <Link
                href="/dashboard/scholarships"
                className="font-mono text-[12px] text-[#0C65D2] hover:underline mt-1 inline-block"
              >
                Browse scholarships →
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
