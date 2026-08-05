"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { X, Plus, Upload, FileText, Link, Loader2, CheckCircle } from "lucide-react";
import { updateProfile, type StudentProfile } from "@/app/lib/api";

// ─── Static option lists ────────────────────────────────────────────────────

const STATES = [
  "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh",
  "Gujarat", "Rajasthan", "West Bengal", "Kerala", "Punjab",
  "Andhra Pradesh", "Bihar", "Chhattisgarh", "Goa", "Haryana",
  "Himachal Pradesh", "Jharkhand", "Madhya Pradesh", "Manipur", "Meghalaya",
  "Odisha", "Telangana", "Uttarakhand",
];
const CATEGORIES  = ["General", "OBC", "SC", "ST", "EWS", "EBC", "SEBC", "VJNT", "DNT"];
const STREAMS = [
  // Engineering & Technology
  "Engineering - Computer Science / IT",
  "Engineering - Electronics & Communication",
  "Engineering - Mechanical",
  "Engineering - Civil",
  "Engineering - Electrical",
  "Engineering - Chemical",
  "Engineering - Aerospace",
  "Engineering - Biotechnology",
  "Engineering - Other",
  // Data & AI
  "Data Science",
  "Artificial Intelligence & ML",
  "Cybersecurity",
  // Business & Management
  "Management / MBA",
  "Business Administration (BBA)",
  "Commerce / B.Com",
  "Finance & Accounting",
  "Marketing",
  "Human Resources",
  "Entrepreneurship",
  // Design & Media
  "Design - UI/UX",
  "Design - Graphic / Visual",
  "Design - Product",
  "Architecture",
  "Media & Journalism",
  "Film & Animation",
  // Science
  "Science - Physics",
  "Science - Chemistry",
  "Science - Biology / Life Sciences",
  "Science - Mathematics / Statistics",
  "Environmental Science",
  // Humanities & Social
  "Arts & Humanities",
  "Psychology",
  "Sociology",
  "Political Science",
  "Economics",
  "Education / Teaching",
  // Health
  "Medical / MBBS",
  "Pharmacy",
  "Nursing",
  "Public Health",
  // Legal
  "Law / LLB",
  // Other
  "Other",
];
const WORK_MODES  = ["Remote", "Onsite", "Hybrid"];
const DURATIONS   = ["1 Month", "3 Months", "6 Months", "6+ Months"];
const CITIES      = ["Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Jaipur", "Remote"];

const SKILL_SUGGESTIONS = [
  "Python", "Java", "JavaScript", "React", "Node.js", "SQL", "Excel",
  "Machine Learning", "Data Analysis", "Figma", "Communication",
  "C++", "HTML/CSS", "Android", "iOS", "Django", "FastAPI", "TypeScript",
];
const INTEREST_SUGGESTIONS = [
  "Software Dev", "Data Science", "Finance", "Marketing", "Design",
  "Product Management", "HR", "Operations", "Research", "Content Writing",
  "Business Development", "Consulting", "E-commerce", "EdTech", "FinTech",
];

// ─── Props ──────────────────────────────────────────────────────────────────

interface Props {
  initial: StudentProfile | null;
  userId: string;
  userEmail: string;
}

// ─── Main component ─────────────────────────────────────────────────────────

