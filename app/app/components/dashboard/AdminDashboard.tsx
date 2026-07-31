"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Users,
  GraduationCap,
  FileText,
  MessageSquare,
  Shield,
  TrendingUp,
  RefreshCw,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Database,
  Play,
  Zap,
  Target,
} from "lucide-react";
import type {
  PlatformAnalytics,
  ConnectorStatusItem,
  DataFreshness,
  AccuracyMetrics,
} from "@/app/lib/api";
import {
  getAdminAnalytics,
  getConnectorStatuses,
  getDataFreshness,
  getAccuracyMetrics,
  triggerConnectorRun,
} from "@/app/lib/api";

interface Props {
  userId: string;
  userEmail: string;
}

export default function AdminDashboard({ userId, userEmail }: Props) {
  const [analytics, setAnalytics] = useState<PlatformAnalytics | null>(null);
  const [connectors, setConnectors] = useState<ConnectorStatusItem[]>([]);
  const [freshness, setFreshness] = useState<DataFreshness | null>(null);
  const [accuracy, setAccuracy] = useState<AccuracyMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [a, c, f, acc] = await Promise.allSettled([
        getAdminAnalytics(userId, userEmail),
        getConnectorStatuses(userId, userEmail),
        getDataFreshness(userId, userEmail),
        getAccuracyMetrics(userId, userEmail),
      ]);
      if (a.status === "fulfilled") setAnalytics(a.value);
      if (c.status === "fulfilled") setConnectors(c.value.connectors);
      if (f.status === "fulfilled") setFreshness(f.value);
      if (acc.status === "fulfilled") setAccuracy(acc.value);
    } finally {
      setLoading(false);
    }
  }, [userId, userEmail]);

  useEffect(() => {
    let isCancelled = false;
    async function loadData() {
      try {
        const [a, c, f, acc] = await Promise.allSettled([
          getAdminAnalytics(userId, userEmail),
          getConnectorStatuses(userId, userEmail),
          getDataFreshness(userId, userEmail),
          getAccuracyMetrics(userId, userEmail),
        ]);
        if (!isCancelled) {
          if (a.status === "fulfilled") setAnalytics(a.value);
          if (c.status === "fulfilled") setConnectors(c.value.connectors);
          if (f.status === "fulfilled") setFreshness(f.value);
          if (acc.status === "fulfilled") setAccuracy(acc.value);
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }
    loadData();
    return () => {
      isCancelled = true;
    };
  }, [userId, userEmail]);

  const handleTrigger = useCallback(
    async (name?: string) => {
      setTriggering(name ?? "all");
      try {
        await triggerConnectorRun(userId, name, userEmail);
        await fetchAll();
      } finally {
        setTriggering(null);
      }
    },
    [userId, userEmail, fetchAll]
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 gap-3">
        <Loader2 size={24} className="animate-spin text-[#0C65D2]" />
        <span className="font-mono text-[13px] text-gray-400">
          Loading admin dashboard…
        </span>
      </div>
    );
  }

  const kpis = analytics?.platform_kpis;

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-syne text-xl font-bold flex items-center gap-2">
            <Zap size={20} className="text-[#0C65D2]" />
            Admin Dashboard
          </h1>
          <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
            Platform analytics, connector health, and accuracy metrics
          </p>
        </div>
        <button
          onClick={() => fetchAll()}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-500 hover:text-[#0C65D2] transition-all"
        >
          <RefreshCw size={12} /> Refresh
        </button>
      </div>

      {/* KPI Cards */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <KpiCard icon={<Users size={16} />} label="Users" value={kpis.total_users} />
          <KpiCard
            icon={<GraduationCap size={16} />}
            label="Opportunities"
            value={kpis.total_opportunities}
          />
          <KpiCard
            icon={<FileText size={16} />}
            label="Applications"
            value={kpis.total_applications}
          />
          <KpiCard
            icon={<MessageSquare size={16} />}
            label="Feedback"
            value={kpis.total_feedback}
          />
          <KpiCard
            icon={<Shield size={16} />}
            label="Audit Events"
            value={kpis.total_audit_events}
          />
        </div>
      )}

      {/* Conversion & Accuracy Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Conversion Rate */}
        {analytics && (
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-gray-500">
              <TrendingUp size={14} />
              <span className="font-mono text-[11px] uppercase tracking-wide">
                Conversion Rate
              </span>
            </div>
            <p className="font-mono text-2xl font-bold text-[#0C65D2]">
              {analytics.conversion.application_conversion_rate}%
            </p>
          </div>
        )}

        {/* Freshness Score */}
        {freshness && (
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-gray-500">
              <Database size={14} />
              <span className="font-mono text-[11px] uppercase tracking-wide">
                Data Freshness
              </span>
            </div>
            <p
              className={`font-mono text-2xl font-bold ${
                freshness.aggregate_freshness_score >= 80
                  ? "text-green-500"
                  : freshness.aggregate_freshness_score >= 50
                    ? "text-amber-500"
                    : "text-red-500"
              }`}
            >
              {freshness.aggregate_freshness_score}%
            </p>
            <p className="font-mono text-[10px] text-gray-400">
              {freshness.stale_connectors} / {freshness.total_connectors} stale
            </p>
          </div>
        )}

        {/* Accuracy */}
        {accuracy && (
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-gray-500">
              <Target size={14} />
              <span className="font-mono text-[11px] uppercase tracking-wide">
                Recommendation Precision
              </span>
            </div>
            <p className="font-mono text-2xl font-bold text-[#0C65D2]">
              {Math.round(accuracy.precision * 100)}%
            </p>
            <p className="font-mono text-[10px] text-gray-400">
              {accuracy.feedback_breakdown.relevant} relevant / {accuracy.feedback_breakdown.total_evaluated} evaluated
            </p>
          </div>
        )}
      </div>

      {/* Connector Status Table */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
            Data Connectors
          </p>
          <button
            onClick={() => handleTrigger()}
            disabled={triggering !== null}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0C65D2] text-white font-mono text-[11px] disabled:opacity-50 transition-all"
          >
            {triggering === "all" ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              <Play size={12} />
            )}
            Run All
          </button>
        </div>

        <div className="border border-black/10 dark:border-white/8 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 dark:bg-[#0F1117] border-b border-black/10 dark:border-white/8">
                <th className="text-left px-4 py-2.5 font-mono text-[11px] text-gray-500 uppercase">
                  Connector
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] text-gray-500 uppercase">
                  Status
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] text-gray-500 uppercase">
                  Last Run
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] text-gray-500 uppercase">
                  Records
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] text-gray-500 uppercase">
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {connectors.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="text-center py-8 font-mono text-[12px] text-gray-400"
                  >
                    No connectors registered
                  </td>
                </tr>
              ) : (
                connectors.map((c) => (
                  <tr
                    key={c.name}
                    className="border-b border-black/5 dark:border-white/5 last:border-0"
                  >
                    <td className="px-4 py-3">
                      <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
                        {c.name}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`flex items-center gap-1.5 font-mono text-[11px] ${
                          c.is_stale
                            ? "text-amber-500"
                            : c.last_error
                              ? "text-red-500"
                              : "text-green-500"
                        }`}
                      >
                        {c.is_stale ? (
                          <AlertTriangle size={12} />
                        ) : c.last_error ? (
                          <XCircle size={12} />
                        ) : (
                          <CheckCircle2 size={12} />
                        )}
                        {c.is_stale ? "Stale" : c.last_error ? "Error" : "Healthy"}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-gray-500">
                      {c.last_run
                        ? new Date(c.last_run).toLocaleString()
                        : "Never"}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-[12px] text-gray-700 dark:text-gray-300">
                      {c.records_processed}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleTrigger(c.name)}
                        disabled={triggering !== null}
                        className="flex items-center gap-1 px-2 py-1 border border-black/10 dark:border-white/8 font-mono text-[10px] text-gray-500 hover:text-[#0C65D2] transition-all ml-auto"
                      >
                        {triggering === c.name ? (
                          <Loader2 size={10} className="animate-spin" />
                        ) : (
                          <Play size={10} />
                        )}
                        Run
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Error Details */}
        {connectors.some((c) => c.last_error) && (
          <div className="flex flex-col gap-2">
            <p className="font-mono text-[11px] text-red-500 uppercase">
              Error Logs
            </p>
            {connectors
              .filter((c) => c.last_error)
              .map((c) => (
                <div
                  key={c.name}
                  className="border border-red-500/20 bg-red-500/5 p-3"
                >
                  <p className="font-mono text-[12px] font-bold text-red-500">
                    {c.name}
                  </p>
                  <p className="font-mono text-[11px] text-red-400 mt-1 whitespace-pre-wrap">
                    {c.last_error}
                  </p>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}

function KpiCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 flex flex-col gap-1">
      <div className="flex items-center gap-2 text-gray-400">
        {icon}
        <span className="font-mono text-[10px] uppercase tracking-wide">
          {label}
        </span>
      </div>
      <p className="font-mono text-xl font-bold text-gray-900 dark:text-[#F0F4FF]">
        {value.toLocaleString()}
      </p>
    </div>
  );
}
