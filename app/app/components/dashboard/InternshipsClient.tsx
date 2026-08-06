"use client";

import React, { useState, useCallback, useTransition, useEffect } from "react";
import {
  Briefcase, Search, BookmarkPlus, ExternalLink,
  CheckCircle, XCircle, MapPin, Clock, Banknote,
  Wifi, Building2, GitMerge, SlidersHorizontal,
  X, ChevronDown, ChevronUp, Loader2, User,
} from "lucide-react";
import type { InternshipMatchResult } from "@/app/lib/api";
import { saveInternship } from "@/app/lib/api";
import FeedbackWidget from "@/app/components/dashboard/FeedbackWidget";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Filters {
  work_type: string;
  duration_max: string;
  stipend_min: string;
  location: string;
  source: string;
}

const EMPTY_FILTERS: Filters = {
  work_type: "", duration_max: "", stipend_min: "", location: "", source: "",
};

interface Props {
  userId: string;
  userEmail: string;
}

const PLATFORMS: Record<string, { label: string; color: string; bg: string }> = {
  internshala: { label: "Internshala", color: "text-[#007bff]", bg: "bg-[#007bff]/8 border-[#007bff]/20" },
  indeed:      { label: "Indeed",      color: "text-[#2557a7]", bg: "bg-[#2557a7]/8 border-[#2557a7]/20" },
  naukri:      { label: "Naukri",      color: "text-[#ff7555]", bg: "bg-[#ff7555]/8 border-[#ff7555]/20" },
  wellfound:   { label: "Wellfound",   color: "text-[#ef4444]", bg: "bg-[#ef4444]/8 border-[#ef4444]/20" },
  unstop:      { label: "Unstop",      color: "text-[#8b5cf6]", bg: "bg-[#8b5cf6]/8 border-[#8b5cf6]/20" },
  aicte:       { label: "AICTE",       color: "text-[#16a34a]", bg: "bg-[#16a34a]/8 border-[#16a34a]/20" },
};

function platformMeta(src: string) {
  return PLATFORMS[src.toLowerCase()] ?? {
    label: src.toUpperCase(), color: "text-gray-500",
    bg: "bg-gray-100/50 border-gray-200 dark:bg-white/5 dark:border-white/10",
  };
}