export default function ProfileForm({ initial, userId, userEmail }: Props) {
  const router  = useRouter();
  const [form, setForm]       = useState<StudentProfile>(initial ?? {});
  const [saving, setSaving]   = useState(false);
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null);

  // ── helpers ────────────────────────────────────────────────────────────

  const set = useCallback(
    (key: keyof StudentProfile, value: unknown) =>
      setForm((f) => ({ ...f, [key]: value })),
    [],
  );

  const setPref = useCallback(
    (key: string, value: unknown) =>
      setForm((f) => ({
        ...f,
        preferences: { ...(f.preferences ?? {}), [key]: value },
      })),
    [],
  );

  const pref = (key: string) => (form.preferences ?? {})[key];

  // ── multi-tag helpers ──────────────────────────────────────────────────

  function addTag(key: keyof StudentProfile, value: string) {
    if (!value.trim()) return;
    const current = (form[key] as string[] | undefined) ?? [];
    if (!current.includes(value.trim())) set(key, [...current, value.trim()]);
  }

  function removeTag(key: keyof StudentProfile, value: string) {
    const current = (form[key] as string[] | undefined) ?? [];
    set(key, current.filter((t) => t !== value));
  }

  function addPrefTag(key: string, value: string) {
    if (!value.trim()) return;
    const current = (pref(key) as string[] | undefined) ?? [];
    if (!current.includes(value.trim())) setPref(key, [...current, value.trim()]);
  }

  function removePrefTag(key: string, value: string) {
    const current = (pref(key) as string[] | undefined) ?? [];
    setPref(key, current.filter((t) => t !== value));
  }

  // ── submit ─────────────────────────────────────────────────────────────

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await updateProfile(userId, form, userEmail);
      setMessage({ text: "Profile saved successfully.", ok: true });
      router.refresh();
    } catch (err) {
      setMessage({ text: err instanceof Error ? err.message : "Save failed", ok: false });
    } finally {
      setSaving(false);
    }
  }

  // ── render ─────────────────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 max-w-2xl">

      {/* heading */}
      <div>
        <h1 className="font-syne text-xl font-bold text-gray-900 dark:text-[#F0F4FF]">
          Student Profile
        </h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Complete your profile for accurate scholarship & internship matching.
        </p>
      </div>

      {/* message banner */}
      {message && (
        <p className={`font-mono text-[12px] px-4 py-2 border flex items-center gap-2 ${
          message.ok
            ? "border-green-500/30 bg-green-500/5 text-green-600"
            : "border-red-400/30 bg-red-400/5 text-red-500"
        }`}>
          {message.ok && <CheckCircle size={13} />}
          {message.text}
        </p>
      )}

      {/* ── Personal Details ─────────────────────────────────────────── */}
      <Section title="Personal Details">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Full name"       value={form.full_name    ?? ""} onChange={(v) => set("full_name",    v)} />
          <Field label="Phone"           value={form.phone        ?? ""} onChange={(v) => set("phone",        v)} />
          <Select label="Gender"   value={form.gender   ?? ""} options={["Male","Female","Other"]}  onChange={(v) => set("gender",   v)} />
          <Select label="Category" value={form.category ?? ""} options={CATEGORIES}                 onChange={(v) => set("category", v)} />
          <Select label="State"    value={form.state    ?? ""} options={STATES}                     onChange={(v) => set("state",    v)} />
          <Field label="District"        value={form.district     ?? ""} onChange={(v) => set("district",     v)} />
          <Field label="Annual family income (₹)" type="number" value={form.income_annual ?? ""} onChange={(v) => set("income_annual", Number(v))} />
        </div>
      </Section>

      {/* ── Academic Info ────────────────────────────────────────────── */}
      <Section title="Academic Info">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="College"    value={form.college    ?? ""} onChange={(v) => set("college",    v)} />
          <Field label="University" value={form.university ?? ""} onChange={(v) => set("university", v)} />
          <Select label="Stream" value={form.stream ?? ""} options={STREAMS} onChange={(v) => set("stream", v)} />
          <Field label="Degree"          value={form.degree        ?? ""} onChange={(v) => set("degree",        v)} />
          <Field label="Year of study"   type="number" value={form.year_of_study  ?? ""} onChange={(v) => set("year_of_study",  Number(v))} />
          <Field label="CGPA"            type="number" value={form.cgpa           ?? ""} onChange={(v) => set("cgpa",           Number(v))} />
          <Field label="12th %"          type="number" value={form.percentage_12th ?? ""} onChange={(v) => set("percentage_12th", Number(v))} />
          <Field
            label="Backlogs (if any)"
            type="number"
            value={form.backlogs ?? ""}
            onChange={(v) => set("backlogs", v === "" ? null : Number(v))}
            hint="Leave blank if none"
          />
        </div>
      </Section>

      {/* ── Skills & Preferences ─────────────────────────────────────── */}
      <Section title="Skills & Preferences">
        <div className="flex flex-col gap-5">

          {/* Skills */}
          <TagInput
            label="Skills"
            hint="e.g. Python, React, Excel, Communication"
            tags={(form.skills ?? []) as string[]}
            suggestions={SKILL_SUGGESTIONS}
            onAdd={(v) => addTag("skills", v)}
            onRemove={(v) => removeTag("skills", v)}
          />

          {/* Areas of Interest */}
          <TagInput
            label="Areas of Interest"
            hint="e.g. Software Dev, Finance, Marketing, Design"
            tags={((pref("interests") as string[]) ?? [])}
            suggestions={INTEREST_SUGGESTIONS}
            onAdd={(v) => addPrefTag("interests", v)}
            onRemove={(v) => removePrefTag("interests", v)}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

            {/* Preferred Work Mode */}
            <Select
              label="Preferred Work Mode"
              value={(pref("work_mode") as string) ?? ""}
              options={WORK_MODES}
              onChange={(v) => setPref("work_mode", v)}
            />

            {/* Preferred Internship Duration */}
            <Select
              label="Preferred Internship Duration"
              value={(pref("pref_duration") as string) ?? ""}
              options={DURATIONS}
              onChange={(v) => setPref("pref_duration", v)}
            />

            {/* Availability / Start Date */}
            <Field
              label="Availability / Start Date"
              type="date"
              value={(pref("availability") as string) ?? ""}
              onChange={(v) => setPref("availability", v)}
            />
          </div>

          {/* Preferred Locations */}
          <TagInput
            label="Preferred Location(s)"
            hint="Type a city and press Enter, or pick below"
            tags={((pref("pref_locations") as string[]) ?? [])}
            suggestions={CITIES}
            onAdd={(v) => addPrefTag("pref_locations", v)}
            onRemove={(v) => removePrefTag("pref_locations", v)}
          />

        </div>
      </Section>

      {/* ── Documents ────────────────────────────────────────────────── */}
      <Section title="Documents">
        <div className="flex flex-col gap-4">

          {/* Resume */}
          <FileOrLink
            label="Resume / CV"
            hint="PDF only · max 5 MB"
            accept=".pdf"
            storedName={(pref("resume_url") as string) ?? ""}
            onUrlSaved={(url) => setPref("resume_url", url)}
            userId={userId}
            docType="resume"
          />

          {/* Portfolio / LinkedIn / GitHub */}
          <label className="flex flex-col gap-1">
            <span className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Portfolio / LinkedIn / GitHub URL
              <span className="ml-1 text-gray-300 dark:text-gray-600">(optional)</span>
            </span>
            <div className="relative">
              <Link size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
              <input
                type="url"
                value={(pref("portfolio_url") as string) ?? ""}
                onChange={(e) => setPref("portfolio_url", e.target.value)}
                placeholder="https://github.com/yourname"
                className="w-full pl-8 pr-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] focus:outline-none focus:border-[#0C65D2]/50"
              />
            </div>
          </label>

          {/* Cover Letter */}
          <FileOrLink
            label="Cover Letter"
            hint="PDF only · optional"
            accept=".pdf"
            storedName={(pref("cover_letter_url") as string) ?? ""}
            onUrlSaved={(url) => setPref("cover_letter_url", url)}
            userId={userId}
            docType="cover_letter"
            optional
          />

        </div>
      </Section>

      {/* readiness score */}
      {initial?.readiness_score !== undefined && (
        <div className="border border-black/10 dark:border-white/8 p-4 flex items-center justify-between">
          <span className="font-mono text-[12px] text-gray-500">Profile readiness score</span>
          <span className="font-syne text-2xl font-bold text-[#0C65D2]">
            {initial.readiness_score}%
          </span>
        </div>
      )}

      <button
        type="submit"
        disabled={saving}
        className="self-start px-6 py-2.5 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] disabled:opacity-50 transition-colors flex items-center gap-2"
      >
        {saving && <Loader2 size={13} className="animate-spin" />}
        {saving ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}

