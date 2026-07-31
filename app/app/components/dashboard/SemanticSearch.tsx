"use client";

import { useState, useCallback } from "react";
import {
  Search,
  Sparkles,
  Calendar,
  DollarSign,
  ExternalLink,
  Loader2,
  Filter,
} from "lucide-react";
import type { SemanticSearchResult } from "@/app/lib/api";
import { searchOpportunitiesSemantic } from "@/app/lib/api";

const CATEGORIES = ["All", "scholarship", "internship", "placement", "hackathon"];

export default function SemanticSearch() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [results, setResults] = useState<SemanticSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!query.trim()) return;
      setLoading(true);
      setSearched(true);
      setError("");
      try {
        const data = await searchOpportunitiesSemantic(
          query.trim(),
          category === "All" ? undefined : category
        );
        setResults(data.matches);
      } catch (err) {
        setResults([]);
        setError(err instanceof Error ? err.message : "Semantic search is temporarily unavailable.");
      } finally {
        setLoading(false);
      }
    },
    [query, category]
  );

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="font-syne text-xl font-bold flex items-center gap-2">
          <Sparkles size={20} className="text-[#0C65D2]" />
          Semantic Search
        </h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Search opportunities using natural language — powered by vector
          similarity
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="flex flex-col gap-3">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search
              size={15}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            />
            <input
              id="semantic-search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. 'engineering scholarship for girls in Maharashtra'"
              className="w-full pl-9 pr-4 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] placeholder:text-gray-300 dark:placeholder:text-[#3B3F51] transition-all focus:border-[#0C65D2]/40 focus:ring-1 focus:ring-[#0C65D2]/20 outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-2.5 bg-[#0C65D2] hover:bg-[#0B5ABD] disabled:opacity-50 text-white font-mono text-[12px] flex items-center gap-2 transition-all"
          >
            {loading ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Search size={14} />
            )}
            Search
          </button>
        </div>

        {/* Category Filters */}
        <div className="flex items-center gap-2">
          <Filter size={13} className="text-gray-400" />
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setCategory(cat)}
              className={`px-3 py-1 font-mono text-[11px] border transition-all ${
                category === cat
                  ? "border-[#0C65D2]/40 bg-[#0C65D2]/8 text-[#0C65D2]"
                  : "border-black/10 dark:border-white/8 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              }`}
            >
              {cat === "All" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </form>

      {/* Results */}
      {loading && (
        <div className="flex items-center justify-center py-16 gap-3">
          <Loader2 size={20} className="animate-spin text-[#0C65D2]" />
          <span className="font-mono text-[12px] text-gray-400">
            Searching vector space…
          </span>
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="flex flex-col items-center py-16 gap-3 border border-black/10 dark:border-white/8">
          <Search size={24} className="text-gray-300" />
          <p className="font-mono text-[12px] text-gray-400">
            {error || "No matching opportunities found. Try a different query."}
          </p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="flex flex-col gap-3">
          <p className="font-mono text-[11px] text-gray-400">
            {results.length} result{results.length !== 1 ? "s" : ""} found
          </p>
          {results.map((r, i) => (
            <SearchResultCard key={r.opportunity_id} result={r} rank={i + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function SearchResultCard({
  result,
  rank,
}: {
  result: SemanticSearchResult;
  rank: number;
}) {
  const relevance = Math.round(result.relevance_score * 100);

  return (
    <div
      className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-3 transition-all hover:border-[#0C65D2]/20"
      style={{ animationDelay: `${rank * 60}ms` }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-8 h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0 font-mono text-[12px] font-bold">
            {rank}
          </div>
          <div className="min-w-0">
            <p className="font-mono text-[14px] font-bold text-gray-900 dark:text-[#F0F4FF]">
              {result.title}
            </p>
            <p className="font-mono text-[11px] text-gray-400 mt-0.5 flex items-center gap-2">
              <span className="px-1.5 py-0.5 border border-black/8 dark:border-white/8 text-[10px] uppercase">
                {result.category}
              </span>
              {result.deadline && (
                <span className="flex items-center gap-1">
                  <Calendar size={10} />
                  {result.deadline}
                </span>
              )}
              {result.amount && (
                <span className="flex items-center gap-1">
                  <DollarSign size={10} />₹{result.amount.toLocaleString()}
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Relevance Score */}
        <div className="text-right shrink-0">
          <p className="font-mono text-lg font-bold text-[#0C65D2]">
            {relevance}%
          </p>
          <p className="font-mono text-[10px] text-gray-400">relevance</p>
        </div>
      </div>

      {result.description && (
        <p className="font-mono text-[12px] text-gray-600 dark:text-[#a8c7fa] leading-relaxed line-clamp-2">
          {result.description}
        </p>
      )}

      {result.source_url && (
        <a
          href={result.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-500 hover:text-[#0C65D2] w-fit transition-all"
        >
          <ExternalLink size={12} /> View Details
        </a>
      )}
    </div>
  );
}
