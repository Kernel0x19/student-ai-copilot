"use client";

import React, { useState, useCallback, useTransition, useEffect } from "react";
import {
  Code2,
  Search,
  ExternalLink,
  MapPin,
  Calendar,
  Trophy,
  Users,
  Globe,
  Building2,
  GitMerge,
  SlidersHorizontal,
  X,
  ChevronDown,
  ChevronUp,
  Loader2,
  Tag,
} from "lucide-react";
import type { HackathonItem } from "@/app/lib/api";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Filters {
  mode: string;
  source: string;
  theme: string;
  prize_min: string;
  location: string;
  deadline_days: string;
}

const EMPTY_FILTERS: Filters = {
  mode: "",
  source: "",
  theme: "",
  prize_min: "",
  location: "",
  deadline_days: "",
};

interface Props {
  userId: string;
  userEmail: string;
}

// ─── Platform metadata ────────────────────────────────────────────────────────

const PLATFORMS: Record<string, { label: string; color: string; bg: string }> =
  {
    unstop: {
      label: "Unstop",
      color: "text-[#8b5cf6]",
      bg: "bg-[#8b5cf6]/8 border-[#8b5cf6]/20",
    },
    devfolio: {
      label: "Devfolio",
      color: "text-[#3b82f6]",
      bg: "bg-[#3b82f6]/8 border-[#3b82f6]/20",
    },
    mlh: {
      label: "MLH",
      color: "text-[#ef4444]",
      bg: "bg-[#ef4444]/8 border-[#ef4444]/20",
    },
    lablab: {
      label: "lablab.ai",
      color: "text-[#10b981]",
      bg: "bg-[#10b981]/8 border-[#10b981]/20",
    },
    devpost: {
      label: "Devpost",
      color: "text-[#0ea5e9]",
      bg: "bg-[#0ea5e9]/8 border-[#0ea5e9]/20",
    },
    hackerearth: {
      label: "HackerEarth",
      color: "text-[#f97316]",
      bg: "bg-[#f97316]/8 border-[#f97316]/20",
    },
    hackindia: {
      label: "HackIndia",
      color: "text-[#ec4899]",
      bg: "bg-[#ec4899]/8 border-[#ec4899]/20",
    },
    hack2skill: {
      label: "Hack2Skill",
      color: "text-[#a855f7]",
      bg: "bg-[#a855f7]/8 border-[#a855f7]/20",
    },
  };

function platformMeta(src: string) {
  return (
    PLATFORMS[src.toLowerCase()] ?? {
      label: src.charAt(0).toUpperCase() + src.slice(1),
      color: "text-gray-500",
      bg: "bg-gray-100/50 border-gray-200 dark:bg-white/5 dark:border-white/10",
    }
  );
}

// ─── Small helpers ────────────────────────────────────────────────────────────

function SourceBadge({ source }: { source: string }) {
  const { label, color, bg } = platformMeta(source);
  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 border font-mono text-[9px] font-bold tracking-wide ${color} ${bg}`}
    >
      {label}
    </span>
  );
}

function ModeBadge({ mode }: { mode: string }) {
  const cfg =
    mode === "online"
      ? {
          icon: <Globe size={9} />,
          label: "Online",
          cls: "text-green-600 bg-green-500/8 border-green-500/20",
        }
      : mode === "hybrid"
        ? {
            icon: <GitMerge size={9} />,
            label: "Hybrid",
            cls: "text-blue-500 bg-blue-500/8 border-blue-500/20",
          }
        : {
            icon: <Building2 size={9} />,
            label: "In-Person",
            cls: "text-amber-600 bg-amber-500/8 border-amber-500/20",
          };
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 border font-mono text-[9px] font-bold ${cfg.cls}`}
    >
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

function FilterPill({
  label,
  onRemove,
}: {
  label: string;
  onRemove: () => void;
}) {
  return (
    <span className="flex items-center gap-1 px-2 py-0.5 bg-[#0C65D2]/10 border border-[#0C65D2]/20 font-mono text-[11px] text-[#0C65D2]">
      {label}
      <button type="button" onClick={onRemove} className="hover:text-red-500">
        <X size={10} />
      </button>
    </span>
  );
}