// ─── Reusable sub-components ─────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="border border-black/10 dark:border-white/8 p-5 flex flex-col gap-4">
      <h2 className="font-syne font-bold text-sm text-gray-900 dark:text-[#F0F4FF]">{title}</h2>
      {children}
    </section>
  );
}

function Field({
  label, value, onChange, type = "text", hint,
}: {
  label: string;
  value: string | number;
  onChange: (v: string) => void;
  type?: string;
  hint?: string;
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
      {hint && <span className="font-mono text-[10px] text-gray-300 dark:text-gray-600">{hint}</span>}
    </label>
  );
}

function Select({
  label, value, options, onChange,
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
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );
}

// ─── TagInput ────────────────────────────────────────────────────────────────

function TagInput({
  label, hint, tags, suggestions, onAdd, onRemove,
}: {
  label: string;
  hint: string;
  tags: string[];
  suggestions: string[];
  onAdd: (v: string) => void;
  onRemove: (v: string) => void;
}) {
  const [input, setInput] = useState("");

  function commit(val: string) {
    if (val.trim()) { onAdd(val); setInput(""); }
  }

  function handleKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      commit(input);
    } else if (e.key === "Backspace" && !input && tags.length > 0) {
      onRemove(tags[tags.length - 1]);
    }
  }

  const unused = suggestions.filter((s) => !tags.includes(s));

  return (
    <div className="flex flex-col gap-1.5">
      <span className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">{label}</span>

      {/* tag bag + input */}
      <div className="min-h-[42px] flex flex-wrap gap-1.5 px-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] focus-within:border-[#0C65D2]/50">
        {tags.map((tag) => (
          <span
            key={tag}
            className="flex items-center gap-1 px-2 py-0.5 bg-[#0C65D2]/10 border border-[#0C65D2]/20 font-mono text-[11px] text-[#0C65D2]"
          >
            {tag}
            <button
              type="button"
              onClick={() => onRemove(tag)}
              className="hover:text-red-500 transition-colors"
              aria-label={`Remove ${tag}`}
            >
              <X size={10} />
            </button>
          </span>
        ))}
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          onBlur={() => commit(input)}
          placeholder={tags.length === 0 ? hint : ""}
          className="flex-1 min-w-[120px] bg-transparent font-mono text-[12px] focus:outline-none placeholder:text-gray-300 dark:placeholder:text-gray-600"
        />
      </div>

      {/* suggestion pills */}
      {unused.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-0.5">
          {unused.slice(0, 12).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onAdd(s)}
              className="flex items-center gap-1 px-2 py-0.5 border border-black/10 dark:border-white/8 font-mono text-[10px] text-gray-400 hover:border-[#0C65D2]/40 hover:text-[#0C65D2] transition-colors"
            >
              <Plus size={9} /> {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── FileOrLink ──────────────────────────────────────────────────────────────

function FileOrLink({
  label, hint, accept, storedName, onUrlSaved, userId, docType, optional = false,
}: {
  label: string;
  hint: string;
  accept: string;
  storedName: string;
  onUrlSaved: (url: string) => void;
  userId: string;
  docType: string;
  optional?: boolean;
}) {
  const inputRef           = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName]   = useState(
    storedName ? storedName.split("/").pop() ?? storedName : "",
  );

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // store filename locally for display
    setFileName(file.name);

    // Upload via existing document upload endpoint
    setUploading(true);
    try {
      const form = new FormData();
      form.append("user_id", userId);
      form.append("document_type", docType);
      form.append("file", file);
      const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res  = await fetch(`${base}/api/v1/documents/upload`, {
        method: "POST",
        body: form,
      });
      if (res.ok) {
        const data = await res.json();
        // store document_id as the reference in preferences
        onUrlSaved(data.document_id ?? file.name);
      } else {
        // fallback: just store the filename so the form still saves
        onUrlSaved(file.name);
      }
    } catch {
      onUrlSaved(file.name);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
        {label}
        {optional && <span className="ml-1 text-gray-300 dark:text-gray-600">(optional)</span>}
      </span>

      <div className="flex items-center gap-3 px-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822]">
        <FileText size={14} className="text-gray-400 shrink-0" />
        <span className="flex-1 font-mono text-[12px] text-gray-500 truncate">
          {fileName || <span className="text-gray-300 dark:text-gray-600">{hint}</span>}
        </span>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-1.5 px-3 py-1 border border-[#0C65D2]/30 text-[#0C65D2] font-mono text-[11px] hover:bg-[#0C65D2]/5 disabled:opacity-50 transition-colors shrink-0"
        >
          {uploading
            ? <Loader2 size={11} className="animate-spin" />
            : <Upload size={11} />}
          {fileName ? "Re-upload" : "Upload"}
        </button>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleFile}
        className="hidden"
        aria-label={`Upload ${label}`}
      />
    </div>
  );
}
