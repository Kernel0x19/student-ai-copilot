"use client";

import { useState } from "react";
import { GraduationCap, Search, BookmarkPlus, ExternalLink, CheckCircle, XCircle } from "lucide-react";
import type { MatchResult } from "@/app/lib/api";
import { saveOpportunity } from "@/app/lib/api";
import FeedbackWidget from "@/app/components/dashboard/FeedbackWidget";

interface Props {
  initialMatches: MatchResult[];
  userId: string;
  userEmail: string;
}

export default function ScholarshipsClient({ initialMatches, userId, userEmail }: Props) {
  const [matches, setMatches] = useState(initialMatches);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/scholarships/recommendations?query=${encodeURIComponent(query)}&limit=20`,
        { headers: { "X-User-Id": userId, "X-User-Email": userEmail } }
      );
      const data = await res.json();
      setMatches(data.matches);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(opportunityId: string) {
    await saveOpportunity(userId, opportunityId, userEmail);
  }

  return (
    <div className="flex flex-col gap-6 transition-all duration-500">
      <div>
        <h1 className="font-syne text-xl font-bold">Scholarship Agent</h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1 transition-all duration-500">
          Matched from NSP, MahaDBT & myScheme — ranked by eligibility fit
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 transition-all duration-500">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Semantic search e.g. engineering girls scholarship Maharashtra"
          className="flex-1 px-4 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] transition-all duration-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-[#0C65D2] text-white font-mono text-[12px] flex items-center gap-2 transition-all duration-500"
        >
          <Search size={14} /> {loading ? "…" : "Search"}
        </button>
      </form>

      <div className="flex flex-col gap-3 transition-all duration-500">
        {matches.length === 0 ? (
          <p className="font-mono text-[12px] text-gray-400 py-10 text-center">
            No matches. Complete your profile for personalized recommendations.
          </p>
        ) : (
          matches.map((m) => (
            <ScholarshipCard key={m.opportunity.id} match={m} onSave={() => handleSave(m.opportunity.id)} userId={userId} userEmail={userEmail} />
          ))
        )}
      </div>
    </div>
  );
}

function ScholarshipCard({ match, onSave, userId, userEmail }: { match: MatchResult; onSave: () => void; userId: string; userEmail: string }) {
  const { opportunity: o, match_score, eligibility, reasons } = match;
  const amount =
    o.amount_min && o.amount_max
      ? `₹${o.amount_min.toLocaleString()} – ₹${o.amount_max.toLocaleString()}`
      : o.amount_max
        ? `Up to ₹${o.amount_max.toLocaleString()}`
        : "Amount varies";

  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-3 transition-all duration-500">
      <div className="flex items-start justify-between gap-4 transition-all duration-500">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-9 h-9 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0">
            <GraduationCap size={16} />
          </div>
          <div className="min-w-0">
            <p className="font-mono text-[14px] font-bold text-gray-900 dark:text-[#F0F4FF]">{o.title}</p>
            <p className="font-mono text-[11px] text-gray-400 mt-0.5">
              {o.source.toUpperCase()} · {amount}
              {o.deadline && ` · Deadline ${o.deadline}`}
            </p>
          </div>
        </div>
        <div className="text-right shrink-0">
          <p className="font-mono text-lg font-bold text-[#0C65D2]">{match_score}%</p>
          <p className="font-mono text-[10px] text-gray-400">match</p>
        </div>
      </div>

      {o.description && (
        <p className="font-mono text-[12px] text-gray-600 dark:text-[#a8c7fa] leading-relaxed">{o.description}</p>
      )}

      <div className="flex items-center gap-2 transition-all duration-500">
        {eligibility.eligible ? (
          <span className="flex items-center gap-1 font-mono text-[11px] text-green-600">
            <CheckCircle size={12} /> Likely eligible
          </span>
        ) : (
          <span className="flex items-center gap-1 font-mono text-[11px] text-red-500">
            <XCircle size={12} /> May not qualify
          </span>
        )}
      </div>

      <ul className="flex flex-col gap-1 transition-all duration-500">
        {reasons.slice(0, 4).map((r, i) => (
          <li key={i} className="font-mono text-[11px] text-gray-500 dark:text-[#6B7280]">{r}</li>
        ))}
      </ul>

      <div className="flex gap-2 pt-1 transition-all duration-500">
        <button
          onClick={onSave}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-[#0C65D2]/30 text-[#0C65D2] font-mono text-[11px] hover:bg-[#0C65D2]/5"
        >
          <BookmarkPlus size={12} /> Save & track
        </button>
        {o.application_url && (
          <a
            href={o.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-500 hover:text-[#0C65D2]"
          >
            <ExternalLink size={12} /> Official portal
          </a>
        )}
        <FeedbackWidget opportunityId={o.id} userId={userId} userEmail={userEmail} />
      </div>
    </div>
  );
}
