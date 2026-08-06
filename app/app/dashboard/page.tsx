export const runtime = "edge";
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
  Inbox,
} from "lucide-react";
import {
  getRecommendations,
  getDashboardStats,
  getApplications,
  getProfile,
} from "@/app/lib/api";

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

function daysLeft(deadline: string) {
  const d = Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000);
  return d;
}

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  let profile = null;
  let stats = { scholarships_matched: 0, internships_available: 0, documents_uploaded: 0, applications_tracked: 0, readiness_score: 0 };
  let scholarships: { id: string; title: string; amount: string; deadline: string; match: number }[] = [];
  let deadlines: { id: string; title: string; date: string; daysLeft: number; type: string }[] = [];
  let applications: { id: string; title: string; status: string; pct: number }[] = [];
  let saved: { id: string; title: string; type: string; saved: string }[] = [];

  try {
    const [profileData, statsData, recData, appsData] = await Promise.all([
      getProfile(user.id, user.email ?? "").catch(() => null),
      getDashboardStats(user.id, user.email ?? "").catch(() => stats),
      getRecommendations(user.id, user.email ?? "").catch(() => ({ matches: [], total: 0, readiness_score: 0 })),
      getApplications(user.id, user.email ?? "").catch(() => []),
    ]);

    profile = profileData;
    stats = statsData;

    scholarships = recData.matches.slice(0, 5).map((m) => ({
      id: m.opportunity.id,
      title: m.opportunity.title,
      amount: m.opportunity.amount_max
        ? `Up to ₹${m.opportunity.amount_max.toLocaleString()}`
        : "—",
      deadline: m.opportunity.deadline ?? "TBD",
      match: m.match_score,
    }));

    deadlines = recData.matches
      .filter((m) => m.opportunity.deadline)
      .slice(0, 5)
      .map((m) => ({
        id: m.opportunity.id,
        title: m.opportunity.title,
        date: m.opportunity.deadline!,
        daysLeft: daysLeft(m.opportunity.deadline!),
        type: "scholarship",
      }))
      .sort((a, b) => a.daysLeft - b.daysLeft);

    applications = appsData.slice(0, 5).map((a) => ({
      id: a.id,
      title: a.opportunity?.title ?? "Application",
      status: a.state.replace(/_/g, " "),
      pct: a.progress_pct,
    }));

    saved = appsData
      .filter((a) => a.saved)
      .slice(0, 5)
      .map((a) => ({
        id: a.id,
        title: a.opportunity?.title ?? "Saved",
        type: "scholarship",
        saved: new Date(a.created_at).toLocaleDateString(),
      }));
  } catch {
  }

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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 transition-all duration-500">
        {[
          {
            label: "Scholarships matched",
            value: String(stats.scholarships_matched),
            icon: <GraduationCap size={16} />,
            color: "text-[#0C65D2]",
          },
          {
            label: "Internships available",
            value: String(stats.internships_available),
            icon: <Briefcase size={16} />,
            color: "text-green-500",
          },
          {
            label: "Documents uploaded",
            value: String(stats.documents_uploaded),
            icon: <FileText size={16} />,
            color: "text-purple-500",
          },
          {
            label: "Applications tracked",
            value: String(stats.applications_tracked),
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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 transition-all duration-500">
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
                Ranked by eligibility fit · Readiness {stats.readiness_score}%
              </p>
            </div>
            <Link
              href="/dashboard/scholarships"
              className="font-mono text-[11px] text-[#0C65D2] hover:underline flex items-center gap-1"
            >
              View all <ChevronRight size={12} />
            </Link>
          </div>
          {scholarships.length === 0 ? (
            <EmptyState
              message="No scholarships matched yet. Complete your profile so the AI can find relevant scholarships for you."
              action={{ label: "Complete profile", href: "/dashboard/profile" }}
            />
          ) : (
            <div className="flex flex-col transition-all duration-500">
              {scholarships.map((s, i) => (
                <Link
                  key={s.id}
                  href="/dashboard/scholarships"
                  className={`flex items-center justify-between gap-4 px-5 py-4 ${i !== scholarships.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group `}
                >
                  <div className="flex items-center gap-3 min-w-0 transition-all duration-500">
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
                </Link>
              ))}
            </div>
          )}
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Upcoming Deadlines
              </p>
              <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                Don&apos;t miss these
              </p>
            </div>
            <Clock size={14} className="text-gray-400 dark:text-[#6B7280]" />
          </div>
          {deadlines.length === 0 ? (
            <EmptyState message="No upcoming deadlines. Save scholarships or internships to track their deadlines here." />
          ) : (
            <div className="flex flex-col">
              {deadlines.map((d, i) => (
                <div
                  key={d.id}
                  className={`flex items-center justify-between gap-3 px-5 py-3.5 transition-all duration-500 ${i !== deadlines.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""}`}
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
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Application Progress
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
              Track your active applications
            </p>
          </div>
          {applications.length === 0 ? (
            <EmptyState
              message="No applications tracked yet. Start applying to scholarships and internships to track them here."
              action={{
                label: "Browse scholarships",
                href: "/dashboard/scholarships",
              }}
            />
          ) : (
            <div className="flex flex-col gap-4 p-5">
              {applications.map((app) => (
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
          <div className="flex items-center justify-between px-5 transition-all duration-500 py-4 border-b border-black/10 dark:border-white/8">
            <div>
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
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
          <EmptyState
            message="AI Chat coming in Phase 2. Use Scholarship Agent for now."
            action={{ label: "Browse scholarships", href: "/dashboard/scholarships" }}
          />
        </div>
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
          <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
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
              className="text-gray-400 dark:text-[#6B7280]"
            />
          </div>
          {saved.length === 0 ? (
            <EmptyState
              message="No saved opportunities yet. Browse scholarships and internships and bookmark ones you're interested in."
              action={{
                label: "Browse scholarships",
                href: "/dashboard/scholarships",
              }}
            />
          ) : (
            <div className="flex flex-col">
              {saved.map((s, i) => (
                <div
                  key={s.id}
                  className={`flex items-center gap-3 px-5 py-3.5 ${i !== saved.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
                >
                  <div className="w-7 h-7 flex items-center justify-center shrink-0 bg-[#0C65D2]/10 border border-[#0C65D2]/20 text-[#0C65D2]">
                    <GraduationCap size={13} />
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