function SourceBadge({ source }: { source: string }) {
  const { label, color, bg } = platformMeta(source);
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 border font-mono text-[9px] font-bold tracking-wide ${color} ${bg}`}>
      {label}
    </span>
  );
}

function FilterPill({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="flex items-center gap-1 px-2 py-0.5 bg-[#0C65D2]/10 border border-[#0C65D2]/20 font-mono text-[11px] text-[#0C65D2]">
      {label}
      <button type="button" onClick={onRemove} className="hover:text-red-500"><X size={10} /></button>
    </span>
  );
}

function ScoreRing({ score }: { score: number }) {
  const color = score >= 70 ? "text-green-500" : score >= 45 ? "text-[#0C65D2]" : "text-gray-400";
  return (
    <div className="text-right shrink-0">
      <p className={`font-mono text-lg font-bold ${color}`}>{Math.round(score)}%</p>
      <p className="font-mono text-[10px] text-gray-400">match</p>
    </div>
  );
}

function buildUrl(base: string, query: string, filters: Filters, limit = 30): string {
  const p = new URLSearchParams();
  if (query.trim())            p.set("query",        query.trim());
  if (filters.work_type)       p.set("work_type",    filters.work_type);
  if (filters.duration_max)    p.set("duration_max", filters.duration_max);
  if (filters.stipend_min)     p.set("stipend_min",  filters.stipend_min);
  if (filters.location.trim()) p.set("location",     filters.location.trim());
  if (filters.source)          p.set("source",       filters.source);
  p.set("limit", String(limit));
  return `${base}/api/v1/internships/recommendations?${p}`;
}

export default function InternshipsClient({ userId, userEmail }: Props) {
  const [matches, setMatches]         = useState<InternshipMatchResult[]>([]);
  const [query, setQuery]             = useState("");
  const [filters, setFilters]         = useState<Filters>(EMPTY_FILTERS);
  const [showFilters, setShowFilters] = useState(false);
  const [isPending, startTransition]  = useTransition();
  const [loading, setLoading]         = useState(true);
  const [searched, setSearched]       = useState(false);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const doSearch = useCallback(async (q: string, f: Filters, isInitial = false) => {
    setLoading(true);
    if (!isInitial) setSearched(true);
    try {
      const res  = await fetch(buildUrl(apiBase, q, f), {
        headers: { "X-User-Id": userId, "X-User-Email": userEmail },
      });
      const data = await res.json();
      setMatches(data.matches ?? []);
    } finally {
      setLoading(false);
    }
  }, [apiBase, userId, userEmail]);

  const didFetchRef = React.useRef(false);
  useEffect(() => {
    if (didFetchRef.current) return;
    didFetchRef.current = true;
    let cancelled = false;
    setLoading(true);
    fetch(buildUrl(apiBase, "", EMPTY_FILTERS), {
      headers: { "X-User-Id": userId, "X-User-Email": userEmail },
    })
      .then((r) => r.json())
      .then((data) => { if (!cancelled) setMatches(data.matches ?? []); })
      .catch(() => {  })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [userId]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    doSearch(query, filters);
  }

  function handleFilterChange(key: keyof Filters, value: string) {
    const next = { ...filters, [key]: value };
    setFilters(next);
    startTransition(() => doSearch(query, next));
  }

  function removeFilter(key: keyof Filters) { handleFilterChange(key, ""); }

  function clearAll() {
    setFilters(EMPTY_FILTERS);
    setQuery("");
    startTransition(() => doSearch("", EMPTY_FILTERS));
  }

  const activePills = [
    filters.work_type    ? { key: "work_type"    as keyof Filters, label: filters.work_type === "remote" ? "Remote" : filters.work_type === "hybrid" ? "Hybrid" : "On-site" } : null,
    filters.duration_max ? { key: "duration_max" as keyof Filters, label: `\u2264 ${filters.duration_max}m` } : null,
    filters.stipend_min  ? { key: "stipend_min"  as keyof Filters, label: `\u20b9${Number(filters.stipend_min).toLocaleString()}+/mo` } : null,
    filters.location     ? { key: "location"     as keyof Filters, label: filters.location } : null,
    filters.source       ? { key: "source"       as keyof Filters, label: platformMeta(filters.source).label } : null,
  ].filter((x): x is { key: keyof Filters; label: string } => x !== null);

  const isBusy = loading || isPending;

  return (
    <div className="flex flex-col gap-5 transition-all duration-500">
      <div className="transition-all duration-500">
        <h1 className="font-syne text-xl font-bold">Internship Finder</h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Matched from Internshala, Indeed, Naukri, Wellfound &amp; Unstop &middot; ranked by your profile fit
        </p>
      </div>
      <form onSubmit={handleSearch} className="flex gap-2 transition-all duration-500">
        <div className="relative flex-1">
          <Search size={14} className="absolute transition-all duration-500 left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search role, skill, company or location&hellip;"
            className="w-full pl-9 pr-4 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] focus:outline-none focus:border-[#0C65D2]/50 transition-all duration-500"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowFilters(v => !v)}
          className={`px-3 py-2.5 border font-mono text-[12px] flex items-center gap-1.5 transition-colors ${showFilters || activePills.length > 0 ? "border-[#0C65D2] text-[#0C65D2] bg-[#0C65D2]/5" : "border-black/10 dark:border-white/8 text-gray-500"}`}
        >
          <SlidersHorizontal size={13} /> Filters
          {activePills.length > 0 && (
            <span className="w-4 h-4 rounded-full bg-[#0C65D2] text-white text-[9px] flex items-center justify-center">{activePills.length}</span>
          )}
          {showFilters ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
        <button type="submit" disabled={isBusy} className="px-5 py-2.5 bg-[#0C65D2] text-white font-mono text-[12px] flex items-center gap-2 disabled:opacity-60">
          {isBusy ? <Loader2 size={13} className="animate-spin" /> : <Search size={13} />} Search
        </button>
      </form>
      {showFilters && (
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 grid grid-cols-2 md:grid-cols-5 gap-4 transition-all duration-500">

          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">Work type</p>
            <div className="flex flex-col gap-1">
              {([{v:"remote",I:Wifi,l:"Remote / WFH"},{v:"hybrid",I:GitMerge,l:"Hybrid"},{v:"onsite",I:Building2,l:"On-site"}] as const).map(({v,I,l}) => (
                <button key={v} type="button" onClick={() => handleFilterChange("work_type", filters.work_type===v?"":v)}
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.work_type===v?"border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]":"border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}>
                  <I size={11} /> {l}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5 transition-all duration-500">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">Max duration</p>
            <div className="flex flex-col gap-1">
              {[{v:"1",l:"Up to 1 month"},{v:"2",l:"Up to 2 months"},{v:"3",l:"Up to 3 months"},{v:"6",l:"Up to 6 months"}].map(({v,l}) => (
                <button key={v} type="button" onClick={() => handleFilterChange("duration_max", filters.duration_max===v?"":v)}
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.duration_max===v?"border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]":"border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}>
                  <Clock size={11} /> {l}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5 transition-all duration-500">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">Min stipend /mo</p>
            <div className="flex flex-col gap-1">
              {[{v:"0",l:"Unpaid / any"},{v:"5000",l:"\u20b95,000+"},{v:"10000",l:"\u20b910,000+"},{v:"15000",l:"\u20b915,000+"}].map(({v,l}) => (
                <button key={v} type="button" onClick={() => handleFilterChange("stipend_min", filters.stipend_min===v?"":v)}
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.stipend_min===v?"border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]":"border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}>
                  <Banknote size={11} /> {l}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5 transition-all duration-500">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">City</p>
            <div className="relative">
              <MapPin size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
              <input value={filters.location} onChange={(e) => handleFilterChange("location", e.target.value)} placeholder="e.g. Mumbai"
                className="w-full pl-8 pr-3 py-1.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[11px] focus:outline-none focus:border-[#0C65D2]/50" />
            </div>
            <div className="flex flex-wrap gap-1 mt-1">
              {["Mumbai","Bangalore","Delhi","Remote"].map(city => (
                <button key={city} type="button" onClick={() => handleFilterChange("location", filters.location===city?"":city)}
                  className={`px-2 py-0.5 border font-mono text-[10px] transition-colors ${filters.location===city?"border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]":"border-black/10 dark:border-white/8 text-gray-400 hover:border-[#0C65D2]/40"}`}>
                  {city}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5 transition-all duration-500">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">Platform</p>
            <div className="flex flex-col gap-1">
              {Object.entries(PLATFORMS).map(([val, { label, color }]) => (
                <button key={val} type="button" onClick={() => handleFilterChange("source", filters.source===val?"":val)}
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.source===val?`border-current bg-current/8 ${color}`:"border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}>
                  <span className={`w-1.5 h-1.5 rounded-full bg-current ${color}`} /> {label}
                </button>
              ))}
            </div>
          </div>

        </div>
      )}

      {activePills.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 transition-all duration-500">
          <span className="font-mono text-[11px] text-gray-400">Active:</span>
          {activePills.map(p => <FilterPill key={p.key} label={p.label} onRemove={() => removeFilter(p.key)} />)}
          <button type="button" onClick={clearAll} className="font-mono text-[11px] text-gray-400 hover:text-red-500 ml-1">Clear all</button>
        </div>
      )}

      {!searched && matches.length > 0 && (
        <div className="flex items-center gap-2 px-3 py-2 border border-[#0C65D2]/20 bg-[#0C65D2]/5 font-mono text-[11px] text-[#0C65D2] transition-all duration-500">
          <User size={12} /> Showing recommendations personalised to your profile. Use search or filters to refine.
        </div>
      )}

      {isBusy ? (
        <div className="flex items-center justify-center py-16 gap-3 font-mono text-[12px] text-gray-400 transition-all duration-500">
          <Loader2 size={16} className="animate-spin text-[#0C65D2]" /> Finding internships&hellip;
        </div>
      ) : matches.length === 0 ? (
        <div className="flex flex-col items-center py-16 gap-2 text-center transition-all duration-500">
          <Briefcase size={32} className="text-gray-300 dark:text-gray-600" />
          <p className="font-mono text-[13px] text-gray-500">No internships found</p>
          <p className="font-mono text-[11px] text-gray-400">
            {activePills.length > 0 ? "Try removing some filters." : "Complete your profile for personalised matches."}
          </p>
          {activePills.length > 0 && (
            <button type="button" onClick={clearAll} className="mt-2 px-4 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-500 hover:text-[#0C65D2]">Clear filters</button>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-3 transition-all duration-500">
          <p className="font-mono text-[11px] text-gray-400">
            {matches.length} result{matches.length !== 1 ? "s" : ""}
            {searched && query ? ` for "${query}"` : ""}
          </p>
          {matches.map(m => (
            <InternshipCard
              key={m.opportunity.id}
              match={m}
              onSave={() => saveInternship(userId, m.opportunity.id, userEmail)}
              userId={userId}
              userEmail={userEmail}
            />
          ))}
        </div>
      )}

    </div>
  );
}


function InternshipCard({ match, onSave, userId, userEmail }: {
  match: InternshipMatchResult;
  onSave: () => void;
  userId: string;
  userEmail: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const [saved, setSaved]       = useState(false);
  const { opportunity: o, match_score, eligibility, reasons } = match;

  const company  = o.raw_data?.company  ?? null;
  const location = o.raw_data?.location ?? null;
  const duration = o.raw_data?.duration ?? null;
  const skills   = (o.eligibility_rules?.skills as string[] | undefined) ?? [];
  const isRemote = !!(location?.toLowerCase().includes("work from home") || location?.toLowerCase().includes("remote"));

  const stipend = o.amount_min && o.amount_max
    ? `\u20b9${o.amount_min.toLocaleString()} \u2013 \u20b9${o.amount_max.toLocaleString()}/mo`
    : o.amount_max ? `Up to \u20b9${o.amount_max.toLocaleString()}/mo`
    : o.amount_min ? `\u20b9${o.amount_min.toLocaleString()}+/mo`
    : null;

  return (
    <div className="border border-black/10 dark:border-white/8 bg-white dark:bg-[#0F1117] flex flex-col transition-all duration-500">
      <div className="flex items-start justify-between gap-4 p-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 bg-[#0C65D2]/8 border border-[#0C65D2]/15 flex items-center justify-center text-[#0C65D2] shrink-0 mt-0.5 transition-all duration-500">
            <Briefcase size={17} />
          </div>
          <div className="min-w-0 flex flex-col gap-0.5">
            <p className="font-mono text-[14px] font-bold text-gray-900 dark:text-[#F0F4FF] leading-snug">{o.title}</p>
            <div className="flex items-center gap-2 flex-wrap mt-0.5">
              {company && <p className="font-mono text-[11px] text-gray-700 dark:text-gray-300">{company}</p>}
              <SourceBadge source={o.source} />
            </div>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1">
              {location && (
                <span className="flex items-center gap-1 font-mono text-[11px] text-gray-400">
                  {isRemote ? <Wifi size={10} className="text-green-500" /> : <MapPin size={10} />}
                  {isRemote ? <span className="text-green-600 dark:text-green-400">Remote</span> : location}
                </span>
              )}
              {duration && <span className="flex items-center gap-1 font-mono text-[11px] text-gray-400"><Clock size={10} /> {duration}</span>}
              {stipend  && <span className="flex items-center gap-1 font-mono text-[11px] text-gray-400"><Banknote size={10} /> {stipend}</span>}
              {o.deadline && <span className="font-mono text-[11px] text-amber-500">Deadline {String(o.deadline)}</span>}
            </div>
          </div>
        </div>
        <ScoreRing score={match_score} />
      </div>

      <div className="px-4 pb-2 flex items-center gap-2 border-t border-black/5 dark:border-white/5 pt-2 transition-all duration-500">
        {eligibility.eligible
          ? <span className="flex items-center gap-1 font-mono text-[11px] text-green-600"><CheckCircle size={12} /> Eligible</span>
          : <span className="flex items-center gap-1 font-mono text-[11px] text-red-400"><XCircle size={12} /> May not qualify</span>}
        <div className="flex-1 h-1 bg-gray-100 dark:bg-white/6 overflow-hidden">
          <div className={`h-full ${match_score>=70?"bg-green-500":match_score>=45?"bg-[#0C65D2]":"bg-gray-300"}`}
            style={{ width: `${Math.min(match_score, 100)}%` }} />
        </div>
        <button type="button" onClick={() => setExpanded(v => !v)}
          className="font-mono text-[10px] text-gray-400 hover:text-[#0C65D2] flex items-center gap-0.5">
          {expanded ? "Less" : "Why this match?"}
          {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
        </button>
      </div>

      {expanded && (
        <div className="px-4 pb-4 flex flex-col gap-3 border-t border-black/5 dark:border-white/5 pt-3 transition-all duration-500">
          {reasons.length > 0 && (
            <div>
              <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide mb-1">Match breakdown</p>
              <ul className="flex flex-col gap-0.5">
                {reasons.map((r, i) => <li key={i} className="font-mono text-[11px] text-gray-500 dark:text-[#6B7280]">{r}</li>)}
              </ul>
            </div>
          )}
          {o.description && (
            <p className="font-mono text-[12px] text-gray-600 dark:text-[#a8c7fa] leading-relaxed">{o.description}</p>
          )}
          {skills.length > 0 && (
            <div>
              <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide mb-1">Skills required</p>
              <div className="flex flex-wrap gap-1.5">
                {skills.map(s => (
                  <span key={s} className="px-2 py-0.5 border border-black/10 dark:border-white/8 font-mono text-[10px] text-gray-500 bg-gray-50 dark:bg-[#161822]">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2 px-4 py-3 border-t border-black/5 dark:border-white/5 transition-all duration-500">
        <button
          type="button"
          onClick={() => { if (!saved) { setSaved(true); onSave(); } }}
          disabled={saved}
          className={`flex items-center gap-1.5 px-3 py-1.5 border font-mono text-[11px] transition-colors ${saved ? "border-green-500/30 text-green-600 bg-green-500/5 cursor-default" : "border-[#0C65D2]/30 text-[#0C65D2] hover:bg-[#0C65D2]/5"}`}
        >
          <BookmarkPlus size={12} /> {saved ? "Saved" : "Save & track"}
        </button>
        {o.application_url && o.application_url !== "#" && (
          <a href={o.application_url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-500 hover:text-[#0C65D2]">
            <ExternalLink size={12} /> Apply now
          </a>
        )}
        <FeedbackWidget opportunityId={o.id} userId={userId} userEmail={userEmail} />
      </div>

    </div>
  );
}
