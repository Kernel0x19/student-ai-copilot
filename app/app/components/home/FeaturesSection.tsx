"use client";
import { useState } from "react";
import {
  GraduationCap,
  FileText,
  CheckCircle,
  Map,
  Briefcase,
  MessageSquare,
} from "lucide-react";

type Feature = {
  id: string;
  icon: React.ReactNode;
  label: string;
  tag: string;
  heading: string;
  description: string;
  points: string[];
  terminal: { prompt: string; type: "command" | "success" | "muted" }[];
};

const FEATURES: Feature[] = [
  {
    id: "scholarship",
    icon: <GraduationCap size={18} />,
    label: "Scholarship discovery",
    tag: "AI-powered",
    heading: "Find every scholarship you qualify for",
    description:
      "The scholarship agent scans hundreds of sources in seconds, cross-references your profile, and surfaces only the ones you're actually eligible for.",
    points: [
      "847+ scholarships indexed across India",
      "Matches based on CGPA, stream, year, and category",
      "Deadline tracking with reminders",
    ],
    terminal: [
      { prompt: "Scanning 847 scholarships...", type: "command" },
      {
        prompt: "Filtering by CSE · 3rd year · OBC · CGPA 8.4",
        type: "command",
      },
      { prompt: "✓ 18 scholarships matched", type: "success" },
      { prompt: "✓ 12 verified eligible", type: "success" },
      { prompt: "✓ 3 deadlines within 30 days", type: "muted" },
    ],
  },
  {
    id: "ocr",
    icon: <FileText size={18} />,
    label: "OCR document analysis",
    tag: "Instant",
    heading: "Upload once, understand everything",
    description:
      "Upload your marksheets, certificates, or offer letters. The OCR agent extracts, structures, and stores every detail so you never re-enter data manually.",
    points: [
      "Supports PDFs, images, and scanned documents",
      "Extracts marks, grades, and subject names",
      "Auto-fills application forms using stored data",
    ],
    terminal: [
      { prompt: "Reading marksheet_sem5.pdf...", type: "command" },
      { prompt: "Extracting subject scores and SGPA", type: "command" },
      { prompt: "✓ 8 subjects extracted", type: "success" },
      { prompt: "✓ SGPA 8.7 calculated", type: "success" },
      { prompt: "✓ Profile updated automatically", type: "muted" },
    ],
  },
  {
    id: "eligibility",
    icon: <CheckCircle size={18} />,
    label: "Eligibility verification",
    tag: "Automated",
    heading: "Know before you apply",
    description:
      "Stop wasting time on applications you won't clear. The eligibility agent reads the fine print and tells you exactly where you stand before you submit.",
    points: [
      "Checks income, caste, institution, and academic criteria",
      "Flags disqualifying conditions upfront",
      "Suggests profile improvements to unlock more opportunities",
    ],
    terminal: [
      { prompt: "Verifying eligibility for NSP scholarship", type: "command" },
      {
        prompt: "Checking income certificate · caste category",
        type: "command",
      },
      { prompt: "✓ Income criterion met (< ₹2.5L)", type: "success" },
      { prompt: "✓ Category OBC verified", type: "success" },
      { prompt: "⚠ Institution approval pending", type: "muted" },
    ],
  },
  {
    id: "career",
    icon: <Map size={18} />,
    label: "Career roadmaps",
    tag: "Personalized",
    heading: "A clear path from where you are to where you want to be",
    description:
      "Tell the career agent your goal. It maps every skill, certification, project, and milestone you need — in order — based on your current profile.",
    points: [
      "Role-specific roadmaps for 50+ career tracks",
      "Prioritized by your existing skills and gaps",
      "Updates dynamically as your profile grows",
    ],
    terminal: [
      { prompt: "Goal: ML Engineer at a product company", type: "command" },
      { prompt: "Analyzing current skills from profile...", type: "command" },
      { prompt: "✓ Roadmap generated — 6 milestones", type: "success" },
      { prompt: "✓ Next step: Complete ML Specialization", type: "success" },
      { prompt: "✓ 3 open-source projects suggested", type: "muted" },
    ],
  },
  {
    id: "internship",
    icon: <Briefcase size={18} />,
    label: "Internship recommendations",
    tag: "Matched",
    heading: "Internships that actually match your profile",
    description:
      "No more scrolling job boards. The internship agent surfaces roles that fit your skills, location preference, and availability — ranked by fit score.",
    points: [
      "Aggregates from Internshala, LinkedIn, and company portals",
      "Ranked by skill match and stipend",
      "One-click application tracking",
    ],
    terminal: [
      { prompt: "Searching internships for CSE · ML track", type: "command" },
      { prompt: "Filtering by remote · ₹10K+ stipend", type: "command" },
      { prompt: "✓ 24 internships found", type: "success" },
      { prompt: "✓ Top match: Google STEP — 94% fit", type: "success" },
      { prompt: "✓ 7 applications pre-filled", type: "muted" },
    ],
  },
  {
    id: "chat",
    icon: <MessageSquare size={18} />,
    label: "AI chat assistant",
    tag: "Always on",
    heading: "Ask anything about your academic journey",
    description:
      "The AI chat assistant knows your full profile — your marks, saved opportunities, deadlines, and goals. Every answer is personalized, not generic.",
    points: [
      "Context-aware answers using your stored profile",
      "Can search scholarships, explain criteria, draft SOPs",
      "Remembers your conversation history",
    ],
    terminal: [
      {
        prompt: "You: Am I eligible for the Inspire scholarship?",
        type: "command",
      },
      { prompt: "Checking your profile against criteria...", type: "command" },
      { prompt: "✓ Science stream confirmed", type: "success" },
      { prompt: "✓ Top 1% criterion: needs verification", type: "muted" },
      { prompt: "Drafting a checklist for you...", type: "muted" },
    ],
  },
];