// ─── URL builder ──────────────────────────────────────────────────────────────

function buildUrl(
  base: string,
  query: string,
  filters: Filters,
  limit = 60,
): string {
  const p = new URLSearchParams();
  if (query.trim()) p.set("query", query.trim());
  if (filters.mode) p.set("mode", filters.mode);
  if (filters.source) p.set("source", filters.source);
  if (filters.theme.trim()) p.set("theme", filters.theme.trim());
  if (filters.prize_min) p.set("prize_min", filters.prize_min);
  if (filters.location.trim()) p.set("location", filters.location.trim());
  if (filters.deadline_days) p.set("deadline_days", filters.deadline_days);
  p.set("limit", String(limit));
  return `${base}/api/v1/hackathons?${p}`;
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function HackathonsClient({ userId, userEmail }: Props) {
  const [items, setItems] = useState<HackathonItem[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [showFilters, setShowFilters] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [loading, setLoading] = useState(true);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const doFetch = useCallback(
    async (q: string, f: Filters) => {
      setLoading(true);
      try {
        const res = await fetch(buildUrl(apiBase, q, f), {
          headers: { "X-User-Id": userId, "X-User-Email": userEmail },
        });
        if (!res.ok) throw new Error(`${res.status}`);
        const data = await res.json();
        setItems(data.items ?? []);
        setTotal(data.total ?? 0);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    },
    [apiBase, userId, userEmail],
  );

  const didFetchRef = React.useRef(false);
  useEffect(() => {
    if (didFetchRef.current) return;
    didFetchRef.current = true;
    doFetch("", EMPTY_FILTERS);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    doFetch(query, filters);
  }

  function handleFilterChange(key: keyof Filters, value: string) {
    const next = { ...filters, [key]: value };
    setFilters(next);
    startTransition(() => doFetch(query, next));
  }

  function removeFilter(key: keyof Filters) {
    handleFilterChange(key, "");
  }

  function clearAll() {
    setFilters(EMPTY_FILTERS);
    setQuery("");
    startTransition(() => doFetch("", EMPTY_FILTERS));
  }

  const activePills = [
    filters.mode
      ? {
          key: "mode" as keyof Filters,
          label:
            filters.mode === "online"
              ? "Online"
              : filters.mode === "hybrid"
                ? "Hybrid"
                : "In-Person",
        }
      : null,
    filters.source
      ? {
          key: "source" as keyof Filters,
          label: platformMeta(filters.source).label,
        }
      : null,
    filters.theme
      ? { key: "theme" as keyof Filters, label: filters.theme }
      : null,
    filters.prize_min
      ? {
          key: "prize_min" as keyof Filters,
          label: `₹${Number(filters.prize_min).toLocaleString()}+ prize`,
        }
      : null,
    filters.location
      ? { key: "location" as keyof Filters, label: filters.location }
      : null,
    filters.deadline_days
      ? {
          key: "deadline_days" as keyof Filters,
          label: `Deadline ≤ ${filters.deadline_days}d`,
        }
      : null,
  ].filter((x): x is { key: keyof Filters; label: string } => x !== null);

  const isBusy = loading || isPending;

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div>
        <h1 className="font-syne text-xl font-bold">Hackathon Finder</h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Live from Unstop, Devfolio, MLH &amp; lablab.ai &middot; plus Devpost,
          HackerEarth, HackIndia &amp; Hack2Skill
        </p>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search hackathon, organizer, theme&hellip;"
            className="w-full pl-9 pr-4 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] focus:outline-none focus:border-[#0C65D2]/50"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowFilters((v) => !v)}
          className={`px-3 py-2.5 border font-mono text-[12px] flex items-center gap-1.5 transition-colors ${showFilters || activePills.length > 0 ? "border-[#0C65D2] text-[#0C65D2] bg-[#0C65D2]/5" : "border-black/10 dark:border-white/8 text-gray-500"}`}
        >
          <SlidersHorizontal size={13} /> Filters
          {activePills.length > 0 && (
            <span className="w-4 h-4 rounded-full bg-[#0C65D2] text-white text-[9px] flex items-center justify-center">
              {activePills.length}
            </span>
          )}
          {showFilters ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
        <button
          type="submit"
          disabled={isBusy}
          className="px-5 py-2.5 bg-[#0C65D2] text-white font-mono text-[12px] flex items-center gap-2 disabled:opacity-60"
        >
          {isBusy ? (
            <Loader2 size={13} className="animate-spin" />
          ) : (
            <Search size={13} />
          )}{" "}
          Search
        </button>
      </form>

      {/* Filter panel */}
      {showFilters && (
        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {/* Mode */}
          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
              Mode
            </p>
            <div className="flex flex-col gap-1">
              {(
                [
                  { v: "online", l: "Online" },
                  { v: "offline", l: "In-Person" },
                  { v: "hybrid", l: "Hybrid" },
                ] as const
              ).map(({ v, l }) => (
                <button
                  key={v}
                  type="button"
                  onClick={() =>
                    handleFilterChange("mode", filters.mode === v ? "" : v)
                  }
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.mode === v ? "border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]" : "border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}
                >
                  {v === "online" ? (
                    <Globe size={11} />
                  ) : v === "hybrid" ? (
                    <GitMerge size={11} />
                  ) : (
                    <Building2 size={11} />
                  )}{" "}
                  {l}
                </button>
              ))}
            </div>
          </div>

          {/* Platform */}
          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
              Platform
            </p>
            <div className="flex flex-col gap-1 overflow-y-auto max-h-40">
              {Object.entries(PLATFORMS).map(([val, { label, color }]) => (
                <button
                  key={val}
                  type="button"
                  onClick={() =>
                    handleFilterChange(
                      "source",
                      filters.source === val ? "" : val,
                    )
                  }
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.source === val ? `border-current bg-current/8 ${color}` : "border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full bg-current ${color}`}
                  />{" "}
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Min prize */}
          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
              Min Prize Pool
            </p>
            <div className="flex flex-col gap-1">
              {[
                { v: "", l: "Any" },
                { v: "1", l: "Has prize" },
                { v: "100000", l: "₹1L+" },
                { v: "500000", l: "₹5L+" },
                { v: "1000000", l: "₹10L+" },
              ].map(({ v, l }) => (
                <button
                  key={l}
                  type="button"
                  onClick={() =>
                    handleFilterChange(
                      "prize_min",
                      filters.prize_min === v ? "" : v,
                    )
                  }
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.prize_min === v ? "border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]" : "border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}
                >
                  <Trophy size={11} /> {l}
                </button>
              ))}
            </div>
          </div>

          {/* Deadline */}
          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
              Register By
            </p>
            <div className="flex flex-col gap-1">
              {[
                { v: "7", l: "This week" },
                { v: "14", l: "2 weeks" },
                { v: "30", l: "1 month" },
                { v: "60", l: "2 months" },
              ].map(({ v, l }) => (
                <button
                  key={v}
                  type="button"
                  onClick={() =>
                    handleFilterChange(
                      "deadline_days",
                      filters.deadline_days === v ? "" : v,
                    )
                  }
                  className={`flex items-center gap-2 px-2.5 py-1.5 border font-mono text-[11px] transition-colors ${filters.deadline_days === v ? "border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]" : "border-black/10 dark:border-white/8 text-gray-500 hover:border-[#0C65D2]/40"}`}
                >
                  <Calendar size={11} /> {l}
                </button>
              ))}
            </div>
          </div>

          {/* Theme search */}
          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
              Theme
            </p>
            <div className="relative">
              <Tag
                size={12}
                className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              />
              <input
                value={filters.theme}
                onChange={(e) => handleFilterChange("theme", e.target.value)}
                placeholder="e.g. AI, Web3"
                className="w-full pl-8 pr-3 py-1.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[11px] focus:outline-none focus:border-[#0C65D2]/50"
              />
            </div>
            <div className="flex flex-wrap gap-1 mt-1">
              {["AI", "Web3", "HealthTech", "FinTech", "IoT"].map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() =>
                    handleFilterChange("theme", filters.theme === t ? "" : t)
                  }
                  className={`px-2 py-0.5 border font-mono text-[10px] transition-colors ${filters.theme === t ? "border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]" : "border-black/10 dark:border-white/8 text-gray-400 hover:border-[#0C65D2]/40"}`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Location */}
          <div className="flex flex-col gap-1.5">
            <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
              Location
            </p>
            <div className="relative">
              <MapPin
                size={12}
                className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              />
              <input
                value={filters.location}
                onChange={(e) => handleFilterChange("location", e.target.value)}
                placeholder="e.g. Bengaluru"
                className="w-full pl-8 pr-3 py-1.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[11px] focus:outline-none focus:border-[#0C65D2]/50"
              />
            </div>
            <div className="flex flex-wrap gap-1 mt-1">
              {["Online", "Bengaluru", "Delhi", "Mumbai"].map((city) => (
                <button
                  key={city}
                  type="button"
                  onClick={() =>
                    handleFilterChange(
                      "location",
                      filters.location === city ? "" : city,
                    )
                  }
                  className={`px-2 py-0.5 border font-mono text-[10px] transition-colors ${filters.location === city ? "border-[#0C65D2] bg-[#0C65D2]/8 text-[#0C65D2]" : "border-black/10 dark:border-white/8 text-gray-400 hover:border-[#0C65D2]/40"}`}
                >
                  {city}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Active filter pills */}
      {activePills.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[11px] text-gray-400">Active:</span>
          {activePills.map((p) => (
            <FilterPill
              key={p.key}
              label={p.label}
              onRemove={() => removeFilter(p.key)}
            />
          ))}
          <button
            type="button"
            onClick={clearAll}
            className="font-mono text-[11px] text-gray-400 hover:text-red-500 ml-1"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Results */}
      {isBusy ? (
        <div className="flex items-center justify-center py-16 gap-3 font-mono text-[12px] text-gray-400">
          <Loader2 size={16} className="animate-spin text-[#0C65D2]" /> Finding
          hackathons&hellip;
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center py-16 gap-2 text-center">
          <Code2 size={32} className="text-gray-300 dark:text-gray-600" />
          <p className="font-mono text-[13px] text-gray-500">
            No hackathons found
          </p>
          <p className="font-mono text-[11px] text-gray-400">
            {activePills.length > 0
              ? "Try removing some filters."
              : "Data is loading — check back shortly."}
          </p>
          {activePills.length > 0 && (
            <button
              type="button"
              onClick={clearAll}
              className="mt-2 px-4 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-500 hover:text-[#0C65D2]"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <p className="font-mono text-[11px] text-gray-400">
            {total} hackathon{total !== 1 ? "s" : ""}
            {query ? ` for "${query}"` : ""}
          </p>
          {items.map((item) => (
            <HackathonCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Card ─────────────────────────────────────────────────────────────────────

function HackathonCard({ item }: { item: HackathonItem }) {
  const [expanded, setExpanded] = useState(false);

  const hasPrize = item.prize_pool > 0;
  const prizeLabel = hasPrize
    ? `₹${item.prize_pool.toLocaleString("en-IN")}`
    : "No cash prize";

  function fmtDate(d: string | null | undefined): string {
    if (!d) return "—";
    try {
      return new Date(d).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch {
      return d;
    }
  }

  const deadlineDate = item.registration_deadline
    ? new Date(item.registration_deadline)
    : null;

  // Compute days left once — avoids calling Date.now() inside JSX (purity lint)
  const nowMs = deadlineDate
    ? deadlineDate.getTime() - new Date().getTime()
    : null;
  const daysLeft = nowMs !== null ? Math.ceil(nowMs / 86_400_000) : null;

  const deadlineColor =
    daysLeft === null
      ? "text-gray-400"
      : daysLeft <= 7
        ? "text-red-500"
        : daysLeft <= 21
          ? "text-amber-500"
          : "text-gray-500";

  return (
    <div className="border border-black/10 dark:border-white/8 bg-white dark:bg-[#0F1117] flex flex-col">
      {/* Top row */}
      <div className="flex items-start justify-between gap-4 p-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 bg-[#0C65D2]/8 border border-[#0C65D2]/15 flex items-center justify-center text-[#0C65D2] shrink-0 mt-0.5">
            <Code2 size={17} />
          </div>
          <div className="min-w-0 flex flex-col gap-0.5">
            <p className="font-mono text-[14px] font-bold text-gray-900 dark:text-[#F0F4FF] leading-snug">
              {item.title}
            </p>
            <div className="flex items-center gap-2 flex-wrap mt-0.5">
              {item.organizer && (
                <p className="font-mono text-[11px] text-gray-700 dark:text-gray-300">
                  {item.organizer}
                </p>
              )}
              <SourceBadge source={item.source} />
              <ModeBadge mode={item.mode} />
            </div>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1">
              {item.location && (
                <span className="flex items-center gap-1 font-mono text-[11px] text-gray-400">
                  <MapPin size={10} /> {item.location}
                </span>
              )}
              {item.team_size && (
                <span className="flex items-center gap-1 font-mono text-[11px] text-gray-400">
                  <Users size={10} /> {item.team_size}
                </span>
              )}
              <span
                className={`flex items-center gap-1 font-mono text-[11px] ${hasPrize ? "text-amber-600 dark:text-amber-400" : "text-gray-400"}`}
              >
                <Trophy size={10} /> {prizeLabel}
              </span>
            </div>
          </div>
        </div>

        {/* Deadline chip */}
        <div className="shrink-0 text-right">
          {item.registration_deadline ? (
            <>
              <p
                className={`font-mono text-[11px] font-semibold ${deadlineColor}`}
              >
                {daysLeft !== null && daysLeft >= 0
                  ? `${daysLeft}d left`
                  : "Closed"}
              </p>
              <p className="font-mono text-[10px] text-gray-400">
                reg deadline
              </p>
            </>
          ) : (
            <p className="font-mono text-[11px] text-gray-400">No deadline</p>
          )}
        </div>
      </div>

      {/* Date row */}
      <div className="px-4 pb-2 flex flex-wrap items-center gap-4 border-t border-black/5 dark:border-white/5 pt-2">
        <span className="flex items-center gap-1.5 font-mono text-[11px] text-gray-400">
          <Calendar size={10} />
          {item.registration_deadline ? (
            <>
              <span className="text-gray-600 dark:text-gray-300">
                Reg closes
              </span>{" "}
              {fmtDate(item.registration_deadline)}
            </>
          ) : (
            "Registration open"
          )}
        </span>
        {item.start_date && (
          <span className="flex items-center gap-1.5 font-mono text-[11px] text-gray-400">
            <Calendar size={10} />
            <span className="text-gray-600 dark:text-gray-300">
              Starts
            </span>{" "}
            {fmtDate(item.start_date)}
            {item.end_date && item.end_date !== item.start_date && (
              <> — {fmtDate(item.end_date)}</>
            )}
          </span>
        )}
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="ml-auto font-mono text-[10px] text-gray-400 hover:text-[#0C65D2] flex items-center gap-0.5"
        >
          {expanded ? "Less" : "Details"}
          {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
        </button>
      </div>

      {/* Expanded: themes */}
      {expanded && item.themes && item.themes.length > 0 && (
        <div className="px-4 pb-3 flex flex-col gap-2 border-t border-black/5 dark:border-white/5 pt-3">
          <p className="font-mono text-[10px] text-gray-400 uppercase tracking-wide">
            Themes
          </p>
          <div className="flex flex-wrap gap-1.5">
            {item.themes.map((t) => (
              <span
                key={t}
                className="px-2 py-0.5 border border-black/10 dark:border-white/8 font-mono text-[10px] text-gray-500 bg-gray-50 dark:bg-[#161822]"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 px-4 py-3 border-t border-black/5 dark:border-white/5">
        {item.apply_link ? (
          <a
            href={item.apply_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-1.5 bg-[#0C65D2] text-white font-mono text-[11px] hover:bg-[#0b58bc] transition-colors"
          >
            <ExternalLink size={11} /> Register Now
          </a>
        ) : (
          <span className="font-mono text-[11px] text-gray-400 italic">
            No link available
          </span>
        )}
      </div>
    </div>
  );
}
