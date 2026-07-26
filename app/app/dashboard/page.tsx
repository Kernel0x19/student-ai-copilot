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
  SearchX,
  Inbox,
} from "lucide-react";

// ── TODO for AI team ──────────────────────────────────────────
// Replace these empty arrays with real data fetched from:
// SCHOLARSHIPS  → your scholarship matching API / Qdrant results
// DEADLINES     → derived from saved/applied scholarships & internships
// CHAT_HISTORY  → chat_history table filtered by user_id
// SAVED         → saved_opportunities table joined with scholarships/internships
// APPLICATIONS  → application_tracking table filtered by user_id
// STATS         → counts from respective tables
// ─────────────────────────────────────────────────────────────

const SCHOLARSHIPS: {
  id: number;
  title: string;
  amount: string;
  deadline: string;
  match: number;
}[] = [];

const DEADLINES: {
  id: number;
  title: string;
  date: string;
  daysLeft: number;
  type: string;
}[] = [];

const CHAT_HISTORY: {
  id: number;
  message: string;
  time: string;
}[] = [];

const SAVED: {
  id: number;
  title: string;
  type: string;
  saved: string;
}[] = [];

const APPLICATIONS: {
  id: number;
  title: string;
  status: string;
  pct: number;
}[] = [];

function EmptyState({
  message,
  action,
}: {
  message: string;
  action?: { label: string; href: string };
}) {
  return (
    <div className="flex flex-col items-center justify-center py-10 px-5 gap-3">
      <Inbox size={22} className="text-gray-300 dark:text-white/20" />
      <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] text-center">
        {message}
      </p>
      {action && (
        <Link
          href={action.href}
          className="font-mono text-[12px] text-[#0C65D2] hover:underline"
        >
          {action.label} →
        </Link>
      )}
    </div>
  );
}

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
            <AlertCircle size={16} className="text-yellow-500 shrink-0" />
            <p className="font-mono text-sm text-yellow-700 dark:text-yellow-400">
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
            value: "—",
            icon: <GraduationCap size={16} />,
            color: "text-[#0C65D2]",
          },
          {
            label: "Internships available",
            value: "—",
            icon: <Briefcase size={16} />,
            color: "text-green-500",
          },
          {
            label: "Documents uploaded",
            value: "0",
            icon: <FileText size={16} />,
            color: "text-purple-500",
          },
          {
            label: "Applications tracked",
            value: "0",
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
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] mt-0.5">
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
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Matched Scholarships
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
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
          {SCHOLARSHIPS.length === 0 ? (
            <EmptyState
              message="No scholarships matched yet. Complete your profile so the AI can find relevant scholarships for you."
              action={{ label: "Complete profile", href: "/dashboard/profile" }}
            />
          ) : (
            <div className="flex flex-col">
              {SCHOLARSHIPS.map((s, i) => (
                <div
                  key={s.id}
                  className={`flex items-center justify-between gap-4 px-5 py-4 ${i !== SCHOLARSHIPS.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0">
                      <GraduationCap size={14} />
                    </div>
                    <div className="min-w-0">
                      <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] truncate">
                        {s.title}
                      </p>
                      <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                        {s.amount} · Deadline {s.deadline}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right">
                      <p className="font-mono text-[12px] text-[#0C65D2] font-bold">
                        {s.match}%
                      </p>
                      <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
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
          )}
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Upcoming Deadlines
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                Don't miss these
              </p>
            </div>
            <Clock size={14} className="text-gray-400 dark:text-[#6B7280]" />
          </div>
          {DEADLINES.length === 0 ? (
            <EmptyState message="No upcoming deadlines. Save scholarships or internships to track their deadlines here." />
          ) : (
            <div className="flex flex-col">
              {DEADLINES.map((d, i) => (
                <div
                  key={d.id}
                  className={`flex items-center justify-between gap-3 px-5 py-3.5 transition-all duration-500 ${i !== DEADLINES.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""}`}
                >
                  <div className="min-w-0">
                    <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] truncate">
                      {d.title}
                    </p>
                    <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
                      {d.date}
                    </p>
                  </div>
                  <span
                    className={`font-mono text-[10px] px-2 py-0.5 border shrink-0 ${
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
          )}
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
              Application Progress
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Track your active applications
            </p>
          </div>
          {APPLICATIONS.length === 0 ? (
            <EmptyState
              message="No applications tracked yet. Start applying to scholarships and internships to track them here."
              action={{
                label: "Browse scholarships",
                href: "/dashboard/scholarships",
              }}
            />
          ) : (
            <div className="flex flex-col gap-4 p-5">
              {APPLICATIONS.map((app) => (
                <div key={app.id}>
                  <div className="flex items-center justify-between mb-1.5">
                    <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] truncate">
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
                  <div className="w-full h-1.5 bg-black/8 dark:bg-white/8 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${app.pct === 100 ? "bg-green-500" : "bg-[#0C65D2]"}`}
                      style={{ width: `${app.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Recent AI Chats
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
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
          {CHAT_HISTORY.length === 0 ? (
            <EmptyState
              message="No conversations yet. Ask the AI anything about scholarships, eligibility, or career paths."
              action={{ label: "Start a chat", href: "/dashboard/chat" }}
            />
          ) : (
            <div className="flex flex-col">
              {CHAT_HISTORY.map((c, i) => (
                <div
                  key={c.id}
                  className={`flex items-start gap-3 px-5 py-3.5 ${i !== CHAT_HISTORY.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer`}
                >
                  <div className="w-6 h-6 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0 mt-0.5">
                    <MessageSquare size={11} />
                  </div>
                  <div className="min-w-0">
                    <p className="font-mono text-[12px] text-gray-700 dark:text-[#a8c7fa] truncate">
                      {c.message}
                    </p>
                    <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] mt-0.5">
                      {c.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="px-5 py-3 border-t border-black/10 dark:border-white/8">
            <Link
              href="/dashboard/chat"
              className="flex items-center justify-center gap-2 w-full py-2 bg-[#0C65D2] text-white font-mono text-[12px] hover:bg-[#0a52b0] transition-colors duration-500"
            >
              <MessageSquare size={13} />
              Start new chat
            </Link>
          </div>
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Saved Opportunities
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                Your bookmarked items
              </p>
            </div>
            <BookmarkCheck
              size={14}
              className="text-gray-400 dark:text-[#6B7280]"
            />
          </div>
          {SAVED.length === 0 ? (
            <EmptyState
              message="No saved opportunities yet. Browse scholarships and internships and bookmark ones you're interested in."
              action={{
                label: "Browse scholarships",
                href: "/dashboard/scholarships",
              }}
            />
          ) : (
            <div className="flex flex-col">
              {SAVED.map((s, i) => (
                <div
                  key={s.id}
                  className={`flex items-center gap-3 px-5 py-3.5 ${i !== SAVED.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
                >
                  <div
                    className={`w-7 h-7 flex items-center justify-center shrink-0 ${
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
                    <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] truncate">
                      {s.title}
                    </p>
                    <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
                      Saved {s.saved}
                    </p>
                  </div>
                  <ChevronRight
                    size={13}
                    className="text-gray-300 dark:text-white/20 group-hover:text-[#0C65D2] shrink-0 transition-colors duration-500"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