const termColor = (type: string) => {
  if (type === "success") return "text-green-500 dark:text-green-400";
  if (type === "muted") return "text-yellow-600 dark:text-yellow-400";
  return "text-blue-600 dark:text-[#a8c7fa]";
};

export default function FeaturesSection() {
  const [active, setActive] = useState(FEATURES[0].id);
  const feature = FEATURES.find((f) => f.id === active)!;

  return (
    <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-16 sm:py-20 lg:py-24 transition-all duration-500">
      <div className="mb-8 sm:mb-12">
        <div className="inline-flex items-center gap-2 bg-[#0C65D2]/10 border border-[#0C65D2]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#0C65D2] dark:text-[#6fa8f5] mb-4 tracking-widest transition-all duration-500">
          <span className="w-1.5 h-1.5 rounded-full bg-[#0C65D2]" />
          WHAT EDUPILOT DOES
        </div>
        <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] tracking-tight transition-all duration-500">
          Six agents. One platform.
        </h2>
        <p className="mt-3 text-gray-500 dark:text-[#6B7280] font-mono text-sm max-w-lg transition-all duration-500">
          Each agent specializes in one job and does it exceptionally well.
          Together they cover your entire student lifecycle.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] xl:grid-cols-[280px_1fr] gap-4 sm:gap-6">
        <div className="flex flex-row lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0 scrollbar-hide">
          {FEATURES.map((f) => (
            <button
              key={f.id}
              onClick={() => setActive(f.id)}
              className={`flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 sm:py-3 text-left transition-all duration-200 cursor-pointer border-b-2 lg:border-b-0 lg:border-l-2 shrink-0 lg:shrink ${
                active === f.id
                  ? "border-[#0C65D2] bg-[#0C65D2]/8 dark:bg-[#0C65D2]/10 text-[#0C65D2]"
                  : "border-transparent text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] hover:bg-gray-50 dark:hover:bg-white/4 transition-all duration-500"
              }`}
            >
              <span className={`shrink-0 ${active === f.id ? "text-[#0C65D2]" : ""}`}>
                {f.icon}
              </span>
              <span className="font-mono text-xs sm:text-sm whitespace-nowrap lg:whitespace-normal">{f.label}</span>
            </button>
          ))}
        </div>

        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] overflow-hidden transition-all duration-500">
          <div className="bg-white dark:bg-[#161822] border-b border-black/10 dark:border-white/8 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-3 transition-all duration-500">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <div className="w-7 h-7 sm:w-8 sm:h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0">
                {feature.icon}
              </div>
              <div className="min-w-0">
                <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-xs sm:text-sm leading-tight">
                  {feature.heading}
                </p>
              </div>
            </div>
            <span className="font-mono text-[10px] bg-[#0C65D2]/10 text-[#0C65D2] dark:text-[#6fa8f5] border border-[#0C65D2]/20 px-2 sm:px-2.5 py-1 tracking-widest shrink-0 transition-all duration-500">
              {feature.tag}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
            <div className="p-4 sm:p-6 md:border-r border-b md:border-b-0 border-black/10 dark:border-white/8 transition-all duration-500">
              <p className="text-gray-600 dark:text-[#6B7280] text-xs sm:text-sm leading-relaxed mb-4 sm:mb-6 transition-all duration-500">
                {feature.description}
              </p>
              <ul className="flex flex-col gap-2.5 sm:gap-3">
                {feature.points.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 sm:gap-2.5">
                    <span className="text-[#0C65D2] mt-0.5 shrink-0">
                      <CheckCircle size={14} />
                    </span>
                    <span className="font-mono text-[11px] sm:text-[12px] text-gray-700 dark:text-[#a8c7fa] transition-all duration-500">
                      {pt}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 sm:p-6">
              <div className="border border-black/10 dark:border-white/8 overflow-hidden h-full transition-all duration-500">
                <div className="bg-gray-100 dark:bg-[#161822] px-3 sm:px-4 py-2 flex items-center gap-2 border-b border-black/10 dark:border-white/8 transition-all duration-500">
                  <span className="w-2 h-2 rounded-full bg-[#ff5f57]" />
                  <span className="w-2 h-2 rounded-full bg-[#febc2e]" />
                  <span className="w-2 h-2 rounded-full bg-[#28c840]" />
                  <span className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] ml-auto transition-all duration-500">
                    agent output
                  </span>
                </div>
                <div className="p-3 sm:p-4 font-mono text-[11px] sm:text-[12px] leading-loose overflow-x-auto">
                  {feature.terminal.map((line, i) => (
                    <div key={i} className="flex items-baseline gap-2">
                      <span className="text-[#0C65D2] select-none shrink-0">
                        ›
                      </span>
                      <span className={`${termColor(line.type)} whitespace-nowrap sm:whitespace-normal`}>
                        {line.prompt}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}