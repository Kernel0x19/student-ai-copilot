"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Bell,
  Mail,
  Smartphone,
  MonitorSpeaker,
  Calendar,
  Sparkles,
  Activity,
  Loader2,
  Check,
} from "lucide-react";
import type { NotificationPreferences } from "@/app/lib/api";
import {
  getNotificationPreferences,
  updateNotificationPreferences,
} from "@/app/lib/api";

interface Props {
  userId: string;
  userEmail: string;
}

const CHANNEL_TOGGLES = [
  {
    key: "email_enabled" as const,
    icon: <Mail size={15} />,
    label: "Email Notifications",
    desc: "Receive updates via email",
  },
  {
    key: "sms_enabled" as const,
    icon: <Smartphone size={15} />,
    label: "SMS Notifications",
    desc: "Urgent alerts via SMS (Twilio)",
  },
  {
    key: "push_enabled" as const,
    icon: <MonitorSpeaker size={15} />,
    label: "Push Notifications",
    desc: "Browser / mobile push via FCM",
  },
];

const TYPE_TOGGLES = [
  {
    key: "deadline_reminders" as const,
    icon: <Calendar size={15} />,
    label: "Deadline Reminders",
    desc: "7-day and 2-day deadline alerts",
  },
  {
    key: "new_matches" as const,
    icon: <Sparkles size={15} />,
    label: "New Matches",
    desc: "When new opportunities match your profile",
  },
  {
    key: "status_updates" as const,
    icon: <Activity size={15} />,
    label: "Status Updates",
    desc: "Application status change alerts",
  },
];

const DEFAULT_PREFS: NotificationPreferences = {
  email_enabled: true,
  sms_enabled: false,
  push_enabled: true,
  deadline_reminders: true,
  new_matches: true,
  status_updates: true,
};

export default function NotificationPrefs({ userId, userEmail }: Props) {
  const [prefs, setPrefs] = useState<NotificationPreferences>(DEFAULT_PREFS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await getNotificationPreferences(userId, userEmail);
        setPrefs(data);
      } catch {
        // Keep defaults on failure (API may not be ready)
      } finally {
        setLoading(false);
      }
    })();
  }, [userId, userEmail]);

  const handleToggle = useCallback(
    (key: keyof NotificationPreferences) => {
      setPrefs((prev) => ({ ...prev, [key]: !prev[key] }));
      setSaved(false);
    },
    []
  );

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      await updateNotificationPreferences(userId, prefs, userEmail);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {
      // silent fail
    } finally {
      setSaving(false);
    }
  }, [userId, userEmail, prefs]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 gap-3">
        <Loader2 size={20} className="animate-spin text-[#0C65D2]" />
        <span className="font-mono text-[12px] text-gray-400">
          Loading preferences…
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-xl">
      <div>
        <h2 className="font-syne text-lg font-bold flex items-center gap-2">
          <Bell size={18} className="text-[#0C65D2]" />
          Notification Settings
        </h2>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Control how and when you receive notifications
        </p>
      </div>

      {/* Channels */}
      <div className="flex flex-col gap-3">
        <p className="font-mono text-[12px] text-gray-500 uppercase tracking-wide">
          Channels
        </p>
        {CHANNEL_TOGGLES.map((ch) => (
          <ToggleRow
            key={ch.key}
            icon={ch.icon}
            label={ch.label}
            desc={ch.desc}
            enabled={prefs[ch.key]}
            onChange={() => handleToggle(ch.key)}
          />
        ))}
      </div>

      {/* Types */}
      <div className="flex flex-col gap-3">
        <p className="font-mono text-[12px] text-gray-500 uppercase tracking-wide">
          Notification Types
        </p>
        {TYPE_TOGGLES.map((t) => (
          <ToggleRow
            key={t.key}
            icon={t.icon}
            label={t.label}
            desc={t.desc}
            enabled={prefs[t.key]}
            onChange={() => handleToggle(t.key)}
          />
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="flex items-center justify-center gap-2 px-4 py-2.5 bg-[#0C65D2] hover:bg-[#0B5ABD] disabled:opacity-50 text-white font-mono text-[12px] transition-all w-full"
      >
        {saving ? (
          <Loader2 size={14} className="animate-spin" />
        ) : saved ? (
          <Check size={14} />
        ) : (
          <Bell size={14} />
        )}
        {saving ? "Saving…" : saved ? "Saved!" : "Save Preferences"}
      </button>
    </div>
  );
}

function ToggleRow({
  icon,
  label,
  desc,
  enabled,
  onChange,
}: {
  icon: React.ReactNode;
  label: string;
  desc: string;
  enabled: boolean;
  onChange: () => void;
}) {
  return (
    <div className="flex items-center justify-between border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] px-4 py-3 transition-all">
      <div className="flex items-center gap-3">
        <span className="text-gray-500">{icon}</span>
        <div>
          <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
            {label}
          </p>
          <p className="font-mono text-[11px] text-gray-400">{desc}</p>
        </div>
      </div>
      <button
        onClick={onChange}
        className={`relative w-11 h-6 rounded-full transition-all ${
          enabled
            ? "bg-[#0C65D2]"
            : "bg-gray-200 dark:bg-[#1C1F2E]"
        }`}
        aria-label={`Toggle ${label}`}
      >
        <span
          className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-all ${
            enabled ? "left-[22px]" : "left-0.5"
          }`}
        />
      </button>
    </div>
  );
}
