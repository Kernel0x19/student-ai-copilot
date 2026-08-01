"use client";
import { UserPlus, FileUp, Search, Bot, Rocket } from "lucide-react";

const STEPS = [
  {
    number: "01",
    icon: <UserPlus size={20} />,
    title: "Create your profile",
    description:
      "Sign up and fill in your academic details — college, stream, year, CGPA, and category. Takes under 2 minutes.",
    detail: "No credit card. No spam.",
  },
  {
    number: "02",
    icon: <FileUp size={20} />,
    title: "Upload your documents",
    description:
      "Upload marksheets, certificates, or income proofs. The OCR agent extracts everything automatically — no manual entry.",
    detail: "PDF, JPG, PNG supported.",
  },
  {
    number: "03",
    icon: <Search size={20} />,
    title: "Agents scan your opportunities",
    description:
      "Scholarship, internship, and eligibility agents run in parallel. They cross-reference your profile against hundreds of live sources.",
    detail: "Results ready in seconds.",
  },
  {
    number: "04",
    icon: <Bot size={20} />,
    title: "Get personalized recommendations",
    description:
      "Your dashboard surfaces only what you qualify for — ranked by deadline, fit score, and opportunity size. No noise.",
    detail: "Updated daily.",
  },
  {
    number: "05",
    icon: <Rocket size={20} />,
    title: "Apply and track progress",
    description:
      "Save opportunities, track application status, get deadline reminders, and ask the AI assistant anything along the way.",
    detail: "All in one place.",
  },
];

export default function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-14 sm:py-20 lg:py-24 border-t border-black/10 dark:border-white/8"
    >
      <div className="mb-10 sm:mb-14 lg:mb-16">
        <div className="inline-flex items-center gap-2 bg-[#0C65D2]/10 border border-[#0C65D2]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#0C65D2] dark:text-[#6fa8f5] mb-4 tracking-widest transition-all duration-500">
          <span className="w-1.5 h-1.5 rounded-full bg-[#0C65D2]" />
          HOW IT WORKS
        </div>
        <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] tracking-tight transition-all duration-500">
          From signup to results
          <span className="text-[#0C65D2]"> in minutes.</span>
        </h2>
        <p className="mt-3 text-gray-500 dark:text-[#6B7280] font-mono text-xs sm:text-sm max-w-lg transition-all duration-500">
          Five steps. No manual searching, no form hell, no missed deadlines.
        </p>
      </div>

      <div className="relative">
        <div className="absolute left-10 top-10 bottom-10 w-px bg-black/10 dark:bg-white/8 hidden lg:block transition-all duration-500" />

        <div className="flex flex-col gap-0">
          {STEPS.map((step, index) => (
            <div
              key={step.number}
              className="relative grid grid-cols-[64px_1fr] lg:grid-cols-[80px_1fr] gap-4 lg:gap-6 group"
            >
              <div className="flex flex-col items-center gap-2 z-10">
                <div className="w-16 h-16 lg:w-20 lg:h-20 border border-black/10 dark:border-white/8 bg-white dark:bg-[#0F1117] group-hover:border-[#0C65D2]/40 group-hover:bg-[#0C65D2]/5 dark:group-hover:bg-[#0C65D2]/10 flex flex-col items-center justify-center gap-1 shrink-0 transition-all duration-500">
                  <span className="font-mono text-[10px] text-[#0C65D2] tracking-widest">
                    {step.number}
                  </span>
                  <span className="text-gray-400 dark:text-[#6B7280] group-hover:text-[#0C65D2] transition-colors duration-500">
                    {step.icon}
                  </span>
                </div>
              </div>

              <div
                className={`pb-8 sm:pb-10 lg:pb-12 ${index === STEPS.length - 1 ? "pb-0" : ""}`}
              >
                <div className="flex flex-wrap items-baseline gap-2 sm:gap-3 mb-2">
                  <h3 className="font-syne text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
                    {step.title}
                  </h3>
                  <span className="font-mono text-[10px] sm:text-[11px] text-gray-400 dark:text-[#6B7280] border border-black/10 dark:border-white/8 px-2 py-0.5 transition-all duration-500">
                    {step.detail}
                  </span>
                </div>
                <p className="text-gray-500 dark:text-[#6B7280] text-xs sm:text-sm leading-relaxed max-w-xl transition-all duration-500">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}