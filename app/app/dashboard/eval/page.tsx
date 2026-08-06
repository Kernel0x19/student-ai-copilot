"use client";

import { useEffect, useState } from "react";
import {
  ShieldCheck,
  AlertCircle,
  RefreshCcw,
  Clock,
  FlaskConical,
  Target,
  Layers,
  BookOpen,
  GraduationCap,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface EvalResults {
  last_updated: string;
  agent: string;
  metrics: {
    faithfulness: number | null;
    answer_relevancy: number | null;
    context_precision: number | null;
    context_recall: number | null;
  };
  sample_size: number;
  source_file: string;
}

const METRIC_CONFIG = [
  {
    key: "faithfulness" as const,
    label: "Faithfulness",
    icon: ShieldCheck,
    color: "from-emerald-500 to-teal-400",
    bgGlow: "rgba(16, 185, 129, 0.12)",
    borderColor: "border-emerald-500/25",
    definition:
      "Every answer is grounded in verified scheme data — measures how often the AI avoids making things up.",
  },
  {
    key: "answer_relevancy" as const,
    label: "Answer Relevancy",
    icon: Target,
    color: "from-blue-500 to-indigo-400",
    bgGlow: "rgba(99, 102, 241, 0.12)",
    borderColor: "border-blue-500/25",
    definition:
      "How directly and completely the AI's answer addresses what you actually asked.",
  },
  {
    key: "context_precision" as const,
    label: "Context Precision",
    icon: Layers,
    color: "from-violet-500 to-purple-400",
    bgGlow: "rgba(139, 92, 246, 0.12)",
    borderColor: "border-violet-500/25",
    definition:
      "The retrieved scholarship data is specifically relevant to your question — signal-to-noise ratio of retrieval.",
  },
  {
    key: "context_recall" as const,
    label: "Context Recall",
    icon: BookOpen,
    color: "from-amber-500 to-orange-400",
    bgGlow: "rgba(245, 158, 11, 0.12)",
    borderColor: "border-amber-500/25",
    definition:
      "The retrieved data covers all the information needed to give a complete answer.",
  },
];

function ScoreRing({ score }: { score: number | null }) {
  if (score === null) {
    return (
      <div className="text-3xl font-bold text-gray-400 dark:text-gray-500 font-mono transition-all duration-500">
        —
      </div>
    );
  }
  const pct = Math.round(score * 100);
  const color =
    pct >= 85
      ? "text-emerald-500"
      : pct >= 70
      ? "text-blue-500"
      : "text-red-400";
  return (
    <div className={`text-4xl font-bold font-mono tabular-nums ${color}`}>
      {pct}
      <span className="text-lg font-normal text-gray-400 dark:text-gray-500 transition-all duration-500">
        %
      </span>
    </div>
  );
}

function MetricCard({
  config,
  value,
}: {
  config: (typeof METRIC_CONFIG)[number];
  value: number | null;
}) {
  const Icon = config.icon;
  return (
    <div
      className={`
        relative flex flex-col gap-4 rounded-2xl p-6
        bg-white dark:bg-[#0F1117]
        border ${config.borderColor} dark:border-opacity-100
        shadow-sm hover:shadow-md dark:shadow-none
        transition-all duration-500
      `}
      style={{
        background: `radial-gradient(ellipse at top left, ${config.bgGlow} 0%, transparent 60%)`,
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <div
            className={`p-2 rounded-xl bg-linear-to-br ${config.color} text-white shadow-sm`}
          >
            <Icon size={16} />
          </div>
          <span className="font-semibold text-sm text-gray-800 dark:text-[#E2E8F0] transition-all duration-500">
            {config.label}
          </span>
        </div>
        {value !== null && (
          <span
            className={`text-xs font-mono px-2 py-0.5 rounded-full ${
              value >= 0.7
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
            }`}
          >
            {value >= 0.7 ? "PASS" : "FAIL"}
          </span>
        )}
      </div>

      {/* Score */}
      <div className="flex items-end gap-3 transition-all duration-500">
        <ScoreRing score={value} />
        {value !== null && (
          <div className="mb-1 flex-1">
            {/* Progress bar */}
            <div className="h-1.5 rounded-full bg-gray-100 dark:bg-white/8 overflow-hidden transition-all duration-500">
              <div
                className={`h-full rounded-full bg-linear-to-r ${config.color} transition-all duration-700`}
                style={{ width: `${Math.round(value * 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-gray-400 mt-1">
              <span>0%</span>
              <span className="text-gray-500">threshold 70%</span>
              <span>100%</span>
            </div>
          </div>
        )}
      </div>

      {/* Definition */}
      <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed transition-all duration-500">
        {config.definition}
      </p>
    </div>
  );
}

function StatPill({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-100 dark:bg-white/6 text-sm transition-all duration-500">
      <Icon size={14} className="text-gray-400 dark:text-gray-500 shrink-0" />
      <span className="text-gray-500 dark:text-gray-400">{label}</span>
      <span className="font-medium text-gray-800 dark:text-[#E2E8F0] font-mono">
        {value}
      </span>
    </div>
  );
}

export default function EvalPage() {
  const [results, setResults] = useState<EvalResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/eval/results`, {
        cache: "no-store",
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `HTTP ${res.status}`);
      }
      setResults(await res.json());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load results");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: "Asia/Kolkata",
      });
    } catch {
      return iso;
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto transition-all duration-500">
      {/* Page header */}
      <div className="flex flex-col gap-2 transition-all duration-500">
        <div className="flex items-center gap-3 transition-all duration-500">
          <div className="p-2.5 rounded-xl bg-linear-to-br from-[#0C65D2] to-violet-500 text-white shadow-md">
            <FlaskConical size={20} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-[#F0F4FF] font-syne">
              AI Quality Report
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Continuous evaluation of EduPilot's scholarship answers
            </p>
          </div>
        </div>

        {/* Trust explainer */}
        <div className="mt-2 p-4 rounded-xl border border-[#0C65D2]/20 bg-[#0C65D2]/5 dark:bg-[#0C65D2]/8 transition-all duration-500">
          <p className="text-sm text-gray-700 dark:text-[#C8D5F0] leading-relaxed">
            <span className="font-semibold text-[#0C65D2]">
              Why does this matter?
            </span>{" "}
            We continuously evaluate our AI's answers against real scholarship
            data to make sure it never gives you incorrect deadlines, wrong
            eligibility criteria, or made-up scheme details. These scores are
            measured by an independent AI judge — not the same model that
            generates your answers.
          </p>
        </div>
      </div>

      {/* Scope badge */}
      <div className="flex flex-wrap items-center gap-3 transition-all duration-500">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#0C65D2]/30 bg-[#0C65D2]/8 text-[#0C65D2] text-xs font-medium transition-all duration-500">
          <GraduationCap size={13} />
          Currently covering: Scholarship Agent
        </div>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          Internship, Hackathon & Jobs agents — coming soon as data pipelines are
          populated
        </span>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center gap-3 py-20 text-gray-400 dark:text-gray-500 transition-all duration-500">
          <RefreshCcw size={18} className="animate-spin" />
          <span className="text-sm">Loading evaluation results…</span>
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className="flex flex-col items-center gap-4 py-16 text-center transition-all duration-500">
          <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/20 text-red-500 transition-all duration-500">
            <AlertCircle size={24} />
          </div>
          <div>
            <p className="font-semibold text-gray-800 dark:text-[#E2E8F0]">
              No evaluation results found
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 max-w-md">
              {error.includes("404")
                ? "Run python eval/ragas_eval.py from the services/ directory to generate results."
                : error}
            </p>
          </div>
          <button
            onClick={fetchResults}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0C65D2] text-white text-sm font-medium hover:bg-[#0B58BC] transition-all duration-500"
          >
            <RefreshCcw size={14} />
            Retry
          </button>
        </div>
      )}

      {/* Results */}
      {!loading && !error && results && (
        <>
          {/* Meta pills */}
          <div className="flex flex-wrap gap-2">
            <StatPill
              icon={Clock}
              label="Last updated"
              value={formatDate(results.last_updated)}
            />
            <StatPill
              icon={FlaskConical}
              label="Sample questions"
              value={String(results.sample_size)}
            />
            <StatPill
              icon={GraduationCap}
              label="Agent"
              value={results.agent.charAt(0).toUpperCase() + results.agent.slice(1)}
            />
          </div>

          {/* Metric cards grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 transition-all duration-500">
            {METRIC_CONFIG.map((config) => (
              <MetricCard
                key={config.key}
                config={config}
                value={results.metrics[config.key]}
              />
            ))}
          </div>

          {/* Methodology note */}
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-white/3 border border-gray-200/80 dark:border-white/6 transition-all duration-500">
            <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
              <span className="font-semibold text-gray-600 dark:text-gray-300 transition-all duration-500">
                Methodology:
              </span>{" "}
              Scores are computed using the{" "}
              <span className="font-mono text-xs">Ragas</span> evaluation
              framework over {results.sample_size} curated test questions.
              Results are evaluated by{" "}
              <span className="font-mono text-xs">gemma4:cloud</span> — a
              deliberately different model family from the generation model —
              to ensure unbiased scoring. This is a pre-computed snapshot;
              live evaluation is never triggered on page load to prevent
              unexpected cost or latency.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
