"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { updateProfile, type StudentProfile } from "@/app/lib/api";

const STATES = [
  "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh",
  "Gujarat", "Rajasthan", "West Bengal", "Kerala", "Punjab",
];
const CATEGORIES = ["General", "OBC", "SC", "ST", "EWS", "EBC", "SEBC", "VJNT", "DNT"];
const STREAMS = ["Engineering", "Medical", "Law", "Management", "Pharmacy", "Architecture", "Arts", "Science"];

interface Props {
  initial: StudentProfile | null;
  userId: string;
  userEmail: string;
}

export default function ProfileForm({ initial, userId, userEmail }: Props) {
  const router = useRouter();
  const [form, setForm] = useState<StudentProfile>(initial ?? {});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const set = (key: keyof StudentProfile, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await updateProfile(userId, form, userEmail);
      setMessage("Profile saved successfully.");
      router.refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h1 className="font-syne text-xl font-bold text-gray-900 dark:text-[#F0F4FF]">Student Profile</h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Complete your profile for accurate scholarship matching and eligibility checks.
        </p>
      </div>

      {message && (
        <p className="font-mono text-[12px] px-4 py-2 border border-[#0C65D2]/30 bg-[#0C65D2]/5 text-[#0C65D2]">
          {message}
        </p>
      )}

      <section className="border border-black/10 dark:border-white/8 p-5 flex flex-col gap-4">
        <h2 className="font-syne font-bold text-sm">Personal Details</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Full name" value={form.full_name ?? ""} onChange={(v) => set("full_name", v)} />
          <Field label="Phone" value={form.phone ?? ""} onChange={(v) => set("phone", v)} />
          <Select label="Gender" value={form.gender ?? ""} options={["Male", "Female", "Other"]} onChange={(v) => set("gender", v)} />
          <Select label="Category" value={form.category ?? ""} options={CATEGORIES} onChange={(v) => set("category", v)} />
          <Select label="State" value={form.state ?? ""} options={STATES} onChange={(v) => set("state", v)} />
          <Field label="District" value={form.district ?? ""} onChange={(v) => set("district", v)} />
          <Field label="Annual family income (₹)" type="number" value={form.income_annual ?? ""} onChange={(v) => set("income_annual", Number(v))} />
        </div>
      </section>

      <section className="border border-black/10 dark:border-white/8 p-5 flex flex-col gap-4">
        <h2 className="font-syne font-bold text-sm">Academic Info</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="College" value={form.college ?? ""} onChange={(v) => set("college", v)} />
          <Field label="University" value={form.university ?? ""} onChange={(v) => set("university", v)} />
          <Select label="Stream" value={form.stream ?? ""} options={STREAMS} onChange={(v) => set("stream", v)} />
          <Field label="Degree" value={form.degree ?? ""} onChange={(v) => set("degree", v)} />
          <Field label="Year of study" type="number" value={form.year_of_study ?? ""} onChange={(v) => set("year_of_study", Number(v))} />
          <Field label="CGPA" type="number" value={form.cgpa ?? ""} onChange={(v) => set("cgpa", Number(v))} />
          <Field label="12th %" type="number" value={form.percentage_12th ?? ""} onChange={(v) => set("percentage_12th", Number(v))} />
        </div>
      </section>

      {initial?.readiness_score !== undefined && (
        <div className="border border-black/10 dark:border-white/8 p-4 flex items-center justify-between">
          <span className="font-mono text-[12px] text-gray-500">Readiness score</span>
          <span className="font-syne text-2xl font-bold text-[#0C65D2]">{initial.readiness_score}%</span>
        </div>
      )}

      <button
        type="submit"
        disabled={saving}
        className="self-start px-6 py-2.5 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] disabled:opacity-50 transition-colors"
      >
        {saving ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string | number;
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] focus:outline-none focus:border-[#0C65D2]/50"
      />
    </label>
  );
}

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] focus:outline-none focus:border-[#0C65D2]/50"
      >
        <option value="">Select…</option>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </label>
  );
}
